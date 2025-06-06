#include <iostream>
#include <cmath>
#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <omp.h>
#include <chrono>
using namespace std;

const float GRAVITY = 9.81;
const float RESTITUTION_COEFF = 0.6;
const float MU_S = 0.7;
const float MU_K = 0.5;
const float SPRING_CONSTANT = 10000.0;
const float DAMPING_COEFF = 50.0;
const float VELOCITY_THRESHOLD = 100.0;
const float MIN_SEPARATION = 0.01;
const float ROLL_FRICTION_COEFF = 0.02;
const float ROT_RESTITUTION_COEFF = 0.5;
const float ANGULAR_DAMPING = 0.1;
const float PI = 3.14159265359;

class Particle {
public:
    float x, y, vx, vy, radius, mass;
    float theta, omega, I;

    Particle(float startX, float startY, float startVx, float startVy, float r, float m)
        : x(startX), y(startY), vx(startVx), vy(startVy), radius(r), mass(m), 
          theta(0.0f), omega(0.0f) {
        calculateMomentOfInertia();
    }

    void calculateMomentOfInertia() {
        I = 0.5f * mass * radius * radius;
    }

    void applyForce(float fx, float fy, float dt) {
        vx += (fx / mass) * dt;
        vy += (fy / mass) * dt;
    }

    void applyTorque(float torque, float dt) {
        omega += (torque / I) * dt;
        omega *= (1.0f - ANGULAR_DAMPING * dt);
    }

    void applyGravity(float dt) {
        vy -= GRAVITY * dt;
    }

    void applyRestitution(float normalX, float normalY) {
        float normalVel = vx * normalX + vy * normalY;
        float newNormalVel = -normalVel * RESTITUTION_COEFF;
        float deltaVx = (newNormalVel - normalVel) * normalX;
        float deltaVy = (newNormalVel - normalVel) * normalY;
        vx += deltaVx;
        vy += deltaVy;
    }

    void updatePosition(float dt) {
        x += vx * dt;
        y += vy * dt;
        theta += omega * dt;
        theta = fmod(theta, 2 * PI);
    }

    std::pair<float, float> getMarkerEndpoint() const {
        float endX = x + radius * cos(theta);
        float endY = y + radius * sin(theta);
        return {endX, endY};
    }
};

class Box {
public:
    float width, height, springConstant;

    Box(float w, float h, float k) : width(w), height(h), springConstant(k) {}

    void handleWallCollisions(Particle &particle, float dt) {
        float overlap;
        float normalForce;
        
        // Left wall
        if (particle.x - particle.radius < 0) {
            overlap = particle.radius - particle.x;
            normalForce = springConstant * overlap;
            float dampingForce = DAMPING_COEFF * particle.vx;
            float totalNormalForce = normalForce - dampingForce;
            
            if (overlap > MIN_SEPARATION) {
                particle.x = particle.radius + MIN_SEPARATION;
            }
            
            float frictionForce = 0.0f;
            if (abs(normalForce) > 1e-6) {
                frictionForce = -MU_K * abs(totalNormalForce) * sign(particle.vy);
                float torque = frictionForce * particle.radius;
                particle.applyTorque(torque, dt);
            }
            
            float rollingTorque = -ROLL_FRICTION_COEFF * abs(normalForce) * particle.radius * sign(particle.omega);
            particle.applyTorque(rollingTorque, dt);
            
            particle.applyForce(totalNormalForce, frictionForce, dt);
            
            if (particle.vx < 0) {
                particle.applyRestitution(1.0f, 0.0f);
                particle.omega *= ROT_RESTITUTION_COEFF;
            }
        }

        // Right wall
        if (particle.x + particle.radius > width) {
            overlap = particle.x + particle.radius - width;
            normalForce = springConstant * overlap;
            float dampingForce = DAMPING_COEFF * particle.vx;
            float totalNormalForce = -normalForce - dampingForce;
            
            if (overlap > MIN_SEPARATION) {
                particle.x = width - particle.radius - MIN_SEPARATION;
            }
            
            float frictionForce = 0.0f;
            if (abs(normalForce) > 1e-6) {
                frictionForce = -MU_K * abs(totalNormalForce) * sign(particle.vy);
                float torque = -frictionForce * particle.radius;
                particle.applyTorque(torque, dt);
            }
            
            float rollingTorque = -ROLL_FRICTION_COEFF * abs(normalForce) * particle.radius * sign(particle.omega);
            particle.applyTorque(rollingTorque, dt);
            
            particle.applyForce(totalNormalForce, frictionForce, dt);
            
            if (particle.vx > 0) {
                particle.applyRestitution(-1.0f, 0.0f);
                particle.omega *= ROT_RESTITUTION_COEFF;
            }
        }

        // Bottom wall
        if (particle.y - particle.radius < 0) {
            overlap = particle.radius - particle.y;
            normalForce = springConstant * overlap;
            float dampingForce = DAMPING_COEFF * particle.vy;
            float totalNormalForce = normalForce - dampingForce;
            
            if (overlap > MIN_SEPARATION) {
                particle.y = particle.radius + MIN_SEPARATION;
            }
            
            float frictionForce = 0.0f;
            if (abs(normalForce) > 1e-6) {
                frictionForce = -MU_K * abs(totalNormalForce) * sign(particle.vx);
                float torque = frictionForce * particle.radius;
                particle.applyTorque(torque, dt);
            }
            
            float rollingTorque = -ROLL_FRICTION_COEFF * abs(normalForce) * particle.radius * sign(particle.omega);
            particle.applyTorque(rollingTorque, dt);
            
            particle.applyForce(frictionForce, totalNormalForce, dt);
            
            if (particle.vy < 0) {
                particle.applyRestitution(0.0f, 1.0f);
                particle.omega *= ROT_RESTITUTION_COEFF;
            }
        }

        // Top wall
        if (particle.y + particle.radius > height) {
            overlap = particle.y + particle.radius - height;
            normalForce = springConstant * overlap;
            float dampingForce = DAMPING_COEFF * particle.vy;
            float totalNormalForce = -normalForce - dampingForce;
            
            if (overlap > MIN_SEPARATION) {
                particle.y = height - particle.radius - MIN_SEPARATION;
            }
            
            float frictionForce = 0.0f;
            if (abs(normalForce) > 1e-6) {
                frictionForce = -MU_K * abs(totalNormalForce) * sign(particle.vx);
                float torque = -frictionForce * particle.radius;
                particle.applyTorque(torque, dt);
            }
            
            float rollingTorque = -ROLL_FRICTION_COEFF * abs(normalForce) * particle.radius * sign(particle.omega);
            particle.applyTorque(rollingTorque, dt);
            
            particle.applyForce(frictionForce, totalNormalForce, dt);
            
            if (particle.vy > 0) {
                particle.applyRestitution(0.0f, -1.0f);
                particle.omega *= ROT_RESTITUTION_COEFF;
            }
        }
    }

    float sign(float val) {
        return (val > 0) - (val < 0);
    }

    void handleParticleCollisions(vector<Particle>& particles, float dt, int num_gangs = 1, int num_workers = 1, int vector_length = 1) {
        int numParticles = particles.size();
        int totalPairs = numParticles * (numParticles - 1) / 2;

        // Offload the flattened loop to the GPU with explicit control over gangs, workers, and vector lengths
        #pragma acc parallel loop gang worker vector num_gangs(num_gangs) num_workers(num_workers) vector_length(vector_length)
        for (int idx = 0; idx < totalPairs; ++idx) {
            int i = idx / numParticles;
            int j = idx % numParticles;

            if (j <= i) {
                i = numParticles - 2 - i;
                j = numParticles - 1 - (idx - (i * (i + 1)) / 2);
            } else {
                j = j - 1;
            }

            if (i < 0 || i >= numParticles || j < 0 || j >= numParticles || i >= j) {
                continue;
            }

            float dx = particles[j].x - particles[i].x;
            float dy = particles[j].y - particles[i].y;
            float dist = sqrt(dx * dx + dy * dy);
            float overlap = particles[i].radius + particles[j].radius - dist;

            if (overlap > 0) {
                float nx = dx / dist;
                float ny = dy / dist;
                float tx = -ny;
                float ty = nx;

                float ri = particles[i].radius;
                float rj = particles[j].radius;
                float vix = particles[i].vx - particles[i].omega * ri * ny;
                float viy = particles[i].vy + particles[i].omega * ri * nx;
                float vjx = particles[j].vx - particles[j].omega * rj * ny;
                float vjy = particles[j].vy + particles[j].omega * rj * nx;

                float dvx = vjx - vix;
                float dvy = vjy - viy;

                float normalVel = dvx * nx + dvy * ny;
                float tangentVel = dvx * tx + dvy * ty;

                float m1 = particles[i].mass;
                float m2 = particles[j].mass;
                float reducedMass = (m1 * m2) / (m1 + m2);

                float normalForce = SPRING_CONSTANT * overlap;
                float frictionForce = 0.0f;

                if (abs(tangentVel) > 0.01f) {
                    frictionForce = -MU_K * abs(normalForce) * (tangentVel > 0 ? 1 : -1);
                } else {
                    frictionForce = -min(MU_S * abs(normalForce), abs(tangentVel) * reducedMass / dt) 
                                  * (tangentVel > 0 ? 1 : -1);
                }

                float totalFx = normalForce * nx + frictionForce * tx;
                float totalFy = normalForce * ny + frictionForce * ty;

                particles[i].applyForce(-totalFx, -totalFy, dt);
                particles[j].applyForce(totalFx, totalFy, dt);

                float torque1 = (frictionForce * ri);
                float torque2 = -(frictionForce * rj);
                particles[i].applyTorque(torque1, dt);
                particles[j].applyTorque(torque2, dt);

                if (normalVel < 0) {
                    float newNormalVel = -normalVel * RESTITUTION_COEFF;
                    float impulse = (newNormalVel - normalVel) * reducedMass;

                    particles[i].vx -= (impulse / m1) * nx;
                    particles[i].vy -= (impulse / m1) * ny;
                    particles[j].vx += (impulse / m2) * nx;
                    particles[j].vy += (impulse / m2) * ny;

                    float rotImpulse = impulse * ROT_RESTITUTION_COEFF;
                    particles[i].omega += (rotImpulse * ri) / particles[i].I;
                    particles[j].omega -= (rotImpulse * rj) / particles[j].I;
                }
            }
        }
    }
};

class Simulation {
public:
    vector<Particle> particles;
    Box box;
    float timeStep;

    Simulation(vector<Particle> p, Box b, float dt) : particles(move(p)), box(b), timeStep(dt) {}

    vector<vector<float>> runStep(int num_gangs = 1, int num_workers = 1, int vector_length = 1) {
        auto start1 = chrono::high_resolution_clock::now();

        // Allocate and keep particles on GPU
        #pragma acc data copy(particles)
        {
            // Parallelized gravity and wall collisions
            #pragma acc parallel loop gang worker vector num_gangs(num_gangs) num_workers(num_workers) vector_length(vector_length)
            for (int i = 0; i < particles.size(); ++i) {
                particles[i].applyGravity(timeStep);
                box.handleWallCollisions(particles[i], timeStep);
            }

            // Parallelized particle-particle collisions with explicit control over gangs, workers, and vector lengths
            box.handleParticleCollisions(particles, timeStep, num_gangs, num_workers, vector_length);

            // Parallelized position updates
            #pragma acc parallel loop gang worker vector num_gangs(num_gangs) num_workers(num_workers) vector_length(vector_length)
            for (int i = 0; i < particles.size(); ++i) {
                particles[i].updatePosition(timeStep);
            }
        }

        auto end1 = chrono::high_resolution_clock::now();
        chrono::duration<double> elapsed1 = end1 - start1;

        // Collect particle positions
        vector<vector<float>> positions;
        for (auto &particle : particles) {
            positions.push_back({particle.x, particle.y, particle.theta, 
                                 particle.getMarkerEndpoint().first, 
                                 particle.getMarkerEndpoint().second});
        }

        return positions;
    }

    double measureExecutionTime(int numSteps, int num_gangs = 1, int num_workers = 1, int vector_length = 1) {
        auto start = chrono::high_resolution_clock::now();

        for (int i = 0; i < numSteps; ++i) {
            runStep(num_gangs, num_workers, vector_length);
        }

        auto end = chrono::high_resolution_clock::now();
        chrono::duration<double> elapsed = end - start;

        return elapsed.count();
    }
};

namespace py = pybind11;

PYBIND11_MODULE(Strongana, m) {
    py::class_<Particle>(m, "Particle")
        .def(py::init<float, float, float, float, float, float>())
        .def("updatePosition", &Particle::updatePosition)
        .def("applyGravity", &Particle::applyGravity)
        .def_readwrite("x", &Particle::x)
        .def_readwrite("y", &Particle::y)
        .def_readwrite("vx", &Particle::vx)
        .def_readwrite("vy", &Particle::vy)
        .def_readwrite("radius", &Particle::radius)
        .def_readwrite("mass", &Particle::mass)
        .def_readwrite("theta", &Particle::theta)
        .def_readwrite("omega", &Particle::omega);

    py::class_<Box>(m, "Box")
        .def(py::init<float, float, float>())
        .def("handleWallCollisions", &Box::handleWallCollisions)
        .def("handleParticleCollisions", &Box::handleParticleCollisions, py::arg("particles"), py::arg("dt"), py::arg("num_gangs") = 1, py::arg("num_workers") = 1, py::arg("vector_length") = 1)
        .def_readwrite("width", &Box::width)
        .def_readwrite("height", &Box::height)
        .def_readwrite("springConstant", &Box::springConstant);

    py::class_<Simulation>(m, "Simulation")
        .def(py::init<vector<Particle>, Box, float>())
        .def("runStep", &Simulation::runStep, py::arg("num_gangs") = 1, py::arg("num_workers") = 1, py::arg("vector_length") = 1)
        .def("measureExecutionTime", &Simulation::measureExecutionTime, py::arg("numSteps"), py::arg("num_gangs") = 1, py::arg("num_workers") = 1, py::arg("vector_length") = 1);
}