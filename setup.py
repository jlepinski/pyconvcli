import setuptools

setuptools.setup(name='pyconvcli',
      version='0.0.2',
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
      install_requires=[
          'pydash==4.9.0',
          'stringcase==1.2.0'
          
      ],
      entry_points={
        'console_scripts': [
            'pyconvcli = pyconvcli.cli:main'
        ],
    }
     )
