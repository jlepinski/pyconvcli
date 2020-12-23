from pyconvcli import PyConvCli
import os

def main():
    cli = PyConvCli('cli',os.path.dirname(os.path.realpath(__file__)))
    cli.run()

def visualize():
    cli= PyConvCli('cli',os.path.dirname(os.path.realpath(__file__)))
    args,parsers = cli.parse_args()
    cli.parsers=parsers
    cli.visualize()