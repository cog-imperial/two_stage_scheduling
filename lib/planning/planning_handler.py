from solvers.sequential import sequential_solve
from solvers.weighting import weighting_solve
from solvers.highest_rank_objective import highest_rank_objective_solve
from solvers.branch_and_bound import branch_and_bound_solve
from ..problem_classes.solver import Solver
from ..problem_classes.schedule import check_feasibility
from ..io_modules.test_files import get_instances
from ..io_modules.solution_files import write_solution_file

def planning_solve():
	
	#methods = ['sequential',
		#'weighting',
		#'highest_rank_objective',
		#'branch_and_bound'
		#]
	
	#commercial_tool = ['cplex', 
		#'gurobi', 
		#None
		#]
	
	# ONLY the following combinations have been implemented:
	# sequential, cplex
	# weighting, cplex
	# weighting, gurobi
	# highest_rank_objective, cplex
	# branch_and_bound, None
	
	# Instead of running everything using a for loop, we run them one by one.
	# The default parameters are 1000s time_limit and 0.0001 gap_tolerance.
	# These parameters can be modified by creating and using appropriate set functions in the class Solver.
	
	method = 'branch_and_bound'
	commercial_tool =  None
	stage = 'planning'
	solver = Solver(method, commercial_tool, stage)
	
	#test_sets = ['wellformed/moderate',
		#'wellformed/intermediate',
		#'wellformed/hard',
		#'degenerate/moderate',
		#'degenerate/intermediate'
		#]
	
	test_set = 'degenerate/intermediate'
	
	instances = get_instances(test_set)
	solve(instances, solver)

def solve(instances, solver):
	
	for instance in instances:
		print(instance.test_set + ', ' + instance.test_id + ': ' + solver.name())
		schedule = call(instance, solver)
		print('Feasibility test: ' + str(check_feasibility(instance, schedule)))
		write_solution_file(instance, solver, schedule)

def call(instance, solver):
	
	if solver.method == 'sequential': return sequential_solve(instance, solver)
	if solver.method == 'highest_rank_objective': return highest_rank_objective_solve(instance, solver)
	if solver.method == 'branch_and_bound': return branch_and_bound_solve(instance, solver)
	if solver.method == 'weighting': return weighting_solve(instance, solver)