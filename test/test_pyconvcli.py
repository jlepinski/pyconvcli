import unittest
from pyconvcli import PyConvCli
import os
import sys
class TestPyConvCli(unittest.TestCase):
    def test_update_parser_for_functions(self):
        sys.argv=["test","here",'custom','route']

        cli = PyConvCli('test',os.path.dirname(os.path.realpath(__file__)))
        args,parsers = cli.parse_args()
        self.assertEqual(len(parsers['test.here.custom.route']['callables']),2)

    def test_groups_feature(self):
        sys.argv=["test","here",'custom','route']

        cli = PyConvCli('test',os.path.dirname(os.path.realpath(__file__)))
        args,parsers = cli.parse_args()
        self.assertEqual(len(parsers['test.here.custom.groups']['callables']['groupsCommand']['groups']),2)

    def test_app(self):
        sys.argv=["test","here",'custom','route']
        cli = PyConvCli('test',os.path.dirname(os.path.realpath(__file__)))
        args,parsers = cli.parse_args()
        cli.parsers=parsers
        cli.visualize()