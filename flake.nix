{
  description = "Biobarna biobarna-scorer - ranks land patches by biodiversity in their habitats";

  inputs = {
    dream2nix.url = "github:nix-community/dream2nix";
    nixpkgs.follows = "dream2nix/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = inputs @ { self, dream2nix, nixpkgs, flake-utils, ... }:
    (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        module = { config, lib, dream2nix, ... }:
          let
            pyproject = lib.importTOML (config.mkDerivation.src + /pyproject.toml);
          in
          {
            imports = [ dream2nix.modules.dream2nix.pip ];

            inherit (pyproject.project) name version;

            mkDerivation = {
              src = ./.;
              nativeBuildInputs = [ pkgs.fish ];
            };

            buildPythonPackage = {
              format = lib.mkForce "pyproject";
              pythonImportsCheck = [ "biobarna-scorer" ];
            };

            pip = {
              pypiSnapshotDate = "2023-10-27";
              requirementsList =
                pyproject.build-system.requires
                  or [ ]
                ++ pyproject.project.dependencies;
              flattenDependencies = true;
            };
          };
      in
      rec {
        packages.default = dream2nix.lib.evalModules {
          packageSets.nixpkgs = inputs.dream2nix.inputs.nixpkgs.legacyPackages.${system};
          modules = [
            module
            {
              paths.projectRoot = ./.;
              paths.projectRootFile = "flake.nix";
              paths.package = ./.;
            }
          ];
        };

        devShells = rec {
          # scorerWithFish = with pkgs; mkShell {
          #   packages = [ fish ];
          #   inputsFrom = [ packages.default ];
          #   shellHook = "fish && exit";
          #   buildInputs = packages.default.config.mkDerivation.nativeBuildInputs;
          # };


          default =  packages.default;
          # default = scorerWithFish;
        };
      }));
}
