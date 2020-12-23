import setuptools
from setuptools.command.build_py import build_py
from setuptools.command.install import install
import subprocess
import os

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

class CliAppInstall(build_py):
     def run(self):
        print("RUNNING NPM INSTALL")
        print(self)
        original_cwd = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(os.path.realpath(__file__)),'pyconvcli','visualizer'))
        subprocess.Popen('npm install && npm run build ', shell=True).communicate() 
        os.chdir(original_cwd)
        build_py.run(self)

setuptools.setup(name='pyconvcli',
      version='0.0.4',
      description='A convention based CLI framework for python',
      author='Joshua Lepinski',
      author_email='joshualepinski@gmail.com',
      url='https://github.com/jlepinski/pyconvcli',
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: Apache Software License"
      ],
      packages=setuptools.find_packages(),
      include_package_data=True,
      long_description=long_description,
      long_description_content_type='text/markdown',
      install_requires=[
          'pydash==4.9.0',
          'stringcase==1.2.0',
          'eel'
          
      ],
      entry_points={
        'console_scripts': [
            'pyconvcli = cli.cli:main',
            'pyconvcli-app = cli.cli:visualize'
        ],
        

    },cmdclass={
        'cli_app_install': CliAppInstall
    }
     )
