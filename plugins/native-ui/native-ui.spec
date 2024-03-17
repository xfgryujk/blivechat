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
NAME = 'native-ui'
# 模块搜索路径
PYTHONPATH = [
    os.path.join(SPECPATH, '..', '..'),  # 为了找到blcsdk
]
# 数据
DATAS = [
    ('plugin.json', '.'),
    ('LICENSE', '.'),
    ('data/config.example.ini', 'data'),
    ('data/blivechat.ico', 'data'),
    ('log/.gitkeep', 'log'),
]
# 动态库
BINARIES = []
if sys.platform == 'win32':
    import wx

    # https://docs.wxpython.org/wx.html2.WebView.html#phoenix-title-webview-backend-edge-msw
    bin_path = os.path.join(os.path.dirname(wx.__file__), 'WebView2Loader.dll')
    BINARIES.append((bin_path, '.'))

block_cipher = None


a = Analysis(
    ['main.pyw'],
    pathex=PYTHONPATH,
    binaries=BINARIES,
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
    icon='data/blivechat.ico',
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
