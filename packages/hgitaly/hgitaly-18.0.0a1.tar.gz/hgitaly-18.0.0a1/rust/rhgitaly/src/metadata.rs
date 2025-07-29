// Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
//
// This software may be used and distributed according to the terms of the
// GNU General Public License version 2 or any later version.
// SPDX-License-Identifier: GPL-2.0-or-later
//! Handling of gRPC metadata
use tonic::metadata::{Ascii, MetadataMap, MetadataValue};

pub const HG_GIT_MIRRORING_MD_KEY: &str = "x-heptapod-hg-git-mirroring";
pub const NATIVE_PROJECT_MD_KEY: &str = "x-heptapod-hg-native";
pub const SKIP_HOOKS_MD_KEY: &str = "x-heptapod-skip-gl-hooks";
pub const ACCEPT_MR_IID_KEY: &str = "x-heptapod-accept-mr-iid";

pub fn correlation_id(metadata: &MetadataMap) -> Option<&MetadataValue<Ascii>> {
    metadata.get("x-gitlab-correlation-id")
}

pub fn get_boolean_md_value(metadata: &MetadataMap, key: &str, default: bool) -> bool {
    if let Some(v) = metadata.get(key) {
        match v.to_str() {
            Err(_) => default,
            Ok(s) => s.eq_ignore_ascii_case("true"),
        }
    } else {
        default
    }
}
