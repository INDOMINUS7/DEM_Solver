# DEM_Solver
Particle-Wall Interaction Simulations
This repository contains two toy problems showcasing the simulation of a particle interacting with the walls of a box using two distinct models: a Hard Sphere Model and a Soft Sphere Model with Hooke's Law.

Overview

These simulations demonstrate how a single particle behaves when it collides with the boundaries of a 2D box, following different physical models. The simulations are implemented in C++ with Python bindings using pybind11, and the resulting animations can be visualized using Python and matplotlib.

Toy Problem 1: Hard Sphere Model
In this model, the particle is treated as a hard sphere. When the particle hits a wall, it reflects without any overlap or deformation. This idealized system assumes perfectly elastic collisions where energy is conserved, and the velocity is reversed upon impact.

Features:
Simple elastic collisions with no deformation.
Particle's position and velocity are updated based on direct velocity reversal upon wall impact.

Toy Problem 2: Soft Sphere Model (Linear Spring)
In this model, the particle is allowed to overlap with the walls, representing a soft interaction. When the particle overlaps with a wall, a restoring force is applied based on Hooke's Law (linear spring model). This force pushes the particle back out of the wall depending on the overlap and a spring constant, leading to more realistic physics.

Features:
Hooke’s Law-based interaction, where force is proportional to overlap.
Verlet integration for smoother and more accurate position updates.
Simulation of the effects of soft, elastic collisions without damping.

Toy Problem 3: Hertzian Contact Model (Nonlinear Spring)
In this model, the particle interacts with the walls of the box based on Hertzian contact mechanics. When the particle overlaps with a wall, a restoring force is applied proportional to the 3/2 power of the overlap. This nonlinear force model creates a stiffer response as the overlap increases, mimicking realistic contact mechanics for soft materials.

Features:

Hertzian contact mechanics, where force is proportional to the 3/2 power of overlap.
Integration of gravitational forces.
Simulation of nonlinear elastic collisions between the particle and the box walls for more accurate physical behavior.

Toy Problem 4: Particle-Particle Collision with Linear Spring
In this model, two particles are allowed to interact and collide within a rectangular box. The interaction is modeled using Hooke's Law (linear spring model) for both particle-wall and particle-particle collisions. When particles or particles with walls overlap, a restoring force is applied, proportional to the overlap. This creates realistic soft collisions between particles.

Features:

Hooke’s Law-based interaction, where force is proportional to the overlap.
Gravity is applied to both particles.
Simulation of particle-particle and particle-wall collisions using a linear spring model for restoring forces.

Toy Problem 5: Multiple Particle Interaction with Spring Forces
This problem expands on the previous soft sphere model, simulating the interaction between multiple particles within a rectangular box. Each particle is treated as a soft sphere, and their collisions are modeled using Hooke's Law (linear spring) both for particle-particle and particle-wall collisions. The particles experience gravity, and the restoring force is proportional to the overlap when collisions occur, ensuring smooth and elastic interactions.

Features:

Hooke’s Law-based particle-particle and particle-wall interactions.
Gravity applied to all particles.
Multiple particle simulation with elastic collisions using the spring constant to model soft collisions.
Verlet integration for smoother updates in particle positions.
