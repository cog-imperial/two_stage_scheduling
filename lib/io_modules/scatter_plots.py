from __future__ import division
from recovered_solution_files import get_recovered_solutions
from test_files import get_instances
from ..problem_classes.solver import Solver

import numpy as np
import matplotlib.pyplot as plt

def produce_scatter_plots():
	
	#methods = ['binding', 'flexible']
	
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
	
	test_set = 'wellformed/moderate'
	
	instances = get_instances(test_set)
	
	normalized_weighted_values = []
	normalized_makespans = []
	
	for instance in instances:
		
		print(instance.test_id)
		
		recovered_solutions = get_recovered_solutions(instance, recovery_solver)
		
		weighted_values = []
		makespans = []
		
		for (schedule, upper_bound, elapsed_time, planning_weighted_value) in recovered_solutions:
			#print('Planning weighted value: ' + str(planning_weighted_value) + ', Upper bound: ' + str(upper_bound))
			#print('Total processing time: ' + str(sum(schedule.C[i] for i in range(len(schedule.C)))))
			weighted_values.append(planning_weighted_value)
			makespans.append(upper_bound)
		
		min_normalization(weighted_values)
		min_normalization(makespans)
		
		normalized_weighted_values += weighted_values
		normalized_makespans += makespans
		
		#print('')
	
	f = plt.figure()
	# Parameter s and alpha specify the size of the marker and alpha blending, respectively.
	plt.scatter(normalized_weighted_values, normalized_makespans, s = 10, alpha = 0.2)
	plt.xlim(0.97, 3.1)
	plt.ylim(0.9, 5.5)
	plt.xlabel('Normalized planning weighted value')
	plt.ylabel('Normalized recovered makespan')
	#plt.show()
	
	f.savefig('data/scatter_plots/' + test_set.replace('/','_') + '.pdf')

# Given a vevtor v, everything is normalized w.r.t. the minimum value
def min_normalization(v):
	v_min = min(v)
	for i in range(len(v)):
		v[i] = v[i] / v_min