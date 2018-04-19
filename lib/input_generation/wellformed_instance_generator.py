from random import uniform, normalvariate
from math import ceil
from ..io_modules.test_files import write_test_file
from ..problem_classes.instance import Instance 

def generate_wellformed_instances():
	
	for test_set in ['wellformed/moderate', 'wellformed/intermediate', 'wellformed/hard']:
		
		if test_set == 'wellformed/moderate': (machines, jobs, q_values) = moderate_test_set_parameters()
		if test_set == 'wellformed/intermediate': (machines, jobs, q_values) = intermediate_test_set_parameters()
		if test_set == 'wellformed/hard': (machines, jobs, q_values) = hard_test_set_parameters()
		
		processing_time_generators = [('uniform', uniform_generator), ('normal', normal_generator), ('symmetric_normal', symmetric_normal_generator)]
		
		test_number = 1
		
		for m in machines:
			for n in jobs:
				for q in q_values:
					for (distribution, generating_function) in processing_time_generators:
						test_id = generate_test_id(test_set, test_number)
						p = generating_function(n, q)
						generated_instance = Instance(test_id, test_set, distribution, m, n, q, p)
						write_test_file(generated_instance)
						test_number += 1

# Given a test number, it returns a unique string id of the corresponding instance.
def generate_test_id(test_set, test_number):
	return test_set.replace('/','_') + '_' + 'instance' + str(test_number)

# Returns the moderate test set parameters.
# (i) number of machines
# (ii) number of jobs
# (iii) processing time parameter
def moderate_test_set_parameters(): 
	(machines, jobs, q_values) = ([3, 4, 5, 6], [20, 30, 40, 50], [100, 1000])
	return (machines, jobs, q_values)

def intermediate_test_set_parameters():
	(machines, jobs, q_values) = ([10, 12, 14, 16], [100, 200, 300, 400], [1000, 10000])
	return (machines, jobs, q_values)
      
def hard_test_set_parameters():
	(machines, jobs, q_values) = ([10, 15, 20, 25], [200, 300, 400, 500], [1000, 10000])
	return (machines, jobs, q_values)


# Processing times w.r.t. uniform distribution U(1,2,...,p_max)
def uniform_generator(n, q):
	p = []
	for j in range(n):
		p.append(int(ceil(uniform(0,q))))
	return p
  
# Processing times w.r.t. normal distribution N(q,q/3)
def normal_generator(n, q):
	p = []
	for j in range(n):
		val = int(round(normalvariate(q,q/3)))
		if val < 1:
			val = 1
		if val > 2*q:
			val = 2*q
		p.append(val)
	return p

# Choose the processing times w.r.t. symmetric of normal distribution N(q,q/3)
def symmetric_normal_generator(n, q):
	p = []
	for j in range(n):
		val = normalvariate(q,q/3)
		if val < q:
			val = q - val
		else:
			val = 2*q - (val - q)
		val=int(round(val))
		
		if val < 0:
			val = 0
		if val > 2*q:
			val = 2*q
		p.append(val)
	return p