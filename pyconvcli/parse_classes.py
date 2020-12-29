

from pydash import get,omit

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
