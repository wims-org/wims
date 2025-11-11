{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    git-hooks = {
      url = "github:cachix/git-hooks.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    { self, ... }@inputs:
    inputs.flake-utils.lib.eachSystem
      [
        "aarch64-linux"
        "x86_64-linux"
      ]
      (
        system:
        let
          pkgs = inputs.nixpkgs.legacyPackages.${system};
          inherit (pkgs) lib;
        in
        {
          checks = {
            pre-commit = inputs.git-hooks.lib.${system}.run {
              src = ./.;
              hooks = {
                # Firmware
                "esphome config" = {
                  enable = true;
                  entry = "${lib.getExe pkgs.esphome} config hardware/esphome/example_reader.yaml";
                  pass_filenames = false;
                  files = "^hardware/esphome/.*.yaml";
                };

                # Nix environment
                nixfmt-rfc-style.enable = true;
                statix.enable = true;

                # backend
                ruff.enable = true;
                isort.enable = true;
              };
            };
          };
          devShells.default = pkgs.mkShell {
            LD_LIBRARY_PATH = lib.makeLibraryPath [
              pkgs.stdenv.cc.cc
              pkgs.libglvnd
              pkgs.glib
            ];
            inherit (self.checks.${system}.pre-commit) shellHook;
            buildInputs = with pkgs; [
              # precommit hooks
              self.checks.${system}.pre-commit.enabledPackages

              # frontend
              nodejs_24

              # backend
              poetry

              # hardware
              python3Packages.pyserial
              esptool
              esphome
              picocom
            ];

          };
          formatter = pkgs.nixfmt-rfc-style;
        }
      );
}
