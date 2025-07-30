import os


def pathResolve(*ps):
    return os.path.normpath(os.path.join(*ps))
