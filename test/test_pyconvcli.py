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