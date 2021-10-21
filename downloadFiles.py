
import paramiko
from scipy.io import loadmat
from collections import OrderedDict
import traceback
import os
import pandas as pd
import cv2
import numpy as np
from PIL import Image

L_MAP = OrderedDict( [
    ( u'\N{Hebrew Letter Alef}'       ,1),
    ( u'\N{Hebrew Letter Bet}'        ,2)   ,
    ( u'\N{Hebrew Letter Gimel}'      ,3)  ,
    ( u'\N{Hebrew Letter Dalet}'      ,4)  ,
    ( u'\N{Hebrew Letter He}'         ,5)   ,
    ( u'\N{Hebrew Letter Vav}'        ,6)      ,
    ( u'\N{Hebrew Letter Zayin}'      ,7)     ,
    ( u'\N{Hebrew Letter Het}'        ,8)     ,
    ( u'\N{Hebrew Letter Tet}'        ,9)    ,
    ( u'\N{Hebrew Letter Yod}'        ,10)     ,
    ( u'\N{Hebrew Letter Final Kaf}'  ,11)  ,
    ( u'\N{Hebrew Letter Kaf}'        ,12)     ,
    ( u'\N{Hebrew Letter Lamed}'      ,13)     ,
    ( u'\N{Hebrew Letter Final Mem}'  ,14)  ,
    ( u'\N{Hebrew Letter Mem}'        ,15)     ,
    ( u'\N{Hebrew Letter Final Nun}'  ,16)  ,
    ( u'\N{Hebrew Letter Nun}'        ,17)     ,
    ( u'\N{Hebrew Letter Samekh}'     ,18)    ,
    ( u'\N{Hebrew Letter Ayin}'       ,19)    ,
    ( u'\N{Hebrew Letter Final Pe}'   ,20)   ,
    ( u'\N{Hebrew Letter Pe}'         ,21)   ,
    ( u'\N{Hebrew Letter Final Tsadi}',22),
    ( u'\N{Hebrew Letter Tsadi}'      ,23) ,
    ( u'\N{Hebrew Letter Qof}'        ,24) ,
    ( u'\N{Hebrew Letter Resh}'       ,26) ,
    ( u'\N{Hebrew Letter Shin}'       ,26) ,
    ( u'\N{Hebrew Letter Tav}'        ,27)
    ]
)



def testMat():
    x = loadmat('/home/olya/PycharmProjects/text2img/data/boundaries.mat')
    print(x.keys())


def getImage( imageName, sftp, isFlipped ):
    folder = imageName.split("-")[0]

    imagesFolder = r"/home/olya/Documents/fragmentsData/newImages"
    remote_folder = r"/specific/disk1/home/nachumd/DSS/DSS_Fragments/fragments"

    allImages = sftp.listdir( r"{}/{}".format(remote_folder, folder) )

    maxLen = 0
    imageToGet = ""
    for n in allImages:
        currLen = len(os.path.commonprefix([n, imageName]))
        if currLen >= maxLen:
            imageToGet = n
            maxLen = currLen


    with sftp.open('{}/{}/{}'.format(remote_folder, folder, imageToGet)) as f:
        img = cv2.imdecode(np.fromstring(f.read(), np.uint8), 1)
        height, width, channels = img.shape
        if isFlipped:
            img = cv2.rotate(img, cv2.ROTATE_180)

        cv2.imwrite( os.path.join( imagesFolder, imageName), img)

    #cv2.imshow("image", img)
    #cv2.waitKey()
    return height, width

def getCropCoordinates( name, sftp):
    coorinatesPath = r"/specific//disk1/home/nachumd/DSS/DSS_Fragments/cords"
    folder = name.split("-")[0]

    allCoord = sftp.listdir(r"{}/{}".format(coorinatesPath, folder))

    maxLen = 0
    coordToGet = ""
    for n in allCoord:
        currLen = len(os.path.commonprefix([n, name]))
        if currLen >= maxLen:
            coordToGet = n
            maxLen = currLen

    with sftp.open('{}/{}/{}'.format(coorinatesPath, folder, coordToGet)) as f:
        data = f.read()

    v = data.decode().split(" ")
    return int(v[0]), int(v[1]), float(v[2])



def getOrigImageParams(name, sftp):
    remotePath = r"/specific/disk1/home/nachumd/DSS/iiif_download/{}".format(name)
    with sftp.open(remotePath) as f:
        img = cv2.imdecode(np.fromstring(f.read(), np.uint8), 1)
        height, width, channels = img.shape
    return height, width





def main():
    outputPath = r"/home/olya/Documents/fragmentsData/newImages"

    p = r'/home/olya/Documents/fragmentsData/0_line_table03.csv'
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect("rack-nachum1.cs.tau.ac.il", 22, username="olyasirkin", password='1QAZ2wsx', timeout=4)
    fliped = pd.read_csv(r"/home/olya/PycharmProjects/text2img/flip.csv")
    fliped = fliped.set_index("image", )
    fliped = fliped[["flip"]].transpose()
    fliped = fliped.to_dict()
    sftp = s.open_sftp()

    df = pd.read_csv(p)
    isFlipped = True
    skip=True
    for v, imageDF in df.groupby('imagename'):
        # (x, y, w, h, cls)
        if not v.startswith("ok/"):
            continue
        imageName = v[3:]
        print(imageName)

        # if imageName == "P201-Fg001-R-C01-R01-D28112013-T115442-LR924_012.jpg":
        #     isFlipped = False
        #     skip = False
        #     break
        if imageName not in fliped:
            continue
        flipedVal = fliped[imageName]["flip"]
        if flipedVal not in [0, 1]:
            continue

        isFlipped = flipedVal==1

        try:
            height, width = getImage(imageName, sftp, isFlipped)
        except:
            print("Get image failed for image {}".format(imageName))
            traceback.print_exc()
            continue
        clsCol = "gt"
        xmin = imageDF[['gt_x1', 'gt_x4', 'gt_x2', 'gt_x3']].min(axis=1)
        xmax = imageDF[['gt_x1', 'gt_x4', 'gt_x2', 'gt_x3']].max(axis=1)
        ymin = imageDF[['gt_y1', 'gt_y4', 'gt_y2', 'gt_y3']].min(axis=1)
        ymax = imageDF[['gt_y1', 'gt_y4', 'gt_y2', 'gt_y3']].max(axis=1)
        try:
            origHeight, origWidth = getOrigImageParams(imageName, sftp)
        except:
            print("get orig image failed for image {}".format(imageName))
            traceback.print_exc()
            continue

        try:
            startCropY, startCropX, ratio = getCropCoordinates(imageName, sftp)
        except:
            print("Get cropped parameters failed for image {}".format(imageName))
            traceback.print_exc()
            continue
        #print("Orig width {}, height {}".format(origWidth, origHeight))
        #print("Image width {}, height {}".format(width, height))
        #print("start cropx  {}, startcrop y {}".format(startCropX, startCropY))


        if isFlipped:
            startCropX = origWidth-width-startCropX
            startCropY = origHeight - height - startCropY
            #print( "{} {}".format(startCropX, startCropY) )

        #startCropX =0
        #startCropY =0
        df = pd.DataFrame()
        df["x"] = xmin - startCropX
        df["y"] = ymin - startCropY
        df["w"] = xmax - xmin
        df["h"] = ymax - ymin
        df["cls"] = imageDF["gt"]
        df["cls"] = df["cls"].map(L_MAP)
        df = df.dropna()
        df.astype(int).to_csv(os.path.join(outputPath, imageName.replace(".jpg", ".csv")), index=False)
        #break




def getTrans( imageName, sftp ):
    print(imageName)
    folder = imageName.split("-")[0]

    imagesFolder = r"/home/olya/Documents/fragmentsData/newImages"
    remote_folder = r'/specific/disk1/home/alexeyp/Tibetan_Transductive/Data/DSS_texts/'
    try:
        allImages = sftp.listdir( r"{}/{}".format(remote_folder, folder) )

        maxLen = 0
        imageToGet = ""
        for n in allImages:
            currLen = len(os.path.commonprefix([n, imageName]))
            if currLen >= maxLen:
                imageToGet = n
                maxLen = currLen


        with sftp.open('{}/{}/{}'.format(remote_folder, folder, imageToGet)) as f:
            with open(  os.path.join(imagesFolder, imageName.replace(".jpg", ".txt")), 'w') as fOut:
                fOut.writelines( f.readlines())
    except:
        print ("getting tracript for image {} failed :(".format(imageName))
        return
    print("getting tracript for image {} Suceeded :)".format(imageName))




def getTrascripts():

    outputPath = r"/home/olya/Documents/fragmentsData/newImages"


    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect("rack-nachum-g01.cs.tau.ac.il", 22, username="olyasirkin", password='1QAZ2wsx', timeout=4)
    sftp = s.open_sftp()
    allImages = os.listdir(outputPath)
    allImages = [i for i in allImages if i.endswith("jpg")]
    for imageName in allImages:
        getTrans(imageName, sftp)






def downloadImage(plate, imageName, manuscript, sftp):



    folder = plate

    imagesFolder = r"/home/olya/Documents/fragmentsData/DSS_Joins1_Test_bw"


    if  os.path.exists(os.path.join(imagesFolder, manuscript, imageName)):
        return

    remote_folder = r"/specific/netapp5_wolf/nachumd/home/nachumd/DSS/fragments_w"

    try:
        allImages = sftp.listdir(r"{}/{}".format(remote_folder, folder))

        maxLen = 0
        imageToGet = ""
        for n in allImages:
            if "LR924" in n and "-R-" in n:
                currLen = len(os.path.commonprefix([n, imageName]))
                if currLen >= maxLen:
                    imageToGet = n
                    maxLen = currLen
        if imageToGet == "":
            print("bw image for {} was not found".format(imageName))
            return
        imageToGetPlate = imageToGet.split("-Fg")[0]
        imageToGetFrag = imageToGet.split("-")[1]
        imageNamePlate = imageName.split("-Fg")[0]
        imageNameFrag = imageName.split("-")[1]
        if imageToGetPlate!=imageNamePlate or imageToGetFrag != imageNameFrag:
            print("may be getting wrong image: to get {} ,getting {}".format(imageName, imageToGet))
            return

        with sftp.open('{}/{}/{}'.format(remote_folder, folder, imageToGet)) as f:
            #print("download {}/{}/{}".format(remote_folder, folder, imageToGet))
            img = cv2.imdecode(np.fromstring(f.read(), np.uint8), 1)
            if not os.path.exists(os.path.join(imagesFolder, manuscript)):
                os.mkdir(os.path.join(imagesFolder, manuscript))
            cv2.imwrite(os.path.join(imagesFolder, manuscript, imageToGet), img)
    except:
        print("could not get {}".format(imageName))
        pass


def downloadBoundary(plate, imageName, manuscript, sftp):



    folder = plate

    imagesFolder = r"/home/olya/Documents/fragmentsData/DSS_Joins_Test_boundaries"


    if  os.path.exists(os.path.join(imagesFolder, manuscript, imageName)):
        return

    remote_folder = r"/specific/netapp5_wolf/nachumd/home/nachumd/DSS/DSS_Fragments/boundaries/fragments_nojp"

    try:
        allImages = sftp.listdir(r"{}/{}".format(remote_folder, folder))

        maxLen = 0
        imageToGet = ""
        for n in allImages:
            currLen = len(os.path.commonprefix([n, imageName]))
            if currLen >= maxLen:
                imageToGet = n
                maxLen = currLen

        with sftp.open('{}/{}/{}'.format(remote_folder, folder, imageToGet)) as f:
            print("download {}/{}/{}".format(remote_folder, folder, imageToGet))

            if not os.path.exists(os.path.join(imagesFolder, plate)):
                os.mkdir(os.path.join(imagesFolder, plate))
            toWrite = open(os.path.join(imagesFolder, plate, imageToGet), 'wb')
            toWrite.write(f.read())
            toWrite.close()
    except:
        print("could not get {}".format(imageName))
        pass



def getBWImages():
    import paramiko
    from PIL import Image
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect("rack-nachum1.cs.tau.ac.il", 22, username="olyasirkin", password='2WSX3edc', timeout=4)
    sftp = s.open_sftp()


    for root, b, im in os.walk(r'/home/olya/Documents/fragmentsData/DSS_Joins_Test'):
        for i in im:
            if i.endswith(".png"):
                splited = i.split("-Fg")
                plate = splited[0]
                manu = root.split("/")[-1]
                downloadImage(plate, i, manu, sftp)



    # for manu in os.listdir(r'/home/olya/Documents/fragmentsData/DSS_Joins_Test'):
    #     manusDir = os.path.join(r'/home/olya/Documents/fragmentsData/DSS_Joins_Test', manu)
    #     for f in os.listdir(manusDir):
    #         splited = f.split("-")
    #         plate = splited[0]
    #         # namestart = splited[0]+"-"+splited[1]+"-"+splited[2]
    #         downloadImage(plate, f, manu, sftp)
    #         #downloadBoundary(plate, f, manu, sftp)


    # s = "/home/olya/Documents/fragmentsData/SQE_image_to_manuscript_list.csv"
    # df = pd.read_csv(s)
    # filenames = df["filename"].tolist()
    # manuscript = df["manuscript"].tolist()
    # for f, m in zip(filenames, manuscript):
    #     if "924" not in f or "-R-" not in f:
    #         continue
    #     splited= f.split("-")
    #     plate = splited[0]
    #     #namestart = splited[0]+"-"+splited[1]+"-"+splited[2]
    #     downloadImage(plate, f, m, sftp)



    print("")





def filterBlacks():
    import shutil
    wrongImages = r'/home/olya/Documents/fragmentsData/wrongBW'
    for root, b, im in os.walk(r'/home/olya/Documents/fragmentsData/DSS_Joins1_Test_bw'):
        for i in im:
            a = np.array(Image.open( os.path.join(root, i)))
            red = a[:,:,0]
            w,h  = red.shape

            notBlack = red[red>5].shape[0]
            valid = notBlack/(w*h)>1/10
            if not valid:
                manu = root.split("/")[-1]
                if not os.path.exists(os.path.join(wrongImages, manu)):
                    os.mkdir(os.path.join(wrongImages, manu))
                print(i)
                shutil.move(os.path.join(root,i), os.path.join(wrongImages, manu, i))





def getSFTP():
    import paramiko
    from PIL import Image
    s = paramiko.SSHClient()
    s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    s.connect("rack-nachum1.cs.tau.ac.il", 22, username="olyasirkin", password='2WSX3edc', timeout=4)
    sftp = s.open_sftp()
    return sftp


def getallImagesNames():

    sftp = getSFTP()

    folderD = '/specific/hadar1/filesD/'
    folderC = '/specific/hadar1/filesC/'
    ret={}
    allImages = sftp.listdir(folderD)
    ret[folderD] =allImages
    allImages = sftp.listdir(folderC)
    ret[folderC] = allImages
    return ret


def getFragmentStr(fragment):
    if fragment<10:
        return "00{}".format(fragment)
    elif fragment<100:
        return "0{}".format(fragment)
    else:
        return str(fragment)

def getFragmentPlacement( plate, fragment, allFragments ):

    for folder, names in allFragments.items():
        for name in names:
            if name.startswith( "P{}-".format(plate)) or name.startswith( "{}-".format(plate)):
                if "-R-" in name and 'LR445' in name and "-Fg{}-".format(getFragmentStr(fragment)) in name:
                    fragmentFullName = os.path.join(folder, name)
                    return fragmentFullName

    return None





def downloadUnknown():
    sftp = getSFTP()
    toFolder = r"/home/olya/Documents/fragmentsData/unknown"
    locations = pd.read_csv("unknownFragsLocs.csv")['location'].tolist()
    for fName in locations:
        with sftp.open(fName) as f:
            print("download {}".format(fName))
            img = cv2.imdecode(np.fromstring(f.read(), np.uint8), 1)
            cv2.imwrite(os.path.join(toFolder, fName.split("/")[-1]), img)


def createImageMap():
    import pandas
    fragments = pandas.read_csv(r'/home/olya/Documents/fragmentsData/unplaced_fragments.csv')
    fragmentToLoc = []
    allFragments = getallImagesNames()
    #listFragments = []

    for plate, fragment in zip( fragments['Plate'].tolist(), fragments['Fragment'].tolist() ):
        fullName = getFragmentPlacement( plate, int(fragment), allFragments )
        if fullName:
            fragmentToLoc.append ((plate, fragment, fullName))




    df = pandas.DataFrame()
    df["plate"] = [ x[0] for x in fragmentToLoc]
    df["fragment"] = [x[1] for x in fragmentToLoc]
    df["location"] = [x[2] for x in fragmentToLoc]
    df.to_csv("unknownFragsLocs.csv")








if __name__ == '__main__':
    from removeEmpty import removeEmpty
    #removeEmpty(r'/home/olya/Documents/fragmentsData/DSS_Joins1_bw')
    #createImageMap()
    downloadUnknown()
    #getTrascripts()
    #filterBlacks()
    #getBWImages()
    # ds = DSSRealDataset(r"/home/olya/Documents/fragmentsData/newImages/", transform=None, target_transform=None)
    # for i in range(len(ds)):
    #     v = ds[i]





