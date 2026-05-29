import os
import subprocess

os.chdir('app/pages')
files = [x for x in os.listdir('.') if '智能求职助手' in x]
if files:
    target = files[0]
    print('Starting chat assistant...')
    subprocess.Popen([
        'D:/Anaconada/envs/pytorch/python.exe',
        '-m', 'streamlit', 'run',
        target,
        '--server.port', '8504',
        '--server.headless', 'true'
    ])
else:
    print('No file found')
