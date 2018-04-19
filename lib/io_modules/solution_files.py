from ..problem_classes.schedule import Schedule

def write_solution_file(instance, solver, schedule):
	
	f=open(solution_file_path(instance, solver), 'w')
	
	f.write('Elapsed time: ' + solver.get_string_value('elapsed_time') + '\n')
	f.write('Nodes explored: ' + solver.get_string_value('nodes_explored') + '\n')
	f.write('Nodes left: ' + solver.get_string_value('nodes_left') + '\n')
	f.write('Relative gap: ' + solver.get_string_value('relative_gap') + '\n')
	f.write('Upper bound: ' + solver.get_string_value('upper_bound') + '\n')
	f.write('Lower bound: ' + solver.get_string_value('lower_bound') + '\n')
	
	for i in range(instance.m):
		f.write('C[' + str(i) + ']=' + str(schedule.C[i]) + '\n')
	
	for j in range(instance.n):
		f.write('y[' + str(j) + ']=' + str(schedule.y[j]) + '\n')
	
	f.close()

def solution_file_path(instance, solver):
	if solver.stage == 'planning':
		if solver.commercial_tool != None:
			return 'data/solutions/' + solver.stage + '/' + instance.test_set + '/' + solver.method + '/' + instance.test_id + '_' + solver.commercial_tool + '.sol'
		else:
			return 'data/solutions/' + solver.stage + '/' + instance.test_set + '/'+ solver.method + '/' + instance.test_id + '.sol'
	else:
		if solver.commercial_tool != None:
			return 'data/solutions/' + solver.stage + '/' + instance.planning_solver.method + '/' + instance.test_set + '/perturbed_' + instance.test_id + '_' + solver.commercial_tool + '.sol'
		else:
			return 'data/solutions/' + solver.stage + '/' + instance.planning_solver.method + '/' + instance.test_set + '/perturbed_' + instance.test_id + '.sol'	  

def read_solution_file(instance, solver):
	
	f = open(solution_file_path(instance, solver), 'r')    
	
	# Read elapsed time
	line = f.readline()
	elapsed_time = float(line[14:])
	time_out = elapsed_time >= solver.time_limit 
	if time_out: elapsed_time = float('inf')
	
	# Read nodes explored
	line = f.readline()
	nodes_explored = line[16:]
	if '-' in nodes_explored: 
		nodes_explored = None
	else:
		nodes_explored = int(nodes_explored)
	
	# Read nodes left
	line = f.readline()
	nodes_left = line[12:]
	if '-' in nodes_left: 
		nodes_left = None
	else:
		nodes_left = int(nodes_left)
	
	
	# Read relative 
	line = f.readline()
	relative_gap = line[14:]
	if '-' in relative_gap: 
		relative_gap = None
	else:
		relative_gap = float(relative_gap)
	#relative_gap = (upper_bound - lower_bound) / upper_bound
	
	# Read upper bound
	line = f.readline()
	upper_bound = float(line[13:])
	
	# Read lower bound
	line = f.readline()
	lower_bound = line[13:]
	if '-' in lower_bound: 
		lower_bound = None
	else:
		lower_bound = float(lower_bound)
	
	solver.set_results(upper_bound, lower_bound, relative_gap, elapsed_time, nodes_explored, nodes_left)
	
	line = f.readline()
	C = []
	i = 0
	while line[0] == 'C':
		val = float( line[2 + len(str(i)) + 2:] )
		C.append(float(val))
		i += 1
		line = f.readline()
	
	y = []
	i = 0
	while line != '':
		val = float(line[2+len(str(i))+2:])
		y.append(int(val))
		i += 1
		line = f.readline()
		
	schedule = Schedule(y, C)
	
	f.close()
	
	return schedule
