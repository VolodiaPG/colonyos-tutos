{
  pkgs,
  lib,
  config,
  inputs,
  ...
}: let
  python = pkgs.python3.withPackages (ps:
    with ps; [
      (
        ps.buildPythonPackage rec {
          pname = "pycolonies";
          version = "v1.0.1";
          src = pkgs.fetchFromGitHub {
            owner = "colonyos";
            repo = "pycolonies";
            rev = "52aaf56";
            hash = "sha256-CrAzoZLTyLPa/Ddk9vhKJW7zYJB3pT9Tkvr7HeHsC5I=";
          };
          propagatedBuildInputs = with ps; [
            requests
            websocket-client
            pydantic
            boto3
          ];
        }
      )
    ]);
in {
  enterShell = ''
    export LANG=en_US.UTF-8
    export LANGUAGE=en_US.UTF-8
    export LC_ALL=en_US.UTF-8
    export LC_CTYPE=UTF-8
    export TZ=Europe/Stockholm
    export COLONIES_SERVER_TLS="false"
    export COLONIES_SERVER_HOST="localhost"
    export COLONIES_SERVER_PORT="50080"
    export COLONIES_MONITOR_PORT="21120"
    export COLONIES_MONITOR_INTERVAL="1"
    export COLONIES_SERVER_ID="039231c7644e04b6895471dd5335cf332681c54e27f81fac54f9067b3f2c0103"
    export COLONIES_SERVER_PRVKEY="fcc79953d8a751bf41db661592dc34d30004b1a651ffa0725b03ac227641499d"
    export COLONIES_DB_HOST="timescaledb"
    export COLONIES_DB_USER="postgres"
    export COLONIES_DB_PASSWORD="rFcLGNkgsNtksg6Pgtn9CumL4xXBQ7"
    export COLONIES_COLONY_NAME="dev"
    export COLONIES_COLONY_ID="4787a5071856a4acf702b2ffcea422e3237a679c681314113d86139461290cf4"
    export COLONIES_COLONY_PRVKEY="ba949fa134981372d6da62b6a56f336ab4d843b22c02a4257dcf7d0d73097514"
    export COLONIES_ID="3fc05cf3df4b494e95d6a3d297a34f19938f7daa7422ab0d4f794454133341ac"
    export COLONIES_PRVKEY="ddf7f7791208083b6a9ed975a72684f6406a269cfa36f1b1c32045c0a71fff05"
    export COLONIES_EXECUTOR_TYPE="cli"
    export COLONIES_EXECUTOR_NAME="dev-docker"
    export EXECUTOR_FS_DIR="/tmp/cfs"
    export EXECUTOR_START_PARALLEL_CONTAINERS="false"
    export EXECUTOR_GPU="false"
    export COLONIES_CRON_CHECKER_PERIOD="1000"
    export COLONIES_GENERATOR_CHECKER_PERIOD="1000"
    export COLONIES_EXCLUSIVE_ASSIGN="true"
    export COLONIES_ALLOW_EXECUTOR_REREGISTER="true"
    export COLONIES_RETENTION="false"
    export COLONIES_RETENTION_POLICY="200"
    export COLONIES_SERVER_PROFILER="false"
    export COLONIES_SERVER_PROFILER_PORT="6060"
    export COLONIES_VERBOSE="false"
    export MINIO_USER="admin"
    export MINIO_PASSWORD="admin12345"
    export AWS_S3_ENDPOINT="localhost:9000"
    export AWS_S3_ACCESSKEY="RrXN2vcLeHjBptG8a3Ay"
    export AWS_S3_SECRETKEY="ivwLB0Luqomq65nNVmoo8fTBgxXgNvqYGC50VQN6"
    export AWS_S3_REGION_KEY=""
    export AWS_S3_BUCKET="colonies-prod"
    export AWS_S3_TLS="false"
    export AWS_S3_SKIPVERIFY="false"

    # When using the Colonies CLI on Windows with Git Bash, Git Bash will interpret file paths
    # starting with a slash (/) and automatically translates these Unix-like paths into
    # Windows-style paths, e.g. /c becomes c:/ This behavior can be disabled by the
    # setting the MSYS_NO_PATHCONV environment variable to 1.
    export MSYS_NO_PATHCONV=1
    export COLONIES_CLI_ASCII="false"
  '';
  languages.python = {
    enable = true;
    package = python;
  };
  packages = [
    python
    (pkgs.buildGoModule rec {
      pname = "colonies";
      version = "v2.0.0";

      src = pkgs.fetchFromGitHub {
        owner = "colonyos";
        repo = "colonies";
        rev = "v1.8.18";
        # hash = "sha256-xhRLlfS95Q601OGLd9Ly1Lo+VFpatJAXLNA/PyGMLvI="
        hash = "sha256-x7fXI5odQvZM/RYub9J61ObSxN592pfYS3lyv6emY7I=";
      };

      vendorHash = null;
      subPackages = ["cmd"];

      ldflags = [
        "-X main.version=${version}"
        "-X main.buildSource=nix"
      ];

      CGO_ENABLED = 0;

      postInstall = ''
        mv $out/bin/cmd $out/bin/colonies
      '';

      meta = with pkgs.lib; {
        description = "Colonies is a distributed framework to implement a meta-operating system.";
        homepage = "https://github.com/colonyos/colonies";
        license = licenses.mit;
        platforms = platforms.unix;
        maintainers = [
          volodiapg
        ];
      };
    })
  ];
}
