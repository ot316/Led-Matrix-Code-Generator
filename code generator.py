import sys
import numpy as np
import cv2
import os
import argparse


def processframe(image):
    
    if isinstance(image, type(None)): 
        raise NameError("File not found") #if no file is found raise error
   
    if image.shape != (16, 16, 3):
        image = cv2.resize(image, (16,16), interpolation = cv2.INTER_AREA)

    for i in range(0,1):
        for ii in range(0,1):
            q1 = image[i:i+8,ii:ii+8,:].transpose(2,0,1).reshape(3,-1)
            q2 = image[i:i+8,ii+8:ii+16,:].transpose(2,0,1).reshape(3,-1)
            q3 = image[i+8:i+16,ii:ii+8,:].transpose(2,0,1).reshape(3,-1)
            q4 = image[i+8:i+16,ii+8:ii+16,:].transpose(2,0,1).reshape(3,-1)
   
    image = np.concatenate((q1,q2,q3,q4), axis=1)
    code =''
    for i in range(0,256):
            colour = str(image[0,i]) + ',' + str(image[1,i]) + ',' + str(image[2,i])
            code = code + f'strip.setPixelColor({i},{colour});\n'
    return(code)    

#main

try: 
    filename = sys.argv[1].lower() #take cli argument of filename
    filetypeindex = str(filename).index('.') #find position of file extension
except: 
    raise NameError("Please specify filename and type as argument e.g. image.png") #if no extension is found raise error

try:
    outputfile = sys.argv[2].lower() #take cli argument of output file
    outputfiletypeindex = str(filename).index('.')
except:
    raise NameError("Please specify output file as second argument e.g. animation.ino") #if no extension is found raise error

filetype = filename[(filetypeindex + 1):] #remove file name to leave filetype29

supportedimagefiletypes = ['png', 'jpg', 'bmp', 'jpeg', 'tif', 'tiff'] #list of supported image file extensions
supportedvideofiletypes = ['gif', 'mp4'] #list of supported video file extensions

if filetype in supportedimagefiletypes:
    image = cv2.imread(filename)
    outputfolder = 'images/' + (outputfile[:(str(outputfile).index('.'))])
    outputfilepath = outputfolder + '/' + outputfile        
    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)     
    with open(outputfilepath,'w+') as code:
        code.write('#include <Adafruit_DotStar.h>\n#include <SPI.h>\n#define DATAPIN    4\n#define CLOCKPIN   5\nAdafruit_DotStar strip(256, DATAPIN, CLOCKPIN, DOTSTAR_BRG);\nvoid setup(){\nstrip.begin();\n')
        code.write(processframe(image))
        code.write('strip.show();\n}\nvoid loop() {}')
    frames = 1
    
elif filetype in supportedvideofiletypes:
    try:
        delayval = int(sys.argv[3])
    except:
        raise NameError("Please specify delay in ms between animation frames as third argument e.g. 100") #if no extension is found raise error
    
    outputfolder = 'animations/' + (outputfile[:(str(outputfile).index('.'))])
    outputfilepath = outputfolder + '/' + outputfile  
    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)      
    vid = cv2.VideoCapture(filename)
    frames = []
    with open(outputfilepath,'w+') as code:
        code.write('#include <Adafruit_DotStar.h>\n#include <SPI.h>\n#define DATAPIN    4\n#define CLOCKPIN   5\nAdafruit_DotStar strip(256, DATAPIN, CLOCKPIN, DOTSTAR_BRG);\nvoid setup(){\nstrip.begin();\nstrip.show()}\nvoid loop(){\n')        
        frames = 0
        while vid.isOpened(): 
            read, frame = vid.read()
            if not read:
                break
            code.write(processframe(frame))
            code.write(f'strip.show();\ndelay({delayval});\n') 
            frames+=1
        code.write('}')

else:
    raise OSError("Unsupported file type") #if no extension is found raise error

print("Code generated successfully")
if frames != 1:
    print(f"Number of frames = {frames}")
    print("estimated animation time = " + str(frames * delayval / 1000) + "s")

    
    
    
    
    



