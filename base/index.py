class Index(object):
	def __init__(self,rootobj,max_layer=30):
		self.root_dict = Layer(0,value=rootobj)
		self.depth = 1
		self.tree_str = list()
		
	def __str__(self):
		pass
		
	def find(self,route):
		p = self.root_dict
		for i in route:
			p = p[i]
		return p.value
		
	def register(self,route,obj):
		p = self.root_dict
		layer = len(route)
		
		for i in route[:-1]:
			if not i in p:
				p[i] = Layer(route.index(i)+1)	#Now .value = None
			p = p[i]
			
		if route[-1] in p:
			if p[route[-1]].value == None:
				p[route[-1]].value = obj
			else:
				raise Exception("Register failed: Index element repeated.")
		else:
			p[route[-1]]=Layer(layer,obj)
		self.depth = max(self.depth,len(route))
		
	def update(self,route,obj):
		p = self.root_dict
		for i in route:
			if not i in p:
				p[i] = Layer(route.index(i)+1)
			p = p[i]
		p.value = obj
		return True
		
	def delete(self,route): #delete one element
		p = self.root_dict
		for i in route:
			if not i in p:
				raise Exception("Delete failed: route not found <%s>" % i);
			p = p[i]
		p.value =  None
		
	def cut(self,route):	#delete the element with its dict (all subelements)
		p = self.root_dict
		for i in route[:-1]:
			if not i in p:
				raise Exception("Delete failed: route not found <%s>" % i);
			p = p[i]
		if route[-1] not in p:
			raise Exception("Delete failed: route not found <%s>" % route[-1]);
		else:
			p.pop(route[-1])
	
	def flush(self,rootobj):
		self.root_dict = Layer(0,rootobj);
		
	def search(self,name):	#dfs search
		found = list()
		self.search_dfs(name,found,self.root_dict,[])
		return found
		
	def search_dfs(self,target_name,result_list,dict,parents):
		for name,sub_dict in dict.items():
			route_now = parents+[name]
			if name == target_name:
				result_list.append(route_now)
			self.search_dfs(target_name,result_list,sub_dict,route_now)
		return 0
				
	def get(self,route):
		p = self.root_dict
		for i in route:
			p = p[i]
		return p.value		

#R[A[CD[E]]B[F]]
#0	1	2	3	4	#这些层在dict中有记录
#Root
#+---A  			#A不是上层最后一个元素 写其子元素时在A上层要加'|'
#|   +---C
#|   |   +---G
#|   |       +---H 
#|   +---D			#D是上层最后一个元素，故写E时在A层不加| 在Root层要加|
#|       +---E
#+---B
#    +---F

	def tree(self):
		self.tree_str.append("ROOT")
		self.tree_dfs(self.root_dict,"")
		return "\n".join(self.tree_str)
		
	def tree_dfs(self,dict,front_str_above):
		str = front_str_above
		layers = list(dict.items())
		if len(layers) != 0:
			for name,sub_dict in layers[:-1]: #由上一级决定下一级的前缀
				self.tree_str.append(str+"+---"+name)
				self.tree_dfs(sub_dict,str+"|   ")
			self.tree_str.append(str+"+---"+layers[-1][0])
			self.tree_dfs(layers[-1][1],str+"    ")
		return 0

#Structure for every layer of index
class Layer(dict):
	def __init__(self,layer,value=None,*args,**kw):
		self.value = value
		self.layer = layer
		super(Layer,self).__init__(*args,**kw)
	
class Index_operator(object):
	def __init__(self,index):
		self.target_index = index
		self.pointer = index.root_dict
		self.father_pointer = None
		
	def operate(self):
		while True:
			pass
