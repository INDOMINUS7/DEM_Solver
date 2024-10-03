#include <iostream>
#include <cmath>
#include <vector>
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

    void handleWallCollisions(Particle &particle, float dt) {
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

    void handleParticleCollisions(Particle &p1, Particle &p2, float dt) {
        float dx = p2.x - p1.x;
        float dy = p2.y - p1.y;
        float dist = sqrt(dx * dx + dy * dy);
        float overlap = p1.radius + p2.radius - dist;

        if (overlap > 0) {
            float forceMagnitude = springConstant * overlap;

            float fx = forceMagnitude * (dx / dist);
            float fy = forceMagnitude * (dy / dist);

            p1.applyForce(-fx, -fy, dt);
            p2.applyForce(fx, fy, dt);
        }
    }
};

class Simulation {
public:
    vector<Particle> particles;
    Box box;
    float timeStep;

    Simulation(vector<Particle> p, Box b, float dt) : particles(p), box(b), timeStep(dt) {}

    vector<vector<float>> runStep() {
        for (auto &particle : particles) {
            particle.applyGravity(timeStep);
            box.handleWallCollisions(particle, timeStep);
        }

        for (size_t i = 0; i < particles.size(); ++i) {
            for (size_t j = i + 1; j < particles.size(); ++j) {
                box.handleParticleCollisions(particles[i], particles[j], timeStep);
            }
        }

        for (auto &particle : particles) {
            particle.updatePosition(timeStep);
        }

        vector<vector<float>> positions;
        for (auto &particle : particles) {
            positions.push_back({particle.x, particle.y});
        }

        return positions;
    }
};

namespace py = pybind11;

PYBIND11_MODULE(FIFTH_TOY_PROBLEM, m) {
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
        .def("handleWallCollisions", &Box::handleWallCollisions)
        .def("handleParticleCollisions", &Box::handleParticleCollisions)
        .def_readwrite("width", &Box::width)
        .def_readwrite("height", &Box::height)
        .def_readwrite("springConstant", &Box::springConstant);

    py::class_<Simulation>(m, "Simulation")
        .def(py::init<vector<Particle>, Box, float>())
        .def("runStep", &Simulation::runStep);
}
