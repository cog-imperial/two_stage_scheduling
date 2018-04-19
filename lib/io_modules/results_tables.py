from __future__ import division, print_function
from os import listdir
from latex_tables import *
from test_files import get_instances
from perturbed_test_files import get_perturbed_instances
from solution_files import read_solution_file
from ..problem_classes.solver import Solver

def generate_planning_results_tables():
	
	# Read solver results
	test_sets = ['moderate', 'hard', 'challenging']
	
	for test_set in test_sets:
	
		instances = get_instances(test_set)
		results = []
		
		for instance in instances:
			
			solvers = [
				Solver('branch_and_bound', None, 'planning'), 
				Solver('weighting', 'cplex', 'planning'), 
				Solver('weighting', 'gurobi', 'planning'), 
				Solver('sequential', 'cplex', 'planning'),
				Solver('highest_rank_objective', 'cplex', 'planning'), 
				Solver('makespan', 'cplex', 'planning')
			]
			
			for solver in solvers:
				schedule = read_solution_file(instance, solver) # solver statistics are stored in the solver object
				results.append((instance, solver, schedule))
		
		tex_file_path = 'data/results_tables/planning/' + test_set + '.tex'
		generate_planning_results_table(test_set, results, tex_file_path)
	

def generate_planning_results_table(test_set, results, tex_file_path):
	
	f = open(tex_file_path, 'w')
	
	write_script_size(f)
	write_begin_long_table(f,8) # there are 8 columns
	#write_begin_adjustbox(f)
	write_hline(f)
	
	instance_name = bold_element('Instance')
	solver_name = bold_element('Solver')
	upper_bound = bold_element('Upper Bound')
	lower_bound = bold_element('Lower Bound')
	gap = bold_element('Gap')
	cpu_time = bold_element('CPU Time')
	nodes_explored = bold_element('Nodes Explored')
	nodes_left = bold_element('Nodes Left')
	first_line = [instance_name, solver_name, upper_bound, lower_bound, gap, cpu_time, nodes_explored, nodes_left]
	write_line(f, first_line)
	write_hline(f)
	
	#test_set_line = [non_centered_multicolumn_element(test_set_label, 8)]
	#write_line(f, test_set_line)
	
	for (instance, solver, schedule) in results:
		
		problem_line = []
		problem_line.append(instance.name())
		problem_line.append(solver.name())
		
		#m = instance.m
		#w = [2**(m-i-1) for i in range(m)]
		#upper_bound = sum(w[i]*schedule.C[i] for i in range(m))
		#problem_line.append(int(upper_bound))
		problem_line.append(solver.get_string_value('upper_bound'))
		problem_line.append(solver.get_string_value('lower_bound'))
		problem_line.append(solver.get_string_value('relative_gap'))
		problem_line.append(solver.get_string_value('elapsed_time'))
		problem_line.append(solver.get_string_value('nodes_explored'))
		problem_line.append(solver.get_string_value('nodes_left'))
		
		write_line(f, problem_line)
		
		if solver.method == 'makespan': write_hline(f)
		
	#write_hline(f)
	
	#write_end_adjustbox(f)
	#write_vspace(f,'-0.2cm')
	write_caption(f, test_set.replace('_', ' ') + ' test set')
	write_label(f,'Table')
	write_end_long_table(f)
	f.close()


def generate_recovery_results_tables():
	
	test_set = 'challenging'
	
	planning_solvers = [
		Solver('weighting', 'cplex', 'planning'),
		#Solver('weighting', 'gurobi', 'planning'),
		Solver('branch_and_bound', None, 'planning'),
		Solver('highest_rank_objective', 'cplex', 'planning'),
		Solver('sequential', 'cplex', 'planning'),
		Solver('makespan', 'cplex', 'planning')
		#Solver('makespan', 'gurobi', 'planning')
	]
	
	perturbed_instances = []
	
	for planning_solver in planning_solvers:
		perturbed_instances += get_perturbed_instances(test_set, planning_solver)
	
	perturbed_instances.sort(key = perturbed_instance_keys)
	
	results = []
	
	for perturbed_instance in perturbed_instances:
		recovery_solver = Solver('milp', 'cplex', 'recovery')
		schedule = read_solution_file(perturbed_instance, recovery_solver)
		results.append((perturbed_instance, recovery_solver, schedule))
	
	tex_file_path = 'data/results_tables/recovery/' + test_set + '.tex'
	generate_recovery_results_table(test_set, results, tex_file_path)

def perturbed_instance_keys(perturbed_instance):
	return int(perturbed_instance.test_id.replace('test_', ''))


def generate_recovery_results_table(test_set, results, tex_file_path):
	
	f = open(tex_file_path, 'w')
	
	write_script_size(f)
	write_begin_long_table(f,4) # there are 8 columns
	#write_begin_adjustbox(f)
	write_hline(f)
	
	instance_name = bold_element('Instance')
	planning_solver_name = bold_element('Planning Solver')
	makespan = bold_element('Makespan')
	recovery_time = bold_element('Recovery Time')
	first_line = [instance_name, planning_solver_name, makespan, recovery_time]
	write_line(f, first_line)
	write_hline(f)
	
	#test_set_line = [non_centered_multicolumn_element(test_set_label, 8)]
	#write_line(f, test_set_line)
	
	for (instance, solver, schedule) in results:
		
		problem_line = []
		problem_line.append(instance.name())
		problem_line.append(instance.planning_solver.name())
		
		#m = instance.m
		#w = [2**(m-i-1) for i in range(m)]
		#upper_bound = sum(w[i]*schedule.C[i] for i in range(m))
		#problem_line.append(int(upper_bound))
		problem_line.append(solver.get_string_value('upper_bound'))
		problem_line.append(solver.get_string_value('elapsed_time'))
		
		write_line(f, problem_line)
		
		if instance.planning_solver.method == 'makespan': write_hline(f)
		
	#write_hline(f)
	
	#write_end_adjustbox(f)
	#write_vspace(f,'-0.2cm')
	write_caption(f, test_set.replace('_', ' ') + ' test set')
	write_label(f,'Table')
	write_end_long_table(f)
	f.close()

