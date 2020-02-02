pyinstaller ^
    --clean ^
    --additional-hooks-dir hooks ^
    --onefile ^
    -w ^
    ah.py

xcopy /Y /I fonts dist\fonts\
xcopy /Y /I music dist\music\
xcopy /Y /I sfx dist\sfx

cd dist
del ah.zip
7za a ah.zip ah.exe fonts\ music\ sfx\
cd ..
