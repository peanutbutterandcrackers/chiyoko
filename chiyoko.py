#!/usr/bin/python3

from time import time
import argparse, mimetypes, os, re, shlex, subprocess, sys

ImageProcessor = "convert -verbose -resize %s '%s' '%s'"
VideoProcessor = "ffmpeg -loglevel quiet -y -i '%s' -b:v 698k -b:a 94k -ar 48000 -s 640x512 -strict -2 '%s'"

def preliminary_checks():
	"""Checks whether or not dependencies are installed properly. If not, exits"""
	dependencies = ['ffmpeg', 'convert']
	missing_dependencies = {}
	pass


def isImage(givenFile):
	"""Returns a Boolean value. True or False. Rough definition of an Image"""
	subject = os.path.abspath(givenFile)
	isImg = ( 'image' in str(mimetypes.guess_type(givenFile)[0]) ) and \
		( 'image' in subprocess.getoutput("file --brief --mime-type '%s'" % subject) )
	return isImg


def isVideo(givenFile):
	"""Checks Whether a File is a Video or not -> Boolean"""
	subject = os.path.abspath(givenFile)
	isVid = ( 'video' in str(mimetypes.guess_type(givenFile)[0]) ) and \
		( 'video' in subprocess.getoutput("file --brief --mime-type '%s'" % subject) )
	return isVid


def isMP4(givenFile):
	"""Checks whether a file is an MP4 or not -> Boolean"""
	# This had to be written because $ file foo.MP4 gave 'audio/mp4'
	subject = os.path.abspath(givenFile)
	isMP4 = ( 'video' in str(mimetypes.guess_type(givenFile)[0]) ) and \
		( 'mp4' in subprocess.getoutput("file --brief --mime-type '%s'" % subject) )
	return isMP4


def figureExportPath(filePath, SOURCE, DEST):
	"""Figures out the export path for a given file"""
	filePath = os.path.abspath(filePath)
	SOURCE = os.path.abspath(SOURCE)
	DEST = os.path.abspath(DEST)
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


def parse_arguments():
	"""Parses Arguments. Created for a cleaner code."""
	global parser, args

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

	if not os.path.exists(args.SOURCE):
		print("The specified source '%s' doesn't exist." % args.SOURCE,
				file=sys.stderr)
		sys.exit(1)
	if not args.DESTINATION == '__in-place__' and not os.path.exists(args.DESTINATION):
		print("The specified destination '%s' doesn't exist." %
				args.DESTINATION, file = sys.stderr)
		sys.exit(1)


def main():
	initTime = time()

	# the "autobots, rollout" part of the script. Initializations.
	parse_arguments()
	SOURCE = os.path.abspath(args.SOURCE)
	if not args.DESTINATION == '__in-place__':
		DEST = os.path.abspath(args.DESTINATION)
	else:
		DEST = os.path.dirname(SOURCE)
	ResizeScale = args.Image_resize_scale
	cloneExportPath = figureExportPath(SOURCE, SOURCE, DEST) # Export Path for the 'clone'
	if os.path.exists(cloneExportPath) and not args.DESTINATION == '__in-place__':
		print("""
			   It seems that there already is a file named '%s' in the specified
			   destination. Maybe it's the output of previous execution of this script.
			   If you want to have a clone generated in the same place, either rename
			   or delete the file, and re-run this script.
			  
			  """ % os.path.basename(SOURCE), file=sys.stderr)
		sys.exit(1)

	# The main part of the script
	ORIGINAL_SIZE = subprocess.getoutput("du -h '%s' | tail -n 1 | cut -f 1" % SOURCE)
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
			filePath = os.path.abspath(_file)	
			exportPath = figureExportPath(filePath, SOURCE, DEST)
			createReqExportPath(exportPath)
			if bool(ResizeScale) and isImage(filePath):
				if ( int(subprocess.getoutput('identify -ping -format "%w"' +
					" '%s'" % _file)) > ResizeScale ):
					print(subprocess.getoutput(ImageProcessor
						 % (ResizeScale, _file, exportPath)))
			elif bool(args.Video) and ( isVideo(filePath) or isMP4(filePath) ):
				print("\nWorking on the video '%s'" % _file)
				print("This will take quite a bit of time... please be patient")
				start_time = time()
				if args.DESTINATION == '__in-place__':
					subprocess.getoutput(VideoProcessor % (_file, 'buffer_'+_file))
					os.rename('buffer_'+_file, _file)
				else:
					subprocess.getoutput(VideoProcessor % (_file, exportPath))
				print("Processed '%s' in %f seconds"
					 % (_file, (time()-start_time)), end='\n\n')
			else:
				print(subprocess.getoutput("cp -v '%s' '%s'" % 
					(_file, exportPath)))

	PROCESSED_SIZE = subprocess.getoutput("du -h '%s' | tail -n 1 | cut -f 1"
		% currentExportPath)

	# Final output. Logs.
	print("\nAll Done!")
	print("Original:   %s\t%s" % (ORIGINAL_SIZE, UNABRIDGED_SOURCE)) 
	print("Processed:  %s\t%s" % (PROCESSED_SIZE, cloneExportPath)) 
	print("\nTime Taken: %f minutes" % (((time() - initTime)) / 60))


if __name__ == '__main__':
	main()
