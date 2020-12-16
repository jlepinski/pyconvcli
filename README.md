# pyconvcli
A convention based CLI framework for python

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


#### step 4
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

1. I need to come up with a convention for configuring details about a subparser. I an thinking of maybe setting up a configuration file where you can add additional metadata for configuring your subparsers without going to multiple places.

2. I would like to get a small app that runs as a visualized version of the cli so you can run your cli by just filling out some forms or using the forms then copy a string that you can just paste in the terminal to run.

3. I would consider putting together an object written to a file representing the cli structure at build time of your project using a cmdclass in your setup.py. This would allow us to create the parsers at runtime without loading or inspecting any classes and would allow you to run your project without importing anything but your entrypoint. The benefits of this would be rather small unles you have a very large project.


### Who do I talk to? ###

* Repo owner or admin joshualepinski@gmail.com