from __future__ import print_function
from ...problem_classes.schedule import Schedule, order_lexicographically, lexicographically_larger, weighted_value
from ...io_modules.log_files import log_file
import cplex

def highest_rank_objective_solve(instance, solver):
	
	model = cplex.Cplex()
	
	set_solver_parameters(model, instance, solver)
	
	# Create a symbol table mapping the makespan problem variables into a one-dimensional vector variable
	x_symbols = ['x[' + str(i) + ',' + str(j) + ']' for i in range(instance.m) for j in range(instance.n)]
	C_symbols = ['C[' + str(i) + ']' for i in range(instance.m)]
	makespan_symbol = 'f'
	
	symbol_table = dict()
	
	index = 0
	for i in range(instance.m):
		for j in range(instance.n):
			symbol_table['x[' + str(i) + ',' + str(j) + ']'] = index 
			index += 1
	
	for i in range(instance.m):
		symbol_table['C[' + str(i) + ']'] = index
		index += 1
	
	symbol_table['f'] = index
	
	
	# Total number of variables
	v = instance.n * instance.m + instance.m + 1
	
	
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
		objective_function_coefficients[symbol_table[C_symbol]] = 0.0
		variable_lower_bounds[symbol_table[C_symbol]] = 0.0
		variable_upper_bounds[symbol_table[C_symbol]] = cplex.infinity
		
	objective_function_coefficients[symbol_table[makespan_symbol]] = 1.0
	variable_lower_bounds[symbol_table[makespan_symbol]] = 0.0
	variable_upper_bounds[symbol_table[makespan_symbol]] = cplex.infinity
	
	variable_names = [x_symbol for x_symbol in x_symbols] + [C_symbol for C_symbol in C_symbols] + [makespan_symbol]
	
	
	# Variable initialization
	model.variables.add(obj = objective_function_coefficients, lb = variable_lower_bounds, ub = variable_upper_bounds, names = variable_names)
	
	# Variable types
	for x_symbol in x_symbols:
		model.variables.set_types(x_symbol, model.variables.type.binary)
	
	for C_symbol in C_symbols:
		model.variables.set_types(C_symbol, model.variables.type.continuous)
	
	model.variables.set_types(makespan_symbol, model.variables.type.continuous)
	
	
	# Constraint population
	rows = []
	right_hand_side_parameters = []
	constraint_senses = []
	constraint_names = [] # Row names.
	
	# Makespan constraints
	for i in range(instance.m):
		values = [0.0 for k in range(v)]
		values[symbol_table['f']] = 1.0
		values[symbol_table['C[' + str(i) + ']']] = -1.0
		
		rows.append([variable_names, values])
		right_hand_side_parameters.append(0.0)
		constraint_senses += 'G' # Greater or equal than.
		constraint_names.append('Makespan ' + str(i))
	
	# Completion time constraints
	for i in range(instance.m):
		values = [0.0 for k in range(v)]
		values[symbol_table['C[' + str(i) + ']']] = 1.0
		
		for j in range(instance.n):
			values[symbol_table['x[' + str(i) + ',' + str(j) + ']']] = -instance.p[j]
		
		rows.append([variable_names, values])
		right_hand_side_parameters.append(0.0)
		constraint_senses += 'E' # Equal to.
		constraint_names.append('Completion time ' + str(i))
	
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
	
	# Timer
	start_time = model.get_time()
	
	model.solve()
	
	# Initialization of the lexicographic best schedule.
	cplex_values = model.solution.get_values()
	lexicographic_best_schedule = convert_cplex_solution_to_schedule(instance, symbol_table, cplex_values)
	lexicographic_best_schedule = order_lexicographically(instance, lexicographic_best_schedule)
	print(lexicographic_best_schedule.C)
	
	nodes_explored = model.solution.progress.get_num_nodes_processed()
	
	# Timer
	mid_time = model.get_time()
	
	print('Phase 1: ' + str(mid_time - start_time) + ' seconds')
	
	model.populate_solution_pool()
	
	# Timer
	end_time = model.get_time()
	
	print('Phase 2: ' + str(end_time - mid_time) + ' seconds')
	 
	# Number of solutions in the solution pool.
	# print(model.solution.pool.get_num())
	
	solution_pool_size = model.solution.pool.get_num(); print('Number of solutions: ' + str(solution_pool_size))
	solution_pool = []
	
	for sol in range(solution_pool_size):
		
		cplex_values = model.solution.pool.get_values(sol)
		schedule = convert_cplex_solution_to_schedule(instance, symbol_table, cplex_values)
		schedule = order_lexicographically(instance, schedule)
		solution_pool.append(schedule)
		#upper_bound = model.solution.get_objective_value()
		#upper_bound = model.solution.pool.get_objective_value(sol)
	
	for schedule in solution_pool:
		if lexicographically_larger(instance, lexicographic_best_schedule, schedule):
			print()
			print(lexicographic_best_schedule.C)
			print('vs')
			print(schedule.C)
			print()
			lexicographic_best_schedule = schedule
	
	#upper_bound = lexicographic_best_schedule.C[0]
	#lower_bound = model.solution.MIP.get_best_objective()
	#relative_gap = (upper_bound - lower_bound) * 1.0 / upper_bound
	
	upper_bound = weighted_value(instance, lexicographic_best_schedule)
	lower_bound = None
	relative_gap = None
	
	elapsed_time = end_time - start_time
	nodes_explored += model.solution.progress.get_num_nodes_processed()
	nodes_left = None
	
	solver.set_results(upper_bound, lower_bound, relative_gap, elapsed_time, nodes_explored, nodes_left)
	
	return lexicographic_best_schedule

def set_solver_parameters(model, instance, solver):
	
	model.parameters.timelimit.set(solver.time_limit)
	model.parameters.mip.tolerances.mipgap.set(solver.gap_tolerance)
	model.parameters.threads.set(1)
	
	#model.parameters.mip.limits.populate.set(1000) # maximum number of solutions generated in the solution pool
	#model.parameters.mip.pool.intensity.set(2) # the suggested approach to populate solution pool
	#model.parameters.mip.pool.replace.set(1) # replace the solution with the worst objective value
	#model.parameters.mip.pool.relgap.set(solver_parameters.mip_gap)
	
	model.parameters.mip.limits.populate.set(2000) # maximum number of solutions generated in the solution pool
	#model.parameters.mip.pool.intensity.set(2) # the suggested approach to populate solution pool
	model.parameters.mip.pool.replace.set(1) # replace the solution with the worst objective value
	#model.parameters.mip.pool.relgap.set(solver_parameters.mip_gap)
	
	model.set_results_stream(log_file(instance, solver))

def convert_cplex_solution_to_schedule(scheduling_instance, symbol_table, cplex_values):
		
		epsilon = 0.0000001
		
		y = [0 for j in range(scheduling_instance.n)]
		
		for i in range(scheduling_instance.m):
			for j in range(scheduling_instance.n):
				if cplex_values[symbol_table['x[' + str(i) + ',' + str(j) + ']']] >= epsilon: 
					y[j] = i
		
		C = [cplex_values[symbol_table['C[' + str(i) + ']']] for i in range(scheduling_instance.m)]  
		
		return Schedule(y, C)
