import shutil
from os import popen, path

PROGRAM_NAME = 'DokiDokiMD'

run_cmd = F'python -m PyInstaller -y -F -w --name={PROGRAM_NAME} ' \
          F'..{path.sep}main.py ' \
          F'-i "..{path.sep}icons{path.sep}favicon.ico" ' \
          F'--add-data "..{path.sep}icons";"icons" '


process = popen(run_cmd)
preprocessed = process.read()
process.close()

shutil.rmtree('build')
try:
    shutil.move(F'dist{path.sep}{PROGRAM_NAME}', '.')
except Exception as e:
    print(F'Could not move files under dist{path.sep}{PROGRAM_NAME}')
try:
    shutil.move(F'dist{path.sep}{PROGRAM_NAME}.exe', '.')
except Exception as e:
    print(F'Could not move dist{path.sep}{PROGRAM_NAME}.exe')
shutil.rmtree('dist')
