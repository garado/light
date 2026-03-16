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
    ]);
    lp3music = pkgs.writeShellScriptBin "lp3music" ''
      PLAYWRIGHT_BROWSERS_PATH=${pkgs.playwright-driver.browsers} \
      PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true \
      ${pythonEnv}/bin/python ${./light.py} "$@"
    '';
  in {
    packages.${system}.default = lp3music;

    apps.${system}.default = {
      type = "app";
      program = "${lp3music}/bin/lp3music";
    };

    devShells.${system}.default = pkgs.mkShell {
      nativeBuildInputs = with pkgs; [
        pythonEnv
        playwright-driver.browsers
        nodejs
      ];

      shellHook = ''
        export PLAYWRIGHT_BROWSERS_PATH=${pkgs.playwright-driver.browsers}
        export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true
      '';
    };
  };
}
