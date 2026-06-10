@echo off 
cd /d "%~dp0" 
tree /F /A > structure.txt 
echo Structure saved to %~dp0structure.txt 
pause