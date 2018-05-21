# Exact Lexicographic Scheduling and Approximate Rescheduling

Date: 27 February 2018  
Authors: Dimitrios Letsios, Ruth Misener  
Contact: `d.letsios@imperial.ac.uk`; `r.misener@imperial.ac.uk`

Source code of the methods proposed in Dimitrios Letsios, Ruth Misener, "Exact Lexicographic Scheduling and Approximate Rescheduling".


This repository contains the source code implementing exact, lexicographic optimization methods for the LexOpt scheduling problem and approximate recovery strategies to deal with instance perturbations. Furthermore, it includes a performance evaluation of exact lexicographic optimization methods and a simulation of two-stage robust scheduling with uncertainty.

The repository contains a collection of randomly generated, initial makespan problem instances. Planning phase solves every such instance according to one among various lexicographic optimization methods. Uncertainty realization perturbs every instance and generates a modified instance which is close to the initial one. Recovery phase solves the perturbed instance according to some recovery strategy. 

The repository contains:
1. a collection of benchmark, randomly generated, makespan problem instances,
2. a source code implementing the lexicographic optimization methods in Python 2.7.6 and Pyomo 4.4.1, 
3. a set of disturbances for each makespan problem instance,
4. a source code implementing the recovery strategies in Python 2.7.6 and Pyomo 4.4.1, and
5. the solutions obtained by an Intel Core i7-4790 CPU 3.60 GHz with 15.6 GB RAM and 64-bit Ubuntu 14.04.

## 1.  Performance Evaluation of Lexicographic Optimization Methods

The repository contains a source code evaluating the performance of exact, lexicographic optimization methods for the makespan scheduling problem. The evaluation consists of two steps: 1) generation of benchmark instances, and 2) application of the lexicographic optimization methods to the instances.

### 1.1  Benchmark Makespan Problem Instances

This repository contains a collection of 384 makespan problem instances. These instances have been generated randomly using the modules `wellformed_instance_generator.py` and `degenerate_instance_generator.py` in directory `lib/input_generation/`. Directory `data/inputs/instances` stores the generated instances. 

We have generated instances with different optimal solution structure (well-formed, degenerate), instance size (moderate, intermediate, hard), and probability distribution for generating the job processing times (uniform, normal, symmetric of the normal). In particular, we have generated 96 well-formed moderate, 96 well-formed intermediate, 96 well-formed hard, 48 degenerate moderate, and 48 degenerate intermediate instances of different sizes. For a given size, we have generated three different instances using each of the three probability distributions for processing time generation.

- Well-formed instances admit an optimal solution close to a perfectly balanced partition. Degenerate solutions have an optimal solution less balanced. In general, well-formed instances are easier to solve than degenerate instances. 

- We have generated instances by varying three parameters specifying the instance size: the number of machines, the number of jobs, and a processing time parameter. We classify the instances with respect to their size into three categories: moderate instances, intermediate instances, and hard instances.

- The processing times of a given instance have been generated using one among three probability distributions: uniform distribution, normal distribution, and symmetric of normal distribution.

An makespan problem instance consists of (i) a number m of machines, (ii) a number n of jobs, (iii) a processing time parameter q, (iv) a probability distribution for generating the processing times, and (v) a vector p of processing times (p[j] is the processing time of job j). This information is stored in a `.dat` file under the following format:

```
m=3
n=20
q=100
distribution uniform
p[0]=14
p[1]=77
p[2]=65
...
```

### 1.2  Lexicographic Optimization Methods

This repository provides a source code that produces a lexicographic optimal solution for the makespan scheduling problem using different exact methods. Directory `lib/planning/solvers` consists of a module for each implemented method. Directory `lib/planning` contains a handler that calls the lexicographic optimization methods for solving each problem instance. 

- Module `sequential.py` implements a sequential method decomposing the lexicographic optimization process into a sequence of mono-objective optimization problems, each one computing the value of one objective function in the lexicographic optimal solution.

- Module `weighting.py` implements a weighting method that formulates a lexicographic optimization problem as an equivalent single objective optimization problem whose objective function is a weighted sum of the original objectives.

- Module `highest_rank_objective.py` implements a highest-rank objective method optimizing the highest-rank objective (i.e. makespan) of the lexicographic scheduling problem, enumerating all optimal solutions, and selecting the lexicographically best one.

- Module `branch_and_bound.py` implements a lexicographic branch-and-bound method that explores the space of all feasible solutions and prunes suboptimal regions using vectorial bounds.

Directory `data/solutions/planning` stores the obtained results. For a given instance, the solution produced by each lexicographic optimization method is stored in `.sol` file. This file contains statistics of the solution process and the obtained solution. The following exact method statistics are stored: (i) elapsed time, (ii) nodes explored, (iii) nodes left, (iv) relative gap, (v) upper bound, and (vi) lower bound. If an entry does not apply for a given method, then the corresponding entry of the solution file stores a dash (i.e. “-”). The remaining entries store the machine completion times and the job assignments. In particular, C[i] is the completion time of machine i. The entry y[j]=i indicates an assignment of job j to machine i. A solution is stored in a `.sol` file under the following format:

```
Elapsed time: 0.29
Nodes explored: 15658
Nodes left: 16
Relative gap: 0.0
Upper bound: 5236
Lower bound: 5236
C[0]=748
C[1]=748
C[2]=748
y[0]=0
y[1]=1
y[2]=2
y[3]=2
...
```

## 2  Two-Stage Scheduling Simulation

The repository contains a source code that simulates a two-stage scheduling model and evaluates the impact of lexicographic optimality on the quality of the recovered solution. A simulation consists of four steps: 1) generation of initial makespan problem instances, 2) computation of a solution pool with multiple, diverse solutions for each instance, 3) perturbation of every instance, 4) recovery of each initial solution in the solution pool into a feasible solution for the perturbed instance. 

### 2.1  Initial Makespan Problem Instances

The initial makespan problem instances are the ones used for evaluating the performance of exact, lexicographic optimization methods. Section 1.1 “Benchmark Makespan Problem Instances” of the current repository description provides information on how to generate the instances. Directory data/inputs/instances stores these initial instances.

### 2.2  Solution pool

A solution pool generator has produced a set of diverse solutions for each initial instance using the CPLEX solution pool feature. Module `solution_pool_generator.py` generates the instances. Module `solution_pool_handler.py` triggers the solution pool generator for each instance. Both modules are stored in directory `lib/solution_pool_generation`.

Directory `data/solutions/pools` stores a solution pool for each initial instance. Each member of the solution pool is stored in a distinct `.sol` file. For instance, the 3rd solution pool member for the well formed, moderate instance5 is stored in a file named `3.sol` located in directory `data/solutions/pools/wellformed/moderate/well_formed_moderate_instance5`.

A solution, i.e. schedule, is associated with a weighted value. Furthermore, it specifies a completion time for each machine and a machine assignment for each job. The term C[i] corresponds to the completion time of machine i and the term y[j] specifies the machine which job j is assigned to. This information of a schedule in a solution pool is stored in a `.sol` file under the following format:

```
Weighted value: 2385.0
C[0]=341.0
C[1]=341.0
C[2]=339.0
y[0]=0
y[1]=1
y[2]=0
y[3]=2
...
```

### 2.3  Perturbations

A perturbator has generated a set of  random disturbances to each initial makespan problem instance. Module `perturbator.py` in directory `lib/input_generation` implements this generator producing machine perturbations and job perturbations.
 
- A machine perturbation is on among: (i) machine activation, or (ii) machine failure. A machine failure specifies the index of a deleted machine.

- A job perturbation is one among: (i) job addition, (ii) job cancellation, (iii) processing time augmentation, or processing time reduction. A job addition specifies the processing time of a new job. A job cancellation specifies the index of a deleted job. A processing time augmentation and a processing time reduction specify a job index and its new processing time.

The number of machine and job perturbations is a small fraction (10%) of the number of machines and jobs, respectively, in the initial instance. Directory `data/inputs/perturbations` stores the randomly generated set of perturbations for each initial instance. These perturbations are stored in a `.prt` file under the following format:

```
Machine failure 0
Job cancellation 9
Job cancellation 1
Job addition 25
Job cancellation 9
...
```

### 2.4  Recovery

This repository provides a source code that recovers an initial solution for an initial makespan problem instance which is perturbed into a feasible solution for the perturbed instance. Recovery takes into account the (i) initial instance, (ii) initial solution, (iii) perturbations. 

The repository implements two recovery strategies based on the number g of allowable modifications on the initial solution: (i) binding recovery, and (ii) flexible recovery. Binding decisions are variable values attainable from the initial solution in the recovery process. 

- Binding recovery maintains all binding decisions.

- Flexible recovery allows modifying a bounded number of binding decisions.

For each combination of initial instance, initial solution, perturbations and recovery strategy, the initial solution is recovered into a feasible solution for the perturbed problem instance. Directory `data/solutions/recovery` stores a recovered solutions.

## 3  Repository Contents

- `data`: 
  all input and output data (problem instances and obtained results).

  - `inputs`: 
    minimum makespan problem instances and perturbations

  - `solutions`: 
    computational results obtained via lexicographic optimization methods and recovery strategies

  - `performance_profiles`: 
    performance profiles of exact lexicographic optimization methods

  - `scatter_plots`: 
    scatter diagrams of the recovered solutions

  - `statistics`: 
    various solver statistics

- `lib`: 
  all implemented modules

  - `input_generation`: 
    source code for random instance generation

  - `planning`: 
    exact lexicographic optimization methods

  - `recovery`: 
    approximate recovery strategies
    
  - `solution_pool_generation`: 
    generation of diverse solutions
    
  - `problem_classes`: 
    essential classes representing problem objects
    
  - `io_modules`: 
    necessary modules for processing input and output files

- `main.py`: 
  root file performing all steps for obtaining the results 

## 4 References
