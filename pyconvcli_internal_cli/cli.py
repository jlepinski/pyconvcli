from pyconvcli import PyConvCli
import os

def main():
    cli = PyConvCli('pyconvcli_internal_cli',os.path.dirname(os.path.realpath(__file__)),'pyconvcli')
    cli.run()

def visualize():
    cli= PyConvCli('pyconvcli_internal_cli',os.path.dirname(os.path.realpath(__file__)),'pyconvcli')
    args,parsers = cli.parse_args()
    cli.parsers=parsers
    cli.visualize()