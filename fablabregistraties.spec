# -*- mode: python -*-

block_cipher = None


a = Analysis(['Main.py'],
             pathex=['C:\\Users\\aboro\\OD\\ict\\pycharm\\FGR'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='fablabregistraties',
          debug=False,
          strip=False,
          upx=True,
          console=False)
coll = COLLECT(exe,
               a.binaries,
               #Tree('resources', prefix='resources\\'),
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='Main')
