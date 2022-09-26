#!/usr/bin/env python
import subprocess
import os

cwd = os.path.dirname(os.path.realpath(__file__))
print('Deleting all files in all migrations folders!')
for root, dirs, files in os.walk(cwd):
    for file in files:
        if(os.path.join(root, file)).__contains__('/migrations/'):
            os.remove(os.path.join(root, file))
print('Migration files deleted!')

subprocess.call(['python', 'manage.py', 'makemigrations'])
for application in ('Dashboard', 'rest_api'):
    subprocess.call(['python', 'manage.py', 'makemigrations', application])

subprocess.call(['python', 'manage.py', 'migrate'])

subprocess.call(['python', 'manage.py', "createsuperuser"])
