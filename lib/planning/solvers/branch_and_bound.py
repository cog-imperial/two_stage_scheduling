from __future__ import print_function, division
from time import time
from heapq import heappush, heappop  
from math import ceil, floor
from ...problem_classes.schedule import Schedule

epsilon = 10**(-7)

class Instance:
	
	def __init__(self, m, n, p):
		
		self.m = m # Number of machines
		self.n = n # Number of jobs
		self.p = p # Job processing times
		
		# Machine weights of the weighting method
		# They are initialized to 1.
		self.w = [1 for i in range(self.m)]
	
	# The machine weights are set with a specified big-M parameter.
	def set_machine_weights(self, M):
		
		self.w = [M**(self.m-i-1) for i in range(self.m)]
	
	# The processing times are sorted in non-increasing order p[1] >= ... >= p[n].
	def sort_processing_times(self):
		
		self.p.sort(reverse = True)
	
	# It returns a lower bound on the weighted value of a lexicographic optimal schedule,
	# using the standard packing argument of uniform load balancing.
	# It exploits the integrality of job processing times.
	def weighted_value_lower_bound(self):
		
		# In the lower bound, machines M[0], ..., M[l-1] have completion time x+1.
		# while machines M[l], ..., M[m-1] have completion time x.
		l = sum(self.p) % self.m # Number of most loaded machines in the bound
		C_lb = [0 for i in range(self.m)]
		
		# Optimal fractional completion times
		for i in range(l):
			C_lb[i] = ceil(sum(self.p)*1.0 / self.m) 
		for i in range(l, self.m):
			C_lb[i] = floor(sum(self.p)*1.0 / self.m) 
		
		# Weighted value of optimal fractional completion times
		lower_bound = 0
		for i in range(self.m):
			lower_bound += C_lb[i] * self.w[i]
		
		return lower_bound
	
	def nodes(self):
		return (self.m ** (self.n + 1) - 1) // (self.m - 1)

class Complete_Schedule:

	def __init__(self, inst, y, C):
		
		self.inst = inst # Instance of the makespan problem
		self.y = y # Assignment of jobs to machines
		self.C = C # Machine completion times
	
	# Given a vactor of machine weights, it returns
	# the weighted value of the schedule.
	def weighted_value(self):
		
		val = 0
		for i in range(self.inst.m):
			val += self.C[i] * self.inst.w[i]
		return val
	      
	def relative_gap(self, lower_bound):
		
		upper_bound = self.weighted_value()
		return (upper_bound - lower_bound) * 1.0 / upper_bound
	
	# It converts any a schedule into a symmetric one with non-increasing order of machine completion times.
	# A bubblesort algorithm is applied.
	def order_machines_lexicographically(self):
		
		for k in range(self.inst.m):
			max_i = k
			for i in range(k+1, self.inst.m):
				if self.C[i] > self.C[max_i]:
					max_i = i
			self.machine_exchange(k, max_i)
	
	# The jobs assigned to machines a and b are exchanged
	def machine_exchange(self, a, b):
		
		for j in range(self.inst.n):
			if self.y[j] == a : self.y[j] = b
			elif self.y[j] == b : self.y[j] = a
		
		temp_C = self.C[a]
		self.C[a] = self.C[b]
		self.C[b] = temp_C

# Modelling the partial schedule in each node of the branch-and-bound tree.
class Partial_Schedule:
	
	def __init__(self, inst, level, y, C):
		
		self.inst = inst
		self.level = level
		self.y = y # Partial assignment of jobs J[0], ..., J[level-1]
		self.C = C # Current machine completion times.
	
	# A complete lexicographic optimal schedule must satisfy the property that C[0] >= ... >= C[m].
	# The function checks whether such a fractional schedule exists.
	# If the function returns False, the node of the branch-and-bound tree associated with
	# the corresponding partial schedule may be rejected.
	def lexicographic_test(self):
		
		remaining_load=sum(self.inst.p[self.level:self.inst.n])
		
		# The gaps that need to be filled in order to end up with a lexicographic schedule
		gaps = [] 
		for i in range(self.inst.m):
			max_C = max(self.C[i:self.inst.m]) # the maximum among t_i,t_{i+1},...,t_m
			gaps.append(max_C - self.C[i])
		required_load = sum(gaps)
		
		return remaining_load >= required_load
	
	def symmetry_test(self):
		# If machine k is empty, then all machines k+1, ..., m must be also empty.
		for k in range(self.inst.m-1):
			if self.C[k] < epsilon:
				for i in range(k+1, self.inst.m):
					if self.C[i] > epsilon:
						return False
		return True
	
	# Constructs a good heuristic schedule maintaining the assignments of the partial schedule.
	def heuristic(self):
		
		# Initialization of heuristic scheudule.
		y_init = [self.y[j] for j in range(self.level)] + [None for j in range(self.level, self.inst.n)] 
		C_init = [self.C[i] for i in range(self.inst.m)] # All machine completion times are zero.
		schedule = Complete_Schedule(self.inst, y_init, C_init)
		
		# Initially, a heuristic schedule is computed, which is not necessarily lexicographic. 
		for j in range(self.level, self.inst.n):
			i = schedule.C.index(min(schedule.C))
			schedule.y[j] = i
			schedule.C[i] += self.inst.p[j]
		
		#C = []
		#for i in range(self.inst.m):
			#C.append(sum(self.inst.p[j] for j in range(self.inst.n) if schedule.y[j]==i))
		#print('Before', C, 'vs', schedule.C)
		#print(schedule.y)
		
		schedule.order_machines_lexicographically()
		
		#C = []
		#for i in range(self.inst.m):
			#C.append(sum(self.inst.p[j] for j in range(self.inst.n) if schedule.y[j]==i))
		#print('After', C, 'vs', schedule.C)
		#print(schedule.y)
		
		return schedule
	
	# The computation of a vectorial lower bound.
	# It requires also computing a vectorial upper bound.
	def vectorial_lower_bound(self, incumbent):
		
		self.ub = []
		self.lb = []
		
		if self.level < self.inst.n:
		
			for k in range(self.inst.m): 
				self.lb.append(self.lower_bound(k))
				self.ub.append(self.upper_bound(k, incumbent))
				self.ub[k] = min(self.ub)
		
			#for k in range(self.inst.m):
				#if self.lb[k] > self.ub[k]:
					#if k >= 2:
						#print('PAPARIA')
					#return infinite_machine_completion_times(self.inst)
		
			return self.lb
	      
	# Computation of the k-th component of the vectorial lower bound.
	def lower_bound(self, k):
		
		# Computation of the lengths of the gaps [t_i,u_i] for the machines 0,1,...,k-1
		# In the case where k=0, gaps is the empty list and sum(gaps) is zero.
		gaps = []
		for i in range(k):
			gaps.append(self.ub[i] - self.C[i])
		gaps_sum = sum(gaps)
		
		# The jobs l,l+1,...,q-1 are rejected and the rejected load becomes equal to sum(p[l:q]).
		q = self.level
		rejected_load=0
		while q < self.inst.n and rejected_load < gaps_sum:
			rejected_load += self.inst.p[q]
			q+=1
			
		# Either q=n, or the rejected_load is greater of equal than gaps_sum.
		# q is the maximum job that will be scheduled on M_k,M_{k+1},...,M_{m-1} in the pseudo-schedule.
		# Avoid an index out of range error
		if q < self.inst.n: 
			pmax = self.inst.p[q]
		else: 
			pmax = 0
		
		# The remaining load, i.e. the load of jobs q,q+1,...,n-1, is assigned to machines k,k+1,...,m-1.
		# and it is a lower bound on what the actually get in a schedule that it is candidate for lexicographic optimal.
		remaining_load = sum(self.inst.p[q:self.inst.n])
		
		# Required load so that the completion times of machines k+1,...,m-1 reach max(t_k,t_{k+1},...,t_{m-1})
		required_load = 0 
		for i in range(k, self.inst.m):
			required_load += max(self.C[k:self.inst.m]) - self.C[i] 
		
		return max( min(self.C[k:self.inst.m]) + pmax, max(self.C[k:self.inst.m]) + max((remaining_load - required_load)*1.0 / (self.inst.m - k), 0) )
	      
	# Computation of the k-th component of the vectorial upper bound
	def upper_bound(self, k, incumbent):
		
		#return incumbent.C[k]
		
		# At least gaps_sum load has to be executed by machines M_0,M_1,...,M_{k-1}
		gaps=[]
		for i in range(k):
			gaps.append(self.lb[i]-self.C[i])
		sum_gaps = sum(gaps)
		
		# The remaining load is an upper bound on what will be executed by machines M_k,...,M_{m-1}
		remaining_load = max(sum(self.inst.p[self.level:self.inst.n]) - sum_gaps,0)
		
		# The starting times of machines M_k,...,M_{m-1} sorted in increasing order
		t = self.C[k:self.inst.m]
		t.sort()
		tmax = max(t)
		
		gap_filling_load = 0
		for i in range(len(t)):
			gap_filling_load += tmax - t[i]
		if remaining_load >= gap_filling_load:
			return min(tmax + (remaining_load - gap_filling_load)*1.0 / (self.inst.m-k) + self.inst.p[self.level], incumbent.C[k])
		
		gap_filling_load = 0
		for i in range(len(t)):
			if gap_filling_load >= remaining_load:
				break
			gap_filling_load += (i+1) * (t[i+1]-t[i])
		t = t[i] - (gap_filling_load-remaining_load)*1.0 / (self.inst.m-i+1)
		
		return min( max( t + self.inst.p[self.level], tmax  ), incumbent.C[k]) 
	
	# It converts a partial schedule of level n into a complete schedule.
	def convert_to_complete_schedule(self):
		if self.level == self.inst.n:
			schedule = Complete_Schedule(self.inst, self.y, self.C)
			schedule.order_machines_lexicographically()
			return schedule

class Node:
	
	def __init__(self, inst, level, partial_schedule):
		
		self.inst = inst
		self.level = level
		self.partial_schedule = partial_schedule
		
	# Returns a list with all child nodes of self node
	def explore(self,global_times):
		
		children=[]
		
		# A node is created for each assignment of job l to one of the machines 0,1,...,e-1
		for i in range(self.inst.m):
			inst = self.partial_schedule.inst
			level = self.partial_schedule.level + 1
			y = list(self.partial_schedule.y) # a new copy of the list in the memory
			y[self.partial_schedule.level] = i
			C = list(self.partial_schedule.C)
			C[i] += self.inst.p[self.partial_schedule.level]
			partial_schedule = Partial_Schedule(inst, level, y, C)
			children.append(Node(self.inst, level, partial_schedule))
			
		return children
		
	# eturns True if the node is a leaf
	def is_leaf(self):
		return self.level == self.inst.n
	      
	def descendants(self):
		return (self.inst.m ** (self.inst.n - self.level) - self.inst.m) // (self.inst.m - 1)
	      
# Algorithm comparing two vectors Ca and Cb of machine completion times.
# It returns True if Ca is strictly lexicographically smaller than Cb, and
# False, otherwise, for the same makespan problem instance.
def lexicographically_smaller(inst, Ca, Cb):
	
	for i in range(inst.m):
		if Ca[i] < Cb[i]:
			return True
		if Ca[i] > Cb[i]:
			return False
	return False


def branch_and_bound_solve(instance, solver):
	
	inst = Instance(instance.m, instance.n, instance.p)
	relative_gap_tolerance = solver.gap_tolerance
	time_limit = solver.time_limit
	
	# Choose weighting method big_M parameter M = 2.
	inst.set_machine_weights(2)
	
	# The processing times are sorted in non-increasing decreasing order.
	inst.sort_processing_times()
	
	# Main body of the branch-and-bound-algorithm.
	start_time = time()
	current_time = start_time
	
	# Initialization of root node partial schedule.
	root = root_node_initialization(inst)
	
	# Number of times that an object of class Node is created.
	nodes_explored = 1
	nodes_pruned_symmetry = 0
	nodes_pruned_makespan_bounding = 0
	nodes_pruned_lower_ranked_bounding = 0 # Because of bounding objectives of lower importance than the makespan
	
	# Initialization of the incumbent
	incumbent = incumbent_initialization(inst)
	global_lower_bound = inst.weighted_value_lower_bound()
	relative_gap = float('inf')
	
	# A stack for storing the active nodes of the search tree.
	stack = []
	stack.append(root)
	
	f = open('data/statistics/branch_and_bound_incumbents/' + instance.test_set.replace('/', '_') + '.txt','a')
	f.write(instance.test_id + '\n')
	f.write('Incumbents:\n')
	
	while len(stack) != 0 and current_time - start_time < time_limit and relative_gap > relative_gap_tolerance:
		
		node = stack.pop()
		child_nodes = node.explore(incumbent)
		nodes_explored += len(child_nodes)
		
		for child_node in child_nodes:
			
			# If the child is a leaf, then it is compared to the currently best-found solution.
			if child_node.is_leaf(): 
				
				#print('leaf found')
				
				found_schedule = child_node.partial_schedule.convert_to_complete_schedule()
				if lexicographically_smaller(inst, found_schedule.C, incumbent.C):
					incumbent = found_schedule
					relative_gap = incumbent.relative_gap(global_lower_bound)
					current_time = time()
					f.write(str(incumbent.C) + ' ' + str(current_time - start_time) + '\n')
				
			else:
				
				if child_node.partial_schedule.lexicographic_test() and child_node.partial_schedule.symmetry_test():
				
					heuristic_schedule = child_node.partial_schedule.heuristic() #print(heuristic_schedule.C)
					if lexicographically_smaller(inst, heuristic_schedule.C, incumbent.C):
						incumbent = heuristic_schedule
						relative_gap = incumbent.relative_gap(global_lower_bound)
						current_time = time()
						f.write(str(incumbent.C) + ' ' + str(current_time - start_time) + '\n')
					
					
					vectorial_lower_bound = child_node.partial_schedule.vectorial_lower_bound(incumbent)
					if lexicographically_smaller(inst, vectorial_lower_bound, incumbent.C): # and weighted_mip_value(c.lb)<(1+0.000001)*global_ub:
						stack.append(child_node)
					else:
						if vectorial_lower_bound[0] > incumbent.C[0]:
							nodes_pruned_makespan_bounding += child_node.descendants()
						else:
							nodes_pruned_lower_ranked_bounding += child_node.descendants()
						
				
				else:
					nodes_pruned_symmetry += child_node.descendants()
					
			
			#print(incumbent.C)
			
		current_time = time()
		
	#check_feasibility(inst, incumbent)
		
	if len(stack) == 0:
		termination_status = 'Completed tree exploration'
	elif relative_gap <= relative_gap_tolerance:
		termination_status = 'Enough tolerance'
	else:
		termination_status = 'Timeout'
	
	elapsed_time = current_time - start_time
	nodes_left = len(stack)
	
	schedule = Schedule(incumbent.y, incumbent.C)
	solver.set_results(incumbent.weighted_value(), global_lower_bound, relative_gap, elapsed_time, nodes_explored, nodes_left)
	
	remaining_nodes = inst.nodes() - nodes_explored - nodes_pruned_symmetry - nodes_pruned_makespan_bounding - nodes_pruned_lower_ranked_bounding
	
	f.write('Elapsed time: ' + str(elapsed_time) + '\n')
	f.write('Termination condition: ' + str(termination_status) + '\n')
	f.write('Nodes explored: ' + str(nodes_explored) + '\n')
	f.write('Nodes left: ' + str(nodes_left) + '\n')
	f.write('Nodes pruned via symmetry handling: ' + magnitude(int(nodes_pruned_symmetry)) + '\n')
	f.write('Nodes pruned via bounding: ' + magnitude(int(nodes_pruned_makespan_bounding)) + '\n')
	f.write('Nodes pruned via bounding lower than makespan objectives: ' + magnitude(int(nodes_pruned_lower_ranked_bounding)) + '\n')
	f.write('Remaining nodes: ' + magnitude(int(remaining_nodes)) + '\n' )
	f.write('\n')
	
	f.close()
	
	return schedule
      
def check_feasibility(inst, schedule):
	C = [0 for i in range(inst.m)]
	for i in range(inst.m):
		for j in range(inst.n):
			if schedule.y[j] == i:
				C[i] += inst.p[j]
	for i in range(inst.m):
		print(C[i], ' vs ', schedule.C[i])

def root_node_initialization(inst):
	
	level = 0
	y = [None for j in range(inst.n)]
	C = [0 for i in range(inst.m)]
	partial_schedule = Partial_Schedule(inst, level, y, C)
	return Node(inst, level, partial_schedule)
      
def incumbent_initialization(inst):
	
	y = [None for j in range(inst.n)]
	C = [float('inf') for i in range(inst.m)]
	return Complete_Schedule(inst, y, C)

#def infinite_machine_completion_times(inst):
#	return [float('inf')] * inst.m

# It returns the order of magnitude of a number of nodes as a string.
# E.g.the order of magnitude of 65249 is 6*10^6
def magnitude(n):
	exponent = len(str(n))
	basis = n // 10**(exponent-1)
	if exponent <= 5:
		return str(n)
	else:
		return str(basis) + '*10^' + str(exponent)

