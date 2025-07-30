
class SWVersion(object):

    def __init__(self, release: int, version: int, sub_version: int):
        self.release = release
        self.version = version
        self.sub_version = sub_version

    def __str__(self):
        return "Version {0:02d}.{1:02d}.{2:02d}".format(self.release, self.version, self.sub_version)