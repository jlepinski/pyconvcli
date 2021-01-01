from pyconvcli import ParserArgGroupType, ParserArgMutuallyExclusiveType, ParserArgType, ArgGroupsDecorator
import argparse

class Please_CLI():
    _cli_path=['here','custom','route']
    def commandOne(self):
        print("command one called")
    def commandTwo(self):
       print("command two called")

class Groups_CLI():
    _cli_path=['here','custom','groups']
    @ArgGroupsDecorator(ParserArgGroupType(name='required',description="my required group"), ParserArgMutuallyExclusiveType(name='exclusive',required=True))
    def groupsCommand(self,arg1:ParserArgType(group='required'),arg2:ParserArgType(group='exclusive'),arg3:ParserArgType(group='exclusive')):
        print("groups command called")

class Testing_CLI():
    _cli_path=['here','testing']
    def testCommand(self,arg1:int,arg2:str,arg3:ParserArgType(type=str,choices=['exclusive','inclusive','indecisive'])):
        print(f'arg1:{arg1}, arg2:{arg2}, arg3:{arg3}')

class CustomName_CLI():
    _cli_path=['there']
    def customNameCommand(self,arg1:ParserArgType('--color',type=str,choices=['red','green','blue']),arg2:ParserArgType('--rgb','-r',type=str, nargs=3),arg3:ParserArgType(type=str,choices=['exclusive','inclusive','indecisive'])):
        print(f'arg1:{arg1}, arg2:{arg2}, arg3:{arg3}')

    def customNameStarNCommand(self,arg:ParserArgType('--rgb','-r',type=str, nargs='*')):
        print(f'arg:{arg}')

    def nargsChoiceCommand(self,arg:ParserArgType('--rgb','-r',type=str, nargs='*', choices=['2','1','4'])):
        print(f'arg:{arg}')

    def thereOrNotCommand(self,feature:ParserArgType(action='store_true'),notfeature:ParserArgType(action='store_false')):
        print(f'feature:{feature},notfeature:{notfeature}')

class Exploritory_CLI():
    _cli_path=[]
    def actionStoreConst(self, constarg:ParserArgType(action='store_const', const=42, default='default')):
        print(f'if the constarg value is passed the const is set and the answer to the universe is {constarg}')

    def fileOpenWidget(self, file:ParserArgType(type=argparse.FileType('r', encoding='UTF-8'))):
        print(f'file {file}')

    def filesNStarOpenWidget(self, file:ParserArgType(type=argparse.FileType('r', encoding='UTF-8'), nargs="*")):
        print(f'file {file}')


    def filesN2OpenWidget(self, file:ParserArgType(type=argparse.FileType('r', encoding='UTF-8'), nargs=2)):
        print(f'file {file}')