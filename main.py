# MODULE IMPORTING

# Makespan problem instance generation
from lib.input_generation.wellformed_instance_generator import generate_wellformed_instances
from lib.input_generation.degenerate_instance_generator import generate_degenerate_instances

# Lexicographic makespan problem solving
from lib.planning.planning_handler import planning_solve

# Exact lexicographic methods performance profiles and results tables
from lib.io_modules.performance_profiles import plot_planning_performance_profiles
#from lib.io_modules.results_tables import generate_planning_results_tables

# Solution pool generation
from lib.solution_pool_generation.solution_pool_handler import produce_solution_pool

# Makespan problem instance disturbances generation
from lib.input_generation.perturbator import generate_perturbations

# Recovery strategies
from lib.recovery.recovery_handler import recovery_solve

# Recovery strategies scatter plots
from lib.io_modules.scatter_plots import produce_scatter_plots



# CODE EXECUTION

# Makespan problem instance generation
#generate_wellformed_instances()
#generate_degenerate_instances()

# Lexicographic makespan problem solving
#planning_solve()

# Exact lexicographic methods performance profiles and results tables
#plot_planning_performance_profiles()

# Multiple solutions generation
#produce_solution_pool()

# Perturbations generation
#generate_perturbations()

# Recovery
recovery_solve()

# Recovery strategies scatter plots
#produce_scatter_plots()