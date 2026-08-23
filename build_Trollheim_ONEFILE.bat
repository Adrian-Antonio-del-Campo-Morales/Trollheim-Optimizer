@echo off
setlocal
cd /d "%~dp0"

set "NO_PAUSE="
if /I "%~1"=="--no-pause" set "NO_PAUSE=1"

echo ================================================
echo  TROLLHEIM - BUILD ONE FILE EXE
echo ================================================

echo.
echo [1/5] Checking Python...
python --version
if errorlevel 1 goto :python_error

echo.
echo [2/5] Checking dependencies...
python -c "import numpy, openpyxl, yaml; print('NumPy:', numpy.__version__, '| openpyxl:', openpyxl.__version__)"
if errorlevel 1 goto :dependency_error

echo.
echo [3/5] Checking PyInstaller and Tkinter...
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 goto :pyinstaller_error

rem Crear una ventana real: tkinter.Tcl() puede funcionar aunque falten los
rem scripts de Tk que necesita la aplicación y que PyInstaller debe incluir.
python -c "import tkinter; root=tkinter.Tk(); root.withdraw(); root.destroy()" >nul 2>&1
if errorlevel 1 (
    rem Este Python tiene Tcl de adorno. Inkscape suele traer una copia sana.
    if exist "C:\Program Files\Inkscape\lib\tcl8.6\init.tcl" (
        set "TCL_LIBRARY=C:\Program Files\Inkscape\lib\tcl8.6"
        set "TK_LIBRARY=C:\Program Files\Inkscape\lib\tk8.6"
        python -c "import tkinter; root=tkinter.Tk(); root.withdraw(); root.destroy()" >nul 2>&1
        if errorlevel 1 goto :tkinter_error
    ) else (
        goto :tkinter_error
    )
)

echo.
echo [4/5] Building native combat kernel...
call build_NATIVE_KERNEL.bat
if errorlevel 1 goto :cython_error

echo.
echo [5/5] Building single EXE...
python -m PyInstaller --noconfirm --clean --onefile --windowed --name Trollheim --paths src --hidden-import trollheim_simulator._combat_fast --add-data "sources\knowledge;sources\knowledge" src\trollheim_simulator\__main__.py
if errorlevel 1 goto :build_error

echo.
echo ================================================
echo  BUILD COMPLETADO
echo ================================================
echo.
echo EXE generado en:
echo %CD%\dist\Trollheim.exe
echo.
call :pause_if_needed
exit /b 0

:python_error
echo ERROR: Python no esta disponible en PATH.
goto :failed

:dependency_error
echo ERROR: Falta alguna dependencia de ejecucion.
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

:cython_error
echo ERROR compilando el kernel nativo de combate.
echo Instala Visual C++ Build Tools y las dependencias de requirements-dev.txt.
goto :failed

:build_error
echo ERROR construyendo Trollheim.exe.

:failed
call :pause_if_needed
exit /b 1

:pause_if_needed
if not defined NO_PAUSE pause
exit /b 0
