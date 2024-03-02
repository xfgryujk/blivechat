# -*- mode: python ; coding: utf-8 -*-
import typing
import subprocess
import sys
if typing.TYPE_CHECKING:
    import os

    from PyInstaller.building.api import COLLECT, EXE, PYZ
    from PyInstaller.building.build_main import Analysis

    SPECPATH = ''
    DISTPATH = ''


# exe文件名、打包目录名
NAME = 'msg-logging'
# 模块搜索路径
PYTHONPATH = [
    os.path.join(SPECPATH, '..', '..'),  # 为了找到blcsdk
]
# 数据
DATAS = [
    ('plugin.json', '.'),
    ('LICENSE', '.'),
    ('log/.gitkeep', 'log'),
]

block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=PYTHONPATH,
    binaries=[],
    datas=DATAS,
    hiddenimports=[],
    hookspath=[],
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
subprocess.run([sys.executable, '-m', 'zipfile', '-c', NAME + '.zip', NAME], cwd=DISTPATH)
