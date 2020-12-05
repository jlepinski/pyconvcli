# pyconvcli
A convention based CLI framework for python

### How do I get set up? ###

In the root directory of your project have a entry point that creates the cli object for example if your root module is in a folder called pyconvclitest you would use the following to run the cli as your entrypoint.
``` 
from pyconvcli import PyConvCli
import os

def main():
    cli = PyConvCli('pyconvclitest',os.path.dirname(os.path.realpath(__file__)))
    cli.run()
```
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

### Plans for the future. 
1. I would like to get a small app that runs as a visualized version of the cli so you can run your cli by just filling out some forms or using the forms then copy a string that you can just paste in the terminal to run.
2. I would consider putting together an object written to a file representing the cli structure at build time of your project using a cmdclass in your setup.py. This would allow us to create the parsers at runtime without loading or inspecting any classes and would allow you to run your project without importing anything but your entrypoint. The benefits of this would be rather small unles you have a very large project.
3. I need to come up with a convention for configuring details about a subparser. I an thinking of maybe setting up a configuration file where you can add additional metadata for configuring your subparsers without going to multiple places.


### Who do I talk to? ###

* Repo owner or admin joshualepinski@gmail.com