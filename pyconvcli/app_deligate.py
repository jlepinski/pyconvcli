"""Main Python application file for the EEL-CRA demo."""

import os
import platform
import random
import sys
import json
import eel
from pydash import map_, find



@eel.expose  # Expose function to JavaScript
def say_hello_py(x):
    """Print message from JavaScript on app initialization, then call a JS function."""
    print('Hello from %s' % x)  # noqa T001
    # eel.say_hello_js('Python {from within say_hello_py()}!')


@eel.expose
def expand_user(folder):
    """Return the full path to display in the UI."""
    return '{}/*'.format(os.path.expanduser(folder))


@eel.expose
def build_options():
    """Return a structure that allows us to build a cli application"""
    delegate = EelDeligate.instance()
    cli = delegate.cli
    start_key=find(cli.parsers.keys(),lambda key: key.find('.')==-1)
    delegate.start_key=start_key
    json_version=build_sub_options(cli.parsers,start_key)
    return json.dumps(json_version)

def build_sub_options(parsers,key):
    parser_object=parsers[key]
    choices=[]
    if 'subparsers' in parser_object and hasattr(parser_object['subparsers'],'choices'):
        sub_keys=list(parser_object['subparsers'].choices.keys())
        for sub_key in sub_keys:
            child_key = '.'.join([key,sub_key])
            if child_key in parsers:
                sub_result = build_sub_options(parsers,child_key)
                choices.append(sub_result)
    if 'callables' in parser_object:
        callables=parser_object['callables']
        for callable_key in callables:
            choices.append(
                {
                    "name":callable_key,
                    "is_callable":True,
                    "key":key,
                    "function_name":callables[callable_key]['function_name'],
                    "form":function_sig_to_json_form_structure(callables[callable_key]['class_ref'],callables[callable_key]['function_name'])
                }
            )
    return {
        "name":key.split('.')[-1],
        "is_callable":False,
        "key":key,
        "choices":choices
    }

def function_sig_to_json_form_structure(class_ref,function_name):
    # ToDo: write a json version of the function signature that can be used to make a form
    return {}

class EelDeligate():

    _instance = None
    cli=None
    start_key=None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            print('Creating new instance')
            cls._instance = cls.__new__(cls)
            # Put any initialization here.
        return cls._instance

    def start(self,develop):
        """Start Eel with either production or development configuration."""

        if develop:
            directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),'visualizer','src')
            app = None
            page = {'port': 3000}
        else:
            directory = os.path.join(os.path.dirname(os.path.realpath(__file__)),'visualizer','build')
            app = 'chrome-app'
            page = 'index.html'

        eel.init(directory, ['.tsx', '.ts', '.jsx', '.js', '.html', '.css'])

        # These will be queued until the first connection is made, but won't be repeated on a page reload
        say_hello_py('Python World!')
        print(directory)
        # eel.say_hello_js('Python World!')   # Call a JavaScript function (must be after `eel.init()`)

        # eel.show_log('https://github.com/samuelhwilliams/Eel/issues/363 (show_log)')

        eel_kwargs = dict(
            host='localhost',
            port=8080,
            size=(1280, 800),
        )
        try:
            eel.start(page, mode=app, **eel_kwargs)
        except EnvironmentError:
            # If Chrome isn't found, fallback to Microsoft Edge on Win10 or greater
            if sys.platform in ['win32', 'win64'] and int(platform.release()) >= 10:
                eel.start(page, mode='edge', **eel_kwargs)
            else:
                raise

