import unittest
from pyconvcli import PyConvCli
import os
import sys
from contextlib import redirect_stdout
from io import StringIO


class TestPyConvCli(unittest.TestCase):

    def test_update_parser_for_functions(self):
        sys.argv = ["test", "here", 'custom', 'route']

        cli = PyConvCli('test', os.path.dirname(os.path.realpath(__file__)),'mycli')
        args, parsers = cli.parse_args()
        self.assertEqual(len(parsers['test.here.custom.route']['callables']), 2)

    def test_groups_feature(self):
        sys.argv = ["test", "here", 'custom', 'route']

        cli = PyConvCli('test', os.path.dirname(os.path.realpath(__file__)),'mycli')
        args, parsers = cli.parse_args()
        self.assertEqual(len(parsers['test.here.custom.groups']['callables']['groupsCommand']['groups']), 2)

    def test_there_or_not_action_stored(self):
        sys.argv = ["test", "there", "thereOrNotCommand", '--feature', '--notfeature']
        cli = PyConvCli('test', os.path.dirname(os.path.realpath(__file__)),'mycli')
        std_out = StringIO()
        with redirect_stdout(std_out):
            cli.run()
        self.assertEqual(std_out.getvalue().strip(),"feature:True,notfeature:False")
        std_out = StringIO()
        sys.argv = ["mycli", "there", "thereOrNotCommand"]
        with redirect_stdout(std_out):
            cli.run()
        self.assertEqual(std_out.getvalue().strip(),"feature:False,notfeature:True")

    def test_app(self):
        sys.argv = ["test", "here", 'custom', 'route']
        cli = PyConvCli('test', os.path.dirname(os.path.realpath(__file__)),'mycli')
        args, parsers = cli.parse_args()
        cli.parsers = parsers
        cli.visualize()
