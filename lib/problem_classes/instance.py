from math import ceil

class Instance:
	
	def __init__(self, test_id, test_set, distribution, m, n, q, p):
		
		self.test_id = test_id
		self.test_set = test_set
		self.distribution = distribution
		self.m = m
		self.n = n
		self.q = q
		self.p = p
		self. perturbed = 'False'
	
	#def set_recovery_parameters(self, bounded_migration_jobs, mu, g, failed_machines, planning_solver):
	def set_recovery_parameters(self, bounded_migration_jobs, mu, g, failed_machines):
		
		self.perturbed = 'True'
		self.bounded_migration_jobs = bounded_migration_jobs # list of already assigned jobs
		self.mu = mu
		#self.g = int(ceil(0.1*self.n)) # bound on migrations
		self.g = g
		self.failed_machines = failed_machines
		#self.planning_solver = planning_solver
	
	def partial_schedule_completion_times(self):
		if self.perturbed:
			C = [0 for i in range(self.m)]
			for j in self.mu:
				C[self.mu[j]] += self.p[j]
			return C
	
	def free_job_processing_times(self): # The processing times of the jobs without fixed assignments
		if self.perturbed:
			free_jobs = dict()
			for j in range(self.n):
				if j not in self.mu:
					free_jobs[j] = self.p[j]
			return free_jobs
	
	#def copy(self):
		#return Instance(self.test_id, self.test_set, self.distribution, self.m, self.n, self.q, self.p)
	
	def name(self):
		return self.test_id.replace('_',' ')
	
	def __str__(self):
		return 'Test Id: ' + self.test_id + '\n' \
			+ 'Test Set: ' + self.test_set + '\n' \
			+ 'Machines: ' + str(self.m) + '\n' \
			+ 'Jobs: ' + str(self.n) + '\n' \
			+ 'Perturbed: ' + str(self.perturbed) + '\n'
			

#def perturbe_instance(instance, planning_solver, schedule, perturbations):
def perturbe_instance(instance, schedule, perturbations, method):
	
	#instance_copy = instance.copy()
	#solver_copy = solver.copy()
	#perturbations_copy = [perturbation.copy() for perturbation in perturbations]
	
	# The following sets store job and machine indices of the initial instance. 
	new_jobs = [] # Processing times of the new jobs
	cancelled_jobs = [] # Jobs which are cancelled
	modified_jobs = [] # Jobs whose processing time is modifed
	failed_machines = []
	new_machines = 0 # Number of new machines
	
	p = list(instance.p)
	
	# New jobs and machines are added by simple appending.
	# Processing time modifications update the corresponding components of vector instance.p.
	# Deleted jobs and machines are marked by adding them to the concelled jobs and failed machines lists. 
	for perturbation in perturbations:
		
		#print(perturbation.category, perturbation.parameters)
		
		if perturbation.category == 'Job addition':
			processing_time = perturbation.parameters[0]
			new_jobs.append(processing_time) # A new job can be placed into any machine for free.
		
		if perturbation.category == 'Job cancellation':
			job = perturbation.parameters[0]
			p[job] = 0
			cancelled_jobs.append(job)
		
		if perturbation.category == 'Processing-time augmentation' or perturbation.category == 'Processing-time reduction':
			job = perturbation.parameters[0]
			new_processing_time = perturbation.parameters[1]
			p[job] = new_processing_time # The processing time is modified here.
			modified_jobs.append(job)
		
		if perturbation.category == 'Machine failure':
			machine = perturbation.parameters[0]
			failed_machines.append(machine)
		
		if perturbation.category == 'Machine activation':
			new_machines += 1
	
	y = list(schedule.y)
	
	for j in range(instance.n):
		if y[j] in failed_machines:
			y[j] = None
	
	m = instance.m + new_machines
	
	# Addition of new jobs.
	n = instance.n + len(new_jobs)
	p += new_jobs # We add the processing times of the new jobs to the list of processing times.
	y += [None]*len(new_jobs) # The assignments of the new jobs are all initialized to None.
	
	# Set and dictionary of assigned jobs (to ignore None assignments) 
	bounded_migration_jobs = []
	mu = dict()
	for j in range(n):
		if y[j] != None:
			bounded_migration_jobs.append(j)
			mu[j] = y[j]
	
	if method == 'binding': g = 0
	if method == 'flexible': g = int(ceil(0.1*n))
	
	perturbed_instance = Instance(instance.test_id, instance.test_set, instance.distribution, m, n, instance.q, p)
	#perturbed_instance.set_recovery_parameters(bounded_migration_jobs, mu, g, failed_machines, planning_solver)
	perturbed_instance.set_recovery_parameters(bounded_migration_jobs, mu, g, failed_machines)
	
	return perturbed_instance

def get_machine(job, job_assignments):
	for (j,i) in job_assignments:
		if j == job:
			return i
