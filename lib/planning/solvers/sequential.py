from __future__ import print_function
from ...problem_classes.schedule import Schedule, order_lexicographically, lexicographically_larger, weighted_value
from ...io_modules.log_files import log_file
import cplex

def sequential_solve(instance, solver):
	
	model = cplex.Cplex()
	
	set_solver_parameters(model, instance, solver)
	
	# Create a symbol table mapping the makespan problem variables into a one-dimensional vector variable
	x_symbols = ['x[' + str(i) + ',' + str(j) + ']' for i in range(instance.m) for j in range(instance.n)]
	C_symbols = ['C[' + str(i) + ']' for i in range(instance.m)]
	
	symbol_table = dict()
	
	index = 0
	for i in range(instance.m):
		for j in range(instance.n):
			symbol_table['x[' + str(i) + ',' + str(j) + ']'] = index 
			index += 1
	
	for i in range(instance.m):
		symbol_table['C[' + str(i) + ']'] = index
		index += 1
	
	
	# Total number of variables
	v = instance.n * instance.m + instance.m
	
	
	# Sense
	model.objective.set_sense(model.objective.sense.minimize)
	
	
	# Objective function variable coefficients and variable bounds
	objective_function_coefficients = [0.0 for k in range(v)]
	variable_lower_bounds = [0.0 for k in range(v)]
	variable_upper_bounds = [0.0 for k in range(v)]
	
	for x_symbol in x_symbols:
		objective_function_coefficients[symbol_table[x_symbol]] = 0.0
		variable_lower_bounds[symbol_table[x_symbol]] = 0.0
		variable_upper_bounds[symbol_table[x_symbol]] = 1.0
	
	for C_symbol in C_symbols:
		if C_symbol == 'C[0]': objective_function_coefficients[symbol_table[C_symbol]] = 1.0
		else: objective_function_coefficients[symbol_table[C_symbol]] = 0.0
		variable_lower_bounds[symbol_table[C_symbol]] = 0.0
		variable_upper_bounds[symbol_table[C_symbol]] = cplex.infinity
	
	variable_names = [x_symbol for x_symbol in x_symbols] + [C_symbol for C_symbol in C_symbols]
	
	
	# Variable initialization
	model.variables.add(obj = objective_function_coefficients, lb = variable_lower_bounds, ub = variable_upper_bounds, names = variable_names)
	
	# Variable types
	for x_symbol in x_symbols:
		model.variables.set_types(x_symbol, model.variables.type.binary)
	
	for C_symbol in C_symbols:
		model.variables.set_types(C_symbol, model.variables.type.continuous)
	
	
	# Constraint population
	rows = []
	right_hand_side_parameters = []
	constraint_senses = []
	constraint_names = [] # Row names.
	
	# Completion time ordering
	for i in range(instance.m - 1):
		values = [0.0 for k in range(v)]
		values[symbol_table['C[' + str(i) + ']']] = 1.0
		values[symbol_table['C[' + str(i+1) + ']']] = -1.0
		
		rows.append([variable_names, values])
		right_hand_side_parameters.append(0.0)
		constraint_senses += 'G' # Greater than or equal to.
		constraint_names.append('Completion time ' + str(i) + 'ordering')
	
	# Completion time computation
	for i in range(instance.m):
		values = [0.0 for k in range(v)]
		values[symbol_table['C[' + str(i) + ']']] = 1.0
		
		for j in range(instance.n):
			values[symbol_table['x[' + str(i) + ',' + str(j) + ']']] = -instance.p[j]
		
		rows.append([variable_names, values])
		right_hand_side_parameters.append(0.0)
		constraint_senses += 'E' # Equal to.
		constraint_names.append('Completion time ' + str(i) + 'computation')
	
	# Job assignment constraints
	for j in range(instance.n):
		values = [0.0 for k in range(v)]
		
		for i in range(instance.m):
			values[symbol_table['x[' + str(i) + ',' + str(j) + ']']] = 1.0
		
		rows.append([variable_names, values])
		right_hand_side_parameters.append(1.0)
		constraint_senses += 'E'
		constraint_names.append('Job assignment ' + str(j))
	
	model.linear_constraints.add(lin_expr = rows, senses = constraint_senses, rhs = right_hand_side_parameters, names = constraint_names)
	
	# Constraint population
	rows = []
	right_hand_side_parameters = []
	constraint_senses = []
	constraint_names = [] # Row names.
	
	# Timer
	start_time = model.get_time()
	
	Copt = []
	nodes_explored = 0
	
	for k in range(instance.m):
		
		if k != 0:
			model.objective.set_linear('C[' + str(k-1) + ']', 0.0)
			model.objective.set_linear('C[' + str(k) + ']', 1.0)
			
			values = [0.0 for i in range(v)]
			values[symbol_table['C[' + str(k-1) + ']']] = 1.0
			rows.append([variable_names, values])
			right_hand_side_parameters.append(Copt[k-1])
			constraint_senses += 'L'
			constraint_names.append('Objective ' + str(k) + ' upper bound')
			
			model.linear_constraints.add(lin_expr = rows, senses = constraint_senses, rhs = right_hand_side_parameters, names = constraint_names)
			
		model.solve()
		
		# Initialization of the lexicographic best schedule.
		cplex_values = model.solution.get_values()
		schedule = convert_cplex_solution_to_schedule(instance, symbol_table, cplex_values)
		schedule = order_lexicographically(instance, schedule)
		print('Step ' + str(k) + ': ')
		print(schedule.C)
		
		Copt.append(schedule.C[k])
		nodes_explored += model.solution.progress.get_num_nodes_processed()
		
		current_time = model.get_time()
		if current_time - start_time > solver.time_limit:
			break
	
	# Timer
	end_time = model.get_time()
	elapsed_time = end_time - start_time
	
	print('Elapsed time ' + str(end_time - start_time) + ' seconds')
	
	#upper_bound = schedule.C[0]
	#lower_bound = model.solution.MIP.get_best_objective()
	#relative_gap = (upper_bound - lower_bound) * 1.0 / upper_bound
	
	upper_bound = weighted_value(instance, schedule)
	lower_bound = None
	relative_gap = None
	nodes_explored = None
	nodes_left = None
	
	solver.set_results(upper_bound, lower_bound, relative_gap, elapsed_time, nodes_explored, nodes_left)
	
	return schedule


def set_solver_parameters(model, instance, solver):
	
	model.parameters.timelimit.set(solver.time_limit)
	model.parameters.mip.tolerances.mipgap.set(solver.gap_tolerance)
	model.parameters.threads.set(1)
	model.set_results_stream(log_file(instance, solver))


def convert_cplex_solution_to_schedule(instance, symbol_table, cplex_values):
	
	epsilon = 0.0000001
	
	y = [0 for j in range(instance.n)]
	
	for i in range(instance.m):
		for j in range(instance.n):
			if cplex_values[symbol_table['x[' + str(i) + ',' + str(j) + ']']] >= epsilon: 
				y[j] = i
	
	C = [cplex_values[symbol_table['C[' + str(i) + ']']] for i in range(instance.m)]  
	
	return Schedule(y, C)
