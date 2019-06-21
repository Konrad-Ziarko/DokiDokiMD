import os
from os import popen

make_spec = 'python3 -m PyInstaller --specpath ../installer/spec --distpath ../installer/dist --workpath ../installer/build --onefile --windowed --name=DokiDokiMD --clean ' \
            '--strip ../dokidokimd/main.py'
run_spec = 'python3 -m PyInstaller ../installer/spec/DokiDokiMD.spec'

run_cmd = make_spec
if os.path.isfile('../installer/spec/DokiDokiMD.spec'):
    run_cmd = run_spec

process = popen(run_cmd)
preprocessed = process.read()
process.close()
