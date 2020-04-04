import shutil
import os
from os import popen

PROGRAM_NAME = 'DokiDokiMD'

run_cmd = F'python -m PyInstaller -y -F -w --name={PROGRAM_NAME} ' \
          F'{os.path.join("..", "main.py")} ' \
          F'-i {os.path.join("..", "icons", "favicon.ico")} ' \
          F'--add-data {os.path.join("..", "icons")};"icons" '


process = popen(run_cmd)
preprocessed = process.read()
process.close()

shutil.rmtree('build')
try:
    os.remove(F'{PROGRAM_NAME}.exe')
    os.remove(F'{PROGRAM_NAME}.spec')
finally:
    pass
try:
    shutil.move(os.path.join('dist', F'{PROGRAM_NAME}.exe'), '.')
except Exception as e:
    print(F'Could not move {os.path.join("dist", F"{PROGRAM_NAME}.exe")}: {e}')
shutil.rmtree('dist')
