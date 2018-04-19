from __future__ import division
from pyomo.environ import *
from pyomo.opt import SolverFactory
from ...problem_classes.schedule import Schedule
from ...io_modules.log_files import read_nodes, log_file


def weighting_solve(instance, solver):
   
	M = 2
	w = [ M**(instance.m-i-1) for i in range(instance.m)]
	
	model = AbstractModel()
	
	# Parameter: number of machines
	model.m = Param(within = NonNegativeIntegers, initialize = instance.m)
	
	# Parameter: number of jobs
	model.n = Param(within = NonNegativeIntegers, initialize = instance.n)
	
	# Parameter: set of machines
	model.M = RangeSet(0, model.m - 1) # set of hot streams
	
	# Parameter: set of machines
	model.J = RangeSet(0, model.n - 1) # set of hot streams
	
	# Parameter: processing times
	model.p = Param(model.J, within = NonNegativeReals, initialize = lambda model, j: instance.p[j])
	
	# Parameter: machine weights
	model.w = Param(model.M, within=PositiveReals, initialize = lambda model, i: w[i])
	
	# Variable: assignment of job j to machine i
	model.x = Var(model.M, model.J, within=Binary)
	
	# Variable: completion time of machine i
	model.C = Var(model.M, within = NonNegativeReals)

	# Objective: machine completion times weighted sum minimization
	def weighted_sum_rule(model):
		return sum(model.w[i]*model.C[i] for i in model.M)
	model.obj_value = Objective(rule = weighted_sum_rule, sense = minimize)
	
	def completion_times_order_rule(model, i):
		if i < model.m-1:
			return model.C[i] >= model.C[i+1]
		else:
			return Constraint.Skip
	model.completion_times_order_constraint = Constraint(model.M, rule = completion_times_order_rule)
	
	#def completion_time_lower_bound_rule(model, i):
		#return model.C[i] >= (1.0 / model.m - i)*sum(model.p[j] for j in model.J) - (1.0 / model.m - i)*sum(model.C[h] for h in model.M if h < i)
	#model.completion_time_lower_bound_constraint = Constraint(model.M, rule = completion_time_lower_bound_rule)
	
	# Constraint: machine completion time computation
	def machine_completion_computation_rule(model, i):
		return model.C[i] == sum(model.p[j]*model.x[i,j] for j in model.J)
	model.machine_completion_computation_constraint = Constraint(model.M, rule = machine_completion_computation_rule)
	
	# Constraint: job assignment
	def job_assignment_rule(model, j):
		return sum(model.x[i,j] for i in model.M) == 1
	model.job_assignment_constraint = Constraint(model.J, rule=job_assignment_rule)
    
	opt = SolverFactory(solver.commercial_tool)
	
	opt.options['threads'] = 1
	opt.options['timelimit'] = solver.time_limit
	opt.options['logfile'] = log_file(instance, solver)
	opt.options['mipgap'] = solver.gap_tolerance
	
	milp_instance = model.create_instance()
	results = opt.solve(milp_instance)
	
	epsilon = 10**(-5)
	y = [i for j in range(instance.n) for i in range(instance.m) if milp_instance.x[i,j].value >= 1 - epsilon]
	C = [milp_instance.C[i].value for i in range(instance.m)]
	
	upper_bound = results.problem.upper_bound
	lower_bound = results.problem.lower_bound
	relative_gap = (upper_bound - lower_bound) * 1.0 / upper_bound
	elapsed_time = results.solver.time
	(nodes_explored, nodes_left) = read_nodes(instance, solver)
	
	schedule = Schedule(y, C)
	solver.set_results(upper_bound, lower_bound, relative_gap, elapsed_time, nodes_explored, nodes_left)
	
	return schedule
    
