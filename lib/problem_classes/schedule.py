class Schedule:
	
	def __init__(self, y, C):
		
		self.y = y
		self.C = C
	
	def __str__(self):
		return 'Machine Completion Times: ' + str(self.C) + '\n'

def order_lexicographically(instance, schedule):
	
	# Sort the machine indexes in non-increasing order of processing times.
	# The machines aresorted in a bubble sort manner. 
	sorted_machine_indexes = [i for i in range(instance.m)]
	
	for iteration in range(instance.m):
		for i in range(instance.m-1):
			if schedule.C[sorted_machine_indexes[i]] < schedule.C[sorted_machine_indexes[i+1]]:
				machine_index = sorted_machine_indexes[i]
				sorted_machine_indexes[i] = sorted_machine_indexes[i+1]
				sorted_machine_indexes[i+1] = machine_index
	
	ordered_C = [schedule.C[sorted_machine_indexes[i]] for i in range(instance.m)]
	ordered_y = [sorted_machine_indexes.index(schedule.y[j]) for j in range(instance.n)]
	
	#for i in range(instance.m):
	#print(str(ordered_C[i]) + ' vs ' + str(sum(instance.p[j] for j in range(instance.n) if ordered_y[j] == i)) )
	
	return Schedule(ordered_y, ordered_C)


def lexicographically_larger(instance, schedule_A, schedule_B):
	
	for i in range(instance.m):
		if schedule_A.C[i] > schedule_B.C[i]:
			return True
		if schedule_A.C[i] < schedule_B.C[i]:
			return False
	
	return False

def check_feasibility(instance, schedule):
	
	C = [0 for i in range(instance.m)]
	for i in range(instance.m):
		for j in range(instance.n):
			if schedule.y[j] == i:
				C[i] += instance.p[j]
	
	epsilon = 10**(-5)
	feasible = True
	for i in range(instance.m):
		if abs(C[i] - schedule.C[i]) > epsilon:
			feasible = False
	
	return feasible

	# Given a vactor of machine weights, it returns
	# the weighted value of the schedule.
def weighted_value(instance, schedule):
	
	M = 2
	w = [M**(instance.m-i-1) for i in range(instance.m)]
	val = 0
	for i in range(instance.m):
		val += schedule.C[i] * w[i]
	return val