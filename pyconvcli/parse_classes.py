

from pydash import get,omit, pick, merge
import argparse
import inspect

class ParserArgType():
    def __init__(self, *args, **kwargs):
        """
        this class will be used to pass allong values to the argparse add_argument function
        """
        #group is seperated out because it is not an original argument to the argparse add_argument function call
        #seperating it out allows us to select a group for our argument to be placed in if it is indicated
        group=get(kwargs,'group')
        if group:
            self.group=group
        self.args=args
        self.kwargs=omit(kwargs,'group')

class ParserArgGroupType():
    def __init__(self, name=None,description=None):
        """
        this class will be used to pass allong values to the argparse add_argument_group function
        """
        self.name=name
        self.description=description

class ParserArgMutuallyExclusiveType():
    def __init__(self, name=None, description=None,required=False):

        """
        this class will be used to pass allong values to the argparse add_mutually_exclusive_group function
        """
        self.name=name
        self.description=description
        self.required=required

def ArgGroupsDecorator(*args):
    def wrapper(func):
        func._arg_groups=args
        return func
    return wrapper

def ActionArguement(*args, **kwargs):
    #inspiration for action command decorator https://stackoverflow.com/questions/8632354/python-argparse-custom-actions-with-additional-arguments-passed

    def wrapper(func):
        def make_action(*original_args,**kwargs):
            class PyconvCliCustomAction(argparse.Action):
                def __call__(self, parser, args, values, option_string=None):
                    # I run some inspection here so the user can have a little more freedom with
                    # their method signature if they want to without having to go to all *args and **kwargs
                    inspected_args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations  = inspect.getfullargspec(func)
                    if varkw==None and varargs==None and len(inspected_args)==1 and inspected_args[0]=='self':
                        func(self)
                    elif varkw==None:
                        params = pick(merge(kwargs,vars(args)),list(inspect.signature(func).parameters.keys()))
                        if func.__name__ in params:
                            params[func.__name__]=values
                        func(self,*original_args,**params)
                    else:
                        params = merge(kwargs,vars(args))
                        if func.__name__ in params:
                            params[func.__name__]=values
                        func(self,*original_args,**params)


            return PyconvCliCustomAction
        if 'action_param_nargs' in kwargs:
            func._action_param_nargs=kwargs['action_param_nargs']
            passed_kwargs=omit(kwargs,'action_param_nargs')
        else:
            func._action_param_nargs=0
            passed_kwargs=kwargs
        func._action_param_action=make_action
        func._action_param_args=args
        func._action_param_kwargs=passed_kwargs
        return func
    return wrapper
