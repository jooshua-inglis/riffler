SET scriptDir=%~dp0

cd %scriptDir%


if NOT EXIST %scriptDir%riffler_env\Scripts\python (
    CALL python -m venv %scriptDir%riffler_env
    CALL %scriptDir%riffler_env\Scripts\activate.bat
    CALL python -m pip install -r requirments.txt
) 

CALL %scriptDir%riffler_env\Scripts\python %scriptDir%riffler.py
