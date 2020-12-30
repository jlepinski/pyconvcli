import os
import inspect
import importlib
import sys
import argparse
import json
from pydash import sort_by, find, group_by,map_, map_values, get,omit
from .app import PyconvcliApp
from .parse_classes import ParserArgType, ParserArgMutuallyExclusiveType,ParserArgGroupType
import tkinter


class PyConvCli():
    def __init__(self,root_module_name,dir_path,entry_name="entry_command_goes_here"):
        self.dir_path=dir_path
        self.root_module_name = root_module_name
        self.config={}
        self.entry_name=entry_name
        config_file_path=os.path.join(self.dir_path,'pyconvcli.json')
        if os.path.isfile(config_file_path): 
            with open(config_file_path) as f:
                self.config = json.load(f)
        self.parsers=None

    def run(self):
        args,parsers = self.parse_args()
        class_ref, function_name = self.find_class_and_function(args,parsers)
        self.run_cli_call(class_ref,function_name,args)

    def get_config_value(self,path,key):
        # keep in mind this will need to be done this way instead of using pydash because the . in pydash has a meaning to create a key path rather than just a key
        if path not in self.config:
            return None
        else:
            return get(self.config[path],key)
        
        
    def parse_args(self):
        parser = argparse.ArgumentParser(description=self.get_config_value(self.root_module_name,'description'))
        # dir_path = os.path.dirname(os.path.realpath(__file__))
        first_root=None
        first_package=None
        visited_roots=[]
        subparsers = parser.add_subparsers(help=self.get_config_value(self.root_module_name,'sub_help'))
        parsers={self.root_module_name:{"parser":parser,"subparsers":subparsers}}
        for root, dirs, files in os.walk(self.dir_path, topdown = True):
            if not first_root:
                first_root = root
            if root in visited_roots:
                continue
            visited_roots.append(root)
            for name in files:
                if name.endswith('.py') and not name.endswith('__.py'):
                
                    module_name = name.split('.py')[0]
                
                    if not root == first_root:
                        path_array = root[len(first_root)+1:len(root)].split(os.sep)
                        path_array.append(module_name)
                        module_name = '.'.join(path_array)
                    
                    if first_package==None:
                        first_package = module_name
                    module = None
                    try:
                        module = importlib.import_module(f'{self.root_module_name}.'+module_name)
                    except ModuleNotFoundError as e:
                        try:
                            module = importlib.import_module(module_name)
                        except ModuleNotFoundError as e:
                            print(e)
                    self.build_args_for_module(module_name,module,parsers)
        args = parser.parse_args()

        return args,parsers
        
    def run_cli_call(self,class_ref,function_name,args):
        fun = getattr(class_ref(),function_name)
        fun(**vars(args))

    def find_class_and_function(self,args,parsers):
        call = sys.argv
        call[0]=self.root_module_name
        list_of_parsers =list(parsers.keys())
        list_of_parsers.reverse()
        call_path = '.'.join(call)
        parser_key = find(list_of_parsers,
            lambda  path: call_path.startswith(path))
        function_name = call_path[len(parser_key)+1:].split('.')[0]
        parser_object = parsers[parser_key]
        if "callables" not in parser_object or function_name=='':
            parser_object['parser'].print_help()
            sys.exit(1)
        return (parser_object["callables"][function_name]['class_ref'],function_name)


    def build_args_for_module(self,module_name,module,parsers):
        for class_name, class_ref in inspect.getmembers(module): # what do I do here?
            if inspect.isclass(class_ref) and (class_ref.__name__.endswith('_CLI') or class_ref.__name__.endswith('_CLI_ROOT')):
                
                if hasattr(class_ref, "_cli_path") and isinstance(class_ref._cli_path, list): 
                    path = self.root_module_name if len(class_ref._cli_path)==0 else f'{self.root_module_name}.'+'.'.join(class_ref._cli_path)
                    self.create_subparser(path,module,parsers)
                    self.update_parser_for_functions(path,parsers,class_ref)
                elif class_ref.__name__.endswith('_CLI_ROOT'):
                    self.create_subparser(self.root_module_name,module,parsers)
                    self.update_parser_for_functions(self.root_module_name,parsers,class_ref)
                else:
                    self.create_subparser(f'{self.root_module_name}.'+module_name,module,parsers)
                    self.update_parser_for_functions(f'{self.root_module_name}.'+module_name,parsers,class_ref)

    def add_group_to_parrser(self,parser,group):
        if group.__class__ is ParserArgGroupType:
            return parser.add_argument_group(group.name,description=group.description)
        if group.__class__ is ParserArgMutuallyExclusiveType:
            return parser.add_mutually_exclusive_group(required=group.required)


    def update_parser_for_functions(self,modul_name,parsers,class_ref):

        parent_path_parser = parsers[modul_name]
           
        for function_name,function_ref in inspect.getmembers(class_ref):
            if inspect.isfunction(function_ref):
                        groups={}
                        if not "callables" in parent_path_parser:
                            parent_path_parser['callables']={}
                        if not "subparsers" in parent_path_parser:
                            parent_path_parser['subparsers']=parent_path_parser['parser'].add_subparsers(help=self.get_config_value(modul_name,'sub_help'))
                        parser=parent_path_parser['subparsers'].add_parser(function_name, description = self.get_config_value(f'{modul_name}.{function_name}','description'))
                        if hasattr(function_ref, '_arg_groups'):
                            groups = map_values(group_by(function_ref._arg_groups, 'name'), lambda groupArray: self.add_group_to_parrser(parser,groupArray[-1]))
                        
                        parent_path_parser['callables'][function_name] ={
                            "parser": parser,
                            "class_ref":class_ref,
                            "function_name":function_name,
                            "groups":groups}
                            
                        for param in inspect.signature(function_ref).parameters.values():
                      
                            parser = parent_path_parser['callables'][function_name]['parser']
                            if param.annotation.__class__==ParserArgType:
                      
                                args = tuple([f'--{param.name}']) if len(param.annotation.args)==0 else param.annotation.args
                                if len(param.annotation.args)>0 and 'dest' not in param.annotation.kwargs:
                                    param.annotation.kwargs['dest'] = param.name
                                if hasattr(param.annotation,'group'):
                                    group = get(groups,param.annotation.group)
                                    if group:
                                        group.add_argument(*args,**param.annotation.kwargs) 
                                    else:
                                        raise Exception(f'it appears that the group "{param.annotation.group}" is referenced by an arguement but not found when building the parser existing groups are {json.dumps(list(groups.keys()))}')
                                else:
                                    parser.add_argument(*args,**param.annotation.kwargs) 
                            if param.annotation == int:
                                parser.add_argument(f'--{param.name}',type=param.annotation)
                            if param.annotation == str:
                                parser.add_argument(f'--{param.name}',type=param.annotation)
                                
                            
    def create_subparser(self,module_name,module,parsers):
        path_array=[]
        module_slice_array = module_name.split('.')
        if module_name==self.root_module_name:
            parser_object = parsers[self.root_module_name]
            if "subparsers" not in parser_object:
                parser_object['subparsers']=parser_object['parser'].add_subparsers(help=self.get_config_value(self.root_module_name,'sub_help'))
            return 
        
        for path_segment in module_slice_array:
            path_array.append(path_segment)
            if '.'.join(path_array) not in parsers:
                if len(path_array)<2:
                    raise Exception(f'could not find root parser to {".".join(path_array)}')
                parser_object = parsers['.'.join(path_array[:-1])]
                if "subparsers" not in parser_object:
                    parser_object['subparsers']=parser_object['parser'].add_subparsers(help=self.get_config_value('.'.join(path_array[:-1]),'sub_help'))
                parsers['.'.join(path_array)] ={"parser": parser_object['subparsers'].add_parser(path_array[-1],description=self.get_config_value(".".join(path_array),'description'))}


    def visualize(self):
        root = tkinter.Tk()
        root.title("Pconvcli App")
        deligate = PyconvcliApp(root, self)
        deligate.cli=self
        deligate.entry_word='pyconvlci'

        deligate.mainloop()

