// Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
//
// This software may be used and distributed according to the terms of the
// GNU General Public License version 2 or any later version.
// SPDX-License-Identifier: GPL-2.0-or-later
pub mod reference;
pub mod revision;
pub mod state;

pub const GITLAB_BRANCH_REF_PREFIX: &[u8] = b"refs/heads/";
pub const GITLAB_SPECIAL_REF_PREFIX: &[u8] = b"refs/";
pub const GITLAB_TAG_REF_PREFIX: &[u8] = b"refs/tags/";
pub const GITLAB_KEEP_AROUND_REF_PREFIX: &[u8] = b"refs/keep-around/";

/// Return the full GitLab ref path of a GitLab branch
pub fn gitlab_branch_ref(name: &[u8]) -> Vec<u8> {
    // TODO allocate just once (final size is already known), same in sibling functions
    let mut res = GITLAB_BRANCH_REF_PREFIX.to_vec();
    res.extend_from_slice(name);
    res
}

/// Return the full GitLab ref path of a GitLab tag
pub fn gitlab_tag_ref(name: &[u8]) -> Vec<u8> {
    let mut res = GITLAB_TAG_REF_PREFIX.to_vec();
    res.extend_from_slice(name);
    res
}

/// Return the full ref path of a GitLab special ref
pub fn gitlab_special_ref_ref(name: &[u8]) -> Vec<u8> {
    let mut res = GITLAB_SPECIAL_REF_PREFIX.to_vec();
    res.extend_from_slice(name);
    res
}

/// Return the full ref path of a GitLab keep-around
pub fn gitlab_keep_around_ref(oid: &str) -> Vec<u8> {
    let mut res = GITLAB_KEEP_AROUND_REF_PREFIX.to_vec();
    res.extend_from_slice(oid.as_bytes());
    res
}

pub fn gitlab_branch_from_ref(ref_name: &[u8]) -> Option<&[u8]> {
    if ref_name.starts_with(GITLAB_BRANCH_REF_PREFIX) {
        Some(&ref_name[GITLAB_BRANCH_REF_PREFIX.len()..])
    } else {
        None
    }
}
