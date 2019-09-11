# in this file, we mailly prepare the environment. for example, folders, data sets etc.
import os

def mkdirs():
    rootDirName = 'DL4Rtree'

    if not os.path.exists(rootDirName):
        os.mkdir(rootDirName)
        print("Directory ", rootDirName, " Created ")
    else:
        print("Directory ", rootDirName, " already exists")

    datasetsDirName = os.path.join(rootDirName, 'datasets')

    if not os.path.exists(datasetsDirName):
        os.mkdir(datasetsDirName)
        print("Directory ", datasetsDirName, " Created ")
    else:
        print("Directory ", datasetsDirName, " already exists")