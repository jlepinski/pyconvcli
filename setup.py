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
      packages=['.'],
      install_requires=[
          'pydash',
      ],
     )
