from os import listdir
from ..problem_classes.instance import Instance

def write_test_file(instance):
	
	f = open(test_file_path(instance.test_id, instance.test_set), 'w')
	
	f.write('m=' + str(instance.m) + '\n')
	f.write('n=' + str(instance.n) + '\n')
	f.write('q=' + str(instance.q) + '\n')
	f.write('distribution ' + instance.distribution + '\n')
	
	for j in range(instance.n):
		f.write('p[' + str(j) + ']=' + str(instance.p[j]) + '\n')
	
	f.close()


def read_test_file(test_id, test_set):
	
	f = open(test_file_path(test_id, test_set), 'r')
	
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
	
	p = []
	for j in range(n):
		line = f.readline()
		line = line[2+len(str(j))+2:]
		p.append(int(line))
	
	f.close()
	
	return Instance(test_id, test_set, distribution, m, n, q, p)

def test_file_path(test_id, test_set):
	return 'data/inputs/instances/' + test_set + '/' + test_id + '.dat'

def test_set_path(test_set):
	return 'data/inputs/instances/' + test_set

def get_instances(test_set):
	
	path = test_set_path(test_set)
	test_files = listdir(path)
	test_ids = [test_file.replace('.dat', '') for test_file in test_files]
	test_ids.sort(key = test_id_keys)
	
	instances = []
	
	for test_id in test_ids:
		instance = read_test_file(test_id, test_set)
		instances.append(instance)
	
	return instances

# Used for sorting tests in decreasing order of their number.
def test_id_keys(test_id):
	if 'wellformed_moderate' in test_id: test_no = int(test_id.replace('wellformed_moderate_instance',''))
	if 'wellformed_intermediate' in test_id: test_no = int(test_id.replace('wellformed_intermediate_instance',''))
	if 'wellformed_hard' in test_id: test_no = int(test_id.replace('wellformed_hard_instance',''))
	if 'degenerate_moderate' in test_id: test_no = int(test_id.replace('degenerate_moderate_instance',''))
	if 'degenerate_intermediate' in test_id: test_no = int(test_id.replace('degenerate_intermediate_instance',''))
	return test_no