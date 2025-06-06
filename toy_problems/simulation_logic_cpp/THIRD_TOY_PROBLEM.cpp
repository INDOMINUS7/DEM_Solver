#include <iostream>
#include <cmath>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
using namespace std;
const float GRAVITY = 9.81;

class Particle {
public:
    float x, y, vx, vy, radius, mass;
    float youngModulus, poissonRatio;

    Particle(float startX, float startY, float startVx, float startVy, float r, float m, float E, float v)
        : x(startX), y(startY), vx(startVx), vy(startVy), radius(r), mass(m), youngModulus(E), poissonRatio(v) {}

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
    float width, height;
    float youngModulus, poissonRatio;

    Box(float w, float h, float E, float v) : width(w), height(h), youngModulus(E), poissonRatio(v) {}

    float calculateHertzianStiffness(float radius, float E, float v) {
        return (4.0f / 3.0f) * (E / (1.0f - v * v)) * sqrt(radius);
    }

    void handleCollisions(Particle &particle, float dt) {
        float overlap, force;
        float hertzianStiffness = calculateHertzianStiffness(particle.radius, particle.youngModulus, particle.poissonRatio);

        if (particle.x - particle.radius < 0) {
            overlap = particle.radius - particle.x;
            force = hertzianStiffness * pow(overlap, 1.5f);
            particle.applyForce(force, 0, dt);
        }

        if (particle.x + particle.radius > width) {
            overlap = particle.x + particle.radius - width;
            force = hertzianStiffness * pow(overlap, 1.5f);
            particle.applyForce(-force, 0, dt);
        }

        if (particle.y - particle.radius < 0) {
            overlap = particle.radius - particle.y;
            force = hertzianStiffness * pow(overlap, 1.5f);
            particle.applyForce(0, force, dt);
        }

        if (particle.y + particle.radius > height) {
            overlap = particle.y + particle.radius - height;
            force = hertzianStiffness * pow(overlap, 1.5f);
            particle.applyForce(0, -force, dt);
        }
    }
};

class Simulation {
public:
    Particle particle;
    Box box;
    float timeStep;

    Simulation(Particle p, Box b, float dt) : particle(p), box(b), timeStep(dt) {}

   vector<float> runStep() {
        particle.applyGravity(timeStep);
        box.handleCollisions(particle, timeStep);
        particle.updatePosition(timeStep);
        return {particle.x, particle.y};
    }
};

namespace py = pybind11;

PYBIND11_MODULE(THIRD_TOY_PROBLEM, m) {
    py::class_<Particle>(m, "Particle")
        .def(py::init<float, float, float, float, float, float, float, float>())
        .def("updatePosition", &Particle::updatePosition)
        .def("applyGravity", &Particle::applyGravity)
        .def_readwrite("x", &Particle::x)
        .def_readwrite("y", &Particle::y)
        .def_readwrite("vx", &Particle::vx)
        .def_readwrite("vy", &Particle::vy)
        .def_readwrite("radius", &Particle::radius);

    py::class_<Box>(m, "Box")
        .def(py::init<float, float, float, float>())
        .def("handleCollisions", &Box::handleCollisions)
        .def_readwrite("width", &Box::width)
        .def_readwrite("height", &Box::height);

    py::class_<Simulation>(m, "Simulation")
        .def(py::init<Particle, Box, float>())
        .def("runStep", &Simulation::runStep);
}
