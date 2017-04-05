#!/usr/bin/python3

from time import time
import argparse, os, re, subprocess, sys

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
	isImg = 'image' in subprocess.getoutput("file --mime-type %s" %
				handleSingleQuotes(subject, shell=True))
	return isImg

def isVideo(givenFile):
	"""Checks Whether a File is a Video or not -> Boolean"""
	subject = os.path.abspath(givenFile)
	isVid = 'video' in subprocess.getoutput("file --mime-type '%s'" %
				handleSingleQuotes(subject, shell=True))
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

	clonedPath = figureExportPath(SOURCE, SOURCE, DEST)
	if os.path.exists(clonedPath) and not args.DESTINATION == '__in-place__':
		print("""
			   It seems that there already is a file named '%s' in the specified
			   destination. Maybe it's the output of previous execution of this
			   script. If you want to have a clone generated in the same destination
			   please either rename or delete the file, and re-run this script.
			  
			  """ % os.path.basename(SOURCE))
		sys.exit(1)

	for dirpath, dirnames, files in os.walk(SOURCE):
		os.chdir(dirpath)
		print()
		print('*' * 10 + "Current Directory: %s" % dirpath + '*' * 10)
		print()
		if not (bool(dirnames) and bool(files)):
			# Clone even the empty directories
			dirpath = os.path.abspath(dirpath)
			dir_exportPath = figureExportPath(dirpath, SOURCE, DEST)
			os.makedirs(dir_exportPath, exist_ok=True)
		for _file in files:
			raw_filePath = os.path.abspath(_file)	
			filePath = handleSingleQuotes(raw_filePath)
			print('filepath: ' + filePath)
			exportPath = figureExportPath(raw_filePath, SOURCE, DEST)
			createReqExportPath(exportPath)
			if bool(ResizeScale) and isImage(_file):
				print(subprocess.getoutput(ImageProcessor
					 % (ResizeScale, filePath, handleSingleQuotes(exportPath))))
			elif bool(args.Video) and isVideo(_file):
				print("\nWorking on the video '%s'" % _file)
				print("This will take quite a bit of time... please be patient")
				start_time = time()
				subprocess.getoutput(VideoProcessor % (filePath,
						handleSingleQuotes(exportPath)))
				print("Processed '%s' in %f seconds"
					 % (_file, (time()-start_time)), end='\n\n')
			else:
				print(subprocess.getoutput("echo -v " +
						handleSingleQuotes(filePath, shell=True) + " " +
						handleSingleQuotes(exportPath, shell=True)))

	print("\nAll Done!")
	print("Original:  ", subprocess.getoutput("du -h '%s' | tail -n 1" %
								handleSingleQuotes(SOURCE, shell=True)))
	print("Processed: ", subprocess.getoutput("du -h '%s' | tail -n 1" % 
								handleSingleQuotes(clonedPath, shell=True)))
	print("Time Taken: %f seconds" % (time() - initTime))

def handleSingleQuotes(path, shell=False):
	"""Returns a backslashed-escaped-single-quote version of path, to feed into
	   subprocess.getoutput(). If calling a command through shell or if said command
	   is a shell-builtin, set shell=True
	"""
	singleQuoteRegex = re.compile(r'(?<![\\$])(\')') # actually, has UNQUOTED single quotes
	hasSingleQuotes = singleQuoteRegex.search(path)
	if hasSingleQuotes:
		fixedPath = singleQuoteRegex.sub(r'\\\g<1>', path)
		fixedPath = "'" + fixedPath + "'"
		if shell:
			fixedPath = re.sub(r'(^.*$)', r"$\g<1>", fixedPath) 
	else:
		fixedPath = path

#	fixedPath = str.encode(fixedPath).decode('unicode_escape')

	return fixedPath


if __name__ == "__main__":
	main()
