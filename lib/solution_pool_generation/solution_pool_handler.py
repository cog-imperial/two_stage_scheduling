from solution_pool_generator import generate_solution_pool
from ..problem_classes.solver import Solver
from ..problem_classes.schedule import check_feasibility
from ..io_modules.test_files import get_instances
from ..io_modules.solution_pool_files import write_solution_pool_file

def produce_solution_pool():
	
	method = 'solution_pool'
	commercial_tool = 'cplex'
	stage = 'solution_pool_generation'
	
	solver = Solver(method, commercial_tool, stage)
	
	#test_sets = ['wellformed/moderate',
		#'wellformed/intermediate',
		#'wellformed/hard',
		#'degenerate/moderate',
		#'degenerate/intermediate'
		#]
	
	test_set = 'degenerate/intermediate'
	
	# The default 100s time limit and 0.0001 gap_tolerance are adopted.
	# In order the change these parameter, appropriate set functions have to implemented and called in Solver class.
	
	instances = get_instances(test_set)
	
	for instance in instances:
		solution_pool = get_solution_pool(instance, solver)
		sol_id = 1 # Id for each member of the solution pool.
		for schedule in solution_pool:
			print('Feasibility test: ' + str(check_feasibility(instance, schedule)))
			write_solution_pool_file(instance, schedule, str(sol_id))
			sol_id += 1

def get_solution_pool(instance, solver):
	print(instance.test_set + ', ' + instance.test_id)
	solution_pool = generate_solution_pool(instance, solver)
	return solution_pool