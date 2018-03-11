#Fri, 22 May 2009 06:07: GMT
from datetime import datetime

class Std_time(object):
	def http_time(self):
		return datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')