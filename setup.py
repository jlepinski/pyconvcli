import setuptools

from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(name='pyconvcli',
      version='0.0.3',
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
          'stringcase==1.2.0'
          
      ],
      entry_points={
        'console_scripts': [
            'pyconvcli = cli.cli:main'
        ],
    }
     )
