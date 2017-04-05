def singQuoteHandler(PATH):	
	import os, re
	
	renamed = {
		# Renamed[fatalName] = properName
		}
	
	fatalNameRegex = re.compile(r"'")
	
	PATH = os.path.abspath(PATH)
	
	while fatalNameRegex.search(PATH):
		# Keep on renaming folder until none of the parent directories of the given
		# folder have a single quote in their name
		fatalPortion = PATH[:(PATH.find(os.sep, PATH.find("'")))]
		os.chdir(os.path.dirname(fatalPortion))
		properPortion = fatalNameRegex.sub('_', os.path.basename(fatalPortion))
		properPath = os.path.dirname(fatalPortion) + os.sep + properPortion
		os.rename(fatalPortion, properPath)
		renamed[fatalPortion] = properPath
		PATH = properPath + PATH[len(fatalPortion):]
	
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

	return renamed

def singQuoteReverser(renamed_dict):
	import os
	for old_names in renamed_dict:
		os.rename(renamed_dict[old_names], old_names)
