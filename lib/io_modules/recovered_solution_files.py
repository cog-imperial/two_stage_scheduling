from ..problem_classes.schedule import Schedule
import os

def write_recovered_solution_file(instance, sol_id, solver, schedule, planning_weighting_value):
	
	f = open(recovered_solution_file_path(instance, solver, sol_id), 'w')
	
	f.write('Elapsed time: ' + solver.get_string_value('elapsed_time') + '\n')
	f.write('Upper bound: ' + solver.get_string_value('upper_bound') + '\n')
	f.write('Planning weighted value: ' + planning_weighting_value + '\n')
	
	for i in range(instance.m):
		f.write('C[' + str(i) + ']=' + str(schedule.C[i]) + '\n')
	
	for j in range(instance.n):
		f.write('y[' + str(j) + ']=' + str(schedule.y[j]) + '\n')
	
	f.close()

def recovered_solution_file_path(instance, solver, sol_id):
	directory = 'data/solutions/recovery/' + instance.test_set + '/' + solver.method + '/' + instance.test_id
	if not os.path.exists(directory):
		os.makedirs(directory)
	return directory + '/' + sol_id + '.sol' 

def read_recovered_solution_file(instance, recovery_solver, sol_id):
	
	f = open(recovered_solution_file_path(instance, recovery_solver, sol_id), 'r')    
	
	# Read elapsed time
	line = f.readline()
	elapsed_time = float(line[14:])
	#time_out = elapsed_time >= solver.time_limit 
	#if time_out: elapsed_time = float('inf')
	
	# Read upper bound
	line = f.readline()
	upper_bound = float(line[13:])
	
	# Read planning weighting value
	line = f.readline()
	planning_weighted_value = float(line[25:])
	
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
	
	return (schedule, upper_bound, elapsed_time, planning_weighted_value)


def get_recovered_solutions(instance, recovery_solver):
	
	path = 'data/solutions/recovery/' + instance.test_set + '/' + recovery_solver.method + '/' + instance.test_id
	sol_files = os.listdir(path)
	sol_ids = [sol_file.replace('.sol', '') for sol_file in sol_files if 'log' not in sol_file]
	sol_ids.sort(key = sol_id_keys)
	
	recovered_solutions = []
	
	for sol_id in sol_ids:
		(schedule, upper_bound, elapsed_time, planning_weighted_value) = read_recovered_solution_file(instance, recovery_solver, sol_id)
		recovered_solutions.append((schedule, upper_bound, elapsed_time, planning_weighted_value))
	
	return recovered_solutions

# Used for sorting tests in decreasing order of their number.
def sol_id_keys(sol_id):
	return int(sol_id)