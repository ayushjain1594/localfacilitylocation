from gurobipy import *

class FacilityLocationModel:
	def __init__(self, data):
		"""
		args:
			data: dictionary
		
		Data must have following data 
		under corresponding key
		
		'periodid': List of all period ids
			for single or mult-period model

		'siteid': List of all unique ids
			representing sites

		'customerid': List of all unique ids
			representing customers

		'sitecapbyperiod': Dictionary of dictionary
			with site capacity as format -
				{
					periodid: {
						siteid: int/float,
					},
				}

		'siteslackcapbyperiod': Dictionary of 
			dictionary with site slack capacity
			as format - 
				{
					periodid: {
						siteid: int/float,
					},
				}

		'customerdembyperiod': Dictionary of 
			dictionary with customer demand 
			as format - 
				{
					periodid: {
						customerid: int/float,
					},
				}
				
		'servicedist': Dictionary containing
			distance (or another related measure)
			for all combinations of 
			siteid and customerid as tuple
			keys - 
				{
					(siteid, custid): int/float,
				}

		'maxopensites': int representing maximum
			number of sites that can be open 
			throughout horizon. This is not exactly 
			same as saying max number of sites 
			open at any given period.
		
		Uses Gurobi Python API for creating model and
		solving. Requires gurobi license. Read more @
		https://www.gurobi.com/
		"""
		try:
			self.periodid = data['periodid']
			self.siteid = data['siteid']
			self.customerid = data['customerid']
			self.sitecapbyperiod = data['sitecapbyperiod']
			self.siteslackcapbyperiod = data['siteslackcapbyperiod']
			self.customerdembyperiod = data['customerdembyperiod']
			self.servicedist = data['servicedist']
			self.maxopensites = data['maxopensites']
		except KeyError as e:
			raise KeyError(f"Missing required data {e}")


	def modelProblem(self, exportmps=False):
		"""
		Method models basic facility location
		with slack capacity for sites.

		Uses Gurobi's python API through gurobipy
		for creating model.

		args:
			exportmps: boolean
				If true, formulation is exported
				as model.mps file.
		"""
		try:
			self.model = Model("Facility Location")

			# variables
			flow = self.model.addVars(
				self.periodid,
				self.siteid,
				self.customerid,
				vtype=GRB.CONTINUOUS,
				lb=0,
				name='flow')

			flowindicator = self.model.addVars(
				self.periodid,
				self.siteid,
				self.customerid,
				vtype=GRB.BINARY,
				name='flowindicator')

			serviceindicator = self.model.addVars(
				self.periodid,
				self.siteid,
				vtype=GRB.BINARY,
				name='serviceindicator')

			siteindicator = self.model.addVars(
				self.siteid,
				vtype=GRB.BINARY,
				name='siteindicator')

			slackcap = self.model.addVars(
				self.periodid,
				self.siteid,
				vtype=GRB.CONTINUOUS,
				lb=0,
				name='slackcap')

			# objective
			self.model.setObjective(
				sum(self.servicedist[i,j]*flowindicator[p,i,j]
					for p in self.periodid
					for i in self.siteid
					for j in self.customerid)
				+ sum(0.1*self.servicedist[i,j]*flow[p,i,j]
					for p in self.periodid
					for i in self.siteid
					for j in self.customerid)
				+ 0.25*sum(slackcap[p,i]
					for p in self.periodid
					for i in self.siteid)
				,
				sense=GRB.MINIMIZE
			)

			# constraints
			self.model.addConstrs(
				sum(flow[p,i,j] for i in self.siteid)
				== self.customerdembyperiod[p][j]
				for p in self.periodid
				for j in self.customerid
			)

			self.model.addConstrs(
				(flowindicator[p,i,j] == 0) >>
				(flow[p,i,j] == 0)
				for p in self.periodid
				for i in self.siteid
				for j in self.customerid
			)

			self.model.addConstrs(
				(serviceindicator[p,i] == 0) >> 
				(flow[p,i,j] == 0)
				for p in self.periodid
				for i in self.siteid
				for j in self.customerid
			)

			self.model.addConstrs(
				(siteindicator[i] == 0) >>
				(serviceindicator[p,i] == 0)
				for p in self.periodid
				for i in self.siteid
			)

			# Max additional 1 site, existing 3
			self.model.addConstr(
				sum(siteindicator[i] for i in self.siteid) 
				<= self.maxopensites
			)

			self.model.addConstrs(
				sum(flow[p,i,j] for j in self.customerid)
				<= self.sitecapbyperiod[p][i] \
				+ slackcap[p,i]
				for p in self.periodid
				for i in self.siteid
			)

			#max slack
			self.model.addConstrs(
				slackcap[p,i] \
				<= self.siteslackcapbyperiod[p][i]
				for p in self.periodid
				for i in self.siteid
			)

		except GurobiError as e:
			print(f"Gurobi Error occured {e}")

		if exportmps:
			self.model.write('model.mps')


	def setParamters(self):
		"""
		Method to set parameters - 
			MIP Gap 1%
			Logfile name gurobilog.txt
		"""
		self.model.setParam(GRB.Param.MIPGap, 0.01)
		self.model.setParam(GRB.Param.LogFile, "gurobilog.txt")


	def solveModel(self):
		"""
		Method to call to solve
		"""
		self.model.optimize()


	def extractSolution(self):
		"""
		Method to extract primary decision that are
		flows from a solved model.
		"""

		if self.model.status == GRB.Status.SUBOPTIMAL or \
		self.model.status == GRB.Status.OPTIMAL:

			flow = {}

			for pid in self.periodid:
				for sid in self.siteid:
					for cid in self.customerid:

						flow[(pid, sid, cid)] = self.model.getVarByName(
							f"x[{pid}, {sid}, {cid}]"
						).X
			return flow
		else:
			print("Model might not have solution available")
			return {}