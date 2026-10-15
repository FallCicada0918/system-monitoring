# -*- mode: python ; coding: utf-8 -*-
import os

base_dir = os.path.abspath(".")
static_source = os.path.join(base_dir, "cyber_pulse", "static")

excludes = [
    'IPython', 'ipykernel', 'jupyter', 'jupyter_client', 'jupyter_core', 'notebook',
    'jedi', 'parso', 'matplotlib', 'PIL', 'Pillow', 'tkinter', '_tkinter',
    'openpyxl', 'tornado', 'zmq', 'pyzmq', 'cryptography', 'paramiko',
    'pandas', 'scipy', 'sympy', 'lark', 'bottle', 'pytest', 'unittest',
    'sqlite3', 'http.server'
]

a = Analysis(
    ['entrypoint.py'],
    pathex=[base_dir],
    binaries=[],
    datas=[
        (static_source, os.path.join('cyber_pulse', 'static')),
        (static_source, 'static'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.wsproto_impl',
        'uvicorn.protocols.websockets.websockets_impl',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        'fastapi',
        'websockets',
        'websockets.legacy',
        'websockets.legacy.server',
        'cyber_pulse',
        'cyber_pulse.cli',
        'cyber_pulse.cli_hud',
        'cyber_pulse.collector',
        'cyber_pulse.app',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='cpulse',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
)
