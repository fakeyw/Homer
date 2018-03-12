class QPOOL(object):
	def __init__(self,max=30):
		self.max=max
		self.Qs=dict()
		
	def showQs(self):
		print("%s Q(s) in QPool" % len(self.Qs))
		for k,v in self.Qs.items():
			print("[%s|%s] in>>%s>>out" % (k,v.len(),v.show()))
		
	def getQ(self,name):
		if name in self.Qs:
			return self.Qs[name]
		else:
			raise Exception("No such queue")
	
	def count(self):
		return len(self.Qs)
		
	def createQ(self,name,max_len=300):
		if name in self.Qs or self.count() >= self.max:
			raise Exception("Can not have more queue")
		else:
			self.Qs[name]=Q(name,max_len)
			return self.Qs[name]
		
	def deleteQ(self,name):
		if name in self.Qs:
			self.Qs.pop(name)
			return True
		else:
			raise Exception("No such queue")
		
class Q(object):
	def __init__(self,name,max_len):
		self.max_len=max_len
		self.items=list()
		self.name=name
		
	def put(self,msg):
		if len(self.items) < self.max_len :
			self.items.insert(0,msg)
			return True
		else:
			raise Exception("Full")
		
	def get(self):
		if self.is_empty():
			return None
		else:
			return self.items.pop()
			
	def len(self):
		return len(self.items)
			
	def delete(self,value):
		self.items.pop(self.items.index(value))
		return True
			
	def see(self):
		if self.is_empty():
			raise Exception("The queue is empty")
		else:
			return self.items[self.count-1]
			
	def get_all(self):
		return self.items
		
	def is_empty(self):
		return True if len(self.items)==0 else False
		
	def empty(self):
		self.items=list()
		
	def show(self):
		if self.is_empty():
			return "[Empty]"
		else:
			return self.items
	