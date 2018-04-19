from ..problem_classes.schedule import Schedule, weighted_value
import os 

def write_solution_pool_file(instance, schedule, sol_id):
	
	f=open(solution_pool_file_path(instance, sol_id), 'w')
	
	f.write('Weighted value: ' + str(weighted_value(instance, schedule)) + '\n')
	
	for i in range(instance.m):
		f.write('C[' + str(i) + ']=' + str(schedule.C[i]) + '\n')
	
	for j in range(instance.n):
		f.write('y[' + str(j) + ']=' + str(schedule.y[j]) + '\n')
	
	f.close()

def solution_pool_file_path(instance, sol_id):
	directory = 'data/solutions/pools/' + instance.test_set + '/' + instance.test_id
	if not os.path.exists(directory):
		os.makedirs(directory)
	return directory + '/' + sol_id + '.sol'  

def read_solution_pool_file(instance, sol_id):
	
	f = open(solution_pool_file_path(instance, sol_id), 'r')    
	
	# Read weighted value
	line = f.readline()
	weighted_value = float(line[16:])
	
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

def solution_pool_path(instance):
	return 'data/solutions/pools/' + instance.test_set + '/' + instance.test_id

def get_solution_pool(instance):
	
	path = solution_pool_path(instance)
	sol_files = os.listdir(path)
	sol_ids = [sol_file.replace('.sol', '') for sol_file in sol_files]
	sol_ids.sort(key = sol_id_keys)
	
	solution_pool = []
	
	for sol_id in sol_ids:
		solution = read_solution_pool_file(instance, sol_id)
		solution_pool.append(solution)
	
	return solution_pool

# Used for sorting tests in decreasing order of their number.
def sol_id_keys(sol_id):
	return int(sol_id)