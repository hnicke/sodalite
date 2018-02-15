import os

from mylogger import logger


# emulates functionality of unix calls pushd and popd,
# but in same process
# stores a list of visited dirs in a stack
class DirService:
    def __init__(self):
        self.pushstack = list()

    def getcwd(self):
        return os.getcwd()

    # travels up:
    # if there is a precessor in the pushstack, visit him
    # if pushstack is emtpy, go straight up to the parent dir
    # returns dirname of target
    def travel_back(self):
        if (len(self.pushstack) > 0):
            dirname = self.__popd()
        else:
            self.__chdir('..')
            dirname = os.getcwd()
        return dirname

    # travels down given path
    # current dir is added to pushstack
    # dirname: travel target
    def travel_to(self, dirname):
        self.__pushd(dirname)

    def __pushd(self, dirname):
        self.pushstack.append(os.getcwd())
        try:
            self.__chdir(dirname)
        except NotADirectoryError:
            # do nothing
            pass
        logger.info("pushstack: " + str(self.pushstack))

    def __popd(self):
        if (len(self.pushstack) > 0):
            dirname = self.pushstack.pop();
            os.chdir(dirname)
        else:
            dirname = None
        logger.info("pushstack: " + str(self.pushstack))
        return dirname

    def __chdir(self, path):
        try:
            os.chdir(path)
        except PermissionError:
            # TODO: show error in gui
            logger.info("Cannot access '" + path + "': Permission Denied")
