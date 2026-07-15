@echo off
echo Executing LaTeX PDF compilation script...
python compile_pdf.py
if %ERRORLEVEL% NEQ 0 (
    echo Compilation failed!
    pause
    exit /b %ERRORLEVEL%
)
echo Compilation finished successfully.
pause
