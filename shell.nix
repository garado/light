{ pkgs ? import <nixpkgs> {} }:
  let
    pythonEnv = pkgs.python312.withPackages (p: with p; [
      playwright
      typer
      rich
    ]);
  
  in
  pkgs.mkShell {
    nativeBuildInputs = with pkgs; [
      pythonEnv
      playwright-driver.browsers
      nodejs
    ];

    shellHook = ''
      export PLAYWRIGHT_BROWSERS_PATH=${pkgs.playwright-driver.browsers}
      export PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS=true
    '';
}

