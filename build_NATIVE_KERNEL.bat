@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

set "VCVARS="
if exist "C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" set "VCVARS=C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"
if exist "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat" set "VCVARS=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
if exist "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat" set "VCVARS=C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Auxiliary\Build\vcvars64.bat"

if not defined VCVARS (
    echo ERROR: No se ha encontrado Visual C++ Build Tools de 64 bits.
    exit /b 1
)

call "%VCVARS%" >nul
if errorlevel 1 exit /b 1
where cl.exe >nul 2>&1
if errorlevel 1 (
    echo ERROR: El entorno de Visual C++ no ha expuesto cl.exe.
    exit /b 1
)

where rc.exe >nul 2>&1
if errorlevel 1 (
    for /f "delims=" %%D in ('dir /b /ad /o-n "C:\Program Files (x86)\Windows Kits\10\bin" 2^>nul') do (
        if not defined WINDOWS_SDK_BIN if exist "C:\Program Files (x86)\Windows Kits\10\bin\%%D\x64\rc.exe" set "WINDOWS_SDK_BIN=C:\Program Files (x86)\Windows Kits\10\bin\%%D\x64"
    )
    if defined WINDOWS_SDK_BIN set "PATH=!WINDOWS_SDK_BIN!;!PATH!"
)
where rc.exe >nul 2>&1
if errorlevel 1 (
    echo ERROR: No se ha encontrado rc.exe del Windows SDK.
    exit /b 1
)

rem El entorno ya esta preparado; evita que setuptools lo sustituya por otro incompleto.
set "DISTUTILS_USE_SDK=1"
set "MSSdk=1"

python -B tools\build_native_kernel.py
exit /b %ERRORLEVEL%
