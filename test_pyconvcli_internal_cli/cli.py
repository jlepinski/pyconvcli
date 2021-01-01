from pyconvcli import PyConvCli
import os

def main():
    cli = PyConvCli('test_pyconvcli_internal_cli',os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
    cli.run()

def visualize():
    cli= PyConvCli('test_pyconvcli_internal_cli',os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
    args,parsers = cli.parse_args()
    cli.parsers=parsers
    cli.visualize()