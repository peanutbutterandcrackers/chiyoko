
from collections import OrderedDict
import os, re

def singleQuoteHandler(PATH, handleChildFiles=True):	
	"""
	Goes through a directory - changes all the single quotes in the pathname PATH to
	underscore characters. If handleChildFiles is set to False, will not change the
	child dirs/files name.
	"""
	
	INIT_WORKING_DIR = os.path.abspath(os.getcwd())

	renamed = OrderedDict()
	
	fatalNameRegex = re.compile(r"'")
	
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

	os.chdir(INIT_WORKING_DIR)

	return renamed, PATH

def singleQuoteReverser(renamed_dict):
	old_names_BottomUp = list(renamed_dict.keys()) # Not really, yet.
	old_names_BottomUp.reverse() # Now we're ready...
	for old_name in old_names_BottomUp:
		os.rename(renamed_dict[old_name], old_name)


if __name__ == "__main__":
	main()
