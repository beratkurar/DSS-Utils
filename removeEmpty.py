
import os


def removeEmpty( folder ):
    #folder = r'/home/olya/Documents/fragmentsData/DSS_Joins_bin'
    for f in os.listdir(folder):
        if  len(os.listdir(os.path.join(folder, f)))==0:
            print(f)
            os.rmdir( os.path.join(folder, f))
