@echo off

:: Vérifie si Python est déjà installé
python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo Python est déjà installé.
    goto :InstallPackages
)

:: Télécharge l'installateur Python (ajustez la version si nécessaire)
echo Téléchargement de l'installateur Python...
bitsadmin /transfer "DownloadPythonInstaller" https://www.python.org/ftp/python/3.9.6/python-3.9.6-amd64.exe "%CD%\python-installer.exe"

:: Installe Python (ajoutez la version que vous souhaitez installer)
echo Installation de Python...
start /wait "" "%CD%\python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

:: Vérifie si l'installation de Python a réussi
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo L'installation de Python a échoué.
    exit /b 1
)

:InstallPackages
echo Installation des packages nécessaires...

:: Mise à jour de pip
python -m pip install --upgrade pip

:: Installation des packages avec pip
pip install lxml
pip install pytz
pip install pysimplegui

mkdir Accrochage

echo Installation terminée.
pause
exit /b 0
