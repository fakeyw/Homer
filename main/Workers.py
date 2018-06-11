import time
import threading

class Worker_thread(threading.Thread):
	def __init__(self,get_task,interval,*args,**kw):
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

class Worker_handler(object):
	def __init__(self,get_task,max_worker=30,interval=0.002):
		self.get_task = get_task
		self.max_worker = max_worker
		self.interval = interval
		self.worker_pool = self.set_worker(max_worker,interval)
		
	def run(self):
		for w in self.worker_pool:
			w.start()
		
	def set_worker(self,max_worker,interval):
		print(' Set workers: %s' % max_worker)
		workers = [Worker_thread(self.get_task,interval) for i in range(max_worker)]
		return workers
				