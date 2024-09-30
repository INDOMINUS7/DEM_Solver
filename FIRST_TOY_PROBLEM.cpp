#include <iostream>
#include <cmath>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

const float GRAVITY = 9.81;

class Particle {
public:
    float x, y;
    float vx, vy;
    float radius;

    Particle(float startX, float startY, float startVx, float startVy, float r)
        : x(startX), y(startY), vx(startVx), vy(startVy), radius(r) {}

    void updatePosition(float dt) {
        x += vx * dt;
        y += vy * dt;  
    }

    void applyGravity(float dt) {
        vy -= GRAVITY * dt;  
    }
};

class Box {
public:
    float width, height;

    Box(float w, float h) : width(w), height(h) {}

    void handleCollisions(Particle &particle) {
        if (particle.x - particle.radius <= 0) {
            particle.vx = fabs(particle.vx);
            particle.x = particle.radius;
        } else if (particle.x + particle.radius >= width) {
            particle.vx = -fabs(particle.vx);
            particle.x = width - particle.radius;
        }

        if (particle.y - particle.radius <= 0) {
            particle.vy = fabs(particle.vy);
            particle.y = particle.radius;
        } else if (particle.y + particle.radius >= height) {
            particle.vy = -fabs(particle.vy);
            particle.y = height - particle.radius;
        }
    }
};

class Simulation {
public:
    Particle particle;
    Box box;
    float timeStep;

    Simulation(Particle p, Box b, float dt) : particle(p), box(b), timeStep(dt) {}

    std::vector<float> runStep() {
        particle.applyGravity(timeStep);   // Applying gravity first to change velocity
        particle.updatePosition(timeStep); // Then update position based on new velocity
        box.handleCollisions(particle);
        return {particle.x, particle.y};
    }
};

namespace py = pybind11;

PYBIND11_MODULE(FIRST_TOY_PROBLEM, m) {
    py::class_<Particle>(m, "Particle")
        .def(py::init<float, float, float, float, float>())
        .def("updatePosition", &Particle::updatePosition)
        .def("applyGravity", &Particle::applyGravity)
        .def_readwrite("x", &Particle::x)
        .def_readwrite("y", &Particle::y)
        .def_readwrite("vx", &Particle::vx)
        .def_readwrite("vy", &Particle::vy)
        .def_readwrite("radius", &Particle::radius);

    py::class_<Box>(m, "Box")
        .def(py::init<float, float>())
        .def("handleCollisions", &Box::handleCollisions)
        .def_readwrite("width", &Box::width)
        .def_readwrite("height", &Box::height);

    py::class_<Simulation>(m, "Simulation")
        .def(py::init<Particle, Box, float>())
        .def("runStep", &Simulation::runStep);
}
