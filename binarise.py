
import sys
import os
import shutil
import subprocess
import cv2
from PIL import Image

def binariseImage(imPath):
    img = cv2.imread(imPath, 0)
    # Otsu's thresholding after Gaussian filtering
    blur = cv2.GaussianBlur(img, (5, 5), 10)
    ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    im = Image.fromarray(th3)
    return im


def binarySavoula(imPath):
    import matplotlib
    import numpy as np
    import matplotlib.pyplot as plt
    from skimage.data import page
    from skimage.filters import (threshold_otsu, threshold_niblack,
                                 threshold_sauvola)

    matplotlib.rcParams['font.size'] = 9

    image =  np.array(Image.open(r'/home/olya/Documents/fragmentsData/DSS_Joins_bw/1Q8/P677-Fg002-R-C01-R01-D17072013-T150731-LR924_012.jpg'))


    window_size = 15

    thresh_sauvola = threshold_sauvola(image, window_size=window_size)


    binary_sauvola = image > thresh_sauvola
    plt.subplot(2, 2, 4)
    plt.imshow(binary_sauvola, cmap=plt.cm.gray)
    plt.title('Sauvola Threshold')
    plt.axis('off')

    plt.show()




def binariseEasy():
    allManuDir = r"/home/olya/Documents/fragmentsData/DSS_Joins_Test_bw"

    for d in os.listdir(allManuDir):
        if d.endswith("_bin"):
            continue
        currDir = os.path.join(allManuDir, d)
        binDir = currDir+"_bin2"
        if not os._exists(binDir):
            os.mkdir(binDir)
        for name in os.listdir(currDir):
            fullName = os.path.join( currDir, name )
            binImage = binariseImage(fullName)
            binImage.save(os.path.join(binDir, name))







def binarise():
    allManuDir = r"/home/olya/Documents/fragmentsData/DSS_Joins1_bw"
    forBinPath = r'/home/olya/Documents/fragmentsData/DSS_Joins/forBin/tmp'

    for f in os.listdir(allManuDir):

        fullManuath = os.path.join(allManuDir, f)
        if not os.path.exists(fullManuath.replace(f, f+"_bin")):
            os.mkdir(fullManuath.replace(f, f+"_bin"))
        if os.path.isdir(os.path.join(fullManuath)):
            for f1 in os.listdir(fullManuath):
                fullPath = os.path.join(fullManuath, f1)
                finalOutPath = fullPath.replace(f, f + "_bin")
                finalOutPath = finalOutPath[:-3] + "tif"
                if os.path.exists(finalOutPath):
                    continue

                dest = os.path.join(forBinPath, f1 )
                shutil.copy(fullPath, dest)
                process = subprocess.Popen(['matlab', '-nodisplay', '-nosplash', '-nodesktop', '-r', "run('/home/olya/Documents/TL_DSS/segmentation_matlab/apply_binarization.m');exit;" ],
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                print(stdout)
                print(stderr)


                binOutput = '/home/olya/Documents/fragmentsData/DSS_Joins/forBin_Bin/tmp/binaries/tmp_sauvola_binary.tif'

                if os.path.exists(binOutput):
                    shutil.copy(binOutput, finalOutPath)
                    os.remove(binOutput)
                    print("done, file output: {}".format(finalOutPath))
                else:
                    print("Error processing {}".format(fullPath))
                if os.path.exists(dest):
                    os.remove(dest)
                if os.path.exists(r"/home/olya/Documents/fragmentsData/DSS_Joins/forBin_Bin/tmp/label/tmp_labels2.bmp"):
                    os.remove(r"/home/olya/Documents/fragmentsData/DSS_Joins/forBin_Bin/tmp/label/tmp_labels2.bmp")

                print("")


def expendBinary():
    import numpy as np
    folder = r'/home/olya/Documents/fragmentsData/DSS_Joins_Test_bw'

    for f in os.listdir(folder):
        if f.endswith("_bin2"):
            for currF in os.listdir(os.path.join( folder, f)):
                if currF.endswith("npy"):
                    continue
                i=0
                allRecs = np.load (os.path.join( folder, f,  currF[:-4]+".npy"), allow_pickle = True).item()['rand_sample']

                if allRecs:
                    img = Image.open(os.path.join(folder, f, currF))
                    img = img.resize((img.size[0] // 2, img.size[1] // 2))
                    if not os.path.exists( os.path.join( folder, f.replace("bin2", "bin3")) ):
                        os.mkdir( os.path.join( folder, f.replace("bin2", "bin3")))
                for rec in allRecs:
                    center, side = rec
                    w, h = center

                    im = img.crop((h - side, w - side, h + side, w + side))
                    im.save( os.path.join( folder, f.replace("bin2", "bin3"), currF[:-4]+str(i)+ currF[-4:]) )
                    i+=1



if __name__ == "__main__":
    #binarise()
    #binariseEasy()
    binarySavoula('')
    expendBinary()