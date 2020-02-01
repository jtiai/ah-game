# Note: File is called ptext because
# https://github.com/pyinstaller/pyinstaller/issues/4626

from PyInstaller.compat import is_win
from PyInstaller.utils.hooks import collect_dynamic_libs

if is_win:
    binaries = collect_dynamic_libs("pygame")
