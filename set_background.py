import shutil
from PIL import Image
import os
from removeEmpty import removeEmpty


def main1():
    import os
    import shutil
    from dataloaders.triplet_loss_dataloader import  getBinarisedImage

    binPath =r'/home/olya/Documents/DataGan/trainBbin'
    regPath = r'/home/olya/Documents/DataGan/trainB'

    for root, b, im in os.walk(r'/home/olya/Documents/fragmentsData/DSS_Joins'):
        for i in im:
            if i.endswith("npy"):
                continue
            fullP = os.path.join(root, i)
            bin = getBinarisedImage(fullP)
            if bin is None:
                continue
            shutil.copy(src = bin, dst=os.path.join(binPath, i[:-3]+"tif"))
            shutil.copy(src=fullP, dst=os.path.join(regPath, i))






def moveBin():
    from distutils.dir_util import copy_tree
    fromFolder =r'/home/olya/Documents/fragmentsData/DSS_Joins_bw'
    toFolderr=r'/home/olya/Documents/fragmentsData/DSS_Joins_bin'
    for f in os.listdir(fromFolder):
        if f.endswith("bin"):

            copy_tree(os.path.join(fromFolder,f), os.path.join(toFolderr,f[:-4]))


def moveGood():
    import shutil
    toFolder = r'/home/olya/Documents/fragmentsData/DSS_Joins_binGood'
    goodFiles = os.listdir(toFolder)
    for root, b, im in os.walk(r'/home/olya/Documents/fragmentsData/DSS_Joins_bin'):
        for i in im:
          if i.endswith("tif") and not i in goodFiles:
              os.remove(os.path.join(root, i))






def setBg( image, i, j ):

    queue =[]

    queue.append((i,j))

    while not len(queue) == 0:
        currI,currJ = queue.pop()
        image[currI][currJ] = 255

        try:
            if image[currI+1][currJ] == 0:
                queue.append((currI+1, currJ))
        except:
            pass

        try:
            if image[currI-1][currJ] == 0:
                queue.append(( currI - 1, currJ))
        except:
            pass
        try:
            if image[currI][currJ+1] == 0:
                queue.append(( currI, currJ + 1))
        except:
            pass
        try:
            if image[currI][currJ-1] == 0:
                queue.append(( currI, currJ - 1))
        except:
            pass
        try:
            if image[currI+1][currJ+1] == 0:
                queue.append(( currI + 1, currJ + 1))
        except:
            pass
        try:
            if image[currI-1][currJ-1] == 0:
                queue.append(( currI - 1, currJ - 1))
        except:
            pass




if __name__ == '__main__':

    cnt=0
    for root, b, im in os.walk(r'/home/olya/Documents/fragmentsData/DSS_Joins_Test_bin'):
        for i in im:
            if i.endswith("tif"):
                imag = Image.open(os.path.join(root, i))
                w,h  = imag.size
                imag = imag.resize((w//2, h//2))
                imag = np.array(imag)
                print(i)
                setBg(imag, 0,0)
                imag = Image.fromarray(imag)
                imag.save()