import sys
import numpy as np
import cv2
import os

def processframe(image):
    
    #if no file is found raise error
    if isinstance(image, type(None)): 
        raise NameError("File not found") 
   
   # resize image to 16 x 16 pixels if necessary
    if image.shape != (16, 16, 3): 
        image = cv2.resize(image, (16,16), interpolation = cv2.INTER_AREA)
    
    image = cv2.flip(image, 1)
    
    # segment image into quaters 
    for i in range(0,1): 
        for ii in range(0,1):
            q1 = image[i:i+8,ii:ii+8,:].transpose(2,0,1).reshape(3,-1)
            q2 = image[i:i+8,ii+8:ii+16,:].transpose(2,0,1).reshape(3,-1)
            q3 = image[i+8:i+16,ii:ii+8,:].transpose(2,0,1).reshape(3,-1)
            q4 = image[i+8:i+16,ii+8:ii+16,:].transpose(2,0,1).reshape(3,-1)
   
   #concatenate quaters into an array
    image = np.concatenate((q1,q2,q3,q4), axis=1)
    image = image*brightnessscalingfactor
    image = image.astype(int)
    return(image)    

#main program

#take cli argument of filename
try: 
    filename = sys.argv[1].lower() 
    filetypeindex = str(filename).index('.') #find position of file extension
except: 
    raise NameError("Please specify filename and type as argument e.g. image.png") #if no extension is found raise error

#take cli argument of output file
try:
    outputfile = sys.argv[2].lower() #take cli argument of output file
    outputfiletypeindex = str(filename).index('.')
except:
    raise NameError("Please specify output file as second argument e.g. animation.ino") #if no extension is found raise error

filetype = filename[(filetypeindex + 1):] #remove file name to leave file type

brightnessscalingfactor = 0.2
framelimit = 50
supportedimagefiletypes = ['png', 'jpg', 'bmp', 'jpeg', 'tif', 'tiff'] #list of supported image file extensions
supportedvideofiletypes = ['gif', 'mp4'] #list of supported video file extensions

# If an image is input
if filetype in supportedimagefiletypes:
    image = cv2.imread(filename)
    outputfolder = 'images/' + (outputfile[:(str(outputfile).index('.'))])
    outputfilepath = outputfolder + '/' + outputfile        
    if not os.path.exists(outputfolder): #create necessary directory for arduino IDE
        os.makedirs(outputfolder)     
    with open(outputfilepath,'w+') as code: #open output file
        code.write('#include <Adafruit_DotStar.h>\n#define DATAPIN    2\n#define CLOCKPIN   3\nAdafruit_DotStar strip(256, DATAPIN, CLOCKPIN, DOTSTAR_RGB);\nvoid setup(){\nstrip.begin();\nfor (int i = 0; i <256; i++){\nstrip.setPixelColor(i,0,0,0);\n}\nstrip.show();\n') #arduino setup code for dotstar LEDs
        image = processframe(image)
        script =''
        #read the RGB values and save generate a string of arduino code containing them
        for i in range(0,256):
                colour = str(int(image[0,i]*brightnessscalingfactor)) + ',' + str(int(image[1,i]*brightnessscalingfactor)) + ',' + str(int(image[2,i]*brightnessscalingfactor))
                script = script + f'strip.setPixelColor({i},{colour});\n'        
        code.write(script)
        code.write('strip.show();\n}\nvoid loop() {}')
    frames = 1 # frames flag indicates image

#If a video is input
elif filetype in supportedvideofiletypes:
    try:
        delayval = int(sys.argv[3]) # take cli argument of delay in milliseconds between frames
    except:
        raise NameError("Please specify delay in ms between animation frames as their dargument e.g. 100") #if no extension is found raise error
    
    outputfolder = 'animations/' + (outputfile[:(str(outputfile).index('.'))]) #create folder from filename
    outputfilepath = outputfolder + '/' + outputfile  
    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder)      
    vid = cv2.VideoCapture(filename) #read video with opencv
    frames = [] # begin to count frames
    with open(outputfilepath,'w+') as code:
        code.write('#include <Adafruit_DotStar.h>\n#define DATAPIN    2\n#define CLOCKPIN   3\nAdafruit_DotStar strip(256, DATAPIN, CLOCKPIN, DOTSTAR_RGB);\nvoid setup(){\nstrip.begin();\nstrip.show();\nfor (int i = 0; i <256; i++){\nstrip.setPixelColor(i,0,0,0);\n}\nstrip.show();}\nvoid loop(){\n')       #arduino setup code  
        frames = 0
        script = ''
        oldframe = np.zeros([3, 256])
        while vid.isOpened(): 
            read, Frame = vid.read()
            if not read or frames > framelimit:
                break
            frame = processframe(Frame)
            framecopy = np.copy(frame)
            for i in range(256):
                    if frame[0,i] != oldframe[0,i] and frame[1,i] != oldframe[1,i] and frame[2,i] != oldframe[2,i]:
                        colour = str(int(frame[0,i])) + ',' + str(int(frame[1,i])) + ',' + str(int(frame[2,i]))
                        script = script + f'strip.setPixelColor({i},{colour});\n'
                        code.write(script)
                        script = ''
            code.write(f'strip.show();\ndelay({delayval});\n') # delay line between frames
            frames+=1
            oldframe = framecopy
        code.write('\nfor (int i = 0; i <256; i++){\nstrip.setPixelColor(i,0,0,0);\n}\nstrip.show();}')

else:
    raise OSError("Unsupported file type") #if no extension is found raise error

#output messages
print("Code generated successfully")
if frames != 1: # only show frames and duration if a video is input
    print(f"Number of frames = {frames}")
    print("estimated animation time = " + str(frames * delayval / 1000) + "s")

    
    
    
    
    



