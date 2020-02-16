pyinstaller ^
    --clean ^
    --additional-hooks-dir hooks ^
    --icon gfx/ah-game-icons.ico ^
    --onefile ^
    -w ^
    ah.py

xcopy /Y /I fonts dist\fonts
xcopy /Y /I music dist\music
xcopy /Y /I sfx dist\sfx
xcopy /Y /I gfx dist\gfx
