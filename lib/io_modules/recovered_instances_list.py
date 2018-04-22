from test_files import read_test_file

def write_recovered_instances_list(selected_instances):

	f = open('data/inputs/recovered_instances.txt', 'w')
	
	for instance in selected_instances:
		f.write(instance.test_set + ' ' + instance.test_id + '\n')
	
	f.close()

def read_recovered_instances_list(test_set_parameter):
	
	recovered_instances_list = []
	
	with open('data/inputs/recovered_instances.txt', 'r') as recovered_instances_list_file:
		for line in recovered_instances_list_file:
			test_set = line.split(' ')[0]
			test_id = line.split(' ')[1].split('\n')[0]
			instance = read_test_file(test_id, test_set)
			if test_set == test_set_parameter:
				recovered_instances_list.append(instance)
	
	return recovered_instances_list