# -*- mode: python ; coding: utf-8 -*-
import shutil
import typing
from pathlib import Path

import webview.__pyinstaller

if typing.TYPE_CHECKING:
    from PyInstaller.building.api import COLLECT, EXE, PYZ
    from PyInstaller.building.build_main import Analysis

    SPECPATH = ''
    DISTPATH = ''


# exe文件名、打包目录名
NAME = 'login'
# 数据
DATAS = [
    ('plugin.json', '.'),
    ('LICENSE', '.'),
    ('log/.gitkeep', 'log'),
]

block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=DATAS,
    hiddenimports=[],
    hookspath=[
        str(Path(webview.__pyinstaller.__file__).parent),  # pyinstaller-hooks-contrib的版本太老了，少打包了js文件...
    ],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name=NAME,
)

# 打包
print('Start to package')
shutil.make_archive(str(Path(DISTPATH) / NAME), 'zip', DISTPATH, NAME)
