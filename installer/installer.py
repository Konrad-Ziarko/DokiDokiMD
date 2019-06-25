from os import popen

run_cmd = 'python -m PyInstaller --onefile ../dokidokimd/main.py --windowed --name=DokiDokiMD --clean'

process = popen(run_cmd)
preprocessed = process.read()
process.close()

