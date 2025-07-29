#! /usr/bin/env bash

# internal function to bluer_ai_seed.
function bluer_ai_seed_arvancloud() {
    # seed is NOT local

    bluer_ai_seed add_kaggle

    bluer_ai_seed add_ssh_key

    bluer_ai_seed add_repo

    seed="${seed}sudo apt-get update$delim"
    seed="${seed}sudo apt install -y python3-pip$delim"
    seed="${seed}sudo apt install -y python3-venv$delim"
    seed="${seed}sudo apt install -y libgl1$delim_section"

    bluer_ai_seed add_bluer_ai_env

    seed="${seed}pip install --upgrade pip --no-input$delim"
    seed="${seed}pip3 install setuptools$delim"
    seed="${seed}pip3 install -e .$delim_section"

    bluer_ai_seed add_repo repo=bluer-objects
    seed="${seed}pip3 install -e .$delim_section"

    seed="${seed}pip3 install --upgrade opencv-python-headless$delim_section"

    seed="${seed}$(bluer_ai_seed add_file $abcli_path_git/bluer-objects/.env \$HOME/git/bluer-objects/.env)$delim_section"

    bluer_ai_seed add_repo repo=bluer-sandbox
    seed="${seed}pip3 install -e .$delim_section"

    bluer_ai_seed add_repo repo=bluer-flow
    seed="${seed}pip3 install -e .$delim_section"

    bluer_ai_seed add_repo repo=assets

    seed="${seed}source \$HOME/git/bluer-ai/bluer_ai/.abcli/bluer_ai.sh$delim_section"
}

function bluer_sandbox_arvancloud_seed() {
    bluer_ai_seed arvancloud "$@"
}
