import time
import threading

class Worker_thread(threading.Thread):
	def __init__(self,get_task,interval=0.002,*args,**kw):
		super(Worker_thread,self).__init__(*args,**kw)
		self.get_task = get_task
		self.interval = interval
		self.__STOP__ = False
		
	def stop(self):
		self.__STOP__ =True
		
	def run(self):
		while True:
			current_task = self.get_task() 
			if current_task != None:
				current_task.run()
			else:
				time.sleep(self.interval)
			if self.__STOP__ :
				break
				
				
				