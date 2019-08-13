#Gif to curses animation


import curses
from PIL import Image
import time
from curses import wrapper
import sys
import os
import os.path
import shutil
import threading

#Declaring global variable (can be set to any arbitrary value as it will be changed by the script later on)
sizeWindow = 70,70

#split the gif into corresponding frames and saving them to temporary folder
def splitGif(location):
	gifImage = Image.open(location)
	os.mkdir("/tmp/gifTmp")
	for frame in range(0,gifImage.n_frames):
			gifImage.seek(frame)
			gifImage.save("/tmp/gifTmp/gif_"+str(frame)+".png")

#Thread target for writing frames to the curses window
def writeScreen(stdscr,stringContainer,i,j,reps):

	curses.start_color()
	
	curses.init_pair(1,curses.COLOR_BLACK,curses.COLOR_BLACK)
	curses.init_pair(2,curses.COLOR_WHITE,curses.COLOR_BLACK)

	blackBox = str(u'\u2588'+u'\u2588')
	w,h = sizeWindow
	y = int(i/w)-1
	x = ((i+2)%w)

	for k in range(i,j):
		if(k%w == 0):
			y+=1
			x = 0
		if(stringContainer[k]=="b"):
			stdscr.addstr(y,x,blackBox,curses.color_pair(1))
		else:
			stdscr.addstr(y,x,blackBox,curses.color_pair(2))
		
		x += 2

	
#Coverts the frames to thumbnails of size corresponding to the current getmaxyx values and saving the frames to strings
def prepImage(location):
	
	locationArray = []
	stringReturn = [] #This contains the final frame strings
	ofile = open("test.txt","w")

	for r,d,f in os.walk(location):
		for file in f:
			if '.png' in file:
				filename = location+"/"+file
			
				charlist = []
				im = Image.open(filename)
				im.thumbnail(sizeWindow,Image.ANTIALIAS)
				im = im.convert("RGB")
				w,h = im.size

				ofile.writelines(str(w)+" "+str(h))

				for l in range(h):
					for k in range(w):
						r,g,b = im.getpixel((l,k))
						if(r>123):
							charlist.append("w")
						if(r<123):
							charlist.append("b")

				
				charlist = charlist[:-1]
				stringReturn.append("".join(charlist))
	
	ofile.close()
	return stringReturn

#The frame reading and writing occurs from here.
def screenWrite(stdscr,stringContainer,reps):
	

	curses.nocbreak()
	curses.noecho()
	stdscr.clear()
	curses.curs_set(0)
	

	for k in range(reps):
		for i in range(len(stringContainer)):
			stdscr.clear()
			length = stringContainer[i]
			threadArray = []

			w,h = sizeWindow

			div = int(h/10)

			for j in range(div):
				if(j==0):
					startPoint = 0
					endPoint = int((w*h)/div)
				else:
					startPoint = int(((w*h)/div)*j)
					endPoint = startPoint+int((w*h)/div)
				
				if(j==(div-1)):
					endPoint = len(stringContainer[i]) - 1
				
				#Frames are being split into (height/10) chunks and sent to be written by threads on the curses screen
				x = threading.Thread(target=writeScreen,args=(stdscr,stringContainer[i],startPoint,endPoint,j))
				x.start()
				threadArray.append(x)
			
			for z in range(len(threadArray)):
				threadArray[z].join()
				
			stdscr.refresh()
			time.sleep(0.07)


#main function
if __name__ == "__main__":
	stdscr = curses.initscr()
	nameFile = sys.argv[1]
	reps = int(sys.argv[2])
	y,x = stdscr.getmaxyx()
	if(y>x):
		sizeWindow = (x,x)
	else:
		sizeWindow = (y,y)
	
	splitGif(nameFile)
	stringContainer = prepImage("/tmp/gifTmp")
	wrapper(screenWrite,stringContainer,reps)
	shutil.rmtree("/tmp/gifTmp")