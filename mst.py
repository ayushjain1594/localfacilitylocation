class Graph:
	"""
	Class to setup graph and create cluster(s)/tree(s)
	of nodes using Kruskal's algorithm with possible 
	limits on total node weight or total tree weight in a 
	cluster/tree
	"""
	def __init__(self, vertices, nodeweights):
		self.V = vertices
		self.graph = []

		self.makeSet(nodeweights)


	def addEdge(self, u, v, w):
		'''
		Method to add graph edges.
		'''
		if self.nodeweightsum.get(u) == None or \
			self.nodeweightsum.get(v) == None:
			# bad argument 
			raise KeyError(
				f"Either {u} or {v} do not belong in vertices." +\
				" Skipping edge.."
			)

		if isinstance(w, int) or isinstance(w, float):
			self.graph.append((u,v,w))
		else:
			raise TypeError(
				f"Arc weight {w} must be either float or int"
			)


	def makeSet(self, nodeweights, default_weight=0):
		'''
		Method to initialize forest of trees with 
		single (self) node.
		'''
		self.metav = {}
		self.arcweightsum = {}
		self.nodeweightsum = {}

		for v in self.V:
			self.metav[v] = {}
			self.metav[v]['p'] = v
			self.metav[v]['rank'] = 0

			self.arcweightsum[v] = 0

			if nodeweights.get(v) == None:
				print(f"Node {v} missing weight, " + \
					f"assigning default {default_weight} weight")
				nodeweights[v] = default_weight

			self.nodeweightsum[v] = nodeweights[v]


	def findSet(self, x):
		'''
		Method of find and return the representative 
		node for cluster/tree containing x
		'''
		if x != self.metav[x]['p']:
			self.metav[x]['p'] = self.findSet(
				self.metav[x]['p'])
		return self.metav[x]['p']


	def findSetArcsWeight(self, x):
		'''
		Method to return sum of arc weights in
		cluster/tree containing x from representative 
		node.
		'''
		return self.arcweightsum[self.findSet(x)]


	def findSetNodesWeight(self, x):
		'''
		Method to return sum of node weights in
		cluster/tree containing x from representative 
		node.
		'''
		return self.nodeweightsum[self.findSet(x)]


	def link(self, x, y, w):
		'''
		Method to update meta data for the two
		clusters/trees being linked through edge (x,y,w)
		depending upon rank
		'''
		if self.metav[x]['rank'] > self.metav[y]['rank']:
			
			self.arcweightsum[self.findSet(x)] = \
				self.findSetArcsWeight(x) \
				+ self.findSetArcsWeight(y) + w

			self.nodeweightsum[self.findSet(x)] = \
				self.findSetNodesWeight(x) \
				+ self.findSetNodesWeight(y)
			
			self.metav[y]['p'] = x
		
		else:
			
			self.arcweightsum[self.findSet(y)] = \
				self.findSetArcsWeight(y) \
				+ self.findSetArcsWeight(x) + w
			
			self.nodeweightsum[self.findSet(y)] = \
				self.findSetNodesWeight(y) \
				+ self.findSetNodesWeight(x)

			self.metav[x]['p'] = y

			if self.metav[x]['rank'] == self.metav[y]['rank']:
				self.metav[y]['rank'] = self.metav[y]['rank'] + 1


	def union(self, x, y, w):
		'''
		Method to union two clusters/trees
		through edge (x,y,w)
		'''
		self.link(self.findSet(x), self.findSet(y), w)


	def mstKruskal(self, maxtreearcswt, maxtreenodeswt):
		'''
		Method to execute modified Kruskal's
		algorithm to create cluster(s)/tree(s)
		'''
		result = []

		# sort edges based on their weight
		self.graph = sorted(self.graph, key=lambda e: e[2])

		for u,v,w in self.graph:
			if self.findSet(u) != self.findSet(v):
				# u and v belong to separate trees

				arcweightcombined = self.findSetArcsWeight(u) \
					+ self.findSetArcsWeight(v) + w
				nodeweightcombined = self.findSetNodesWeight(u) \
					+ self.findSetNodesWeight(v)

				if (arcweightcombined <= maxtreearcswt) and \
				(nodeweightcombined <= maxtreenodeswt):
					# adding this edge does not violate max tree
					# arc weight or max tree node weight

					result.append((u,v,w))
					self.union(u, v, w)

		return result


	def getClusters(self, maxtreearcswt, maxtreenodeswt):
		'''
		Method to call modified kruskal's and 
		retrive cluster(s)/tree(s) in to nice 
		format with additional information
		on cluster/tree
		'''
		clusters = {}
		connected = {v: False for v in self.V}

		resultedges = self.mstKruskal(maxtreearcswt, maxtreenodeswt)
		for u, v, w in resultedges:
			# find representative node
			p = self.findSet(u)

			if clusters.get(p) == None:
				clusters[p] = {'arcs':[]}

			clusters[p]['arcs'].append((u,v,w))

			connected[u] = True
			connected[v] = True

		# for single node trees/clusters, if any
		for node, status in connected.items():
			if status == False:
				# no arcs
				clusters[node] = {'arcs': []}

		representatives = clusters.keys()

		for rep in representatives:
			# get total tree arc weight and tree node weight
			clusters[rep]['treearcweight'] = self.findSetArcsWeight(rep)
			clusters[rep]['treenodeweight'] = self.findSetNodesWeight(rep)

		return clusters



def prettyPrint(nesteddict, indent=0):
	'''
	Function to print nested dictionary
	'''
	for key, value in nesteddict.items():
		print('\t' * indent + str(key))
		if isinstance(value, dict):
			prettyPrint(value, indent+1)
		else:
			print('\t' * (indent+2) + str(value))


def test1():
	v = [1, 2, 3, 4, 5, 6, 7, 8, 9]

	nodewt = {
		1: 5,
		2: 5,
		3: 9,
		4: 1,
		5: 7,
		6: 8,
		7: 9,
		8: 2,
		9: 3}

	g = Graph(v, nodewt)

	g.addEdge(1, 2, 4)
	g.addEdge(1, 3, 9)
	g.addEdge(2, 3, 2)
	g.addEdge(4, 5, 1)
	g.addEdge(5, 6, 2)
	g.addEdge(5, 7, 1)
	g.addEdge(3, 7, 2)
	g.addEdge(8, 9, 2)
	g.addEdge(1, 9, 4)
	g.addEdge(5, 8, 1)
	
	clusters = g.getClusters(25, 30)
	prettyPrint(clusters)


if __name__ == '__main__':
	test1()