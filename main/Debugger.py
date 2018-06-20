import os
import threading
import time
import sys
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

pat = re.compile(r'(.*)[\\|/](.*)\.py')

class FileEventHandler(FileSystemEventHandler):
	def __init__(self,executable):
		FileSystemEventHandler.__init__(self)
		self.executable = executable

	def on_modified(self, event):
		path = os.path.realpath(event.src_path)
		print("Modified: ",path)
		os.execl(self.executable,self.executable,*sys.argv)

#这个类用于空控制进程重启，以后可能用于提供集群多进程运行状态监控？
class Process_handler(object):
	def __init__(self):
		pass
		
		
	def restart(self):
		pass
		
class monitor_thread(threading.Thread):
	def __init__(self): #这里应先对要监控的文件进行建模
		pass
	
	def run(self):
		pass
		
class Debugger(object):
	def __init__(self):
		executable = sys.executable
		self.event_handler = FileEventHandler(executable)
		self.observer = Observer()
		self.path_set = set()
		for _,v in sys.modules.items():
			try:
				path = pat.findall(v.__file__)[0][0]
				self.path_set.add(path)
			except Exception as e:
				pass
		for i in self.path_set:
			#print(i)
			self.observer.schedule(self.event_handler,i,recursive=False)
				
	def run(self):
		print('[*]Debugger is working...')
		self.observer.start()
		
	
				
				
		