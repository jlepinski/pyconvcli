from pyconvcli import ParserArgType
import inspect
from pydash import omit
from os import path
import os
import stringcase

class New_CLI():
    def cli(self,
            project_name:ParserArgType(type=str, help="the name of your project", required=True),
            root_package_name:ParserArgType(type=str, default='cli', help="the name of your cli package"),
            cli_call_word:ParserArgType(type=str,help="the string that will be added to your path to call your cli"),
            version:ParserArgType(type=str, default='0.0.1', help="the version of your project")=None,
            author:ParserArgType(type=str,help="the author of your project")=None,
            author_email:ParserArgType(type=str, help="the email of the author of your project")=None,
            description:ParserArgType(type=str, help="the description of your project")=None,
            ):
        self.module(name=project_name)
        os.chdir(project_name)
        print(root_package_name,project_name)
        self.setup_file(entry_package_name=root_package_name,entry_point=cli_call_word,name=project_name,version=version,author=author,author_email=author_email,description=description)
        self.module(name=root_package_name)
        os.chdir(root_package_name)
        self.entry_class(root_package_name)
        self.module(name="hello")
        os.chdir("hello")
        self.cli_class(class_name="world")
        
        print("TODO:create new cli project")

    def cli_class(self,
                class_name:ParserArgType(type=str, required=True),
                cli_path:ParserArgType(type=str)=None):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"resources","cli_class_template.txt"), 'r') as f:
                file_content=f.read().format(name=stringcase.capitalcase(class_name), cli_path=cli_path)
                
                f = open(f'{stringcase.trimcase(class_name)}.py', "w")
                f.write(file_content)
                f.close()
        print(f'TODO:create new cli class named {class_name}')

    def entry_class(self,root_package_name):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"resources","entry_class_template.txt"), 'r') as f:
            file_content=f.read().format(entry_module_name=stringcase.trimcase(root_package_name))
            
            f = open(f'cli.py', "w")
            f.write(file_content)
            f.close()

    def module(self,name:ParserArgType(type=str, required=True)):
        os.mkdir(name)
        open(os.path.join(name,'__init__.py'), "x")
    
    def setup_file(self, 
        entry_package_name:ParserArgType(type=str, required = True),
        entry_point:ParserArgType(type=str, required = True),
        name:ParserArgType(type=str, required=True),
        version:ParserArgType(type=str, default='0.0.1')=None,
        author:ParserArgType(type=str)=None,
        author_email:ParserArgType(type=str)=None,
        description:ParserArgType(type=str)=None,
        ):
            # if path.exists("setup.py"):
            #     raise Exception ('the setup.py file already exists in this directory')
            assign_if_there = inspect.getfullargspec(self.setup_file).args[3:]
            print(entry_package_name,name)
            setup_content=""
            for variable in assign_if_there:
                if locals()[variable]:
                    setup_content=f'{setup_content}{variable}="{locals()[variable]}",\n        '
    
            print("created a setup.py file")
            with open(f'{os.path.dirname(os.path.realpath(__file__))}/resources/setup_template.txt', 'r') as f:
                setup_file=f.read().format(profile_info=setup_content.strip(' \t\n\r'), cli_entry_point=entry_point,project_name=name, entry_package=entry_package_name)
                
                f = open("setup.py", "w")
                f.write(setup_file)
                f.close()