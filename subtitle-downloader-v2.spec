# -*- mode: python -*-
a = Analysis(['subtitle-downloader-v2.py'],
             pathex=['/home/archit/Desktop/subtitle_downloader_v2'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='subtitle-downloader-v2',
          debug=False,
          strip=None,
          upx=True,
          console=True )
