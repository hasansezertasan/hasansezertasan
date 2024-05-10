# Windows Installer

echo Installing Scoop
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

echo Instlaling pyenv-win
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
Remove-Item -Path "./install-pyenv-win.ps1"

echo Installing Rye - Not Supported on Windows via PS yet

echo Install PipX Packages
Get-Content pipx-requirements.txt | ForEach-Object { pipx install $_ }

echo Install Pip Requirements
pip install -r requirements.txt
