from random import randint
from ..io_modules.test_files import get_instances
from ..io_modules.recovered_instances_list import write_recovered_instances_list, read_recovered_instances_list

def select_perturbed_instances():
	
	test_sets = [
		'wellformed/moderate',
		'wellformed/intermediate',
		'degenerate/moderate',
		'degenerate/intermediate',
		]
	
	selected_instances = []
	
	for test_set in test_sets:
		instances = instance_selection(test_set)
		for instance in instances:
			selected_instances.append(instance)
	
	write_recovered_instances_list(selected_instances)
	
	selected_instances = read_recovered_instances_list()
	for instance in selected_instances:
		print(instance.test_set + ' ' + instance.test_id)
	
def instance_selection(test_set):
	instances = get_instances(test_set)
	
	selected_instances = []
	
	while len(selected_instances) < 5:
		inst = randint(0,len(instances)-1)
		if instances[inst] not in selected_instances:
			selected_instances.append(instances[inst])
	
	return selected_instances