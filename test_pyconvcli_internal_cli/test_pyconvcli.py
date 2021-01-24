import unittest
from pyconvcli import PyConvCli
import os
import sys
from contextlib import redirect_stdout
from io import StringIO
import pkg_resources
from argparse import ArgumentError


class TestPyConvCli(unittest.TestCase):

    def test_update_parser_for_functions(self):
        sys.argv = ['test_pyconvcli_internal_cli', "here", 'custom', 'route']

        cli = PyConvCli('test_pyconvcli_internal_cli', os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
        args, parsers = cli.parse_args()
        self.assertEqual(len(parsers['test_pyconvcli_internal_cli.here.custom.route']['callables']), 2)

    def test_groups_feature(self):
        sys.argv = ['test_pyconvcli_internal_cli', "here", 'custom', 'route']

        cli = PyConvCli('test_pyconvcli_internal_cli', os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
        args, parsers = cli.parse_args()
        self.assertEqual(len(parsers['test_pyconvcli_internal_cli.here.custom.groups']['callables']['groupsCommand']['groups']), 2)

    def test_there_or_not_action_stored(self):
        sys.argv = ['test_pyconvcli_internal_cli', "there", "thereOrNotCommand", '--feature', '--notfeature']
        cli = PyConvCli('test_pyconvcli_internal_cli', os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
        std_out = StringIO()
        with redirect_stdout(std_out):
            cli.run()
        self.assertEqual(std_out.getvalue().strip(),"feature:True,notfeature:False")
        std_out = StringIO()
        sys.argv = ['pyconvcli-test', "there", "thereOrNotCommand"]
        with redirect_stdout(std_out):
            cli.run()
        self.assertEqual(std_out.getvalue().strip(),"feature:False,notfeature:True")

    def test_already_existing_path_as_callable(self):
        sys.argv = ['test_pyconvcli_internal_cli', "here", "testing", '--ascii', '<()()()>']
        cli = PyConvCli('test_pyconvcli_internal_cli', os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
        std_out = StringIO()
        with redirect_stdout(std_out):
            cli.run()
        self.assertEqual(std_out.getvalue().strip(),"ascii: '<()()()>'")

    def test_already_existing_at_root_path_as_callable(self):
        sys.argv = ['test_pyconvcli_internal_cli', "here", '--ascii', '<()()()>']
        cli = PyConvCli('test_pyconvcli_internal_cli', os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
        std_out = StringIO()
        with redirect_stdout(std_out):
            cli.run()
        self.assertEqual(std_out.getvalue().strip(),"ascii: '<()()()>'")

    def test_already_existing_at_root_path_as_callable(self):
        sys.argv = ['test_pyconvcli_internal_cli', "there"]
        cli = PyConvCli('test_pyconvcli_internal_cli', os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
        std_out = StringIO()
        with redirect_stdout(std_out):
            cli.run()
        self.assertEqual(std_out.getvalue().strip(),'no params but I was called')

    def test_action_command(self):
        sys.argv = ['test_pyconvcli_internal_cli', "--version"]
        cli = PyConvCli('test_pyconvcli_internal_cli', os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
        std_out = StringIO()
        with redirect_stdout(std_out):
            cli.run()
        self.assertEqual(std_out.getvalue().strip(),pkg_resources.get_distribution("pyconvcli").version)

    def test_2_narg_action_command(self):
        sys.argv = ['test_pyconvcli_internal_cli', "--nargs2test",'3','resd']
        cli = PyConvCli('test_pyconvcli_internal_cli', os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
        std_out = StringIO()
        with redirect_stdout(std_out):
            cli.run()
        self.assertEqual(std_out.getvalue().strip(),str(['3', 'resd']))
        sys.argv = ['test_pyconvcli_internal_cli', "--nargs2test",'3','resd','greens']
        with self.assertRaises(SystemExit):
            cli = PyConvCli('test_pyconvcli_internal_cli', os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
            cli.run()
        sys.argv = ['test_pyconvcli_internal_cli', "--nargs2test",'hello']
        with self.assertRaises(SystemExit):
            cli = PyConvCli('test_pyconvcli_internal_cli', os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
            cli.run()

    def test_star_narg_action_command(self):
        sys.argv = ['test_pyconvcli_internal_cli', "--nargsstartest",'3','resd']
        cli = PyConvCli('test_pyconvcli_internal_cli', os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
        std_out = StringIO()
        with redirect_stdout(std_out):
            cli.run()
        self.assertEqual(std_out.getvalue().strip(),str(['3', 'resd']))
        sys.argv = ['test_pyconvcli_internal_cli', "--nargsstartest",'3','resd','greens']

        cli = PyConvCli('test_pyconvcli_internal_cli', os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
        std_out2 = StringIO()

        with redirect_stdout(std_out2):
            cli.run()
        self.assertEqual(std_out2.getvalue().strip(),str(['3', 'resd', 'greens']))
        sys.argv = ['test_pyconvcli_internal_cli', "--nargsstartest",'hello']

        cli = PyConvCli('test_pyconvcli_internal_cli', os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
        std_out3 = StringIO()
        with redirect_stdout(std_out3):
            cli.run()
        self.assertEqual(std_out3.getvalue().strip(),str(['hello']))

        sys.argv = ['test_pyconvcli_internal_cli', "--nargsstartest",'hello', 'there']

        cli = PyConvCli('test_pyconvcli_internal_cli', os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
        std_out3 = StringIO()
        with redirect_stdout(std_out3):
            cli.run()
        # just testing or demonstrating that with * as nargs we can't enter other sub commands
        self.assertEqual(std_out3.getvalue().strip(),str(['hello', 'there']))


    def test_app(self):
        sys.argv = ['test_pyconvcli_internal_cli', "here", 'custom', 'route']
        cli = PyConvCli('test_pyconvcli_internal_cli', os.path.dirname(os.path.realpath(__file__)),'pyconvcli-test')
        args, parsers = cli.parse_args()
        cli.parsers = parsers
        cli.visualize()
