from __future__ import division, print_function
from math import log
from subprocess import call
from ..problem_classes.solver import Solver
from ..io_modules.test_files import get_instances
from ..io_modules.perturbed_test_files import get_perturbed_instances
from ..io_modules.solution_files import read_solution_file
import os

def plot_planning_performance_profiles():
	
	# A performance profile is generated for each of the following test sets.
	#test_sets = ['wellformed/moderate',
		#'wellformed/intermediate',
		#'wellformed/hard',
		#'degenerate/moderate',
		#'degenerate/intermediate'
		#]
	
	test_set = 'wellformed/intermediate'
	
	# A performance profile is generated for each of the following metrics.
	#metrics = ['elapsed_time', 'upper_bound']
	
	metric = 'upper_bound'
	
	# A performance profile plots a line for each of the following solvers.
	solvers = [
		Solver('branch_and_bound', None, 'planning'), 
		Solver('weighting', 'cplex', 'planning'), 
		Solver('weighting', 'gurobi', 'planning'), 
		Solver('sequential', 'cplex', 'planning'),
		Solver('highest_rank_objective', 'cplex', 'planning') 
	]
	
	tex_file_path = 'data/performance_profiles/' + test_set + '/' + test_set.replace('/','_') + '_' + metric + '.tex'
	instances = get_instances(test_set)
	plot_planning_performance_profile(test_set, instances, solvers, metric, tex_file_path)


# Thelw na ftiaxv mia lista me [(solver,values)] gia to metric pou me endiaferei.
#def plot_performance_profile(difficulty, data_type):
def plot_planning_performance_profile(test_set, instances, solvers, metric, tex_file_path):
	
	# setting the discretization for each value of \tau
	if metric == 'elapsed_time' : (scale, tau_init, tau_step, tau_margin) = ('log2', 0, 0.05, 0.5)
	if metric == 'upper_bound' and test_set == 'wellformed/moderate': (scale, tau_init, tau_step, tau_margin) = ('', 1, 0.0001, 0.0001)
	#if metric == 'upper_bound' and difficulty == 'moderate': (scale, tau_init, tau_step, tau_margin) = ('log2', 0, 0.01, 0.5)
	if metric == 'upper_bound' and test_set =='intermediate': (scale, tau_init, tau_step, tau_margin) = ('', 1, 0.0005, 0.001)
	if metric == 'upper_bound' and test_set =='hard': (scale, tau_init, tau_step, tau_margin) = ('', 1, 0.01, 0.005)
	
	#print(scale)
	
	solver_values = dict() 
	
	for instance in instances:
		for solver in solvers:
			
			schedule = read_solution_file(instance, solver) # solver statistics are stored in the solver object
			value = solver.get_value(metric)
			
			#print(solver.solver_name + ': ' + str(value))
			
			if metric == 'elapsed_time':
				
				if value < 0.01:
					value = 0.01
				
				if value < solver.time_limit:
					solver_values[(solver, instance)] = value
				else:
					solver_values[(solver, instance)] = float('inf')
			
			elif metric == 'upper_bound':
				m = instance.m
				w = [2**(m-i-1) for i in range(m)]
				value = sum(w[i]*schedule.C[i] for i in range(m))
				solver_values[(solver, instance)] = value
			
			else:
				solver_values[(solver, instance)] = value
			
	for instance in instances:
		print(instance.test_id)
		
		for solver in solvers:
			print(solver.name() + ': ' + str(solver_values[(solver, instance)]))
			
		print()
	
	def f(x,scale):
		if scale == 'log2':
			return log(x,2)
		else:
			return x
	
	solver_ratios = dict()
	global_failures = 0
	all_solvers_failure = dict()
	
	for instance in instances:
		
		min_value = min( [solver_values[(solver, instance)] for solver in solvers] )
		all_solvers_failure[instance] = min_value == float('inf')
		
		if not all_solvers_failure[instance]:
			for solver in solvers:
				solver_ratios[(solver, instance)] = f( solver_values[(solver, instance)] / min_value, scale)
		else: 
			global_failures += 1
	
	#for instance in instances:
		#print(instance.test_id)
		
		#for solver in solvers:
			#print(solver.solver_name + ': ' + str(solver_ratios[(solver, instance)]))
			
		#print()
	
	solver_profiles = dict()
	tau_values = []
	
	all_distinct_ratios = set([value for value in solver_ratios.values() if value != float('inf')])
	max_tau = max(all_distinct_ratios) 
	
	str_max_tau = str(max_tau + (max_tau - tau_init)/24)
	
	if scale != 'log2':
		if str(max_tau + 5*tau_step)[::-1].find('.') > 4: # if the number of digits is large, then round to the 4 most important
			str_max_tau = "%.4f" % max_tau
		scale = '[' + str(tau_init) + ',' + str_max_tau + ']'
	
	tau = tau_init
	j = 0 #counter for probabilities
	
	while tau <= max_tau:
		
		tau_values.append(tau)
		
		for solver in solvers:
			
			#print(solver.solver_name)
			
			solver_profiles[(solver, tau)] = 0
			
			for instance in instances:
				
				#print(instance.test_id)
				
				if not all_solvers_failure[instance]:
				
					if solver_ratios[(solver, instance)] <= tau: 
						solver_profiles[(solver, tau)] += 1 
			
			solver_profiles[(solver, tau)] /= float(len(instances))
			
		tau += tau_step    
		print(tau_step)
		#print(tau, 'vs', max_tau)
	
	#for tau in tau_values:
		#print('tau: ' + str(tau))
		#for solver in solvers:
			#print(solver_profiles[(solver, tau)])
		#print()
	
	colors =  ['red', 'blue', 'green!50!black', 'yellow!50!black', 'magenta', 'brown']
	
	#new_style = 'dash pattern={on 2pt off 1pt on 2pt off 1pt}'
	styles = ['solid', 'dashed', 'dotted', 'dashdotted', 'densely dotted', 'loosely dotted']
	
	plots = []
	i=0
	for solver in solvers:
		plots.append((colors[i], styles[i], [solver_profiles[(solver,tau)] for tau in tau_values], solver.name()))
		i += 1
		print(solver.name())
	
	#print(len(plots))
	
	#for (a, b, c, d) in plots:
		#print(a + ' ' + b + ' ' + str(len(c)) + ' ' + d)
	
	def add_tex_coordinates(tex, colour, style, grouped_results):
		print(r'\addplot[const plot, mark=none, %s, %s]' % (colour, style), file=tex)
		print(r'coordinates', file=tex)
		print(r'{', file=tex)
		print(r'('+ str(tau_init)+',0)', file=tex)
		last_ratio = 1
		last_rho = 1
		
		for tau, value in grouped_results:
			print(r'(%s, %s)' % (str(tau), str(value)), file=tex)
		print(r'};', file=tex)
		
	def add_can_solve_line(val, tau, tex, colour):
		print(r'\addplot[mark=triangle*, %s] coordinates {(1,%.15f) (%d,%.15f)};' % (colour,val,tau,val), file=tex)
		
	def add_tex_figure(tex):
		
		print(metric)
		caption_beginning = 'Performance profiles for the ' + test_set.replace('_', ' ') + ' test set with ' + str(solver.time_limit) + ' seconds timeout: ' + metric.replace('_', ' ') + 's on ' + scale + ' scale.'
		
		print(r'\begin{figure}', file=tex)
		print(r'\centering', file=tex)
		print(r'\begin{tikzpicture}', file=tex)
		
		print(r'\begin{axis}[legend pos=south east, xmin=' + str(tau_init - (max_tau - tau_init)/36) +', xmax=' + str_max_tau + ', ymin=0, ymax=1.01, width=\\textwidth, xlabel=$\\tau$, ylabel=$\\rho$, ', file=tex)
		if metric == 'upper_bound' and test_set == 'moderate':
			print(r'xtick={1,1.002,1.004, 1.006, 1.008}, xticklabels={1,1.002,1.004,1.006,1.008}, ytick={0,0.2,0.4,0.6,0.8,1}, ', file=tex)
		print(r']', file=tex)
		#print(r'\begin{axis}[legend pos=south east, xmin=0, ymin=0, ymax=1.01, width=\textwidth, xlabel=$\tau$, ylabel=$\rho$]', file=tex)
		
		for colour, style, profile, name in plots:
			add_tex_coordinates(tex, colour, style, zip(tau_values, profile))
			print(r'\addlegendentry{%s}' % name, file=tex)
		print(r'\end{axis}', file=tex)
		print(r'\end{tikzpicture}', file=tex)
		print(r'\caption{%s' % (caption_beginning), file=tex)
		for colour, style, profile, name in plots:
			if plots.index((colour, style, profile, name)) < len(plots) - 1:
				print('{\color{' + colour + '} ' + style + ': ' + name + '},', file=tex)
			else:
				print('{\color{' + colour + '} ' + style + ': ' + name + '}. }', file=tex)		
		print(r'\end{figure}', file=tex)
		
		
	#tex_file_path='easy_nodes_explored.tex'    
	with open(tex_file_path, 'w') as tex:
		print(r'\documentclass{article}', file=tex)
		print('', file=tex)
		print(r'\usepackage[lmargin=1in, rmargin=1in]{geometry}', file=tex)    
		print(r'\usepackage{amsmath, amssymb, amsthm}', file=tex)
		print(r'\usepackage{lmodern}', file=tex)
		print(r'\usepackage{tikz}', file=tex)
		print(r'\usepackage{pgfplots}', file=tex)
		print(r'\usepackage{color}', file=tex)
		print('')
		print(r'\begin{document}', file=tex)
		
		add_tex_figure(tex)
		
		print(r'\end{document}', file=tex)
	
	cwd = os.getcwd()
	os.chdir(os.path.dirname(tex_file_path))
	call(['pdflatex', test_set.replace('/','_') + '_' + metric + '.tex'])
	os.chdir(cwd)
	#print(tex_file_path)