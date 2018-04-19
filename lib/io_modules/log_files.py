## It return the number of explored nodes by the solver 
## for the instance test_id in the .log file produced by the solver.
#def read_nodes_explored(instance, solver):
	
	#f = open(log_file(instance, solver), 'r')
	#text = f.read()
	
	#if solver.commercial_tool == 'cplex':
		#s_success = find_substring_between(text, 'Nodes = ', ' ')
		#s_failure = find_substring_between(text, 'Nodes = ', '\n')
		#if len(s_success) < len(s_failure):
			#s = s_success
		#else:
			#s = s_failure
	
	#if solver.commercial_tool == 'gurobi':
		#s = find_substring_between(text, 'Explored ', ' nodes')
	
	#f.close()
	
	#return int(s)
      
# It return the number of nodes left to be explored by the solver 
# for the instance test_id in the .log file produced by the solver.
def read_nodes(instance, solver):
	
	f = open(log_file(instance, solver), 'r')
	text = f.read()
	f.close()
	
	f = open(log_file(instance, solver), 'r')
	lines = f.readlines()
	f.close()
	
	if solver.commercial_tool == 'cplex':
		string = find_substring_between(text, 'Nodes = ', '\n')
		if '(' not in string:
			nodes_explored = int(string)
			nodes_left = 0 # if cplex terminated successfully, the number of nodes left is 0
		else:
			(nodes_explored, nodes_left) = string.split(' (')
			nodes_explored = int(nodes_explored)
			nodes_left = int(nodes_left.split(')')[0])
	
	if solver.commercial_tool == 'gurobi':
		if 'Cutting planes' in text:
			keyword = 'Cutting planes'
		else:
			keyword = 'Explored'
		
		for line in lines:
			if keyword in line:
				nodes_line = lines[lines.index(line) - 2]
				nodes_line = nodes_line[1:]
				nodes_explored = int(nodes_line.split()[0])
				nodes_left = int(nodes_line.split()[1])
	
	return (nodes_explored, nodes_left)
      
# It finds the substring of s between the pred string and the succ string     
def find_substring_between(s, former, latter):
	start = s.find(former) + len(former)
	end = s.find(latter, start)
	return s[start:end]


def log_file(instance, solver):
	if solver.stage == 'planning':
		if solver.commercial_tool:
			log_file_name = 'data/solutions/' + solver.stage + '/' + instance.test_set + '/' + solver.method + '/' + instance.test_id + '_' + solver.commercial_tool + '.log' 
			print(log_file_name)
			return log_file_name
		else:
			return 'data/solutions/' + solver.stage + '/' + instance.test_set + '/' + solver.method + '/' + instance.test_id + '.log' 
	else:
		if solver.commercial_tool:
			return 'data/solutions/' + solver.stage + '/' + instance.planning_solver.method + '/' + instance.test_set + '/perturbed_' + instance.test_id + '_' + solver.commercial_tool + '.log' 
		else:
			return 'data/solutions/' + solver.stage + '/' + instance.planning_solver.method + '/' + instance.test_set + '/perturbed' + instance.test_id + '.log' 

def recovery_log_file(instance, solver, sol_id):
	return 'data/solutions/recovery/' + instance.test_set + '/' + solver.method + '/' + instance.test_id + '/' + sol_id + '.log' 