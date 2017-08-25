#!/usr/bin/python3

from time import time
import argparse, mimetypes, os, re, shlex, subprocess, sys

ImageProcessor = "convert -verbose -resize %s %s %s"
VideoProcessor = "ffmpeg -loglevel quiet -y -i %s -b:v 698k -b:a 94k -ar 48000 -s 640x512 -strict -2 %s"

def preliminary_checks():
	"""Checks whether or not dependencies are installed properly. If not, exits"""
	dependencies = ['ffmpeg', 'convert']
	missing_dependencies = {}
	pass


def is_image(_file):
	"""Checks whether a file is an image or not -> boolean"""
	return ('image' in str(mimetypes.guess_type(_file)[0])) and \
		('image' in subprocess.getoutput("file --brief --mime-type %s"
		% os.path.abspath(shlex.quote(_file))))


def image_is_larger_than_resize_scale(img_file):
	"""Checks whether or not an image file is larger than the specified resize scale"""
	return int(subprocess.getoutput('identify -ping -format "%w"' +
					" %s" % shlex.quote(img_file))) > IMAGE_RESIZE_SCALE


def is_video(_file):
	"""Checks whether a file is a video or not -> boolean"""
	return ('video' in str(mimetypes.guess_type(_file)[0])) or \
		('video' in subprocess.getoutput("file --brief --mime-type %s"
		% os.path.abspath(shlex.quote(_file))))


def figure_export_path(_file, SOURCE, DESTINATION):
	"""Figures out the export path for a given file"""
	file_path = os.path.abspath(_file)
	DESTINATION = os.path.abspath(DESTINATION)
	return DESTINATION + os.sep + file_path[re.search(SOURCE, _file).start():]


def create_export_path(req_export_path):
	"""Creates required export paths"""
	if not os.path.isdir(os.path.basename(req_export_path)):
		req_export_path = os.path.dirname(req_export_path)
	os.makedirs(req_export_path, exist_ok=True)


def parse_arguments():
	"""Parses Arguments. Created for a cleaner code."""
	global parser, args
	global SOURCE, DESTINATION
	global IMAGE_RESIZE_SCALE, clone_export_path

	parser = argparse.ArgumentParser(description="clone a directory hierarchy "
 		+ "and compress multimedia files along the way")
	parser.add_argument('SOURCE', help='Input Path')
	parser.add_argument('DESTINATION', help='Output Path' + 
		" set to '__in-place__' to make the modifications in place")
	parser.add_argument('-I', '--Image-Resize-Scale', metavar='n',
			help='Turns on image resizing [default resize scale: 1300]',
			type=int, nargs='?', const=1300)
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

	SOURCE = os.path.abspath(args.SOURCE)
	if not args.DESTINATION == '__in-place__':
		DESTINATION = os.path.abspath(args.DESTINATION)
	else:
		DESTINATION = os.path.dirname(SOURCE)
	IMAGE_RESIZE_SCALE = args.Image_Resize_Scale

	clone_export_path = figureExportPath(SOURCE, SOURCE, DESTINATION)
	if os.path.exists(clone_export_path) and not args.DESTINATION == '__in-place__':
		print("""
			   It seems that there already is a file named '%s' in the specified
			   destination. Maybe it's the output of previous execution of this script.
			   If you want to have a clone generated in the same place, either rename
			   or delete the file, and re-run this script.
			  
			  """ % os.path.basename(SOURCE), file=sys.stderr)
		sys.exit(1)

	if not (bool(IMAGE_RESIZE_SCALE) or bool(args.Video)):
		print("Please specify either -I or -V flag. Exiting.", file=sys.stderr)
		sys.exit(1)


def main():
	init_time = time()
	preliminary_checks()
	parse_arguments()

	ORIGINAL_SIZE = subprocess.getoutput("du -h '%s' | tail -n 1 | cut -f 1" % SOURCE)

	for dirpath, subdirs, files in os.walk(SOURCE):
		os.chdir(dirpath)
		print('\n' + '*' * 10 + "Current Directory: %s" % dirpath + '*' * 10 + '\n')
		if not (bool(subdirs) and bool(files)):
			# Clone even the empty dirs/subdirs
			dirpath = os.path.abspath(dirpath)
			create_export_path(figure_export_path(dirpath, SOURCE, DESTINATION))
		for _file in files:
			file_path = os.path.abspath(_file)
			export_path = figure_export_path(file_path, SOURCE, DESTINATION)
			create_export_path(export_path)
			_file, export_path = shlex.quote(_file), shlex.quote(export_path)
			if bool(IMAGE_RESIZE_SCALE) and is_image(file_path):
					if image_is_larger_than_resize_scale(file_path):
						print(subprocess.getoutput(ImageProcessor
							 % (ResizeScale, _file,
							 	export_path)))
			elif bool(args.Video) and isVideo(file_path):
				print("\nWorking on the video '%s'" % _file)
				print("This will take quite a bit of time... please be patient")
				start_time = time()
				if args.DESTINATION == '__in-place__':
					subprocess.getoutput(VideoProcessor % (_file, 
						shlex.quote('buffer_'+_file)))
					os.rename('buffer_'+_file, _file)
				else:
					subprocess.getoutput(VideoProcessor % (_file, export_path))
				print("Processed '%s' in %f seconds"
					 % (_file, (time()-start_time)), end='\n\n')
			else:
				print(subprocess.getoutput("cp -v '%s' '%s'" % 
					(_file, export_path)))

	PROCESSED_SIZE = subprocess.getoutput("du -h '%s' | tail -n 1 | cut -f 1"
		% clone_export_path)

	print("\nAll Done!")
	print("Original:   %s\t%s" % (ORIGINAL_SIZE, SOURCE))
	print("Processed:  %s\t%s" % (PROCESSED_SIZE, clone_export_path))
	print("\nTime Taken: %f minutes" % (((time() - init_time)) / 60))


if __name__ == '__main__':
	main()
