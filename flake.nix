{
  description = "Unofficial Light Phone API and CLI";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
    python = pkgs.python312;

    light-phone-api = python.pkgs.buildPythonPackage {
      pname = "light-phone-api";
      version = "0.1.1";
      pyproject = true;
      src = ./light_api;
      build-system = [ python.pkgs.hatchling ];
      dependencies = with python.pkgs; [
        httpx
        attrs
        python-dateutil
        keyring
        mutagen
      ];
    };

    light-phone-cli-tui = python.pkgs.buildPythonPackage {
      pname = "light-phone-cli-tui";
      version = "0.1.1";
      pyproject = true;
      src = ./light_cli_tui;
      build-system = [ python.pkgs.hatchling ];
      dependencies = with python.pkgs; [
        click
        rich-click
        rich
        textual
        pyperclip
        light-phone-api
      ];
    };

  in {
    packages.${system} = {
      inherit light-phone-api light-phone-cli-tui;
      default = light-phone-cli-tui;
    };

    apps.${system}.default = {
      type = "app";
      program = "${light-phone-cli-tui}/bin/light";
    };

    devShells.${system}.default = pkgs.mkShell {
      nativeBuildInputs = with pkgs; [
        (python.withPackages (p: with p; [
          click
          rich
          rich-click
          mutagen
          keyring
          secretstorage
          textual
          httpx
          attrs
        ]))
        uv
        pyright
        openapi-python-client
      ];

      shellHook = ''
        export LD_LIBRARY_PATH=${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH
        export PYTHONPATH=${pkgs.python312}/lib/python3.12/site-packages:$PYTHONPATH
      '';
    };
  };
}
