import os
import subprocess
import glob

os.chdir('app/pages')
files = [x for x in os.listdir('.') if x.startswith('07')]
if files:
    target = files[0]
    print('Starting salary negotiator...')
    subprocess.Popen([
        'D:/Anaconada/envs/pytorch/python.exe',
        '-m', 'streamlit', 'run',
        target,
        '--server.port', '8503',
        '--server.headless', 'true'
    ])
else:
    print('No file found')
