#include <iostream>
#include <cmath>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
using namespace std;
const float GRAVITY = 9.81;

class Particle {
public:
    float x, y, vx, vy, radius, mass;

    Particle(float startX, float startY, float startVx, float startVy, float r, float m)
        : x(startX), y(startY), vx(startVx), vy(startVy), radius(r), mass(m) {}

    void applyForce(float fx, float fy, float dt) {
        vx += (fx / mass) * dt;
        vy += (fy / mass) * dt;
    }

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
    float width, height, springConstant;

    Box(float w, float h, float k) : width(w), height(h), springConstant(k) {}

    void handleCollisions(Particle &particle, float dt) {
        float overlap, force;

        if (particle.x - particle.radius < 0) {
            overlap = particle.radius - particle.x;
            force = springConstant * overlap;
            particle.applyForce(force, 0, dt);
        }

        if (particle.x + particle.radius > width) {
            overlap = particle.x + particle.radius - width;
            force = springConstant * overlap;
            particle.applyForce(-force, 0, dt);
        }

        if (particle.y - particle.radius < 0) {
            overlap = particle.radius - particle.y;
            force = springConstant * overlap;
            particle.applyForce(0, force, dt);
        }

        if (particle.y + particle.radius > height) {
            overlap = particle.y + particle.radius - height;
            force = springConstant * overlap;
            particle.applyForce(0, -force, dt);
        }
    }
};

class Simulation {
public:
    Particle particle1, particle2;
    Box box;
    float timeStep;

    Simulation(Particle p1, Particle p2, Box b, float dt) : particle1(p1), particle2(p2), box(b), timeStep(dt) {}

    void handleParticleCollisions(float dt) {
        float dx = particle2.x - particle1.x;
        float dy = particle2.y - particle1.y;
        float distance = std::sqrt(dx * dx + dy * dy);
        float overlap = (particle1.radius + particle2.radius) - distance;

        if (overlap > 0) {
            float force = box.springConstant * overlap;

            float nx = dx / distance;
            float ny = dy / distance;

            particle1.applyForce(-force * nx, -force * ny, dt);
            particle2.applyForce(force * nx, force * ny, dt);
        }
    }

    vector<std::vector<float>> runStep() {
        particle1.applyGravity(timeStep);
        particle2.applyGravity(timeStep);

        box.handleCollisions(particle1, timeStep);
        box.handleCollisions(particle2, timeStep);

        handleParticleCollisions(timeStep);

        particle1.updatePosition(timeStep);
        particle2.updatePosition(timeStep);

        return {{particle1.x, particle1.y}, {particle2.x, particle2.y}};
    }
};

namespace py = pybind11;

PYBIND11_MODULE(FOURTH_TOY_PROBLEM, m) {
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
        .def(py::init<Particle, Particle, Box, float>())
        .def("runStep", &Simulation::runStep);
}
