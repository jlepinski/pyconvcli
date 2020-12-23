# pyconvcli
A convention based CLI framework for python

This framework builds on the argparse library making it easy to setup and build a cli by convention from code without having to string together the hierarchy yourself. You simpley create a cli project using the cli which is built using the framework itself, and create classes with functions. We utilize the type annotation to configure your cli attributes for you using the same params as the argparse.add_argument function with an expansion of the 'group' attribute to let you assign a parameter to a group. You can create groups using our decorator which adds metadata to the function so that we can assign the parameters to the correct group.

### How do I get set up? ###

#### step 1
run the install command
`pip3 install pyconvcli`

#### step 2

run the command to create a new cli project in the directory you want to create it in.

for example

`pyconvcli new cli --project_name example --cli_call_word mycli`

the usage is as follows
```
usage: pyconvcli new cli [-h] --project_name PROJECT_NAME
                         [--root_package_name ROOT_PACKAGE_NAME]
                         [--cli_call_word CLI_CALL_WORD] [--version VERSION]
                         [--author AUTHOR] [--author_email AUTHOR_EMAIL]
                         [--description DESCRIPTION]

optional arguments:
  -h, --help            show this help message and exit
  --project_name PROJECT_NAME
                        the name of your project
  --root_package_name ROOT_PACKAGE_NAME
                        the name of your cli package
  --cli_call_word CLI_CALL_WORD
                        the string that will be added to your path to call
                        your cli
  --version VERSION     the version of your project
  --author AUTHOR       the author of your project
  --author_email AUTHOR_EMAIL
                        the email of the author of your project
  --description DESCRIPTION
                        the description of your project
```

#### step 3
in order to create a command you need to create a class in your project that either ends with _CLI in the name or _CLI_ROOT. if it ends with cli the command will be the file path from the root of your project followed by the function name. If it is _CLI_ROOT it will be the function name followed by the root command of your project

This is an example of the code to add a root command
```
import time
from pyconvcli import ParserArgType


class Alternative_CLI_ROOT():
    def dance(
        self,
        rythem:ParserArgType(type=int, choices=range(60),dest="rythem",required=True),
        song:str,
        duration:int):
        """
        params 
        rythem: movements per minute
        time: minutes
        song: song to dance to

        """
        start_time = time.time()
        count=0
        print(f'{song} playing.....')
        while time.time()-start_time< (duration*60):
            if(count % 2) == 0:
                print('<("<)')
            else:
                print('(>")>')
            count = count +1
            time.sleep((60/rythem))
```
You can also optionally add a _cli_path attribut to the class with a value of the string array you want to declare the path as. This will have a higher priority and allow you to declare the path to your action set.

### Plans for the future. 

1. I would like to get a small app that runs as a visualized version of the cli so you can run your cli by just filling out some forms or using the forms then copy a string that you can just paste in the terminal to run.

2. I would consider putting together an object written to a file representing the cli structure at build time of your project using a cmdclass in your setup.py. This would allow us to create the parsers at runtime without loading or inspecting any classes and would allow you to run your project without importing anything but your entrypoint. The benefits of this would be rather small unles you have a very large project.


### Who do I talk to? ###

* Repo owner or admin joshualepinski@gmail.com