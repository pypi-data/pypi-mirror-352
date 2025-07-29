use std::fs::File;
use std::io::Read;

use build_const::ConstWriter;

fn build_constants() -> Result<(), Box<dyn std::error::Error>> {
    // use `for_build` in `build.rs`
    let mut consts = ConstWriter::for_build("constants")?.finish_dependencies();
    let mut version = String::new();
    File::open("../../hgitaly/VERSION")?.read_to_string(&mut version)?;

    // Add a value that is a result of "complex" calculations
    consts.add_value("HGITALY_VERSION", "&str", version.trim());
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    build_constants()?;
    tonic_build::configure()
        .build_server(true)
        .out_dir("src/generated")
        .protoc_arg("--experimental_allow_proto3_optional")
        .generate_default_stubs(true)
        .compile(
            &[
                "../../protos/analysis.proto",
                "../../protos/blob.proto",
                "../../protos/commit.proto",
                "../../protos/diff.proto",
                "../../protos/mercurial-aux-git.proto",
                "../../protos/mercurial-changeset.proto",
                "../../protos/mercurial-operations.proto",
                "../../protos/mercurial-repository.proto",
                "../../protos/ref.proto",
                "../../protos/remote.proto",
                "../../protos/operations.proto",
                "../../protos/repository.proto",
                "../../protos/server.proto",
            ],
            &[
                // include paths
                "../../protos",
                "../dependencies/proto",
            ],
        )
        .unwrap();
    Ok(())
}
