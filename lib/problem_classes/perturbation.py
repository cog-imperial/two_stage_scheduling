# Class modelling instance perturbations.
# Category: Perturbation type as String 
# Parameters: Perturbation parameters as list
# The following perturnations are considered:
# 1) Category: 'Job addition', Parameters: processing time
# 2) Category: 'Job cancellation', Parameters: job index
# 3) Category: 'Processing-time augmentation', Parameters: job index, new processing time
# 4) Category: 'Processing-time reduction', Parameters: job index, new processing time
# 5) Category: 'Machine activation', Parameters: (no parameters)
# 6) Category: 'Machine failure', Parameters: machine index

class Perturbation:
	
	def __init__(self, category, parameters):
		self.category = category
		self.parameters = parameters
	
	def copy(self):
		return Perturbation(str(self.category), list(self.parameters))
