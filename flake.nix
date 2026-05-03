{
  description = "Unofficial Light Phone music API";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
    pythonEnv = pkgs.python312.withPackages (p: with p; [
      playwright
      click
      rich
      rich-click
      mutagen
      keyring
      secretstorage
      textual
      httpx
      attrs
    ]);
    light = pkgs.writeShellScriptBin "light" ''
      PLAYWRIGHT_BROWSERS_PATH=${pkgs.playwright-driver.browsers} \
      PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true \
      PYTHONPATH=${./light_client}:${./light_api}:$PYTHONPATH \
      ${pythonEnv}/bin/python -m light_cli_tui.cli "$@"
    '';
  in {
    packages.${system}.default = light;

    apps.${system}.default = {
      type = "app";
      program = "${light}/bin/light";
    };

    devShells.${system}.default = pkgs.mkShell {
      nativeBuildInputs = with pkgs; [
        pythonEnv
        uv
        playwright-driver.browsers
        pyright
        openapi-python-client
      ];

      shellHook = ''
        export PLAYWRIGHT_BROWSERS_PATH=${pkgs.playwright-driver.browsers}
        export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true
      '';
    };
  };
}
