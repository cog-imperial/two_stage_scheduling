from os import listdir
from ..problem_classes.instance import Instance
from test_files import test_set_path

def write_perturbed_test_file(instance, solver):
	
	f = open(perturbed_test_file_path(instance.test_id, instance.test_set, solver), 'w')
	
	f.write('m=' + str(instance.m) + '\n')
	f.write('n=' + str(instance.n) + '\n')
	f.write('q=' + str(instance.q) + '\n')
	f.write('distribution ' + instance.distribution + '\n')
	
	if len(instance.failed_machines) != 0:
		failed_machines = str(instance.failed_machines)
		failed_machines = failed_machines.replace('[','')
		failed_machines = failed_machines.replace(']','')
		failed_machines = failed_machines.replace(',','')
		f.write('failed machines ' + failed_machines + '\n')
	else:
		f.write('failed machines -\n')
	
	f.write('g=' + str(instance.g) + '\n' )
	
	for j in range(instance.n):
		f.write('p[' + str(j) + ']=' + str(instance.p[j]) + '\n')
	
	for j in instance.mu:
		if instance.mu[j] != None:
			f.write('mu[' + str(j) + ']=' + str(instance.mu[j]) + '\n')
	
	f.close()


def read_perturbed_test_file(test_id, test_set, solver):
	
	f = open(perturbed_test_file_path(test_id, test_set, solver), 'r')
	
	# number of machines
	line = f.readline()
	m = int(line[2:len(line)-1])
	
	# number of jobs
	line = f.readline()
	n = int(line[2:len(line)-1])
	
	# processing time parameter
	line = f.readline()
	q = int(line[2:len(line)-1])
	
	# distribution
	line = f.readline()
	distribution = line[13:len(line)-1]
	
	# failed machines
	line = f.readline()
	if '-' not in line:
		string_failed_machines = line[16:len(line)-1]
		string_failed_machines = string_failed_machines.split(' ')
		failed_machines = [int(string_machine) for string_machine in string_failed_machines]
	else:
		failed_machines = []
	
	# migrations bound
	line = f.readline()
	g = int(line[2:len(line)-1])
	
	p = []
	for j in range(n):
		line = f.readline()
		line = line[2+len(str(j))+2:]
		p.append(int(line))
	
	mu = dict()
	line = f.readline()
	while line != '':
		(job, machine) = line.split('=') 
		job = job.split('[')[1]
		job = job.split(']')[0]
		job = int(job)
		machine = int(machine)
		mu[job] = machine
		line = f.readline()
	
	bounded_migration_jobs = []
	for j in mu:
		bounded_migration_jobs.append(j)
	
	f.close()
	
	instance = Instance(test_id, test_set, distribution, m, n, q, p)
	instance.set_recovery_parameters(bounded_migration_jobs, mu, g, failed_machines, solver)
	
	return instance

def perturbed_test_file_path(test_id, test_set, planning_solver):
	if planning_solver.commercial_tool:
		return 'data/inputs/perturbed_instances/' + planning_solver.method + '/' + test_set + '/perturbed_' + test_id + '_' + planning_solver.commercial_tool + '.dat'
	else:
		return 'data/inputs/perturbed_instances/' + planning_solver.method + '/' + test_set + '/perturbed_' + test_id + '.dat'

def get_perturbed_instances(test_set, planning_solver):
	
	path = test_set_path(test_set)
	test_files = listdir(path)
	test_ids = [test_file.replace('.dat', '') for test_file in test_files]
	test_ids.sort(key = test_id_keys)
	
	instances = []
	
	for test_id in test_ids:
		instance = read_perturbed_test_file(test_id, test_set, planning_solver)
		instances.append(instance)
	
	return instances

# Used for sorting tests in decreasing order of their number.
def test_id_keys(test_id):
	return int(test_id.replace('test_', ''))
