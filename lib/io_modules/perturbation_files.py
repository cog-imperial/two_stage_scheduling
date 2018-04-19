from ..problem_classes.perturbation import Perturbation

def write_perturbation_file(instance, perturbations):
	
	f = open(perturbation_file_path(instance), 'w')
	
	for perturbation in perturbations:
		f.write(perturbation.category)
		for parameter in perturbation.parameters:
			f.write(white_space())
			f.write(str(parameter))
		f.write(new_line())
	
	f.close()

def read_perturbation_file(instance):
	
	f = open(perturbation_file_path(instance), 'r')
	
	perturbations = []
	for line in f:
		words = line.split(' ')
		category = words[0] + white_space() + words[1]
		parameters = [int(word) for word in words[2:]]
		perturbations.append(Perturbation(category, parameters))
	
	f.close()
	
	return perturbations

# Helper functions

def perturbation_file_path(instance):
	return 'data/inputs/perturbations/' + instance.test_set + '/' + instance.test_id + '.prt'

def new_line():
	return '\n'

def white_space():
	return ' '