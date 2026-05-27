import os
import subprocess
import glob

os.chdir('app/pages')
files = [x for x in os.listdir('.') if x.startswith('06')]
if files:
    target = files[0]
    print('Starting resume parser...')
    subprocess.Popen([
        'D:/Anaconada/envs/pytorch/python.exe',
        '-m', 'streamlit', 'run',
        target,
        '--server.port', '8501',
        '--server.headless', 'true'
    ])
else:
    print('No file found')
