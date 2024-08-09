{ pkgs ? import <nixpkgs> {} }:
    pkgs.mkShell {
        nativeBuildInputs = with pkgs; [python3 python312Packages.numpy python312Packages.matplotlib python312Packages.aiohttp python312Packages.async-timeout];
}