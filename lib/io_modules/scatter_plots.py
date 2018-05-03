from __future__ import division
from recovered_solution_files import get_recovered_solutions
from test_files import get_instances
from ..problem_classes.solver import Solver
from recovered_instances_list import read_recovered_instances_list

import numpy as np
import matplotlib.pyplot as plt

def produce_scatter_plots():
	
	#methods = ['binding', 'flexible']
	
	method = 'flexible'
	commercial_tool = 'cplex'
	stage = 'recovery'
	recovery_solver = Solver(method, commercial_tool, stage)
	
	#test_sets = ['wellformed/moderate',
		#'wellformed/intermediate',
		#'wellformed/hard',
		#'degenerate/moderate',
		#'degenerate/intermediate'
		#] 
	
	#test_set = 'degenerate/intermediate'
	test_set = 'wellformed'
	
	#instances = get_instances(test_set)
	instances = read_recovered_instances_list(test_set + '/moderate')
	instances += read_recovered_instances_list(test_set + '/intermediate')
	
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
	

	SMALL_SIZE = 18
	MEDIUM_SIZE = 18
	BIGGER_SIZE = 18

	plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
	plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
	plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
	plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
	plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
	plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
	
	plt.xlabel('Normalized planning weighted value')
	plt.ylabel('Normalized recovered makespan')
	#plt.show()
	
	f.savefig('data/scatter_plots/' + test_set.replace('/','_') + '_' + method + '.pdf')

# Given a vevtor v, everything is normalized w.r.t. the minimum value
def min_normalization(v):
	v_min = min(v)
	for i in range(len(v)):
		v[i] = v[i] / v_min