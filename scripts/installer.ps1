# Windows Installer

echo - Installing Scoop
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression

echo - Installing Hatch
$winVer = (Get-WmiObject -Class Win32_OperatingSystem).OSArchitecture
$winVer = $winVer -replace "(\d+)(.*)", '$1'
msiexec /passive /i https://github.com/pypa/hatch/releases/latest/download/hatch-$winVer.msi

echo - Installing pyenv-win
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
Remove-Item -Path "./install-pyenv-win.ps1"

echo - Installing Rye - Not Supported on Windows via PS yet

echo - Install PipX Packages
Get-Content pipx-requirements.txt | ForEach-Object {
    $package = $_.Split(" ")[0]
    $version = $_.Split(" ")[1]
    pipx install $package==$version
}

echo - Install Pip Requirements
pip install -r requirements.txt

echo - Install Scoop Packages
scoop import scoop/scoop.json

echo - Install Winget Packages
winget import winget/winget.json
