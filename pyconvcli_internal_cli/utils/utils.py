import pkg_resources
class Utility_CLI():
    _cli_path=[]
    def version(self):
        print(pkg_resources.get_distribution("pyconvcli").version)
    def smile(self):
        print(":)")

