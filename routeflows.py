from multiprocessing import Pool
from math import radians, cos, sin, acos, asin
import time

from tsp import TSP
from mst import Graph

def calculateDistance(lat1, lon1, lat2, lon2):
	lat1_ = radians(lat1)
	lon1_ = radians(lon1)
	lat2_ = radians(lat2)
	lon2_ = radians(lon2)
	try:
		dist = round(3958.75 * (
			acos(sin(lat1_)*sin(lat2_) \
				+ cos(lat1_)*cos(lat2_)*cos(lon1_-lon2_))), 
			2)

		return dist
	except ValueError:
		print("Error occured calculating distance")
		print(lat1, lon1, lat2, lon2)
		print(lat1_, lon1_, lat2_, lon2_)
		raise ValueError


class RouteFlows:

	def __init__(self, srclat, srclon, cuslat, cuslon, 
	sites, customers, maxarcweights, maxnodeweights):
		self.distmat = {}
		self.maxarcweights = maxarcweights
		self.maxnodeweights = maxnodeweights
		self.lat = {**srclat, **cuslat}
		self.lon = {**srclon, **cuslon}
		#self.setupDistanceMatrix(sites+customers)


	def setupDistanceMatrix(self, alllocations):
		for ind, loc1 in enumerate(alllocations):
			for loc2 in alllocations[ind+1:]:
				dist = calculateDistance(
					self.lat[loc1], self.lon[loc1],
					self.lat[loc2], self.lon[loc2]
				)
				self.distmat[(loc1, loc2)] = dist
				self.distmat[(loc2, loc1)] = dist


	def clusterizeCustomers(self, customerweights):
		"""
		Method to create clusters of customers
		based on customer weights and constraints
		around cluster total arc weights and total 
		node weight
		args:
			customerweights: dictionary
				Key, value pairs of customer id and 
				corresponding weight
		"""
		customers = list(customerweights.keys())
		graph = Graph(customers, customerweights)

		# add graph edges
		for ind, customerid1 in enumerate(customers):
			for customerid2 in customers[ind+1:]:
				graph.addEdge(customerid1, customerid2,
					self.distmat[customerid1, customerid2]
				)
		clusters = graph.getClusters(self.maxarcweights, self.maxnodeweights)

		return (customers, clusters)


	def createFlowRoutes(self, dfflow, periodid, scenarioid):
		cluster_rows = []
		route_rows = []
		route_paths = []

		sites = dfflow.SiteID.unique().tolist()

		"""
		customerweights = [
			dict(dfflow[dfflow.SiteID == siteid][['CustomerID', 'FlowUnits']].values
			) for siteid in sites
		]
		"""

		# assuming 8 core
		p = Pool(8)
		#clusterized = p.map(self.clusterizeCustomers, customerweights)

		for ind, siteid in enumerate(sites):
			print(f"Creating flow routes for site {siteid}")

			#customers, clusters = clusterized[ind]

			customerweights = dict(
				dfflow[dfflow.SiteID == siteid][['CustomerID', 'FlowUnits']].values
			)
			start = time.time()
			self.setupDistanceMatrix([siteid] + list(customerweights.keys()))
			delta = time.time() - start
			print(f"Created distance matrix in {delta}")

			start = time.time()
			customers, clusters = self.clusterizeCustomers(customerweights)
			delta = time.time() - start
			print(f"Received clusters in {delta}")
			seen = {customer: False for customer in customers}

			routearguments = []

			clusterid = 1
			for parent, config in clusters.items():

				edges = config['arcs']
				nodecount = len(edges) + 1
				arcweights = config['treearcweight']
				nodeweights = config['treenodeweight']

				nodesinthistree = []

				cluster_rows.append(
					[scenarioid, periodid, siteid, clusterid,
					parent, nodecount, arcweights, nodeweights]
				)
				seen[parent] = True
				nodesinthistree.append(parent)

				for edge in edges:
					u, v, w = edge
					for node in [u, v]:
						if seen[node] == False:
							cluster_rows.append(
								[scenarioid, periodid, siteid, clusterid,
								node, nodecount, arcweights, nodeweights]
							)
							seen[node] = True
							nodesinthistree.append(node)

				routearguments.append((siteid, nodesinthistree))
				clusterid += 1

			start = time.time()
			routes = p.map(self.createRoute, routearguments)
			'''
			routes = []
			for arg in routearguments:
				start = time.time()
				routes.append(self.createRoute(arg))
				delta = time.time() - start
				print(f"Route available in {delta}")
			'''
			delta = time.time() - start
			print(f"Received Routes in {delta}")

			for routeid in range(1, clusterid):
				route = routes[routeid - 1]

				tourlen = len(route)

				d_cumulated = 0

				for i in range(1, tourlen):
					locid = route[i]
					try:
						d = self.distmat[route[i-1], route[i]]
					except TypeError:
						print(i)
						print(route)
						print(tourlen)
						print(route[i-1])
						print(route[i])
						d = 0
					d_cumulated += d
					loctype = 'Customer' if i < tourlen-1 else 'Site'

					if i == 1:
						legtype = 'First'
					elif i == tourlen - 1:
						legtype = 'Final'
					else:
						legtype = 'Intermediate'

					route_rows.append(
						[scenarioid, periodid, siteid, 
						routeid, i, loctype, locid, d, 
						d_cumulated, legtype]
					)

					prevlocid = route[i-1]
					srcdestcombined = str(prevlocid)+'-'+str(locid)
					pathkey = str(scenarioid)+"-"+str(periodid)+"-"+\
						str(siteid)+"-"+str(routeid)+"-"+legtype+"-"+srcdestcombined

					path = [scenarioid, periodid, siteid, routeid, pathkey]

					route_paths.append(
						path+[self.lat[prevlocid], self.lon[prevlocid], d]
					)
					route_paths.append(
						path+[self.lat[locid], self.lon[locid], d]
					)
			

		return cluster_rows, route_rows, route_paths
	


	def createRoute(self, inputs):
		siteid, customerids = inputs
			
		vertices = [siteid] + customerids
		tsp = TSP(vertices)

		# site to customer edges
		for customerid in customerids:
			tsp.addEdge(siteid, customerid, 
				self.distmat[siteid, customerid]
			)
			tsp.addEdge(customerid, siteid,
				self.distmat[customerid, siteid]
			)

		# customer to customer edges
		for customerid1 in customerids:
			for customerid2 in customerids:
				if customerid1 != customerid2:
					tsp.addEdge(customerid1, customerid2,
						self.distmat[customerid1, customerid2]
					)


		greedytour, greedytourlen = tsp.greedyTour(startnode=siteid)
		threeopttour, threeopttourlen = tsp.threeOPT(greedytour)

		#print(len(customerids))
		#print(threeopttour)

		return threeopttour


def test():
	from model import LocalFacilityLocation
	fcp = LocalFacilityLocation()

	rf = RouteFlows(fcp.siteLat, fcp.siteLon, fcp.customerLat, fcp.customerLon,
		fcp.siteID, fcp.customerID, 700, 700)

	import pandas as pd
	dfflow = pd.read_csv('flow.csv')
	dfflow = dfflow[dfflow.PeriodID == 2020]

	customerweights = dict(
		dfflow[dfflow.SiteID == 'S-1'][['CustomerID', 'FlowUnits']].values
	)
	rf.setupDistanceMatrix(['S-1'] + list(customerweights.keys()))

	customers, clusters = rf.clusterizeCustomers(customerweights)
	for key, val in clusters.items():
		print(key, val)
	#cluster, route, paths = rf.createFlowRoutes(dfflow, 2020, 3)

def test2():
	from model import LocalFacilityLocation
	fcp = LocalFacilityLocation()

	rf = RouteFlows(fcp.siteLat, fcp.siteLon, fcp.customerLat, fcp.customerLon,
		fcp.siteID, fcp.customerID, 7, 700)

	customers = [1746.0, 1263.0, 1387.0, 1120.0, 1728.0, 1648.0, 1972.0, 
	1044.0, 1605.0, 1341.0, 1747.0, 1535.0, 1692.0, 1699.0, 
	1035.0, 1107.0, 1037.0, 1370.0, 1363.0, 1481.0, 1707.0, 
	1719.0, 1989.0, 1281.0, 1080.0, 1813.0, 1143.0, 1657.0, 
	1342.0, 1603.0, 1343.0, 1638.0, 1871.0, 1121.0, 1589.0, 
	1823.0, 1156.0, 1601.0, 1671.0, 3965.0, 1816.0, 1194.0, 
	1770.0, 3850.0]

	rf.setupDistanceMatrix(['S-1']+customers)
	

	for key, val in rf.distmat.items():
		if val == 0:
			print(key, val)
	rf.createRoute(('S-1', customers))

if __name__ == '__main__':
	test2()