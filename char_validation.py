import subprocess
import os
import shlex
import sys
sys.path.append('/home/olya/krakenDir')

def isValid(imagePath):
    krakenPath = r'/home/olya/krakenDir'

    outPath = imagePath[:-3]+"xml"
    commandLine = '-a -i {} {} segment -i {}/models/Qumran_bl_61.mlmodel ocr -m {}/models/Qumran_tr1_13.mlmodel'.format(imagePath, outPath, krakenPath, krakenPath)
    print("running kraken on image: {}".format(imagePath))
    command_line = "{}/venv/bin/python3.6 {}/kraken/krakenCli.py {}".format(krakenPath, krakenPath, commandLine)
    args = shlex.split(command_line)
    try:
        subprocess.run(args, cwd= '/home/olya/krakenDir')
    except:
        print("Error in image: {}".format(imagePath))

    print("done")
    #run glyth text alighment
    glythdir = r'/home/olya/text-alignment'
    os.chdir(glythdir)
    sys.path.append(glythdir)

    commandLine = "{}/venv/bin/python3.7 {}/glyph/alignment/main.py".format(glythdir, glythdir)
    commandLine = "{} {} {}/models/Qumran_tr1_13.mlmodel {}".format(commandLine, outPath, krakenPath, imagePath)
    print("running: {}".format(commandLine))
    args = shlex.split(commandLine)
    try:
        subprocess.run(args)#, cwd=glythdir)
    except:
        print("Error in image: {}".format(imagePath))



def main():

    imagePath = '/home/olya/Documents/fragmentsData/LettersAlef/1Q8/P677-Fg007-R-C01-R01-D17072013-T154913-LR924_012_glyph3.jpg'
    isValid(imagePath)

if __name__ == '__main__':
    main()