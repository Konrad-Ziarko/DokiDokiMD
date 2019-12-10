from os import popen

run_cmd = 'python -m PyInstaller -y -F --onefile ../dokidokimd/main.py --windowed --name=DokiDokiMD --clean -i "../icons/favicon.ico" '

process = popen(run_cmd)
preprocessed = process.read()
process.close()

