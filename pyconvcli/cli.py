from pyconvcli import PyConvCli
import os

def main():
    cli = PyConvCli('pyconvcli',os.path.dirname(os.path.realpath(__file__)))
    cli.run()