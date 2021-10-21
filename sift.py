
import  cv2
def getKeypoint(im):
    if len(im.shape) == 3:
        small = im[:, :, 0]
    else:
        small = im
    h,w = small.shape
    maxx, maxy = 0, 0
    minx, miny = w, h
    for y in range(h):
        for x in range(w):
            if small[y,x] == 0:
                if y < miny:
                    miny = y
                if y>maxy:
                    maxy = y
                if x < minx:
                    minx = x
                if x > maxx:
                    maxx = x

    px = minx + (maxx - minx)//2
    py = miny + (maxy - miny) // 2
    size = max( (maxx - minx), (maxy - miny) )
    size = size*1.2
    return cv2.KeyPoint(px,py,size)


if __name__ == "__main__":
    import numpy as np
    import cv2 as cv
    binImage = r"C:\Users\olyas\Desktop\alef.jpg"
    im = cv2.imread(binImage)
    im2= im.copy()
    sift = cv2.SIFT_create()

    keypoints =  [getKeypoint(im)]
    points, desc = sift.compute( im, keypoints)
    desc = desc[1]
    cv2.drawKeypoints(im, keypoints, im2, flags = cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    cv.imwrite('sift_keypoints.jpg', im2)