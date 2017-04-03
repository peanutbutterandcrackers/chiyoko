#!/usr/bin/python3

from time import time
import argparse, os, subprocess

ImageProcessor = "convert -verbose -resize %s '%s' '%s'"
VideoProcessor = "avconv -loglevel quiet -y -i '%s' -b:v 698k -b:a 94k -ar 48000 -s 640x512 '%s'"

def figureExportPath(filePath, SOURCE, DEST):
	"""Figures out the export path for a given file"""
	filePath = os.path.abspath(filePath)
	refDir = os.path.basename(SOURCE)
	filePath_List = filePath.split(os.sep)
	reqTail_List = filePath_List[filePath_List.index(refDir):]
	reqTail = '%s' % os.sep .join(reqTail_List)
	reqPath = os.path.join(DEST, reqTail)
	return reqPath

def createReqExportPath(reqPath):
	"""Checks whether or not the required path exists; creates non-existant"""
	reqPath = os.path.abspath(reqPath)
	if not os.path.isdir(os.path.basename(reqPath)):
		reqPath = os.path.split(reqPath)[0]
	if not os.path.exists(reqPath):
		os.makedirs(reqPath)

def isImage(givenFile):
	"""Returns a Boolean value. True or False. Rough definition of an Image"""
	subject = os.path.abspath(givenFile)
	isImg = 'image' in subprocess.getoutput("file --mime-type %s" % subject)
	return isImg

def isVideo(givenFile):
	"""Checks Whether a File is a Video or not -> Boolean"""
	subject = os.path.abspath(givenFile)
	isVid = 'video' in subprocess.getoutput("file --mime-type '%s'" % subject)
	return isVid

def main():

	initTime = time()
	parser = argparse.ArgumentParser(description="clone a directory hierarchy "
 		+ "and compress multimedia files along the way")
	parser.add_argument('SOURCE', help='Input Path')
	parser.add_argument('DESTINATION', help='Output Path' + 
		" set to '__in-place__' to make the modifications in place")
	parser.add_argument('-I', '--Image-resize-scale', metavar='n',
			help='Turns on image resizing [default resize scale: 1000]',
			type=int, nargs='?', const=1000) 
	parser.add_argument('-V', '--Video',
 			help='Turns on video compression',
			action='store_true')
	args = parser.parse_args()

	SOURCE = os.path.abspath(args.SOURCE)
	if not args.DESTINATION == '__in-place__':
		DEST = os.path.abspath(args.DESTINATION)
	else:
		DEST = os.path.dirname(SOURCE)
	ResizeScale = args.Image_resize_scale

	for dirpath, dirnames, files in os.walk(SOURCE):
		os.chdir(dirpath)
		print()
		print('*' * 10 + "Current Directory: %s" % dirpath + '*' * 10)
		print()
		for _file in files:
			filePath = os.path.abspath(_file)	
			exportPath = figureExportPath(filePath, SOURCE, DEST)
			createReqExportPath(exportPath)
			if bool(ResizeScale) and isImage(_file):
				print(subprocess.getoutput(ImageProcessor
					 % (ResizeScale, _file, exportPath)))
			elif bool(args.Video) and isVideo(_file):
				print("\nWorking on the video '%s'" % _file)
				print("This will take quite a bit of time... please be patient")
				start_time = time()
				subprocess.getoutput(VideoProcessor % (_file, exportPath))
				print("Processed '%s' in %f seconds"
					 % (_file, (time()-start_time)), end='\n\n')
			else:
				print(subprocess.getoutput("cp -v '%s' '%s'" % 
					(filePath, exportPath)))

	print("\nAll Done!")
	print("Original:  ", subprocess.getoutput("du -h '%s' | tail -n 1" % SOURCE))
	print("Processed: ", subprocess.getoutput("du -h '%s' | tail -n 1" %
			 os.sep .join([DEST, os.path.basename(SOURCE)])))
	print("Time Taken: %f seconds" % (time() - initTime))

if __name__ == "__main__":
	main()
