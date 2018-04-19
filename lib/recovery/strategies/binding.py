from __future__ import division
from pyomo.environ import *
from pyomo.opt import SolverFactory
from ...problem_classes.schedule import Schedule, order_lexicographically
from ...io_modules.log_files import recovery_log_file, read_nodes

def bindingly_recover(instance, sol_id, solver):
	
	model = AbstractModel()
	
	# Parameter: number of machines
	model.m = Param(within = NonNegativeIntegers, initialize = instance.m)
	
	# Parameter: number of jobs
	model.n = Param(within = NonNegativeIntegers, initialize = instance.n)
	
	# Parameter: allowable number of migrations
	model.g = Param(within = NonNegativeIntegers, initialize = instance.g)
	
	# Parameter: set of machines
	model.M = RangeSet(0, model.m - 1) # set of hot streams
	
	# Parameter: subset of failed machines
	model.MF = Set(within = model.M, initialize = instance.failed_machines)
	
	# Parameter: set of machines
	model.J = RangeSet(0, model.n - 1) # set of hot streams
	
	# Parameter: subset of assigned jobs
	model.JA = Set(within = model.J, initialize = instance.bounded_migration_jobs)
	
	# Parameter: processing times
	model.p = Param(model.J, within = NonNegativeIntegers, initialize = lambda model, j: instance.p[j])
	
	# Parameter: machines of assigned jobs
	model.mu = Param(model.JA, within = NonNegativeIntegers, initialize = lambda model, j: instance.mu[j])
	
	# Variable: assignment of job j to machine i
	model.x = Var(model.M, model.J, within=Binary)
	
	# Variable: completion time of machine i
	model.C = Var(model.M, within = NonNegativeIntegers)
	
	# Variable: makespan
	model.Cmax = Var(within = NonNegativeIntegers)
	
	# Objective: makespan minimization
	def makespan_rule(model):
		return model.Cmax
	model.obj_value = Objective(rule=makespan_rule, sense=minimize) 
	
	# Constraint: makespan computation
	def makespan_computation_rule(model, i):
		return model.Cmax >= model.C[i]
	model.makespan_computation_constraint = Constraint(model.M, rule = makespan_computation_rule)
	
	# Constraint: machine completion time computation
	def machine_completion_computation_rule(model, i):
		return model.C[i] == sum(model.p[j]*model.x[i,j] for j in model.J)
	model.machine_completion_computation_constraint = Constraint(model.M, rule = machine_completion_computation_rule)
	
	# Constraint: job assignment
	def job_assignment_rule(model, j):
		return sum(model.x[i,j] for i in model.M) == 1
	model.job_assignment_constraint = Constraint(model.J, rule=job_assignment_rule)
	
	# Constraint: bounded migrations
	def bounded_migrations_rule(model, j):
		return sum(sum(model.x[i,j] for i in model.M if model.mu[j]!=i) for j in model.JA) <= model.g
	model.bounded_migrations_constraint = Constraint(model.J, rule = bounded_migrations_rule)
	
	# Constraint: failed machines
	def failed_machines_rule(model, i):
		return sum(model.x[i,j] for j in model.J) == 0
	model.failed_machines_constraint = Constraint(model.MF, rule = failed_machines_rule)
	
	opt = SolverFactory(solver.commercial_tool)
	
	opt.options['threads'] = 1
	opt.options['timelimit'] = solver.time_limit
	opt.options['logfile'] = recovery_log_file(instance, solver, sol_id)
	opt.options['mipgap'] = solver.gap_tolerance
	
	milp_instance = model.create_instance()
	results = opt.solve(milp_instance)
	#instance.load(results)
	
	epsilon = 10**(-5)
	y = [i for j in range(instance.n) for i in range(instance.m) if milp_instance.x[i,j].value >= 1 - epsilon]
	C = [milp_instance.C[i].value for i in range(instance.m)]
	
	upper_bound = results.problem.upper_bound
	#lower_bound = results.problem.lower_bound
	#relative_gap = (upper_bound - lower_bound) * 1.0 / upper_bound
	elapsed_time = results.solver.time
	#(nodes_explored, nodes_left) = read_nodes(instance, solver)
	
	schedule = Schedule(y, C)
	schedule = order_lexicographically(instance, schedule)
	
	solver.set_recovery_results(upper_bound, elapsed_time)
	
	return schedule