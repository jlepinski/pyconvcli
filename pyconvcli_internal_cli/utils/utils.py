import pkg_resources
from pyconvcli import ActionArguement
class Utility_CLI():
    _cli_path=[]
    @ActionArguement()
    def version(self):
        print(pkg_resources.get_distribution("pyconvcli").version)


