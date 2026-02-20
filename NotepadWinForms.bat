@echo off
setlocal
cd /d "%~dp0"

set EXE_PATH=%~dp0bin\Release\net8.0-windows\NotepadWinForms.exe
if exist "%EXE_PATH%" (
  start "" "%EXE_PATH%"
  exit /b 0
)

where dotnet >nul 2>nul
if %errorlevel% neq 0 (
  echo .NET SDK non trovato.
  echo Apri il progetto in Visual Studio e fai Build (Release), poi rilancia questo file.
  pause
  exit /b 1
)

echo Eseguo build Release la prima volta...
dotnet build NotepadWinForms.csproj -c Release
if %errorlevel% neq 0 (
  echo Build fallita.
  pause
  exit /b 1
)

start "" "%EXE_PATH%"
