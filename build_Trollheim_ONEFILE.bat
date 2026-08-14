@echo off
setlocal
cd /d "%~dp0"

echo ================================================
echo  TROLLHEIM - BUILD ONE FILE EXE
echo ================================================

echo.
echo [1/4] Checking Python...
python --version
if errorlevel 1 goto :python_error

echo.
echo [2/4] Checking dependencies...
python -c "import numpy; print('NumPy:', numpy.__version__)"
if errorlevel 1 goto :dependency_error

echo.
echo [3/4] Checking PyInstaller and Tkinter...
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 goto :pyinstaller_error

python -c "import tkinter; tkinter.Tcl()" >nul 2>&1
if errorlevel 1 (
    rem Este Python tiene Tcl de adorno. Inkscape suele traer una copia sana.
    if exist "C:\Program Files\Inkscape\lib\tcl8.6\init.tcl" (
        set "TCL_LIBRARY=C:\Program Files\Inkscape\lib\tcl8.6"
        set "TK_LIBRARY=C:\Program Files\Inkscape\lib\tk8.6"
    ) else (
        goto :tkinter_error
    )
)

echo.
echo [4/4] Building single EXE...
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Trollheim --paths src src\trollheim_simulator\__main__.py
if errorlevel 1 goto :build_error

echo.
echo ================================================
echo  BUILD COMPLETADO
echo ================================================
echo.
echo EXE generado en:
echo %CD%\dist\Trollheim.exe
echo.
pause
exit /b 0

:python_error
echo ERROR: Python no esta disponible en PATH.
goto :failed

:dependency_error
echo ERROR: Falta NumPy.
echo Ejecuta: python -m pip install -r requirements.txt
goto :failed

:pyinstaller_error
echo ERROR: PyInstaller no esta instalado.
echo Ejecuta: python -m pip install pyinstaller
goto :failed

:tkinter_error
echo ERROR: La instalacion de Tkinter/Tcl no funciona.
echo Repara la instalacion de Python incluyendo Tcl/Tk y vuelve a intentarlo.
goto :failed

:build_error
echo ERROR construyendo Trollheim.exe.

:failed
pause
exit /b 1
