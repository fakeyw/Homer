import os

class File_handler(object):
	pass


def file_check(path,including_folder=False):
	res = False
	permission = 0
	if including_folder:
		res = os.path.exists(path)
	else:	
		res = os.path.isfile(path)
	if res != False:
		if os.access(path,os.R_OK):
			permission |= 1<<2
		if os.access(path,os.W_OK):
			permission |= 1<<1
		if os.access(path,os.X_OK):
			permission |= 1<<0
		
	return res,permission