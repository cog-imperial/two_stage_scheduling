class Solver:
	
	def __init__(self, method, commercial_tool, stage):
		
		self.method = method
		self.commercial_tool = commercial_tool
		self.stage = stage
		if stage == 'planning' or stage == 'solution_pool_generation':
			self.time_limit = 1000
		if stage == 'recovery':
			self.time_limit = 100
		self.gap_tolerance = 0.0001
		self.has_run = False
	
	def set_results(self, upper_bound, lower_bound, relative_gap, elapsed_time, nodes_explored, nodes_left):
		
		self.has_run = True
		self.upper_bound = upper_bound
		self.lower_bound = lower_bound
		self.relative_gap = relative_gap
		self.elapsed_time = elapsed_time
		self.nodes_explored = nodes_explored
		self.nodes_left = nodes_left
	
	def set_recovery_results(self, upper_bound, elapsed_time):
		
		self.has_run = True
		self.upper_bound = upper_bound
		self.elapsed_time = elapsed_time
	
	def get_value(self, metric):
		
		if self.has_run:
			if metric == 'upper_bound': return self.upper_bound
			if metric == 'lower_bound': return self.lower_bound
			if metric == 'relative_gap': return self.relative_gap
			if metric == 'elapsed_time': return self.elapsed_time
			if metric == 'nodes_explored': return self.nodes_explored
	
	def get_string_value(self, metric):
			if metric == 'upper_bound' and self.upper_bound != None: 
				return str(self.upper_bound)
			elif metric == 'lower_bound' and self.lower_bound != None: 
				return str(int(round(self.lower_bound, 0)))
			elif metric == 'relative_gap' and self.relative_gap != None: 
				return str(round(self.relative_gap*100, 3))
			elif metric == 'elapsed_time' and self.elapsed_time != None: 
				return str(round(self.elapsed_time, 2))
			elif metric == 'nodes_explored' and self.nodes_explored != None: 
				return str(self.nodes_explored)
			elif metric == 'nodes_left' and self.nodes_left != None: 
				return str(self.nodes_left)
			else:
				return '-'
	
	def name(self):
		if self.method in ['weighting']: return self.method + ' ' + self.commercial_tool
		if self.method in ['branch_and_bound', 'sequential', 'highest_rank_objective', 'makespan']: return self.method.replace('_', ' ')
		if self.method in ['binding', 'flexible']: return self.stage + ' ' + self.method + ' ' + self.commercial_tool
	
	#def copy(self):
		#solver_copy = Solver(self.method, self.commercial_tool, self.stage)
		#if self.has_run:
			#solver_copy.set_results(self.upper_bound, self.lower_bound, self.relative_gap, self.elapsed_time, self.nodes_explored, self.nodes_left)
		#return solver_copy
