from random import uniform, normalvariate
from math import ceil, log
from ..io_modules.test_files import write_test_file
from ..problem_classes.instance import Instance 

def generate_degenerate_instances():
	
	for test_set in ['degenerate/moderate', 'degenerate/intermediate']:
		
		if test_set == 'degenerate/moderate': (machines, jobs) = moderate_test_set_parameters()
		if test_set == 'degenerate/intermediate': (machines, jobs) = intermediate_test_set_parameters()
		
		processing_time_generators = [('uniform', uniform_generator), ('normal', normal_generator), ('symmetric_normal', symmetric_normal_generator)]
		
		test_number = 1
		
		for m in machines:
			for n in jobs[m]:
				for (distribution, generating_function) in processing_time_generators:
					test_id = generate_test_id(test_set, test_number)
					p = generating_function(n, degenerate_encoding_number(m,n))
					generated_instance = Instance(test_id, test_set, distribution, m, n, degenerate_encoding_number(m,n), p)
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
	machines = [3, 4, 5, 6]
	jobs = dict()
	jobs[3] = [20, 25, 30, 35]
	jobs[4] = [25, 30, 35, 40] 
	jobs[5] = [30, 35, 40, 45] 
	jobs[6] = [35, 40, 45, 50]
	return (machines, jobs)

def intermediate_test_set_parameters():
	machines = [10, 12, 14, 16]
	jobs = dict()
	jobs[10] = [40, 50, 60, 70]
	jobs[12] = [45, 55, 65, 75] 
	jobs[14] = [55, 65, 75, 85] 
	jobs[16] = [60, 70, 80, 90]
	return (machines, jobs)

# The degenerate encoding number serves as q in the case of degenerate instance generation.
def degenerate_encoding_number(m, n):
	bits = int(ceil((log(m,2) / (m-1)) * n))
	#return m * (2 ** bits) 
	return 2 ** bits

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