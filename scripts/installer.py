from os import popen

process = popen(
    'python -m PyInstaller --specpath ../spec --distpath ../dist --workpath ../build ../dokidokimd/core/controller.py')
preprocessed = process.read()
process.close()
