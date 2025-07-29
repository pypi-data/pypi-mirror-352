// Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
//
// This software may be used and distributed according to the terms of the
// GNU General Public License version 2 or any later version.
// SPDX-License-Identifier: GPL-2.0-or-later
use std::cmp::Ordering;
use std::fmt::{Debug, Formatter};
use std::path::Path;
use std::string::String;
use std::sync::Arc;

use async_stream::try_stream;
use futures::pin_mut;
use futures_core::stream::Stream;
use tokio::sync::mpsc;
use tokio_stream::{wrappers::ReceiverStream, StreamExt};

use tonic::{metadata::Ascii, metadata::MetadataValue, Code, Request, Response, Status, Streaming};
use tracing::{info, instrument};

use hg::revlog::changelog::Changelog;
use hg::NodePrefix;

use crate::config::Config;
use crate::errors::{
    status_with_structured_error, unimplemented_with_issue, FromReferenceNotFoundError,
};
use crate::git::ZERO_SHA_1;
use crate::gitaly::ref_service_client::RefServiceClient;
use crate::gitaly::ref_service_server::{RefService, RefServiceServer};
use crate::gitaly::{
    find_tag_error, list_refs_request, list_refs_response, DeleteRefsRequest, DeleteRefsResponse,
    FindAllBranchesRequest, FindAllBranchesResponse, FindAllRemoteBranchesRequest,
    FindAllRemoteBranchesResponse, FindAllTagsRequest, FindAllTagsResponse, FindBranchRequest,
    FindBranchResponse, FindDefaultBranchNameRequest, FindDefaultBranchNameResponse,
    FindLocalBranchesRequest, FindLocalBranchesResponse, FindRefsByOidRequest,
    FindRefsByOidResponse, FindTagError, FindTagRequest, FindTagResponse, GetTagMessagesRequest,
    GetTagMessagesResponse, GetTagSignaturesRequest, GetTagSignaturesResponse,
    ListBranchNamesContainingCommitRequest, ListBranchNamesContainingCommitResponse,
    ListRefsRequest, ListRefsResponse, ListTagNamesContainingCommitRequest,
    ListTagNamesContainingCommitResponse, RefExistsRequest, RefExistsResponse,
    ReferenceNotFoundError, Repository, SortDirection, Tag, UpdateReferencesRequest,
    UpdateReferencesResponse,
};
use crate::gitlab::revision::{existing_default_gitlab_branch, map_full_ref, RefError};
use crate::gitlab::state::{
    has_gitlab_default_branch, lookup_typed_ref_as_node, stream_gitlab_branches,
    stream_gitlab_special_refs, stream_gitlab_tags, stream_keep_arounds_file, StateFileError,
    TypedRef,
};
use crate::gitlab::{
    gitlab_branch_ref, gitlab_keep_around_ref, gitlab_special_ref_ref, gitlab_tag_ref,
    reference::RefPattern, GITLAB_BRANCH_REF_PREFIX, GITLAB_TAG_REF_PREFIX,
};
use crate::message::{self, parse_timestamp_line};
use crate::metadata::correlation_id;
use crate::repository::{
    aux_git_to_main_hg, default_repo_spec_error_status, is_repo_aux_git, load_repo, repo_store_vfs,
};
use crate::repository::{load_changelog_and_then, RepoLoadError, RequestWithRepo};
use crate::sidecar;
use crate::streaming::{AsyncResponseSender, BlockingResponseSender, ResultResponseStream};
use crate::util::{bytes_strings_as_str, tracing_span_id};

#[derive(Debug)]
pub struct RefServiceImpl {
    config: Arc<Config>,
    sidecar_servers: Arc<sidecar::Servers>,
}

impl RequestWithRepo for FindTagRequest {
    fn repository_ref(&self) -> Option<&Repository> {
        self.repository.as_ref()
    }
}

impl RequestWithRepo for FindDefaultBranchNameRequest {
    fn repository_ref(&self) -> Option<&Repository> {
        self.repository.as_ref()
    }
}

impl RequestWithRepo for ListRefsRequest {
    fn repository_ref(&self) -> Option<&Repository> {
        self.repository.as_ref()
    }
}

impl FromReferenceNotFoundError for FindTagError {
    fn from_reference_not_found_error(err: ReferenceNotFoundError) -> Self {
        FindTagError {
            error: Some(find_tag_error::Error::TagNotFound(err)),
        }
    }
}

#[tonic::async_trait]
impl RefService for RefServiceImpl {
    async fn find_default_branch_name(
        &self,
        request: Request<FindDefaultBranchNameRequest>,
    ) -> Result<Response<FindDefaultBranchNameResponse>, Status> {
        let (metadata, _ext, inner) = request.into_parts();

        self.inner_find_default_branch_name(inner, correlation_id(&metadata))
            .await
    }

    async fn find_local_branches(
        &self,
        request: Request<FindLocalBranchesRequest>,
    ) -> ResultResponseStream<FindLocalBranchesResponse> {
        // see also hgitaly#234
        sidecar::server_streaming!(self, request, RefServiceClient, find_local_branches)
    }

    async fn find_all_branches(
        &self,
        request: Request<FindAllBranchesRequest>,
    ) -> ResultResponseStream<FindAllBranchesResponse> {
        // see also hgitaly#234
        sidecar::server_streaming!(self, request, RefServiceClient, find_all_branches)
    }

    async fn find_all_tags(
        &self,
        request: Request<FindAllTagsRequest>,
    ) -> ResultResponseStream<FindAllTagsResponse> {
        // see also hgitaly#233
        sidecar::server_streaming!(self, request, RefServiceClient, find_all_tags)
    }

    async fn find_tag(
        &self,
        request: Request<FindTagRequest>,
    ) -> Result<Response<FindTagResponse>, Status> {
        let (metadata, _ext, inner) = request.into_parts();

        self.inner_find_tag(inner, correlation_id(&metadata)).await
    }

    async fn find_all_remote_branches(
        &self,
        request: Request<FindAllRemoteBranchesRequest>,
    ) -> ResultResponseStream<FindAllRemoteBranchesResponse> {
        sidecar::server_streaming!(self, request, RefServiceClient, find_all_remote_branches)
    }

    async fn ref_exists(
        &self,
        request: Request<RefExistsRequest>,
    ) -> Result<Response<RefExistsResponse>, Status> {
        let (metadata, _ext, inner) = request.into_parts();

        self.inner_ref_exists(inner, correlation_id(&metadata))
            .await
    }

    async fn find_branch(
        &self,
        request: Request<FindBranchRequest>,
    ) -> Result<Response<FindBranchResponse>, Status> {
        sidecar::unary!(self, request, RefServiceClient, find_branch)
    }

    #[instrument(name = "update_references", skip(self, request))]
    async fn update_references(
        &self,
        request: Request<Streaming<UpdateReferencesRequest>>,
    ) -> Result<Response<UpdateReferencesResponse>, Status> {
        sidecar::client_streaming!(self, request, RefServiceClient, update_references)
    }

    async fn delete_refs(
        &self,
        request: Request<DeleteRefsRequest>,
    ) -> Result<Response<DeleteRefsResponse>, Status> {
        sidecar::unary!(self, request, RefServiceClient, delete_refs)
    }

    async fn list_branch_names_containing_commit(
        &self,
        request: Request<ListBranchNamesContainingCommitRequest>,
    ) -> ResultResponseStream<ListBranchNamesContainingCommitResponse> {
        sidecar::server_streaming!(
            self,
            request,
            RefServiceClient,
            list_branch_names_containing_commit
        )
    }

    async fn list_tag_names_containing_commit(
        &self,
        request: Request<ListTagNamesContainingCommitRequest>,
    ) -> ResultResponseStream<ListTagNamesContainingCommitResponse> {
        sidecar::server_streaming!(
            self,
            request,
            RefServiceClient,
            list_tag_names_containing_commit
        )
    }

    async fn get_tag_signatures(
        &self,
        _request: Request<GetTagSignaturesRequest>,
    ) -> ResultResponseStream<GetTagSignaturesResponse> {
        Err(unimplemented_with_issue(75))
    }

    async fn get_tag_messages(
        &self,
        request: Request<GetTagMessagesRequest>,
    ) -> ResultResponseStream<GetTagMessagesResponse> {
        sidecar::server_streaming!(self, request, RefServiceClient, get_tag_messages)
    }

    async fn list_refs(
        &self,
        request: Request<ListRefsRequest>,
    ) -> ResultResponseStream<ListRefsResponse> {
        let (metadata, _ext, inner) = request.into_parts();

        self.inner_list_refs(inner, correlation_id(&metadata)).await
    }

    async fn find_refs_by_oid(
        &self,
        request: Request<FindRefsByOidRequest>,
    ) -> Result<Response<FindRefsByOidResponse>, Status> {
        sidecar::unary!(self, request, RefServiceClient, find_refs_by_oid)
    }
}

struct RefExistsTracingRequest<'a>(&'a RefExistsRequest);

impl Debug for RefExistsTracingRequest<'_> {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("RefExistRequest")
            .field("repository", &self.0.repository)
            .field("ref", &String::from_utf8_lossy(&self.0.r#ref))
            .finish()
    }
}

struct FindTagTracingRequest<'a>(&'a FindTagRequest);

impl Debug for FindTagTracingRequest<'_> {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("FindTagRequest")
            .field("repository", &self.0.repository)
            .field("tag_name", &String::from_utf8_lossy(&self.0.tag_name))
            .finish()
    }
}

impl prost::Name for FindTagError {
    const NAME: &'static str = "FindTagError";
    const PACKAGE: &'static str = "gitaly";
}

struct ListRefsTracingRequest<'a>(&'a ListRefsRequest);

impl Debug for ListRefsTracingRequest<'_> {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("ListRefsRequest")
            .field("repository", &self.0.repository)
            .field("head", &self.0.head)
            .field("patterns", &bytes_strings_as_str(&self.0.patterns))
            .field(
                "pointing_at_oids",
                &bytes_strings_as_str(&self.0.pointing_at_oids),
            )
            .finish()
    }
}

// References chunks have more elements than commit chunks,
// because a reference is smaller than a commit. One day we'll do a lazy chunker based
// on actual wire size, as Gitaly uses (not systematically, though)
const LIST_REFS_CHUNK_SIZE: usize = 100;

impl RefServiceImpl {
    #[instrument(name = "find_default_branch_name", skip(self, request))]
    async fn inner_find_default_branch_name(
        &self,
        mut request: FindDefaultBranchNameRequest,
        correlation_id: Option<&MetadataValue<Ascii>>,
    ) -> Result<Response<FindDefaultBranchNameResponse>, Status> {
        tracing_span_id!();
        info!("Processing, repository={:?}", &request.repository);

        if let Some(main_hg_path) = aux_git_to_main_hg(&request) {
            let main_hg_path = main_hg_path.to_owned();
            if let Some(repo) = request.repository.as_mut() {
                repo.relative_path = main_hg_path;
            }
        }

        let store_vfs = repo_store_vfs(&self.config, &request.repository)
            .await
            .map_err(default_repo_spec_error_status)?;

        Ok(Response::new(FindDefaultBranchNameResponse {
            name: existing_default_gitlab_branch(&store_vfs)
                .await
                .map_err(|e| {
                    Status::internal(format!(
                        "Error reading or checking GitLab default branch: {:?}",
                        e
                    ))
                })?
                .map(|ref name_node| gitlab_branch_ref(&name_node.0))
                .unwrap_or_else(Vec::new),
        }))
    }

    #[instrument(name = "ref_exists", skip(self, request), fields(span_id))]
    async fn inner_ref_exists(
        &self,
        request: RefExistsRequest,
        correlation_id: Option<&MetadataValue<Ascii>>,
    ) -> Result<Response<RefExistsResponse>, Status> {
        tracing_span_id!();
        info!(
            "Processing, request={:?}",
            RefExistsTracingRequest(&request)
        );

        let store_vfs = repo_store_vfs(&self.config, &request.repository)
            .await
            .map_err(default_repo_spec_error_status)?;

        let value = match map_full_ref(&store_vfs, &request.r#ref, |_tr| (), |_ka| ()).await {
            Ok(()) => Ok(true),
            Err(RefError::NotFound) => Ok(false),
            Err(RefError::MissingRefName) => Ok(false),
            Err(RefError::NotAFullRef) => Err(Status::invalid_argument("invalid refname")),
            Err(RefError::GitLabStateFileError(e)) => Err(Status::internal(format!("{:?}", e))),
        }?;

        Ok(Response::new(RefExistsResponse { value }))
    }

    #[instrument(name = "find_tag", skip(self, request), fields(span_id))]
    async fn inner_find_tag(
        &self,
        request: FindTagRequest,
        correlation_id: Option<&MetadataValue<Ascii>>,
    ) -> Result<Response<FindTagResponse>, Status> {
        tracing_span_id!();
        info!("Processing, request={:?}", FindTagTracingRequest(&request));

        let store_vfs = repo_store_vfs(&self.config, &request.repository)
            .await
            .map_err(default_repo_spec_error_status)?;

        let tag_name = request.tag_name.clone();
        let commit =
            match lookup_typed_ref_as_node(stream_gitlab_tags(&store_vfs).await?, &tag_name)
                .await
                .map_err(|e| Status::internal(format!("GitLab state file error: {:?}", e)))?
            {
                None => {
                    return Err(status_with_structured_error(
                        Code::NotFound,
                        "tag does not exist",
                        FindTagError::reference_not_found_error(gitlab_tag_ref(&tag_name)),
                    ));
                }
                Some(node) => {
                    // TODO totally duplicated from FindCommit. Find a way to make a helper!
                    load_changelog_and_then(
                        self.config.clone(),
                        request,
                        default_repo_spec_error_status,
                        move |_req, _repo, cl| {
                            message::commit_for_node_prefix_or_none(cl, node.into()).map_err(|e| {
                                Status::internal(format!("Repository corruption {:?}", e))
                            })
                        },
                    )
                    .await
                }
            }?;

        Ok(Response::new(FindTagResponse {
            tag: Some(Tag {
                name: tag_name,
                target_commit: commit,
                ..Default::default()
            }),
        }))
    }

    #[instrument(name = "list_refs", skip(self, request), fields(span_id))]
    async fn inner_list_refs(
        &self,
        request: ListRefsRequest,
        correlation_id: Option<&MetadataValue<Ascii>>,
    ) -> ResultResponseStream<ListRefsResponse> {
        tracing_span_id!();
        info!("Processing, request={:?}", ListRefsTracingRequest(&request));

        let (tx, rx) = mpsc::channel(128);
        let tx: AsyncResponseSender<_> = tx.into();

        if is_repo_aux_git(&request) {
            // TODO cases of missing repo and empty repo
            tx.send(Ok(ListRefsResponse {
                references: vec![list_refs_item_str(b"ALL", ZERO_SHA_1)],
            }))
            .await;

            return Ok(Response::new(Box::pin(ReceiverStream::new(rx))));
        }

        let config = self.config.clone();
        let store_vfs = repo_store_vfs(&config, &request.repository)
            .await
            .map_err(default_repo_spec_error_status)?;

        let req_repo = request.repository.as_ref().cloned();

        let (sort_key, sort_direction) = request
            .sort_by
            .as_ref()
            .map_or((0, 0), |sb| (sb.key, sb.direction));

        tokio::spawn(async move {
            let stream = list_refs_stream(&request, &store_vfs);
            pin_mut!(stream); // needed for iteration

            let mut collect = Vec::new();
            while let Some(res) = stream.next().await {
                match res {
                    Err(e) => {
                        tx.send(Err(Status::internal(format!("State file error: {:?}", e))))
                            .await;
                    }
                    Ok(gitlab_ref) => collect.push(gitlab_ref),
                }
            }
            if sort_key == list_refs_request::sort_by::Key::Refname as i32 {
                if sort_direction == SortDirection::Ascending as i32 {
                    collect.sort_by(|r1, r2| r1.name.cmp(&r2.name))
                } else {
                    collect.sort_by(|r1, r2| r2.name.cmp(&r1.name))
                }
            }
            let min_len = if request.head { 2 } else { 1 };
            if collect.len() >= min_len {
                for chunk in collect.chunks(LIST_REFS_CHUNK_SIZE) {
                    // HEAD is not returned by Gitaly if no other ref matches criteria
                    tx.send(Ok(ListRefsResponse {
                        references: chunk.to_vec(),
                    }))
                    .await;
                }
            }
        });

        let output_stream = ReceiverStream::new(
            if sort_key == list_refs_request::sort_by::Key::Refname as i32 {
                rx
            } else {
                // we need to spawn a separate thread to open changelog,
                // retrieve all references in there,
                // collect them again and finally sort using changelog information
                let (repo_tx, repo_rx) = mpsc::channel(1);
                let repo_tx: BlockingResponseSender<_> = repo_tx.into();
                tokio::task::spawn_blocking(move || {
                    list_refs_date_sort(sort_direction, req_repo, &config, rx, &repo_tx)
                        .unwrap_or_else(|e| {
                            repo_tx.send(Err(e));
                        })
                });
                repo_rx
            },
        );

        Ok(Response::new(Box::pin(output_stream)))
    }
}

fn list_refs_date_sort(
    sort_direction: i32,
    req_repo: Option<Repository>,
    config: &Config,
    mut receiver: mpsc::Receiver<Result<ListRefsResponse, Status>>,
    sender: &BlockingResponseSender<ListRefsResponse>,
) -> Result<(), Status> {
    let mut collect = Vec::new();
    while let Some(res) = receiver.blocking_recv() {
        collect.extend_from_slice(&res?.references);
    }

    let repo = load_repo(config, req_repo.as_ref()).map_err(|e| match e {
        RepoLoadError::SpecError(e) => default_repo_spec_error_status(e),
        RepoLoadError::LoadError(e) => {
            Status::internal(format!("Error loading repository: {:?}", e))
        }
    })?;
    let cl = repo
        .changelog()
        .map_err(|e| Status::internal(format!("Could not open changelog: {:?}", e)))?;

    if sort_direction == SortDirection::Ascending as i32 {
        collect.sort_by(|r1, r2| list_refs_cmp_date(sender, &cl, r1, r2));
    } else {
        collect.sort_by(|r1, r2| list_refs_cmp_date(sender, &cl, r2, r1));
    }
    for chunk in collect.chunks(LIST_REFS_CHUNK_SIZE) {
        sender.send(Ok(ListRefsResponse {
            references: chunk.to_vec(),
        }));
    }
    Ok(())
}

/// Just syntactical shortcut, case where target sha is UTF-8 slice
fn list_refs_item_str(name: &[u8], target: &str) -> list_refs_response::Reference {
    list_refs_response::Reference {
        name: name.to_vec(),
        target: target.to_owned(),
        ..Default::default()
    }
}

/// Compare dates of changesets targeted by the references, sending errors to the channel
fn list_refs_cmp_date(
    sender: &BlockingResponseSender<ListRefsResponse>,
    changelog: &Changelog,
    ref1: &list_refs_response::Reference,
    ref2: &list_refs_response::Reference,
) -> Ordering {
    let date1 = list_refs_ref_date_error_send(sender, changelog, ref1);
    let date2 = list_refs_ref_date_error_send(sender, changelog, ref2);
    date1.cmp(&date2)
}

/// Same as [`list_refs_ref_date`], sending error to the given Sender
///
/// In case of error, it is sent to the channel, and a value is still returned, but should not
/// matter, as the error should reach the client.
fn list_refs_ref_date_error_send(
    sender: &BlockingResponseSender<ListRefsResponse>,
    changelog: &Changelog,
    reference: &list_refs_response::Reference,
) -> u64 {
    list_refs_ref_date(changelog, reference).unwrap_or_else(|e| {
        sender.send(Err(e));
        0
    })
}

fn list_refs_ref_date(
    changelog: &Changelog,
    reference: &list_refs_response::Reference,
) -> Result<u64, Status> {
    let hex = &reference.target;
    let node = NodePrefix::from_hex(hex)
        .map_err(|_| Status::internal(format!("Invalid node format in reference: '{}'", hex)))?;
    let data = changelog.data_for_node(node).map_err(|e| {
        Status::internal(format!(
            "Could not access changelog data for '{}': {:?}",
            hex, e
        ))
    })?;
    Ok(parse_timestamp_line(data.timestamp_line())
        .map_err(|e| Status::internal(format!("Invalid timestamp line for {}: {}", hex, e)))?
        .0 as u64)
}

/// Just syntactical shortcut, case where target sha is bytes slice
fn list_refs_item_bytes(name: &[u8], target: &[u8]) -> list_refs_response::Reference {
    list_refs_response::Reference {
        name: name.to_vec(),
        target: String::from_utf8_lossy(target).to_string(),
        ..Default::default()
    }
}

/// Simple matcher for `patterns` and `pointing_at_oids`
///
/// In a later move, we might want to introduce a threshold above which it uses
/// internally a [`Hashset`] or something alike. Hence in particular, we make no effort
/// to avoid copying the oids from a [`ListRefsRequest`] (not so easy with `stream!`),
/// as it is only done once and a future more efficient version will have to do it anyway.
/// Besides, it is only lucky that the incoming type is bytes and could be later deprecated
/// in the protocol in favour of UTF-8 strings, since oids are ASCII anyway.
struct ListRefsMatcher<'req> {
    patterns: Vec<RefPattern<'req>>,
    oids: Vec<Vec<u8>>,
}

impl<'req> ListRefsMatcher<'req> {
    fn new(request: &'req ListRefsRequest) -> Self {
        let patterns: Vec<RefPattern> = request
            .patterns
            .iter()
            .map(|pat| RefPattern::new(pat))
            .collect();
        Self {
            patterns,
            oids: request.pointing_at_oids.to_vec(),
        }
    }

    fn match_oid(&self, oid: &[u8]) -> bool {
        if self.oids.is_empty() {
            true
        } else {
            self.oids.iter().any(|wanted| wanted == oid)
        }
    }

    fn ref_path_if_match(
        &self,
        typed_ref: &TypedRef,
        full_path_builder: impl FnOnce(&[u8]) -> Vec<u8>,
    ) -> Option<Vec<u8>> {
        if !self.match_oid(&typed_ref.target_sha) {
            return None;
        }
        // TODO perf we could perform the matching before doing any allocation.
        // (taking the prefix for this type of TypedRef as argument instead
        // of the builder closure).
        // It could make a difference when most of the refs are discarded
        let ref_path = full_path_builder(&typed_ref.name);
        if self.ref_patterns_match(&ref_path) {
            return Some(ref_path);
        }
        None
    }

    fn keep_around_ref_path_if_match(&self, ka: &str) -> Option<Vec<u8>> {
        if !self.match_oid(ka.as_bytes()) {
            return None;
        }
        let ref_path = gitlab_keep_around_ref(ka);
        if self.ref_patterns_match(&ref_path) {
            return Some(ref_path);
        }
        None
    }

    fn ref_patterns_match(&self, ref_path: &[u8]) -> bool {
        for pattern in self.patterns.iter() {
            if pattern.matches(ref_path) {
                return true;
            }
        }
        false
    }
}

fn list_refs_stream<'r>(
    request: &'r ListRefsRequest,
    store_vfs: &'r Path,
) -> impl Stream<Item = Result<list_refs_response::Reference, StateFileError>> + 'r {
    try_stream! {
        let mut pseudo_all = false;

        let mut iter_all = true;
        let mut iter_branches = false;
        let mut iter_tags = false;

        if request.patterns.len() == 1 {
            let pat = &request.patterns[0];
            if pat == b"refs/" {
                pseudo_all = true;
            } else if pat.starts_with(GITLAB_BRANCH_REF_PREFIX) {
                iter_branches = true;
                iter_all = false;
            } else if pat.starts_with(GITLAB_TAG_REF_PREFIX) {
                iter_tags = true;
                iter_all = false;
            }
        }

        if !request.pointing_at_oids.is_empty() {
            pseudo_all = false;
        }

        let matcher = ListRefsMatcher::new(request);

        let branches = if iter_branches || iter_all {
            stream_gitlab_branches(store_vfs).await?
        } else {
            None
        };

        let tags = if iter_tags || iter_all {
            stream_gitlab_tags(store_vfs).await?
        } else {
            None
        };

        let special_refs = if iter_all {
            stream_gitlab_special_refs(store_vfs).await?
        } else {
            None
        };

        let keep_arounds = if iter_all {
            stream_keep_arounds_file(store_vfs).await?
        } else {
            None
        };

        if pseudo_all {
            // cheap yet a bit fuzzy way to check if the repo is empty
            if has_gitlab_default_branch(store_vfs).await? {
                yield list_refs_item_str(b"ALL", ZERO_SHA_1);
            }
        }

        if request.head {
            if let Some((_branch, node)) = existing_default_gitlab_branch(store_vfs).await?
            {
                // TODO double cloning (format + ref + clone in list_refs_item)
                yield list_refs_item_str(b"HEAD", &format!("{:x}", node));
            }
        }

        // We preorder as branches, keep-arounds, special_refs and tags to minimize the number
        // of transpositions in final sort by ref path.
        if let Some(branch_stream) = branches {
            for await res in branch_stream {
                let branch = res?;
                if let Some(as_ref) = matcher.ref_path_if_match(&branch, gitlab_branch_ref) {
                    yield list_refs_item_bytes(&as_ref, &branch.target_sha);
                }
            }
        }

        if let Some(ka_stream) = keep_arounds {
            for await res in ka_stream {
                let ka = res?;
                if let Some(as_ref) = matcher.keep_around_ref_path_if_match(&ka) {
                    yield list_refs_item_str(&as_ref, &ka);
                }
            }
        }

        if let Some(special_refs_stream) = special_refs {
            for await res in special_refs_stream {
                let sref = res?;
                if let Some(as_ref) = matcher.ref_path_if_match(&sref, gitlab_special_ref_ref) {
                    yield list_refs_item_bytes(&as_ref, &sref.target_sha);
                }
            }
        }

        if let Some(tag_stream) = tags {
            for await res in tag_stream {
                let tag = res?;
                if let Some(as_ref) = matcher.ref_path_if_match(&tag, gitlab_tag_ref) {
                    yield list_refs_item_bytes(&as_ref, &tag.target_sha);
                }
            }
        }

    }
}

/// Takes care of boilerplate that would instead be in the startup sequence.
pub fn ref_server(
    config: &Arc<Config>,
    sidecar_servers: &Arc<sidecar::Servers>,
) -> RefServiceServer<RefServiceImpl> {
    RefServiceServer::new(RefServiceImpl {
        config: config.clone(),
        sidecar_servers: sidecar_servers.clone(),
    })
}
