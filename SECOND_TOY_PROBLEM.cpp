#include <iostream>
#include <cmath>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

const float GRAVITY = 9.81;  // Gravity constant

class Particle {
public:
    float x, y;
    float vx, vy;
    float radius;
    float mass;

    // Constructor
    Particle(float startX, float startY, float startVx, float startVy, float r, float m)
        : x(startX), y(startY), vx(startVx), vy(startVy), radius(r), mass(m) {}

    // Apply force based on Hooke's law (F = ma)
    void applyForce(float fx, float fy, float dt) {
        vx += (fx / mass) * dt;
        vy += (fy / mass) * dt;
    }

    // Update position using Verlet integration
    void updatePosition(float dt) {
        x += vx * dt;
        y += vy * dt;
    }

    // Apply gravity to the vertical velocity
    void applyGravity(float dt) {
        vy -= GRAVITY * dt;
    }
};

class Box {
public:
    float width, height;
    float springConstant;  // Hooke's law constant

    // Constructor
    Box(float w, float h, float k) : width(w), height(h), springConstant(k) {}

    // Handle collisions with walls using Hooke's law for restoring force
    void handleCollisions(Particle &particle, float dt) {
        float overlap, force;

        // Check collision with the left wall
        if (particle.x - particle.radius < 0) {
            overlap = particle.radius - particle.x;
            force = springConstant * overlap;
            particle.applyForce(force, 0, dt);  // Push the particle to the right
        }

        // Check collision with the right wall
        if (particle.x + particle.radius > width) {
            overlap = particle.x + particle.radius - width;
            force = springConstant * overlap;
            particle.applyForce(-force, 0, dt);  // Push the particle to the left
        }

        // Check collision with the bottom wall
        if (particle.y - particle.radius < 0) {
            overlap = particle.radius - particle.y;
            force = springConstant * overlap;
            particle.applyForce(0, force, dt);  // Push the particle upward
        }

        // Check collision with the top wall
        if (particle.y + particle.radius > height) {
            overlap = particle.y + particle.radius - height;
            force = springConstant * overlap;
            particle.applyForce(0, -force, dt);  // Push the particle downward
        }
    }
};

class Simulation {
public:
    Particle particle;
    Box box;
    float timeStep;

    // Constructor
    Simulation(Particle p, Box b, float dt) : particle(p), box(b), timeStep(dt) {}

    // Run a single time step of the simulation
    std::vector<float> runStep() {
        particle.applyGravity(timeStep);  // Apply gravity to the particle
        box.handleCollisions(particle, timeStep);  // Handle any collisions with the box
        particle.updatePosition(timeStep);  // Update the particle's position
        return {particle.x, particle.y};  // Return the updated position
    }
};

namespace py = pybind11;

// Expose the classes and functions to Python using pybind11
PYBIND11_MODULE(SECOND_TOY_PROBLEM, m) {
    py::class_<Particle>(m, "Particle")
        .def(py::init<float, float, float, float, float, float>())
        .def("updatePosition", &Particle::updatePosition)
        .def("applyGravity", &Particle::applyGravity)
        .def_readwrite("x", &Particle::x)
        .def_readwrite("y", &Particle::y)
        .def_readwrite("vx", &Particle::vx)
        .def_readwrite("vy", &Particle::vy)
        .def_readwrite("radius", &Particle::radius);

    py::class_<Box>(m, "Box")
        .def(py::init<float, float, float>())
        .def("handleCollisions", &Box::handleCollisions)
        .def_readwrite("width", &Box::width)
        .def_readwrite("height", &Box::height)
        .def_readwrite("springConstant", &Box::springConstant);

    py::class_<Simulation>(m, "Simulation")
        .def(py::init<Particle, Box, float>())
        .def("runStep", &Simulation::runStep);
}
