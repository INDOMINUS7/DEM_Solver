#include <iostream>
#include <cmath>
#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <omp.h>
#include <chrono>

using namespace std;

const float GRAVITY = 9.81;

class Particle {
public:
    float x, y, vx, vy, radius, mass;
    char padding[64];  

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

    void handleParticleCollisions(vector<Particle>& particles, float dt) {
        int n = particles.size();
        vector<vector<float>> localFx(n, vector<float>(omp_get_max_threads(), 0.0f));
        vector<vector<float>> localFy(n, vector<float>(omp_get_max_threads(), 0.0f));

        #pragma omp parallel for schedule(dynamic)
        for (int i = 0; i < n; ++i) {
            int tid = omp_get_thread_num();

            for (int j = i + 1; j < n; ++j) {
                float dx = particles[j].x - particles[i].x;
                float dy = particles[j].y - particles[i].y;
                float dist = sqrt(dx * dx + dy * dy);
                float overlap = particles[i].radius + particles[j].radius - dist;

                if (overlap > 0) {
                    float forceMagnitude = springConstant * overlap;

                    float fx = forceMagnitude * (dx / dist);
                    float fy = forceMagnitude * (dy / dist);

                    localFx[i][tid] -= fx;
                    localFy[i][tid] -= fy;
                    localFx[j][tid] += fx;
                    localFy[j][tid] += fy;
                }
            }
        }

        // Aggregate forces across threads and apply to particles
        for (int i = 0; i < n; ++i) {
            float totalFx = 0.0f, totalFy = 0.0f;

            #pragma omp parallel for reduction(+:totalFx,totalFy)
            for (int tid = 0; tid < omp_get_max_threads(); ++tid) {
                totalFx += localFx[i][tid];
                totalFy += localFy[i][tid];
            }

            particles[i].applyForce(totalFx, totalFy, dt);
        }
    }
};

class Simulation {
public:
    vector<Particle> particles;
    Box box;
    float timeStep;

    Simulation(vector<Particle> p, Box b, float dt) : particles(move(p)), box(b), timeStep(dt) {}

    vector<vector<float>> runStep() {
        auto start1 = chrono::high_resolution_clock::now();
        #pragma omp parallel for
        for (int i = 0; i < particles.size(); ++i) {
            particles[i].applyGravity(timeStep);
            box.handleWallCollisions(particles[i], timeStep);
        }
        auto end1 = chrono::high_resolution_clock::now();
        chrono::duration<double> elapsed1 = end1 - start1;
        ///cout << "Loop 1 (Wall collisions): " << elapsed1.count() << " seconds.\n";

        auto start2 = chrono::high_resolution_clock::now();
        box.handleParticleCollisions(particles, timeStep);
        auto end2 = chrono::high_resolution_clock::now();
        chrono::duration<double> elapsed2 = end2 - start2;
        //cout << "Loop 2 (Particle collisions): " << elapsed2.count() << " seconds.\n";

        auto start3 = chrono::high_resolution_clock::now();
        #pragma omp parallel for
        for (int i = 0; i < particles.size(); ++i) {
            particles[i].updatePosition(timeStep);
        }
        auto end3 = chrono::high_resolution_clock::now();
        chrono::duration<double> elapsed3 = end3 - start3;
        //cout << "Loop 3 (Position updates): " << elapsed3.count() << " seconds.\n";

        vector<vector<float>> positions;
        for (auto &particle : particles) {
            positions.push_back({particle.x, particle.y});
        }

        return positions;
    }

    double measureExecutionTime(int numSteps) {
        auto start = chrono::high_resolution_clock::now();

        for (int i = 0; i < numSteps; ++i) {
            runStep();
        }

        auto end = chrono::high_resolution_clock::now();
        chrono::duration<double> elapsed = end - start;

        return elapsed.count();
    }
};

namespace py = pybind11;

PYBIND11_MODULE(SIXTH_TOY_PROBLEM, m) {
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
        .def("runStep", &Simulation::runStep)
        .def("measureExecutionTime", &Simulation::measureExecutionTime);
}
