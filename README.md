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
