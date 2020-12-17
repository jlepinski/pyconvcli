from pyconvcli import ParserArgGroupType, ParserArgMutuallyExclusiveType, ParserArgType, ArgGroupsDecorator

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