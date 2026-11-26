@echo off
setlocal
set "INPUT=%~f1"
cd /d "%~dp0"
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
if "%~1"=="" (
    py -3 -u -m src.cli -f examples\db_config.cfg
) else (
    py -3 -u -m src.cli -f "%INPUT%"
)
endlocal
