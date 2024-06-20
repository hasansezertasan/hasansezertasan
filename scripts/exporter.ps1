# Windows Exporter

echo - Exporting Scoop Packages
scoop export > scoop/scoop.json

echo - Exporting Winget Packages
winget export winget/winget.json

echo - Exporting pyenv # TODO

echo - Exporting PipX Packages
pipx list --short > pipx-requirements.txt

echo - Exporting Pip Requirements
pip freeze > pip-requirements.txt

echo - Exporting GitHub CLI Extensions
gh extension list > gh-extensions.txt
