#!/usr/bin/python3

from collections import OrderedDict
from time import time
import argparse, mimetypes, os, re, subprocess, sys

ImageProcessor = "convert -verbose -resize %s '%s' '%s'"
VideoProcessor = "avconv -loglevel quiet -y -i '%s' -b:v 698k -b:a 94k -ar 48000 -s 640x512 '%s'"


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


def singleQuoteHandler(PATH, handleChildFiles=True, handleParents=True):	
	"""
	Goes through a directory - changes all the single quotes in the pathname PATH to
	underscore characters. If handleChildFiles is set to False, will not change the
	child dirs/files name.
	"""
	renamed = OrderedDict()
	fatalNameRegex = re.compile(r"'")

	if handleParents:
		while fatalNameRegex.search(PATH):
			# Keep on renaming folder until none of the parent directories of the given
			# folder have a single quote in their name
			singleQuoteIndex = PATH.find("'")
			succeedingSepIndex = PATH.find(os.sep, singleQuoteIndex)
			if succeedingSepIndex == -1:
				succeedingSepIndex = None
			fatalPortion = PATH[:succeedingSepIndex]
			os.chdir(os.path.dirname(fatalPortion))
			properPortion = fatalNameRegex.sub('_', os.path.basename(fatalPortion))
			properPath = os.path.dirname(fatalPortion) + os.sep + properPortion
			os.rename(fatalPortion, properPath)
			renamed[fatalPortion] = properPath
			PATH = properPath + PATH[len(fatalPortion):]

	if handleChildFiles:
		redoWalk = True
		while redoWalk:
			for dirPath, dirNames, files in os.walk(PATH):
				redoWalk = False
				os.chdir(dirPath)
				if fatalNameRegex.search(dirPath):
					properName = fatalNameRegex.sub('_', os.path.basename(dirPath))
					dirPath = os.path.abspath(dirPath)
					properPath = os.sep .join([os.path.dirname(dirPath), properName])
					os.rename(dirPath, properPath)
					renamed[dirPath] = properPath
					redoWalk = True
				for _dir in dirNames:
					if fatalNameRegex.search(_dir):
						properName = fatalNameRegex.sub('_', _dir)
						_dirPath = os.path.abspath(_dir)
						properPath = os.sep .join([os.path.dirname(_dirPath), properName])
						os.rename(_dirPath, properPath)
						renamed[_dirPath] = properPath
						redoWalk = True
				for _file in files:
					if fatalNameRegex.search(_file):
						filePath = os.path.abspath(_file)
						properName = fatalNameRegex.sub('_', _file)
						properPath = os.sep .join([os.path.dirname(filePath), properName])
						os.rename(filePath, properPath)
						renamed[filePath] = properPath
						redoWalk = True
				if redoWalk:
					break

	return renamed, PATH


def singleQuoteReverser(renamed_dict):
	"""Reverses The Changes Made By the singleQuoteHandler function.
	   In the SOURCE!!! (only)
	"""
	# The reason why OrderedDict was employed was so that this traversal could be
	# made from the child directories to parent directories so that none of the
	# paths might be 'broken'. An ordered bottom-Up, instead of a disordered top-down.
	for old_name in reversed(renamed_dict):
		os.rename(renamed_dict[old_name], old_name)


def figureAlteredDestination(DEST, renamed_dict): 
	"""Given the destination and renamed_dict, returns the altered Destination,
	if any. Useful when the source and destination are in the same directory-tree.
	"""
	newDest = DEST # just assuming, and is useful later on
	test_chunk = DEST
	if DEST in renamed_dict:
		newDest = renamed_dict[DEST]
	else:
		while test_chunk != '/':
			test_chunk = os.path.dirname(test_chunk)
			if test_chunk in renamed_dict:
				newDest = renamed_dict[test_chunk] + newDest[len(test_chunk):]

	return newDest


def cloneNameSourcerer(SOURCE, DEST):
	"""Turns the clone names back to the way they were named back in the source. The
	   name's a bad pun and this function is supposed to be the last one of the 'rever-
	   se' functions to be executed.
	   Since by the time of execution of this function, the source and the 1st dest will
	   have been restored to original already, give it the original source and dest.
	"""
	originalNameList = []

	for _dir, _dirs, _files in os.walk(SOURCE):
		os.chdir(_dir)
		originalNameList.append(os.path.abspath(_dir))
		for eachDir in _dirs:
			originalNameList.append(os.path.abspath(eachDir))
		for _file in _files:
			originalNameList.append(os.path.abspath(_file))

	for originalName in reversed(originalNameList): # Has to be reversed. Bottom to top.
		originalExportPath = figureExportPath(originalName, SOURCE, DEST)
		processedExportPath = re.sub(r'\'', '_', originalExportPath)
		exportPathOriginalChunk = originalExportPath[:len(DEST)]
		exportPathOtherChunk = processedExportPath[len(exportPathOriginalChunk):]
		currentExportPath = exportPathOriginalChunk + exportPathOtherChunk
		if os.path.exists(currentExportPath):
			os.rename(currentExportPath,
				os.path.dirname(currentExportPath)
				+ os.sep
				+ re.sub(r'_', r"'", os.path.basename(currentExportPath)))


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
	UNABRIDGED_DEST = DEST
	UNABRIDGED_SOURCE = SOURCE
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

	# starts the work; renames paths with single quotes (') to have (_) instead of (')
	renamed_dict_src, SOURCE = singleQuoteHandler(SOURCE)
	destHasBeenAltered = not os.path.exists(DEST)
	if destHasBeenAltered:
		OLD_DEST = DEST
		DEST = figureAlteredDestination(OLD_DEST, renamed_dict_src)
	renamed_dict_dest, DEST = singleQuoteHandler(DEST, handleChildFiles=False)

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
	currentExportPath = figureExportPath(SOURCE, SOURCE, DEST)
	PROCESSED_SIZE = subprocess.getoutput("du -h '%s' | tail -n 1 | cut -f 1"
		% currentExportPath)

	# This part reverses the changes made by the single-quote-handler function(s)
	singleQuoteReverser(renamed_dict_dest)
	singleQuoteReverser(renamed_dict_src)
	cloneNameSourcerer(UNABRIDGED_SOURCE, UNABRIDGED_DEST)
	
	# Final output. Logs.
	print("\nAll Done!")
	print("Original:   %s\t%s" % (ORIGINAL_SIZE, UNABRIDGED_SOURCE)) 
	print("Processed:  %s\t%s" % (PROCESSED_SIZE, cloneExportPath)) 
	print("\nTime Taken: %f minutes" % (((time() - initTime)) / 60))


if __name__ == '__main__':
	main()
