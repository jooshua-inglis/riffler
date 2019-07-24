SET scriptDir=%~dp0

cd %scriptDir%

if NOT EXIST (
    CALL python -m venv %scriptDir%\riffler_env
    CALL %scriptDir%\riffler_env\bin\activate.bat
    CALL pip install -r requirments.txt
) 

CALL %scirptDir%\riffler_env\bin\python %scriptPath%\src\main.py