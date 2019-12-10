import shutil
from os import popen, path, unlink

PROGRAM_NAME = 'DokiDokiMD'

run_cmd = F'python -m PyInstaller -y -F -w --name={PROGRAM_NAME} ' \
          F'..{path.sep}dokidokimd/main.py ' \
          F'-i "..{path.sep}icons{path.sep}favicon.ico" ' \
          F'--add-data "..{path.sep}icons";"..{path.sep}icons" '


process = popen(run_cmd)
preprocessed = process.read()
process.close()

shutil.rmtree('build')
try:
    shutil.move(F'dist{path.sep}{PROGRAM_NAME}', '.')
except:
    pass
try:
    shutil.move(F'dist{path.sep}{PROGRAM_NAME}.exe', '.')
except:
    pass
shutil.rmtree('dist')
unlink(F'{PROGRAM_NAME}.spec')
