{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    devshell.url = "github:numtide/devshell";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
      ...
    }@inputs:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = with inputs; [
            devshell.overlays.default
          ];
        };
      in
      {
        devShells.default = pkgs.devshell.mkShell {
          devshell = {
            name = "Tacklebox";
            startup = {
              install-uv-dependencies.text = "uv sync --all-groups --locked";
              source-venv = {
                text = ''
                  source .venv/bin/activate
                  export PATH="${pkgs.ruff}/bin:${pkgs.basedpyright}/bin:$PATH"
                '';
                deps = [ "install-uv-dependencies" ];
              };
              ensure-data-dir-exists.text = ''mkdir -p "$PRJ_DATA_DIR"'';
            };
          };

          commands = with pkgs; [
            { package = uv; }
            { package = ruff; } # the ruff pip package installs a dynamically linked binary that cannot run on NixOS
            { package = basedpyright; } # same as ruff
            { package = typos; }
          ];

          packages = with pkgs; [
            stdenv.cc.cc
            python3
          ];

          env = [
            {
              name = "CPPFLAGS";
              eval = "-I$DEVSHELL_DIR/include";
            }
            {
              name = "LDFLAGS";
              eval = "-L$DEVSHELL_DIR/lib";
            }
            {
              name = "LD_LIBRARY_PATH";
              eval = "$DEVSHELL_DIR/lib:$LD_LIBRARY_PATH";
            }
            {
              name = "UV_PYTHON_PREFERENCE";
              value = "only-system";
            }
            {
              name = "UV_PYTHON_DOWNLOADS";
              value = "never";
            }
          ];

          motd = ''
            {33}🔨 Welcome to the {208}Tacklebox{33} Devshell!{reset}
            $(type -p menu &>/dev/null && menu)
          '';
        };
      }
    );
}
