import cv2
import os
from PIL import Image
import numpy as np

#import pytesseract
#pytesseract.pytesseract.tesseract_cmd = 'tesseract'

def binariseImage(imPath):
    img = cv2.imread(imPath, 0)

    #text = pytesseract.image_to_string(img)
    #print(text)

    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #### extract all contours
    # contours,_ = cv2.findContours(img.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #
    # # debug: draw all contours
    # cv2.drawContours(img, contours, -1, (0, 255, 0), 10)
    # cv2.imshow('Contours', img)
    #
    # cv2.imwrite("all_contours.jpg", img)



    # Otsu's thresholding after Gaussian filtering
    blur = cv2.GaussianBlur(img, (5, 5), 10)
    ret3, th3 = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    #im = Image.fromarray(th3)

    th3  = np.invert(th3)
    #====================================
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(th3, connectivity=8)
    # connectedComponentswithStats yields every seperated component with information on each of them, such as size
    # the following part is just taking out the background which is also considered a component, but most of the time we don't want that.
    sizes = stats[1:, -1];
    nb_components = nb_components - 1

    # minimum size of particles we want to keep (number of pixels)
    # here, it's a fixed value, but you can set it as you want, eg the mean of the sizes or whatever
    min_size = 500

    # your answer image
    img2 = np.zeros((output.shape))
    # for every component in the image, you keep it only if it's above min_size
    for i in range(0, nb_components):
        if sizes[i] >= min_size:
            img2[output == i + 1] = 255
    im = Image.fromarray(np.invert(img2.astype(np.uint8)))
    return im


def binariseEasy():
    allManuDir = r"/home/olya/Documents/fragmentsData/Lettersshin"

    for d in os.listdir(allManuDir):
        if d.endswith("_bin"):
            continue
        currDir = os.path.join(allManuDir, d)
        binDir = currDir+"_bin"
        if not os.path.exists(binDir):
            os.mkdir(binDir)
        for name in os.listdir(currDir):
            fullName = os.path.join( currDir, name )
            binImage = binariseImage(fullName)
            binImage.save(os.path.join(binDir, name))




def removeBadLetters():
    import sys
    sys.path.append('/home/olya/krakenDir/')
    from kraken.krakenCli import  loadModel, letterExist
    import shutil
    nm = loadModel()
    #exist = letterExist(nm['default'], 'letter_.jpg')

    allManuDir = r"/home/olya/Documents/fragmentsData/Letterslamed"
    badLetters = r"/home/olya/Documents/fragmentsData/LetterslamedBad"
    for d in os.listdir(allManuDir):
        if not d.endswith("_bin"):
            continue
        binDir = os.path.join(allManuDir, d)

        for name in os.listdir(binDir):
            fullName = os.path.join(binDir, name)
            letterOk = letterExist(nm['default'], fullName, letterToFind ='ל')
            if not letterOk:
                shutil.move(fullName, badLetters)
                print("bad")
            else:
                print("good")




def flatten():
    import shutil
    fromFolder= '/home/olya/Documents/fragmentsData/Letters/Lettersshin'
    toFolder = '/home/olya/Documents/fragmentsData/Letters/LettersshinFlat'
    if not os.path.exists(toFolder):
        os.makedirs(toFolder)
    for d in os.listdir(fromFolder):
        if not d.endswith("_bin"):
            continue
        binDir = os.path.join(fromFolder, d)
        if len(os.listdir(binDir)) == 0:
            os.rmdir(binDir)
            print("removed {}".format(binDir))
            continue
        for name in os.listdir(binDir):
            fullName = os.path.join(binDir, name)
            shutil.copy(fullName,  os.path.join(toFolder, name))



def fremoveBad():
    import shutil
    fromFolder= '/home/olya/Documents/fragmentsData/Letters/LettersAlef'
    toFolder = '/home/olya/Documents/fragmentsData/Letters/LettersAlefFlat'
    badFolder = '/home/olya/Documents/fragmentsData/LettersAlefBad'
    allGoodLetters = os.listdir(toFolder)
    if not os.path.exists(toFolder):
        os.makedirs(toFolder)
    for d in os.listdir(fromFolder):
        if not d.endswith("_bin"):
            continue
        binDir = os.path.join(fromFolder, d)
        for name in os.listdir(binDir):
            if name not in  allGoodLetters:
                fullName = os.path.join(binDir, name)
                shutil.move(fullName,  os.path.join(badFolder, name))
        if len(os.listdir(binDir)) == 0:
            os.rmdir(binDir)
            print("removed {}".format(binDir))
            continue


def invForLetter(folder):
    ret = {}
    ret_fragments = {}
    for d in os.listdir(folder):
        if not d.endswith("_bin"):
            continue
        manu = d[:-4]
        binDir = os.path.join(folder, d)
        allLetters = os.listdir(binDir)
        ret[manu] = len(allLetters)

        fragments = [s.split("-")[1] for s in allLetters ]
        ret_fragments[manu] = len(set(fragments))


    return ret, ret_fragments




def makeInventory():
    import pandas as pd
    inv = {}
    alef, alefF = invForLetter('/home/olya/Documents/fragmentsData/Letters/LettersAlef')
    lamed, lamedF = invForLetter('/home/olya/Documents/fragmentsData/Letters/Letterslamed')
    shin, shinF = invForLetter('/home/olya/Documents/fragmentsData/Letters/Lettersshin')
    for d, name in [(alef, 'alef'), (alefF, 'alef_fragments_num'),  (lamed, 'lamed'), (lamedF, 'lamed_fragments_num'),
                    (shin, 'shin'), (shinF, 'shin_fragments_num')]:
        for k,v in d.items():
            if k not in inv:
                inv[k] = {}
            inv[k][name] = v


    df = pd.DataFrame.from_dict(inv).fillna(0).transpose()
    df.to_csv("inventory.csv")

















def main():
    makeInventory()
    #flatten()
    #fremoveBad()
    #removeBadLetters()
    #binariseEasy()





if __name__ == '__main__':
    main()
