from __future__ import division
from random import randint
from ..problem_classes.instance import perturbe_instance
from ..problem_classes.solver import Solver
from ..problem_classes.perturbation import Perturbation
from ..io_modules.test_files import get_instances
from ..io_modules.solution_files import read_solution_file
from ..io_modules.perturbation_files import write_perturbation_file
#from ..io_modules.perturbed_test_files import write_perturbed_test_file
from math import ceil


def generate_perturbations():
	
	# Every instance is perturbed.
	test_sets = ['wellformed/moderate',
		'wellformed/intermediate',
		'wellformed/hard',
		'degenerate/moderate',
		'degenerate/intermediate'
		]
	
	for test_set in test_sets:  
		
		machine_perturbators = [
			machine_activation,
			machine_failure
		]
		
		job_perturbators = [
			job_addition, 
			job_cancellation, 
			processing_time_augmentation, 
			processing_time_reduction,
		]
		
		instances = get_instances(test_set)
		perturbe(instances, machine_perturbators, job_perturbators)


def perturbe(instances, machine_perturbators, job_perturbators):
	
	for instance in instances:
		
		perturbations = []
		
		# The degree up to which the instance is perturbed.
		# Number of perturbations as a function of the input parameters.
		np = int(ceil(instance.n * 0.2))
		mp = int(ceil(instance.m * 0.2))
		
		for i in range(mp):
			machine_perturbator = machine_perturbators[randint(0,1)]
			machine_perturbation = machine_perturbator(instance)
			perturbations.append(machine_perturbation)
		
		for j in range(np):
			job_perturbator = job_perturbators[randint(0,3)] # Random selection of perturbation function
			job_perturbation = job_perturbator(instance) # Generate perturbation at random
			perturbations.append(job_perturbation)
		
		write_perturbation_file(instance, perturbations)


def job_addition(inst):
	processing_time = randint(0, 2*inst.q+1)
	(category, parameters) = ('Job addition', [processing_time])
	return Perturbation(category, parameters)

def job_cancellation(inst):
	job = randint(0, inst.n-1)
	(category, parameters) = ('Job cancellation', [job])
	return Perturbation(category, parameters)

def processing_time_augmentation(inst):
	job = randint(0, inst.n-1)
	processing_time = randint(inst.p[job]+1, 2*inst.q+1)
	(category, parameters) = ('Processing-time augmentation', [job, processing_time])
	return Perturbation(category, parameters)
      
def processing_time_reduction(inst):
	job = randint(0, inst.n-1)
	if inst.p[job] > 1:
		processing_time = randint(1, inst.p[job]-1)
		(category, parameters) = ('Processing-time reduction', [job, processing_time])
		return Perturbation(category, parameters)
	else:
		(category, parameters) = ('Job cancellation', [job])
		return Perturbation(category, parameters)

def machine_activation(inst):
	(category, parameters) = ('Machine activation', [])
	return Perturbation(category, parameters)

def machine_failure(inst):
	machine = randint(0, inst.m-1)
	(category, parameters) = ('Machine failure', [machine])
	return Perturbation(category, parameters)