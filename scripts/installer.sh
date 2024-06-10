#!/bin/bash

echo - Installing Brew
# /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

echo - Installing pyenv
# curl https://pyenv.run | bash
# TODO: How to install pyenv, through brew or curl?

echo - Installing Rye
# curl -sSf https://rye-up.com/get | bash
# TODO: How to install rye, through brew or curl?

echo - Install PipX Packages
# FIXME: This doesn't work as expected, need to fix it.
while IFS= read -r line
do
    read -ra ADDR <<< "$line"
    pipx install "${ADDR[0]}" --quiet
done < "pipx-requirements.txt"

echo - Install Pip Requirements
pip install -r requirements.txt

echo - Installing Brew Packages
# [Export/Reinstall your installed program list via homebrew - Everton Araújo - Medium](https://epma.medium.com/export-reinstall-your-installed-program-list-via-homebrew-35edef3f44f6)
