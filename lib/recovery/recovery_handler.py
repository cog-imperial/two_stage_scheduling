from __future__ import print_function
from ..io_modules.perturbation_files import read_perturbation_file
from ..io_modules.test_files import get_instances
from ..problem_classes.instance import perturbe_instance
from ..problem_classes.solver import Solver
from ..problem_classes.schedule import check_feasibility
from ..io_modules.solution_pool_files import get_solution_pool
from ..problem_classes.schedule import weighted_value
from ..problem_classes.instance import perturbe_instance
from ..io_modules.recovered_solution_files import write_recovered_solution_file
from ..io_modules.recovered_instances_list import read_recovered_instances_list
from strategies.binding import bindingly_recover
from strategies.flexible import flexibly_recover

def recovery_solve():
	
	method = 'binding'
	commercial_tool = 'cplex'
	stage = 'recovery'
	recovery_solver = Solver(method, commercial_tool, stage)
	
	#test_sets = ['wellformed/moderate',
		#'wellformed/intermediate',
		#'wellformed/hard',
		#'degenerate/moderate',
		#'degenerate/intermediate'
		#]
	
	## List of initial instances (before uncertainty realization)
	#test_set = 'wellformed/intermediate'
	#instances = get_instances(test_set)
	
	test_set = 'degenerate/intermediate'
	instances = read_recovered_instances_list(test_set)
	
	for instance in instances:
		
		print(instance.test_id)
		solution_pool = get_solution_pool(instance)
		
		perturbations = read_perturbation_file(instance)
		
		solution_pool = [schedule for schedule in solution_pool]
		
		for schedule in solution_pool:
			
			sol_id = str(solution_pool.index(schedule) + 1); print(sol_id)
			
			planning_weighted_value = str(weighted_value(instance, schedule))
			
			perturbed_instance = perturbe_instance(instance, schedule, perturbations, method)
			print(sum(perturbed_instance.p))
			
			recovered_schedule = solve(perturbed_instance, sol_id, recovery_solver)
			print(sum(recovered_schedule.C))
			
			write_recovered_solution_file(perturbed_instance, sol_id, recovery_solver, recovered_schedule, planning_weighted_value)

def solve(perturbed_instance, sol_id, recovery_solver):
	
	print(perturbed_instance.test_set + ', ' + perturbed_instance.test_id)
	recovered_schedule = call(perturbed_instance, sol_id, recovery_solver)
	return recovered_schedule

def call(perturbed_instance, sol_id, solver):
	
	if solver.method == 'binding': 
		return bindingly_recover(perturbed_instance, sol_id, solver)
	if solver.method == 'flexible':
		return flexibly_recover(perturbed_instance, sol_id, solver)