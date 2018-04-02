import sys
import os
sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)))
from main.Owner import Homer_owner

'''
Outer sys
may giving statistics
'''
class Homer(object):
	def __init__(self):
		print('Welcome to be with Homer!')
		print('Github: https://github.com/fakeyw/Homer')
		self.Owner = Homer_owner()
		self.register = self.Owner.register
		self.put_resp = self.Owner.put_resp
		
	def run(self,host='127.0.0.1',port=8989):
		self.Owner.run(host,port)
		print("\nSite map:\n %s" % self.site_map())
		
	def site_map(self):
		return self.Owner.callback_index.tree()
		
	def info(self):
		pass
	
	
	
	
	