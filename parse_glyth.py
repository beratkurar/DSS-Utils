import xml.etree.ElementTree as ET
import os
ALEF =  'א'
SHIN =  'ש'
LAMED =  'ל'
LETTER_TO_GET = {'shin':SHIN} #{"alef": ALEF, 'shin':SHIN, 'lamed':LAMED}
from parse_alto import parse_alto as pa
from PIL import Image, ImageDraw, ImageFont


def parseXML(path, image_filename, letter):
    ret = []
    retBoxes = []
    alto_elements = pa(path)
    image = Image.open(image_filename)
    for i, line in enumerate(alto_elements):
        for j, word in enumerate(line.children):
            for k, char in enumerate(word.children):
                if char.content == letter or letter is None:
                    bbox = char.bbox.expand(-1).serialize()
                    if letter == ALEF:
                        bbox[0]-=25
                        bbox[2]+=25
                        width =bbox[2]-bbox[0]
                        height = bbox[3]-bbox[1]
                        if height > 3 * width:
                            continue
                    elif letter == LAMED:
                        bbox[0] -= 25
                        bbox[2] += 25
                        width = bbox[2] - bbox[0]
                        height = bbox[3] - bbox[1]
                        if height > 5 * width:
                            continue
                    elif letter == SHIN:
                        bbox[0] -= 25
                        bbox[2] += 25
                        width = bbox[2] - bbox[0]
                        height = bbox[3] - bbox[1]
                        if height > 3 * width:
                            continue
                    elif letter is None:#get all letters
                        width = bbox[2] - bbox[0]
                        height = bbox[3] - bbox[1]
                        if height > 5 * width:
                            continue
                    retBoxes.append(bbox)
                    im = image.crop(bbox)
                    ret.append(im)

    return ret, retBoxes




def getDescriptors():
    from sift import getKeypoint
    import cv2
    import numpy as np
    for root, b, im in os.walk(r'/home/olya/Documents/fragmentsData/DSS_Joins_bw'):
        manu = root.split("/")[-1]
        if 'bin' in manu:
            continue
        for i in im:
            if i.endswith("_glyph.xml"):
                fullPath = os.path.join(root, i)
                imName = fullPath.replace("_glyph.xml", '.jpg')
                binImage = os.path.join(root + "_bin", i.replace('_glyph.xml', '.tif'))

                letters, boxes = parseXML(fullPath, imName, None)
                #create keypoints from boxes
                if len(boxes) == 0:
                    continue


                image = Image.open(binImage)
                imagecv  = cv2.imread(binImage)
                imagecv2 = imagecv.copy()
                allKeypoints = []
                for box in boxes:
                    left, upper, right, lower = box

                    im = image.crop(box)
                    keypoint = getKeypoint(np.array(im))
                    x, y = keypoint.pt
                    x+=left
                    y+=upper
                    keypoint = cv2.KeyPoint(x,y,keypoint.size)
                    allKeypoints.append(keypoint)
                cv2.drawKeypoints(imagecv, allKeypoints, imagecv2, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)



                cv2.imwrite('sift_keypoints.jpg', imagecv2)
                img = Image.open('sift_keypoints.jpg')
                img1 = ImageDraw.Draw(img)
                for b in boxes:

                    img1.rectangle(b,  outline="red")
                img.show()



                #get descriptors from keypoints
                sift = cv2.SIFT_create()
                points, desc = sift.compute(imagecv, allKeypoints)
                desc = desc[1]
                print("")


                #1000 means from descriptors to create disctionary








def main():
    '''
    get specific letter from glyph
    :return:
    '''

    for letterName, letterValue in LETTER_TO_GET.items():

        lettersRoot = r'/home/olya/Documents/fragmentsData/Letters{}'.format(letterName)
        if not os.path.exists(lettersRoot):
            os.mkdir(lettersRoot)
        for root, b, im in os.walk(r'/home/olya/Documents/fragmentsData/DSS_Joins_bw'):
            manu = root.split("/")[-1]
            if 'bin' in manu:
                continue
            for i in im:
                if i.endswith("_glyph.xml"):
                    fullPath = os.path.join(root, i)
                    imName = fullPath.split("/")[-1][:-4]
                    letters = parseXML(fullPath, fullPath.replace("_glyph.xml", '.jpg') , letterValue)
                    if letters:
                        if not os.path.exists(os.path.join(lettersRoot, manu)):
                            os.mkdir(os.path.join(lettersRoot, manu))
                    for i, im in enumerate(letters):

                        lettersPath = os.path.join(lettersRoot, manu, imName+str(i)+".jpg")
                        try:
                            im.save(lettersPath)
                        except:
                            print("falied to save")


if __name__ == "__main__":
    #main()
    getDescriptors()
    parseXML('/home/olya/Documents/fragmentsData/LettersAlef/1Q8/P677-Fg006-R-C01-R01-D17072013-T154042-LR924_012_glyph1_glyph.xml',
             '/home/olya/Documents/fragmentsData/LettersAlef/1Q8/P677-Fg006-R-C01-R01-D17072013-T154042-LR924_012_glyph1.jpg', 'alef')