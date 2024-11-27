#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status.

# Function to print big messages
print_big_message() {
    echo
    echo "*******************************************************************"
    for msg in "$@"; do
        echo "* $msg"
    done
    echo "*******************************************************************"
    echo
}

# Move to the script's directory
cd "$(dirname "$0")"

# Check for spaces in the current directory path
if [[ "$PWD" =~ \  ]]; then
    echo "This script relies on Miniconda which cannot be silently installed under a path with spaces."
    exit 1
fi

# Check for special characters in the installation path
if [[ "$PWD" =~ [!\#\$\%\&\(\)\*\+,\;\<\=\>\?\@\[\]\^\`\{\|\}\~] ]]; then
# if [[ "$PWD" =~ [!#\$%&\(\)\*\+,\;<=>\?@\[\]\^\`\{\|\}\~] ]]; then
    SPCHARMESSAGE=("WARNING: Special characters were detected in the installation path!"
                   "This can cause the installation to fail!")
    print_big_message "${SPCHARMESSAGE[@]}"
fi

# Configuration
INSTALL_DIR="$PWD/installer_files"
CONDA_ROOT_PREFIX="$INSTALL_DIR/conda"
INSTALL_ENV_DIR="$INSTALL_DIR/env"
MINICONDA_DOWNLOAD_URL="https://repo.anaconda.com/miniconda/Miniconda3-py310_23.3.1-0-Linux-x86_64.sh"
MINICONDA_CHECKSUM="aef279d6baea7f67940f16aad17ebe5f6aac97487c7c03466ff01f4819e5a651"

# Check if conda exists
conda_exists=false
if [[ -x "$CONDA_ROOT_PREFIX/bin/conda" ]]; then
    conda_exists=true
fi

# If necessary, install conda into a contained environment
if [[ "$conda_exists" == false ]]; then
    echo "Downloading Miniconda from $MINICONDA_DOWNLOAD_URL to $INSTALL_DIR/miniconda_installer.sh"
    mkdir -p "$INSTALL_DIR"
    curl -L "$MINICONDA_DOWNLOAD_URL" -o "$INSTALL_DIR/miniconda_installer.sh" || { echo "Miniconda failed to download."; exit 1; }

    # Verify checksum
    checksum=$(sha256sum "$INSTALL_DIR/miniconda_installer.sh" | awk '{print $1}')
    if [[ "$checksum" != "$MINICONDA_CHECKSUM" ]]; then
        echo "The checksum verification for miniconda_installer.sh has failed."
        rm "$INSTALL_DIR/miniconda_installer.sh"
        exit 1
    else
        echo "The checksum verification for miniconda_installer.sh has passed successfully."
    fi

    echo "Installing Miniconda to $CONDA_ROOT_PREFIX"
    bash "$INSTALL_DIR/miniconda_installer.sh" -b -f -p "$CONDA_ROOT_PREFIX"

    # Test the conda binary
    echo "Miniconda version:"
    "$CONDA_ROOT_PREFIX/bin/conda" --version || { echo "Miniconda not found."; exit 1; }

    # Delete the Miniconda installer
    rm "$INSTALL_DIR/miniconda_installer.sh"
fi

# Create the installer environment
if [[ ! -d "$INSTALL_ENV_DIR" ]]; then
    echo "Creating conda environment with Python 3.10.9"
    "$CONDA_ROOT_PREFIX/bin/conda" create -y -k --prefix "$INSTALL_ENV_DIR" python=3.10.9 || { echo "Conda environment creation failed."; exit 1; }
fi

# Check if conda environment was actually created
if [[ ! -x "$INSTALL_ENV_DIR/bin/python" ]]; then
    echo "Conda environment is empty."
    exit 1
fi

# Environment isolation
export PYTHONNOUSERSITE=1
unset PYTHONPATH
unset PYTHONHOME

# Activate installer environment
source "$CONDA_ROOT_PREFIX/bin/activate" "$INSTALL_ENV_DIR" || { echo "Conda activation failed."; exit 1; }

echo "Conda environment activated with Python 3.10.9"

# Your further setup can go here
apt-get install -y portaudio19-dev
conda init bash

# Keep the shell open
exec "$SHELL"
