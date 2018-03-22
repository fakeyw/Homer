from base.index import Index,Layer

class Url_index(Index):
	def __init__(self,*args,**kw):
		super(Url_index,self).__init__(*args,**kw)
		#self.stop_layer = 0
		
	def register(self,route,obj):
		p = self.root_dict
		layer = len(route)
		if layer != 0:
			for i in route[:-1]:
				if not i in p:
					if i == '$' and len(p) == 0:
						p[i] = Layer(route.index(i)+1)	#Now .value = None
					elif i != '$' and '$' not in p:
						p[i] = Layer(route.index(i)+1)
					else:
						raise Exception("Register failed: route overlapped.")
				p = p[i]
			
			if route[-1] in p:
				if p[route[-1]].value == None:
					p[route[-1]].value = obj
				else:
					raise Exception("Register failed: Index element repeated.")
			else:
				p[route[-1]]=Layer(layer,obj)
		else:
			if p.value == None:
				p.value = obj
			else:
				raise Exception("Register failed: Index element repeated.")
				
		self.depth = max(self.depth,layer)
		
	def url_find(self,route):
		url_params = []
		p = self.root_dict
		for i in route:
			if i in p:
				p = p[i]
			elif '$' in p:
				url_params.append(i)
				p = p['$']
			else:
				return None,None
		return p.value,url_params
		
#Maybe i should deal with Exceptions?


