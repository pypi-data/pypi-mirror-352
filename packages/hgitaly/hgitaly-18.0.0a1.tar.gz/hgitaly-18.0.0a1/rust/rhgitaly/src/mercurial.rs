// Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
//
// This software may be used and distributed according to the terms of the
// GNU General Public License version 2 or any later version.
//
// SPDX-License-Identifier: GPL-2.0-or-later
//! Utilities for Mercurial content handling
use std::cmp::min;
use std::collections::VecDeque;
use std::num::NonZeroU8;
use tracing::warn;

use hg::errors::HgError;
use hg::repo::Repo;
use hg::revlog::changelog::Changelog;
use hg::revlog::manifest::{Manifest, ManifestEntry, Manifestlog};
use hg::revlog::{Node, NodePrefix, RevlogError, NULL_REVISION};
use hg::utils::hg_path::HgPath;

use crate::gitaly::{tree_entry::EntryType, ObjectType, TreeEntry};
use crate::util::common_subpath_split;

use super::git;
use super::oid::{blob_oid, tree_oid};
use tracing::debug;

#[derive(Debug, Default)]
/// Common representation for metadata of content presented as if they were Git inner objects.
///
/// The intended application if for blob and trees gRPC methods. These metadata
/// are to be converted to final gRPC messages (including data chunks),
/// depending on actual needs.
///
/// Fields that are both not always needed and potentially expensive to compute are
/// enclosed in an [`Option`] and meant to be set by the service layer, since they
/// are specific to the method being implemented.
pub struct ObjectMetadata {
    pub oid: String,
    pub obj_type: ObjectType,
    pub size: i64,
    /// Object permissions, as expected by Gitaly clients, hence encoded as Git would.
    pub mode: i32,
    /// Useful in the `GetBlobs` gRPC method, but not in `GetBlob`.
    /// The first field is the revision (UTF-8 in both methods),
    /// the second is the path.
    pub revision_path: Option<(String, Vec<u8>)>,
}

pub const EXECUTABLE_FLAG: Option<NonZeroU8> = NonZeroU8::new(b'x');
pub const LINK_FLAG: Option<NonZeroU8> = NonZeroU8::new(b'l');
pub const TREE_FLAG: Option<NonZeroU8> = NonZeroU8::new(b't');

/// Encode as Git would the file permissions recorded in a [`ManifestEntry`].
fn git_perms(entry: &ManifestEntry) -> Result<i32, HgError> {
    match entry.flags {
        None => Ok(git::OBJECT_MODE_NON_EXECUTABLE),
        EXECUTABLE_FLAG => Ok(git::OBJECT_MODE_EXECUTABLE),
        LINK_FLAG => Ok(git::OBJECT_MODE_LINK),
        // TREE_FLAG is actually only used in treemanifest, but stil possible
        TREE_FLAG => Ok(git::OBJECT_MODE_TREE),
        Some(f) => Err(HgError::CorruptedRepository(format!(
            "Unsupported manifest flag {}",
            f
        ))),
    }
}

/// Return data and metadata for an expected blob at given changeset and path.
///
/// The changeset is specified as a [`NodePrefix`], hence resolution can fail, with
/// [`RevlogError::InvalidRevision`] when it does not exist.
///
/// If the path does not exist in the specified changeset, `Ok(None)` is returned.
pub fn lookup_blob(
    repo: &Repo,
    changeset_node_prefix: NodePrefix,
    path: &[u8],
) -> Result<Option<(Vec<u8>, ObjectMetadata)>, RevlogError> {
    let changelog = repo.changelog()?;
    let manifestlog = repo.manifestlog()?;
    // Not using `repo.manifest_for_node()` because we will need the changelog entry
    // to provide a full changeset Node ID in the final construction.
    changelog_entry_manifest(&changelog, &manifestlog, changeset_node_prefix)?
        .map(|(cs_node, manifest)| {
            let hg_path = HgPath::new(path);
            manifest
                .find_by_path(hg_path)? // closure now has to return Result
                .map(|manifest_entry| read_blob(repo, &cs_node, manifest_entry, hg_path))
                .transpose() // to return Result
        })
        .transpose()
        .map(|oo| oo.flatten())
}

pub fn changelog_entry_manifest(
    changelog: &Changelog,
    manifestlog: &Manifestlog,
    changeset_node_prefix: NodePrefix,
) -> Result<Option<(Node, Manifest)>, RevlogError> {
    let rev = changelog.rev_from_node(changeset_node_prefix)?;
    if rev == NULL_REVISION {
        return Ok(None);
    }
    // TODO submit upstream an `entry_for_rev` to avoid back-and-forth
    // between Revision and UncheckedRevision
    let changelog_entry = changelog.entry_for_unchecked_rev(rev.into())?;
    let manifest = manifestlog.data_for_node(changelog_entry.data()?.manifest_node()?.into())?;
    Ok(Some((*changelog_entry.as_revlog_entry().node(), manifest)))
}

pub fn read_blob(
    repo: &Repo,
    changeset_node: &Node,
    manifest_entry: ManifestEntry,
    hg_path: &HgPath,
) -> Result<(Vec<u8>, ObjectMetadata), RevlogError> {
    {
        let file_node = manifest_entry.node_id()?;
        let file_log = repo.filelog(hg_path)?;
        let fl_data = file_log.data_for_node(file_node)?;
        let data = fl_data.into_file_data()?;
        let size = data.len();
        Ok((
            data,
            ObjectMetadata {
                size: size as i64,
                mode: git_perms(&manifest_entry)?,
                obj_type: ObjectType::Blob,
                oid: blob_oid(changeset_node, hg_path.as_bytes()),
                ..Default::default()
            },
        ))
    }
}

/// Relevant metadata a directory item , which can be a file or a sub-directory
///
/// The `manifest_entry` field is `None` if and only if the item is a sub-directory.
/// Otherwise the [`ManifestEntry`] provides metadata of the file.
#[derive(Debug)]
pub struct DirectoryEntry<'m> {
    pub relative_path: Vec<u8>,
    pub mode: i32,
    pub manifest_entry: Option<ManifestEntry<'m>>,
}

impl DirectoryEntry<'_> {
    pub fn is_file(&self) -> bool {
        self.manifest_entry.is_some()
    }
}

impl PartialEq for DirectoryEntry<'_> {
    fn eq(&self, other: &Self) -> bool {
        if self.relative_path != other.relative_path || self.mode != other.mode {
            false
        } else {
            match (self.manifest_entry.as_ref(), other.manifest_entry.as_ref()) {
                (Some(e), Some(f)) => manifest_entry_eq(e, f),
                (None, None) => true,
                _ => false,
            }
        }
    }
}

fn manifest_entry_eq<'m>(e: &ManifestEntry<'m>, f: &ManifestEntry<'m>) -> bool {
    // TODO upstream implement PartialEq for ManifestEntry, pretty much as this
    e.path == f.path && e.hex_node_id == f.hex_node_id
}

impl Eq for DirectoryEntry<'_> {}

/// Represent the content at some path, either a file, with a [`ManifestEntry`] for metadata,
/// or a directory with its entries.
#[derive(Debug)]
pub enum PathContent<'m> {
    File(ManifestEntry<'m>),
    Directory(Vec<DirectoryEntry<'m>>),
    NotFound,
}

impl PartialEq for PathContent<'_> {
    fn eq(&self, other: &Self) -> bool {
        match (self, other) {
            (PathContent::NotFound, PathContent::NotFound) => true,
            (PathContent::File(e), PathContent::File(f)) => manifest_entry_eq(e, f),
            (PathContent::Directory(v), PathContent::Directory(w)) => v == w,
            _ => false,
        }
    }
}

impl Eq for PathContent<'_> {}

/// Return the list of entries that are sitting right at path.
///
/// Similarly to `/bin/ls`, if `path` is a directory, its contents are listed, otherwise
/// file metadata are returned.
pub fn ls_path<'m>(manifest: &'m Manifest, path: &[u8]) -> Result<PathContent<'m>, RevlogError> {
    inner_ls_path(manifest.iter(), path)
}

fn inner_ls_path<'m, IM>(manifest: IM, path: &[u8]) -> Result<PathContent<'m>, RevlogError>
where
    IM: IntoIterator<Item = Result<ManifestEntry<'m>, HgError>>,
{
    let mut listing = Vec::new();
    let pl = path.len();

    for entry_res in manifest {
        let entry = entry_res?;
        let ep = entry.path.as_bytes();
        if !ep.starts_with(path) {
            if !listing.is_empty() {
                break;
            } else {
                continue;
            }
        }
        debug!("Considering manifest path {:?}", ep);
        // exact match is always first, because manifest is lexicographically ordered
        if ep.len() == pl {
            // so ep == path
            debug!("Exact match for {:?} and {:?}", ep, pl);
            return Ok(PathContent::File(entry));
        }

        debug!("Checking if we are in a subdir with {:?}", ep);
        if pl > 0 && ep[pl] != b'/' {
            if !listing.is_empty() {
                break;
            } else {
                continue;
            }
        }

        let rel_path = if pl > 0 { &ep[pl + 1..] } else { ep };
        debug!("Analyzing subdir for {:?} (rel_path={:?})", ep, rel_path);
        // first iteration on split can be `None` only if rel_path is empty,
        // which would mean in this context that entry.path has a trailing slash
        // (guaranteed not to happen in the Manifest data structure)
        if let Some(sub_rel_path) = rel_path.split(|c| *c == b'/').next() {
            if sub_rel_path.len() == rel_path.len() {
                listing.push(DirectoryEntry {
                    relative_path: rel_path.to_vec(),
                    mode: git_perms(&entry)?,
                    manifest_entry: Some(entry),
                });
            } else {
                if let Some(previous) = listing.last() {
                    if previous.relative_path == sub_rel_path {
                        continue;
                    }
                }
                listing.push(DirectoryEntry {
                    relative_path: sub_rel_path.to_vec(),
                    mode: git::OBJECT_MODE_TREE,
                    manifest_entry: None,
                });
            }
        }
    }
    Ok(if listing.is_empty() {
        PathContent::NotFound
    } else {
        PathContent::Directory(listing)
    })
}

/// Read the given manifest directory, sort with sub-directories first,
/// and collect separately with offset and limit
///
/// Offset and limit are for both sub-directories and files. For instance, if `limit` is less than
/// the number of sub-directories, the collection of files is empty, even if some have
/// lexicographically smaller names than all sub-directories.
///
/// If the given directory is not found, returns `None`.
pub fn ls_path_sorted_dirs_first<S, F>(
    manifest: &Manifest,
    path: &[u8],
    offset: usize,
    limit: usize,
) -> Result<Option<(S, F)>, RevlogError>
where
    S: Extend<Vec<u8>> + Default,
    F: FromIterator<Vec<u8>>,
{
    inner_ls_path_sorted_dirs_first(manifest.iter(), path, offset, limit)
}

fn inner_ls_path_sorted_dirs_first<'m, IM, S, F>(
    manifest: IM,
    path: &[u8],
    offset: usize,
    limit: usize,
) -> Result<Option<(S, F)>, RevlogError>
where
    IM: IntoIterator<Item = Result<ManifestEntry<'m>, HgError>>,
    S: Extend<Vec<u8>> + Default,
    F: FromIterator<Vec<u8>>,
{
    // TODO maybe more efficient for later iteration to have a Vec of paths and the index
    // of the separation between subtrees and files

    // we won't neet that much capacity for both, but it is reasonable and spare us
    // repeated allocations.
    let mut subtrees = S::default();
    let mut file_paths = Vec::with_capacity(offset + limit);
    // we need to construct both vectors so that (with subtrees first) the
    // pushing at most `limit` elements in both vecs, then we'll trim further
    // because we cannot know until we've iterated to the end in the worst case
    // how many subtrees there are
    let (mut off_count, mut tree_lim_count, mut file_lim_count) = (0, 0, 0);
    match inner_ls_path(manifest, path)? {
        PathContent::NotFound => {
            return Ok(None);
        }
        PathContent::File(_entry) => {
            warn!(
                "Requested path means a directory, but a file was found instead in manifest \
                     (after trimmming trailing slashes)."
            );
            return Ok(None);
        }
        PathContent::Directory(dir_entries) => {
            for dir_entry in dir_entries.into_iter() {
                if tree_lim_count >= limit {
                    break;
                }
                if dir_entry.manifest_entry.is_none() {
                    off_count += 1;
                    if off_count > offset {
                        tree_lim_count += 1;
                        subtrees.extend(Some(dir_entry.relative_path));
                    }
                } else if file_lim_count < limit + offset {
                    file_lim_count += 1;
                    file_paths.push(dir_entry.relative_path)
                }
            }
        }
    }
    let file_paths: F = if tree_lim_count == 0 {
        // subtrees were at most just enough to reach offset
        let end = min(offset - off_count + limit, file_paths.len());
        file_paths[(offset - off_count)..end]
            .iter()
            .cloned()
            .collect()
    } else {
        file_paths.truncate(limit - tree_lim_count);
        file_paths.into_iter().collect()
    };

    Ok(Some((subtrees, file_paths)))
}

/// An iterator over manifest, yielding only entries from a given sub directory
///
/// This could be upstreamed to hg-core, where it would benefit the (private) binary search
/// method to avoid linear scanning for the directory starting point.
struct ManifestDirIterator<'a, 'm, IM>
where
    IM: Iterator<Item = Result<ManifestEntry<'m>, HgError>>,
{
    /// Path of the directory, without trailing slash
    path: &'a [u8],
    in_dir: bool,
    manifest_iter: IM,
}

impl<'a, 'm, IM> ManifestDirIterator<'a, 'm, IM>
where
    IM: Iterator<Item = Result<ManifestEntry<'m>, HgError>>,
{
    fn new(manifest_iter: IM, path: &'a [u8]) -> Self {
        ManifestDirIterator {
            path,
            manifest_iter,
            in_dir: false,
        }
    }

    /// Return the length of the string prefix corresponding to path, hence with trailing slash.
    ///
    /// This is meant so that, if `self.path` is `"foo"`, then `"foo/bar"[self.path_len()..]` is
    /// `"bar"`. It also handles the case where `self.path` is empty correctly, sparing the callers
    /// to check for this special case.
    fn prefix_len(&self) -> usize {
        let pl = self.path.len();
        if pl == 0 {
            0
        } else {
            pl + 1
        }
    }

    /// Derive from `self.path` a string prefix ready for concatenation with a relative path.
    fn prefix(&self) -> Vec<u8> {
        let mut v = self.path.to_vec();
        if !v.is_empty() {
            v.push(b'/');
        }
        v
    }

    fn is_path_inside(&self, other_path: &[u8]) -> bool {
        let pl = self.path.len();
        pl == 0
            || (other_path.len() > pl
                && other_path[pl] == b'/'
                && other_path.starts_with(self.path))
    }
}

impl<'a, 'm, IM> Iterator for ManifestDirIterator<'a, 'm, IM>
where
    IM: Iterator<Item = Result<ManifestEntry<'m>, HgError>>,
{
    type Item = Result<ManifestEntry<'m>, HgError>;

    fn next(&mut self) -> Option<Self::Item> {
        while let Some(entry_res) = self.manifest_iter.next() {
            match entry_res {
                Err(e) => {
                    return Some(Err(e));
                }
                Ok(entry) => {
                    if !self.is_path_inside(entry.path.as_bytes()) {
                        if self.in_dir {
                            // we're leaving the directory to list, job done
                            return None;
                        } else {
                            // we have not entered the directory to list yet
                            continue;
                        }
                    }
                    return Some(Ok(entry));
                }
            }
        }
        None
    }
}

/// Result of splitting a path for first and last segment
struct PathWithTopLevelDir<'a> {
    /// The full path, for flat_path computation
    path: &'a [u8],
    /// The top level directory in the path (first segment)
    top_level: &'a [u8],
}

/// Analyze the given `sub_path`, splitting the directory part to get its top-level.
///
/// The given (full) `entry_path` is for error messages only.
///
/// If `sub_path` is a top-level file, `None` is returned. Otherwise, the returned
/// [`PathWithTopLevelDir`] encloses the directory part of `sub_path`.
///
/// The computation relies on expectations for Mercurial manifeset entries, which are reflected
/// by the returned errors. Using the full entry path here should help with error inspection.
fn split_dir_and_top_level<'a>(
    sub_path: &'a [u8],
    entry_path: &[u8],
) -> Result<Option<PathWithTopLevelDir<'a>>, HgError> {
    let mut rsplit = sub_path.rsplitn(2, |c| *c == b'/');
    rsplit.next().ok_or_else(|| {
        HgError::corrupted(format!(
            "Manifest entry with trailing slash: {:?}",
            entry_path
        ))
    })?;
    rsplit
        .next()
        .map(|dir_path| {
            let top_level = dir_path.splitn(2, |c| *c == b'/').next().ok_or_else(|| {
                HgError::corrupted(format!(
                    "Manifest entry with double slash: {:?}",
                    entry_path
                ))
            })?;
            Ok(PathWithTopLevelDir {
                top_level,
                path: dir_path,
            })
        })
        .transpose()
}

/// Iterator yielding a [`TreeEntry`] without flat path for each top-level file or directory in a
/// manifest directory.
pub struct DirIteratorWithoutFlatPaths<'a, 'm, IM>
where
    IM: Iterator<Item = Result<ManifestEntry<'m>, HgError>>,
{
    /// Is expected to be the repetition of an incoming request "oid" field,
    /// often something like `branch/default` and not a real OID
    commit_oid: String,
    changeset_node: Node,
    manifest_dir_iter: ManifestDirIterator<'a, 'm, IM>,
    current_subdir: &'m [u8],
}

impl<'a, 'm, IM> DirIteratorWithoutFlatPaths<'a, 'm, IM>
where
    IM: Iterator<Item = Result<ManifestEntry<'m>, HgError>>,
{
    pub fn new(commit_oid: String, changeset_node: Node, manifest: IM, path: &'a [u8]) -> Self {
        Self {
            commit_oid,
            changeset_node,
            manifest_dir_iter: ManifestDirIterator::new(manifest, path),
            current_subdir: &[],
        }
    }

    fn tree_entry(
        &self,
        path: &[u8],
        oid: String,
        obj_type: EntryType,
        mode: i32,
    ) -> Result<TreeEntry, HgError> {
        Ok(TreeEntry {
            oid,
            mode,
            commit_oid: self.commit_oid.clone(),
            path: path.to_vec(),
            r#type: obj_type as i32,
            flat_path: Vec::new(),
        })
    }
}

impl<'a, 'm, IM> Iterator for DirIteratorWithoutFlatPaths<'a, 'm, IM>
where
    IM: Iterator<Item = Result<ManifestEntry<'m>, HgError>>,
{
    type Item = Result<TreeEntry, HgError>;

    fn next(&mut self) -> Option<Self::Item> {
        while let Some(entry_res) = self.manifest_dir_iter.next() {
            match entry_res {
                Err(e) => {
                    return Some(Err(e));
                }
                Ok(entry) => {
                    let ep = entry.path.as_bytes();
                    let sp = &ep[self.manifest_dir_iter.prefix_len()..];
                    match split_dir_and_top_level(sp, ep) {
                        Ok(None) => match git_perms(&entry) {
                            Err(e) => return Some(Err(e)),
                            Ok(mode) => {
                                return Some(self.tree_entry(
                                    ep,
                                    blob_oid(&self.changeset_node, ep),
                                    EntryType::Blob,
                                    mode,
                                ));
                            }
                        },
                        Ok(Some(split)) => {
                            if split.top_level != self.current_subdir {
                                self.current_subdir = split.top_level;
                                let full_path = &ep
                                    [..self.manifest_dir_iter.prefix_len() + split.top_level.len()];
                                return Some(self.tree_entry(
                                    full_path,
                                    tree_oid(&self.changeset_node, full_path),
                                    EntryType::Tree,
                                    git::OBJECT_MODE_TREE,
                                ));
                            }
                        }
                        Err(e) => return Some(Err(e)),
                    }
                }
            }
        }
        None
    }
}

pub struct RecursiveDirIterator<'a, 'm, IM>
where
    IM: Iterator<Item = Result<ManifestEntry<'m>, HgError>>,
{
    /// Is expected to be the repetition of an incoming request "oid" field,
    /// often something like `branch/default` and not a real OID
    commit_oid: String,
    changeset_node: Node,
    manifest_dir_iter: ManifestDirIterator<'a, 'm, IM>,
    current_subdir: &'m [u8],
    /// Queue of `TreeEntry` messages that have to be emitted.
    ///
    /// Each manifest entry can give rise to several `TreeEntry` messages to yield,
    /// because of intermediate directories. Hence we store them in this queue.
    ///
    /// Each call to `next()` pops either pops from the queue or consumes one or several
    /// manifest entries, possibly pushing several more entries in the queue beside yielding
    /// one.
    to_yield: VecDeque<Result<TreeEntry, HgError>>,
}

impl<'a, 'm, IM> RecursiveDirIterator<'a, 'm, IM>
where
    IM: Iterator<Item = Result<ManifestEntry<'m>, HgError>>,
{
    pub fn new(commit_oid: String, changeset_node: Node, manifest: IM, path: &'a [u8]) -> Self {
        Self {
            commit_oid,
            changeset_node,
            manifest_dir_iter: ManifestDirIterator::new(manifest, path),
            current_subdir: "".as_ref(),
            to_yield: VecDeque::new(),
        }
    }

    fn tree_entry(
        &self,
        path: &[u8],
        oid: String,
        obj_type: EntryType,
        mode: i32,
    ) -> Result<TreeEntry, HgError> {
        Ok(TreeEntry {
            oid,
            mode,
            commit_oid: self.commit_oid.clone(),
            path: path.to_vec(),
            r#type: obj_type as i32,
            flat_path: Vec::new(), // resulting flat_path is always default for recursive queries
        })
    }
}

impl<'a, 'm, IM> Iterator for RecursiveDirIterator<'a, 'm, IM>
where
    IM: Iterator<Item = Result<ManifestEntry<'m>, HgError>>,
{
    type Item = Result<TreeEntry, HgError>;

    fn next(&mut self) -> Option<Self::Item> {
        if let Some(entry) = self.to_yield.pop_front() {
            return Some(entry);
        }

        while let Some(entry_res) = self.manifest_dir_iter.next() {
            match entry_res {
                Err(e) => {
                    return Some(Err(e));
                }
                Ok(entry) => {
                    let ep = entry.path.as_bytes();
                    let sp = &ep[self.manifest_dir_iter.prefix_len()..];

                    let (mut subdir, rem_idx) = common_subpath_split(self.current_subdir, sp);
                    for i in rem_idx..sp.len() {
                        if sp[i] != b'/' {
                            continue;
                        }
                        subdir = &sp[..i];
                        let fulldir = &ep[..i + self.manifest_dir_iter.prefix_len()];
                        self.to_yield.push_back(self.tree_entry(
                            fulldir,
                            tree_oid(&self.changeset_node, fulldir),
                            EntryType::Tree,
                            git::OBJECT_MODE_TREE,
                        ));
                    }
                    self.current_subdir = subdir;

                    match git_perms(&entry) {
                        Err(e) => {
                            self.to_yield.push_back(Err(e));
                        }
                        Ok(mode) => {
                            self.to_yield.push_back(self.tree_entry(
                                ep,
                                blob_oid(&self.changeset_node, ep),
                                EntryType::Blob,
                                mode,
                            ));
                        }
                    }
                }
            }
        }
        self.to_yield.pop_front()
    }
}

/// Non recursive iterator over a directory, including "flat path" information
pub struct DirIteratorWithFlatPaths<'a, 'm, IM>
where
    IM: Iterator<Item = Result<ManifestEntry<'m>, HgError>>,
{
    /// Is expected to be the repetition of an incoming request "oid" field,
    /// often something like `branch/default` and not a real OID
    commit_oid: String,
    changeset_node: Node,
    manifest_dir_iter: ManifestDirIterator<'a, 'm, IM>,
    /// Queue of `TreeEntry` messages that have to be emitted.
    ///
    /// Each manifest entry can give rise to several `TreeEntry` messages to yield,
    /// because of intermediate directories. Hence we store them in this queue.
    ///
    /// each call to `next()` either pops an element from the queue or reads next manifest
    /// line.
    to_yield: VecDeque<Result<TreeEntry, HgError>>,
}

impl<'a, 'm, IM> DirIteratorWithFlatPaths<'a, 'm, IM>
where
    IM: Iterator<Item = Result<ManifestEntry<'m>, HgError>>,
{
    pub fn new(commit_oid: String, changeset_node: Node, manifest: IM, path: &'a [u8]) -> Self {
        Self {
            commit_oid,
            changeset_node,
            manifest_dir_iter: ManifestDirIterator::new(manifest, path),
            to_yield: VecDeque::new(),
        }
    }

    fn dir_tree_entry(&self, rel_path: &[u8], rel_flat_path: &[u8]) -> Result<TreeEntry, HgError> {
        let mut path = self.manifest_dir_iter.prefix();
        path.extend_from_slice(rel_path);
        let mut flat_path = self.manifest_dir_iter.prefix();
        flat_path.extend_from_slice(rel_flat_path);
        Ok(TreeEntry {
            oid: tree_oid(&self.changeset_node, &path),
            mode: git::OBJECT_MODE_TREE,
            commit_oid: self.commit_oid.clone(),
            path,
            r#type: EntryType::Tree as i32,
            flat_path,
        })
    }

    fn file_tree_entry(&self, path: &[u8], mode: i32) -> Result<TreeEntry, HgError> {
        Ok(TreeEntry {
            mode,
            oid: blob_oid(&self.changeset_node, path),
            commit_oid: self.commit_oid.clone(),
            path: path.to_vec(),
            r#type: EntryType::Blob as i32,
            flat_path: path.to_vec(),
        })
    }

    fn enqueue_file_entry(&mut self, entry: &ManifestEntry) {
        match git_perms(entry) {
            Err(e) => {
                self.to_yield.push_back(Err(e));
            }
            Ok(mode) => {
                self.to_yield
                    .push_back(self.file_tree_entry(entry.path.as_bytes(), mode));
            }
        }
    }

    /// Main scanning loop for [`Iterator`] implementation
    ///
    /// Returns `Result<()>` whereas `next()` returns instead of `Option<Result<T>>`
    /// to make error treatment easier (question-mark operator). Therefore this method
    /// only pushes to `self.to_yield`.
    fn inner_next(&mut self) -> Result<(), HgError> {
        let mut current_subdir: Option<&[u8]> = None;
        let mut current_flat_path: &[u8] = &[];

        while let Some(entry_res) = self.manifest_dir_iter.next() {
            let entry = entry_res?;
            let ep = entry.path.as_bytes();
            let sp = &ep[self.manifest_dir_iter.prefix_len()..];

            if let Some(subdir) = current_subdir {
                let (common_flat_path, rem_idx) = common_subpath_split(current_flat_path, sp);
                if rem_idx != 0 {
                    current_flat_path = common_flat_path
                } else {
                    // we are leaving current_subdir, so schedule to yield it and clear it
                    // so that the later check whether we are entering a new one or simply have
                    // a top-level file runs.
                    self.to_yield
                        .push_back(self.dir_tree_entry(subdir, current_flat_path));
                    current_subdir = None
                }
            }

            if current_subdir.is_none() {
                match split_dir_and_top_level(sp, ep)? {
                    None => {
                        self.enqueue_file_entry(&entry);
                        break;
                    }
                    Some(split) => {
                        current_subdir = Some(split.top_level);
                        current_flat_path = split.path;
                    }
                }
            }
        }
        // If the last entry is not a top-level file, then the loop ends without yielding
        // `current_subdir`, hence we need to do it now.
        if let Some(subdir) = current_subdir {
            self.to_yield
                .push_back(self.dir_tree_entry(subdir, current_flat_path));
        }
        Ok(())
    }
}

impl<'a, 'm, IM> Iterator for DirIteratorWithFlatPaths<'a, 'm, IM>
where
    IM: Iterator<Item = Result<ManifestEntry<'m>, HgError>>,
{
    type Item = Result<TreeEntry, HgError>;

    fn next(&mut self) -> Option<Self::Item> {
        if let Some(entry) = self.to_yield.pop_front() {
            return Some(entry);
        }

        match self.inner_next() {
            Ok(()) => self.to_yield.pop_front(),
            Err(e) => Some(Err(e)),
        }
    }
}

#[cfg(test)]
mod tests {

    use super::*;

    /// Return a [`ManifestEntry`] suitable for tests that care only about paths
    fn path_manifest_entry(path: &'static str) -> ManifestEntry {
        ManifestEntry {
            path: HgPath::new(path.as_bytes()),
            hex_node_id: b"",
            flags: None,
        }
    }

    fn clone_manifest_entry<'a>(e: &'a ManifestEntry<'_>) -> ManifestEntry<'a> {
        ManifestEntry {
            path: e.path,
            hex_node_id: e.hex_node_id,
            flags: e.flags,
        }
    }

    /// Return something suitable to test the algorithm behind [`ls_path`] from only paths.
    ///
    /// For [`ls_path`] correctness, the node ids and flags don't matter much, hence we give
    /// them fixed, arbitrary values.
    /// For convenience paths are string slices, static not to bother with lifetimes.
    fn paths_manifest(paths: Vec<&'static str>) -> Vec<Result<ManifestEntry, HgError>> {
        paths
            .into_iter()
            .map(|path| Ok(path_manifest_entry(path)))
            .collect()
    }

    #[test]
    fn test_ls_path_simple() {
        let manifest = paths_manifest(vec!["bar", "foo/some", "foo0"]);
        assert_eq!(
            inner_ls_path(manifest.into_iter(), b"foo").unwrap(),
            PathContent::Directory(vec![DirectoryEntry {
                relative_path: b"some".to_vec(),
                mode: git::OBJECT_MODE_NON_EXECUTABLE,
                manifest_entry: Some(path_manifest_entry("foo/some")),
            }])
        );
        let manifest = paths_manifest(vec!["bar", "foo/some", "foo0"]);
        assert_eq!(
            inner_ls_path(manifest.into_iter(), b"").unwrap(),
            PathContent::Directory(vec![
                DirectoryEntry {
                    relative_path: b"bar".to_vec(),
                    mode: git::OBJECT_MODE_NON_EXECUTABLE,
                    manifest_entry: Some(path_manifest_entry("bar")),
                },
                DirectoryEntry {
                    relative_path: b"foo".to_vec(),
                    mode: git::OBJECT_MODE_TREE,
                    manifest_entry: None
                },
                DirectoryEntry {
                    relative_path: b"foo0".to_vec(),
                    mode: git::OBJECT_MODE_NON_EXECUTABLE,
                    manifest_entry: Some(path_manifest_entry("foo0")),
                },
            ])
        );

        // other climbing case
        let manifest = paths_manifest(vec!["foo/some", "other"]);
        assert_eq!(
            inner_ls_path(manifest.into_iter(), b"foo").unwrap(),
            PathContent::Directory(vec![DirectoryEntry {
                relative_path: b"some".to_vec(),
                mode: git::OBJECT_MODE_NON_EXECUTABLE,
                manifest_entry: Some(path_manifest_entry("foo/some")),
            }])
        );

        // other diving case
        let manifest = paths_manifest(vec!["foo.", "foo/some"]);
        assert_eq!(
            inner_ls_path(manifest.into_iter(), b"foo").unwrap(),
            PathContent::Directory(vec![DirectoryEntry {
                relative_path: b"some".to_vec(),
                mode: git::OBJECT_MODE_NON_EXECUTABLE,
                manifest_entry: Some(path_manifest_entry("foo/some")),
            }])
        );

        let manifest = paths_manifest(vec!["bar", "foo/some", "foo0"]);
        assert_eq!(
            inner_ls_path(manifest.into_iter(), b"bar").unwrap(),
            PathContent::File(path_manifest_entry("bar")),
        );

        let manifest = paths_manifest(vec!["bar", "foo/some", "foo0"]);
        assert_eq!(
            inner_ls_path(manifest.into_iter(), b"foo0").unwrap(),
            PathContent::File(path_manifest_entry("foo0")),
        );

        let manifest = paths_manifest(vec!["bar", "foo"]);
        assert_eq!(
            inner_ls_path(manifest.into_iter(), b"alien").unwrap(),
            PathContent::NotFound,
        );
    }

    #[test]
    fn test_ls_path_dir_several_files() {
        let manifest = paths_manifest(vec!["foo.", "foo/a", "foo/b", "foo0"]);
        assert_eq!(
            inner_ls_path(manifest.into_iter(), b"foo").unwrap(),
            PathContent::Directory(vec![
                DirectoryEntry {
                    relative_path: b"a".to_vec(),
                    mode: git::OBJECT_MODE_NON_EXECUTABLE,
                    manifest_entry: Some(path_manifest_entry("foo/a")),
                },
                DirectoryEntry {
                    relative_path: b"b".to_vec(),
                    mode: git::OBJECT_MODE_NON_EXECUTABLE,
                    manifest_entry: Some(path_manifest_entry("foo/b")),
                }
            ])
        )
    }

    #[test]
    fn test_ls_path_dir_with_sub() {
        let manifest = paths_manifest(vec![
            "foo.",
            "foo/a",
            "foo/sub/a",
            "foo/sub/b",
            "foo/subb",
            "foo0",
        ]);
        assert_eq!(
            inner_ls_path(manifest.into_iter(), b"foo").unwrap(),
            PathContent::Directory(vec![
                DirectoryEntry {
                    relative_path: b"a".to_vec(),
                    mode: git::OBJECT_MODE_NON_EXECUTABLE,
                    manifest_entry: Some(path_manifest_entry("foo/a")),
                },
                DirectoryEntry {
                    relative_path: b"sub".to_vec(),
                    mode: git::OBJECT_MODE_TREE,
                    manifest_entry: None,
                },
                DirectoryEntry {
                    relative_path: b"subb".to_vec(),
                    mode: git::OBJECT_MODE_NON_EXECUTABLE,
                    manifest_entry: Some(path_manifest_entry("foo/subb")),
                },
            ])
        )
    }

    fn ls_path_sorted_dirs_first<'m>(
        manifest: &[&'static str],
        path: &[u8],
        offset: usize,
        limit: usize,
    ) -> Result<Option<(Vec<Vec<u8>>, Vec<Vec<u8>>)>, RevlogError> {
        inner_ls_path_sorted_dirs_first(
            paths_manifest(manifest.to_vec()).into_iter(),
            path,
            offset,
            limit,
        )
    }

    #[test]
    fn test_ls_path_sorted_subdirs_first() -> Result<(), RevlogError> {
        let manifest = vec![
            "foo.",
            "foo/a",
            "foo/sub/a",
            "foo/sub/b",
            "foo/subb",
            "foo/yetanother",
            "foo2/a",
            "foo2/b",
            "topfile1",
            "topfile2",
        ];

        let (subtrees, files) = ls_path_sorted_dirs_first(&manifest, b"foo", 0, 2)?.unwrap();
        assert_eq!(subtrees, vec![b"sub".to_vec()]);
        assert_eq!(files, vec![b"a".to_vec()]);

        // cases where offset is after dirs
        let (subtrees, files) = ls_path_sorted_dirs_first(&manifest, b"foo", 3, 1)?.unwrap();
        assert!(subtrees.is_empty());
        assert_eq!(files, vec![b"yetanother".to_vec()]);

        let (subtrees, files) = ls_path_sorted_dirs_first(&manifest, b"foo", 1, 2)?.unwrap();
        assert!(subtrees.is_empty());
        assert_eq!(files, vec![b"a".to_vec(), b"subb".to_vec()]);

        let (subtrees, files) = ls_path_sorted_dirs_first(&manifest, b"foo", 1, 3)?.unwrap();
        assert!(subtrees.is_empty());
        assert_eq!(
            files,
            vec![b"a".to_vec(), b"subb".to_vec(), b"yetanother".to_vec()]
        );

        let (subtrees, files) = ls_path_sorted_dirs_first(&manifest, b"foo", 2, 2)?.unwrap();
        assert!(subtrees.is_empty());
        assert_eq!(files, vec![b"subb".to_vec(), b"yetanother".to_vec()]);

        let (subtrees, files) = ls_path_sorted_dirs_first(&manifest, b"foo", 1, 100)?.unwrap();
        assert!(subtrees.is_empty());
        assert_eq!(
            files,
            vec![b"a".to_vec(), b"subb".to_vec(), b"yetanother".to_vec()]
        );

        // cases where offset is in dirs
        let (subtrees, files) = ls_path_sorted_dirs_first(&manifest, b"", 0, 0)?.unwrap();
        assert!(subtrees.is_empty());
        assert!(files.is_empty());

        let (subtrees, files) = ls_path_sorted_dirs_first(&manifest, b"", 0, 1)?.unwrap();
        assert_eq!(subtrees, vec![b"foo".to_vec()]);
        assert!(files.is_empty());

        let (subtrees, files) = ls_path_sorted_dirs_first(&manifest, b"", 0, 2)?.unwrap();
        assert_eq!(subtrees, vec![b"foo".to_vec(), b"foo2".to_vec()]);
        assert!(files.is_empty());

        let (subtrees, files) = ls_path_sorted_dirs_first(&manifest, b"", 0, 3)?.unwrap();
        assert_eq!(subtrees, vec![b"foo".to_vec(), b"foo2".to_vec()]);
        assert_eq!(files, vec![b"foo.".to_vec()]);

        let (subtrees, files) = ls_path_sorted_dirs_first(&manifest, b"", 1, 2)?.unwrap();
        assert_eq!(subtrees, vec![b"foo2".to_vec()]);
        assert_eq!(files, vec![b"foo.".to_vec()]);

        let (subtrees, files) = ls_path_sorted_dirs_first(&manifest, b"", 1, 3)?.unwrap();
        assert_eq!(subtrees, vec![b"foo2".to_vec()]);
        assert_eq!(files, vec![b"foo.".to_vec(), b"topfile1".to_vec()]);

        let (subtrees, files) = ls_path_sorted_dirs_first(&manifest, b"", 1, 100)?.unwrap();
        assert_eq!(subtrees, vec![b"foo2".to_vec()]);
        assert_eq!(
            files,
            vec![b"foo.".to_vec(), b"topfile1".to_vec(), b"topfile2".to_vec()]
        );

        Ok(())
    }

    #[test]
    fn test_manifest_dir_iterator() {
        let manifest = paths_manifest(vec!["foo/a", "foo/sub/a", "top-file"]);
        let iter = ManifestDirIterator::new(manifest.into_iter(), b"");
        let res: Vec<&[u8]> = iter.map(|r| r.unwrap().path.as_bytes()).collect();
        assert_eq!(
            res,
            vec![
                b"foo/a".as_ref(),
                b"foo/sub/a".as_ref(),
                b"top-file".as_ref(),
            ]
        );

        let manifest = paths_manifest(vec![
            "foo.",
            "foo/a",
            "foo/sub/a",
            "foo/sub/b",
            "foo/subb",
            "foo0",
            "other/file",
        ]);
        let iter = ManifestDirIterator::new(manifest.into_iter(), b"foo");
        let res: Vec<&[u8]> = iter.map(|r| r.unwrap().path.as_bytes()).collect();
        assert_eq!(
            res,
            vec![
                b"foo/a".as_ref(),
                b"foo/sub/a".as_ref(),
                b"foo/sub/b".as_ref(),
                b"foo/subb".as_ref(),
            ]
        );
    }

    fn testing_blob_flat_path(cs_node: &Node, path: &[u8], flat_path: &[u8]) -> TreeEntry {
        TreeEntry {
            path: path.to_vec(),
            r#type: EntryType::Blob as i32,
            mode: git::OBJECT_MODE_NON_EXECUTABLE,
            commit_oid: "branch/test".to_owned(),
            oid: blob_oid(cs_node, path),
            flat_path: flat_path.to_vec(),
        }
    }

    fn testing_blob(cs_node: &Node, path: &[u8]) -> TreeEntry {
        testing_blob_flat_path(cs_node, path, &[])
    }

    fn testing_tree_flat_path(cs_node: &Node, path: &[u8], flat_path: &[u8]) -> TreeEntry {
        TreeEntry {
            path: path.to_vec(),
            r#type: EntryType::Tree as i32,
            mode: git::OBJECT_MODE_TREE,
            commit_oid: "branch/test".to_owned(),
            oid: tree_oid(cs_node, path),
            flat_path: flat_path.to_vec(),
        }
    }

    fn testing_tree(cs_node: &Node, path: &[u8]) -> TreeEntry {
        testing_tree_flat_path(cs_node, path, &[])
    }

    #[test]
    fn test_dir_iterator_without_flat_paths() {
        let cs_node = Node::from_hex(b"1234567812345678123456781234567812345678").unwrap();

        let manifest = paths_manifest(vec!["foo/a"]);
        let iter = DirIteratorWithoutFlatPaths::new(
            "branch/test".to_owned(),
            cs_node,
            manifest.into_iter(),
            &[],
        );
        let res: Vec<TreeEntry> = iter.map(|r| r.unwrap()).collect();
        assert_eq!(res, vec![testing_tree(&cs_node, b"foo"),]);

        let manifest = paths_manifest(vec![
            "foo.",
            "foo/a",
            "foo/sub/a",
            "foo/sub/b",
            "foo/subb",
            "foo0",
        ]);
        let iter = DirIteratorWithoutFlatPaths::new(
            "branch/test".to_owned(),
            cs_node,
            manifest.into_iter(),
            b"foo",
        );
        let res: Vec<TreeEntry> = iter.map(|r| r.unwrap()).collect();
        assert_eq!(
            res,
            vec![
                testing_blob(&cs_node, b"foo/a"),
                testing_tree(&cs_node, b"foo/sub"),
                testing_blob(&cs_node, b"foo/subb"),
            ]
        );

        let manifest = paths_manifest(vec!["foo.", "foo/a", "foo/sub/ssub/b", "foo/subb", "foo0"]);
        let iter = DirIteratorWithoutFlatPaths::new(
            "branch/test".to_owned(),
            cs_node,
            manifest.into_iter(),
            b"foo",
        );
        let res: Vec<TreeEntry> = iter.map(|r| r.unwrap()).collect();
        assert_eq!(
            res,
            vec![
                testing_blob(&cs_node, b"foo/a"),
                testing_tree(&cs_node, b"foo/sub"),
                testing_blob(&cs_node, b"foo/subb"),
            ]
        );
    }

    #[test]
    fn test_recursive_dir_iter() {
        let cs_node = Node::from_hex(b"1234567812345678123456781234567812345678").unwrap();

        let manifest = paths_manifest(vec!["foo/a"]);
        let iter =
            RecursiveDirIterator::new("branch/test".to_owned(), cs_node, manifest.into_iter(), &[]);
        let res: Vec<TreeEntry> = iter.map(|r| r.unwrap()).collect();
        assert_eq!(
            res,
            vec![
                testing_tree(&cs_node, b"foo"),
                testing_blob(&cs_node, b"foo/a"),
            ]
        );

        let manifest = paths_manifest(vec![
            "foo.",
            "foo/a",
            "foo/sub/a",
            "foo/sub/b",
            "foo/subb",
            "foo0",
        ]);
        let iter = RecursiveDirIterator::new(
            "branch/test".to_owned(),
            cs_node,
            manifest.into_iter(),
            b"foo",
        );
        let res: Vec<TreeEntry> = iter.map(|r| r.unwrap()).collect();
        assert_eq!(
            res,
            vec![
                testing_blob(&cs_node, b"foo/a"),
                testing_tree(&cs_node, b"foo/sub"),
                testing_blob(&cs_node, b"foo/sub/a"),
                testing_blob(&cs_node, b"foo/sub/b"),
                testing_blob(&cs_node, b"foo/subb"),
            ]
        );

        let manifest = paths_manifest(vec![
            "foo.",
            "foo/a",
            "foo/sub/a",
            "foo/sub/ssub/b",
            "foo/subb",
            "foo0",
        ]);
        let iter = RecursiveDirIterator::new(
            "branch/test".to_owned(),
            cs_node,
            manifest.into_iter(),
            b"foo",
        );
        let res: Vec<TreeEntry> = iter.map(|r| r.unwrap()).collect();
        assert_eq!(
            res,
            vec![
                testing_blob(&cs_node, b"foo/a"),
                testing_tree(&cs_node, b"foo/sub"),
                testing_blob(&cs_node, b"foo/sub/a"),
                testing_tree(&cs_node, b"foo/sub/ssub"),
                testing_blob(&cs_node, b"foo/sub/ssub/b"),
                testing_blob(&cs_node, b"foo/subb"),
            ]
        );
    }

    fn assert_with_flat_paths(
        manifest: &[Result<ManifestEntry, HgError>],
        dir: &[u8],
        expected: Vec<(EntryType, &[u8], &[u8])>,
    ) {
        let cs_node = Node::from_hex(b"1234567812345678123456781234567812345678").unwrap();
        let iter = DirIteratorWithFlatPaths::new(
            "branch/test".to_owned(),
            cs_node,
            manifest
                .iter()
                .map(|res| Ok(clone_manifest_entry(res.as_ref().unwrap()))),
            dir,
        );
        let expected: Vec<TreeEntry> = expected
            .into_iter()
            .map(|(etype, path, flat_path)| match etype {
                EntryType::Tree => testing_tree_flat_path(&cs_node, path, flat_path),
                EntryType::Blob => testing_blob_flat_path(&cs_node, path, flat_path),
                EntryType::Commit => {
                    panic!("Unexpected commit entry")
                }
            })
            .collect();

        let collected: Vec<_> = iter.map(|r| r.unwrap()).collect();
        assert_eq!(collected, expected);
    }

    #[test]
    fn test_dir_iter_flat_paths() {
        let manifest = paths_manifest(vec!["foo/a"]);
        assert_with_flat_paths(&manifest, b"", vec![(EntryType::Tree, b"foo", b"foo")]);

        let manifest = paths_manifest(vec![
            "foo.",
            "foo/a",
            "foo/sub/a",
            "foo/sub/b",
            "foo/subb",
            "foo0",
        ]);
        assert_with_flat_paths(
            &manifest,
            b"foo",
            vec![
                (EntryType::Blob, b"foo/a", b"foo/a"),
                (EntryType::Tree, b"foo/sub", b"foo/sub"),
                (EntryType::Blob, b"foo/subb", b"foo/subb"),
            ],
        );

        let manifest = paths_manifest(vec!["foo.", "foo/a", "foo/sub/ssub/b", "foo/subb", "foo0"]);
        assert_with_flat_paths(
            &manifest,
            b"foo",
            vec![
                (EntryType::Blob, b"foo/a", b"foo/a"),
                (EntryType::Tree, b"foo/sub", b"foo/sub/ssub"),
                (EntryType::Blob, b"foo/subb", b"foo/subb"),
            ],
        );
    }

    #[test]
    fn test_flat_paths_issue_heptapod_1464() {
        let manifest = paths_manifest(vec![
            "a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p/test",
            "a/b/c/d/e/f/g/h/i/j/k/l/test",
            "a/b/c/d/e/f/g/h/test",
            "a/b/c/d/test",
        ]);

        assert_with_flat_paths(&manifest, b"", vec![(EntryType::Tree, b"a", b"a/b/c/d")]);
        assert_with_flat_paths(&manifest, b"a", vec![(EntryType::Tree, b"a/b", b"a/b/c/d")]);
        assert_with_flat_paths(
            &manifest,
            b"a/b/c/d",
            vec![
                (EntryType::Tree, b"a/b/c/d/e", b"a/b/c/d/e/f/g/h"),
                (EntryType::Blob, b"a/b/c/d/test", b"a/b/c/d/test"),
            ],
        );
    }
}
