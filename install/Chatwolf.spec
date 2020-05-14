# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['run.pyw'],
             pathex=['C:\\Users\\Max\\source\\repos\\maxschmi\\chatwolf'],
             binaries=[],
             datas=[('README.md', '.'), ('LICENSE.txt', '.'), ('install/UNINSTALL.txt', '.'), ('doc/pdf/chatwolf.pdf', 'doc/'), ('chatwolf/data/messages', 'chatwolf/data/messages'), ('chatwolf/data/conf_root.json', 'chatwolf/data/'), ('chatwolf/data/icon.png', 'chatwolf/data/')],
             hiddenimports=['pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Chatwolf',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , version='install\\file_version_info.txt', icon='install\\icon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Chatwolf')
