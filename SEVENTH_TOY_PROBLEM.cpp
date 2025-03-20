#include <iostream>
#include <cmath>
#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <omp.h>


#include <algorithm>
using namespace std;

const float GRAVITY = 9.81;
const float RESTITUTION_COEFF = 0.6;      // Restitution coefficient for inelastic collisions
const float MU_S = 0.7;                   // Static friction coefficient
const float MU_K = 0.5;                   // Kinetic friction coefficient
const float SPRING_CONSTANT = 10000.0;
const float DAMPING_COEFF = 50.0;    // Added damping coefficient for wall collisions
const float VELOCITY_THRESHOLD = 100.0; // Maximum allowed velocity
const float MIN_SEPARATION = 0.01;       // Spring constant for particle interactions

class Particle {
public:
    float x, y, vx, vy, radius, mass;

    Particle(float startX, float startY, float startVx, float startVy, float r, float m)
        : x(startX), y(startY), vx(startVx), vy(startVy), radius(r), mass(m) {}

    void applyForce(float fx, float fy, float dt) {
        vx += (fx / mass) * dt;
        vy += (fy / mass) * dt;
    }

    void applyGravity(float dt) {
        vy -= GRAVITY * dt;
    }

    // Updated restitution method that only affects the normal component
    void applyRestitution(float normalX, float normalY) {
        
        float normalVel = vx * normalX + vy * normalY;
        
        // Only apply restitution to the normal component
        float newNormalVel = -normalVel * RESTITUTION_COEFF;
        
        // Update velocities
        float deltaVx = (newNormalVel - normalVel) * normalX;
        float deltaVy = (newNormalVel - normalVel) * normalY;
        
        vx += deltaVx;
        vy += deltaVy;
    }

    void updatePosition(float dt) {
        x += vx * dt;
        y += vy * dt;
    }
};

class Box {
public:
    float width, height, springConstant;

    Box(float w, float h, float k) : width(w), height(h), springConstant(k) {}

    void handleWallCollisions(Particle &particle, float dt) {
        // Add velocity clamping to prevent numerical instability
        
        
        float overlap;
        float normalForce;
        
        // Left wall
        if (particle.x - particle.radius < 0) {
            overlap = particle.radius - particle.x;
            
            // Calculate normal force with damping
            normalForce = springConstant * overlap;
            float dampingForce = DAMPING_COEFF * particle.vx;  // Damping based on normal velocity
            float totalNormalForce = normalForce - dampingForce;
            
            // Ensure minimum separation after collision
            if (overlap > MIN_SEPARATION) {
                particle.x = particle.radius + MIN_SEPARATION;
            }
            
            // Only apply friction if there's significant normal force
            float frictionForce = 0.0f;
            if (abs(normalForce) > 1e-6) {
                frictionForce = -MU_K * abs(totalNormalForce) * sign(particle.vy);
            }
            
            particle.applyForce(totalNormalForce, frictionForce, dt);
            
            // Apply restitution only if moving towards the wall
            if (particle.vx < 0) {
                particle.applyRestitution(1.0f, 0.0f);
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
            }
            
            particle.applyForce(totalNormalForce, frictionForce, dt);
            
            if (particle.vx > 0) {
                particle.applyRestitution(-1.0f, 0.0f);
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
            }
            
            particle.applyForce(frictionForce, totalNormalForce, dt);
            
            if (particle.vy < 0) {
                particle.applyRestitution(0.0f, 1.0f);
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
            }
            
            particle.applyForce(frictionForce, totalNormalForce, dt);
            
            if (particle.vy > 0) {
                particle.applyRestitution(0.0f, -1.0f);
            }
        }
    }

    // Helper function for sign determination
    float sign(float val) {
        return (val > 0) - (val < 0);
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
                    // Normal vector pointing from particle i to j
                    float nx = dx / dist;
                    float ny = dy / dist;
                    
                    // Tangential vector (perpendicular to normal)
                    float tx = -ny;
                    float ty = nx;
                    
                    // Relative velocity
                    float dvx = particles[j].vx - particles[i].vx;
                    float dvy = particles[j].vy - particles[i].vy;
                    
                    // Normal component of relative velocity
                    float normalVel = dvx * nx + dvy * ny;
                    
                    // Tangential component of relative velocity
                    float tangentVel = dvx * tx + dvy * ty;
                    
                    // Calculate new normal velocity after collision with restitution
                    float m1 = particles[i].mass;
                    float m2 = particles[j].mass;
                    float reducedMass = (m1 * m2) / (m1 + m2);
                    
                    // Spring force (normal direction)
                    float normalForce = SPRING_CONSTANT * overlap;
                    
                    // Friction force calculation
                    float frictionForce = 0.0f;
                    if (abs(tangentVel) > 0.01f) {  // Only apply kinetic friction if there's significant tangential velocity
                        frictionForce = -MU_K * abs(normalForce) * (tangentVel > 0 ? 1 : -1);
                    } else {  // Apply static friction
                        frictionForce = -min(MU_S * abs(normalForce), abs(tangentVel) * reducedMass / dt) 
                                      * (tangentVel > 0 ? 1 : -1);
                    }
                    
                    // Total forces in normal and tangential directions
                    float totalFx = normalForce * nx + frictionForce * tx;
                    float totalFy = normalForce * ny + frictionForce * ty;
                    
                    // Apply forces respecting Newton's third law
                    float forceFactor1 = 1.0f / m1;
                    float forceFactor2 = 1.0f / m2;
                    
                    // Apply forces to the thread-local arrays
                    localFx[i][tid] -= totalFx * forceFactor1;
                    localFy[i][tid] -= totalFy * forceFactor1;
                    localFx[j][tid] += totalFx * forceFactor2;
                    localFy[j][tid] += totalFy * forceFactor2;
                    
                    // Apply restitution
                    if (normalVel < 0) {  // Only apply restitution for approaching particles
                        float newNormalVel = -normalVel * RESTITUTION_COEFF;
                        float impulse = (newNormalVel - normalVel) * reducedMass;
                        
                        // Update velocities directly for restitution
                        #pragma omp critical
                        {
                            particles[i].vx -= (impulse / m1) * nx;
                            particles[i].vy -= (impulse / m1) * ny;
                            particles[j].vx += (impulse / m2) * nx;
                            particles[j].vy += (impulse / m2) * ny;
                        }
                    }
                }
            }
        }

        // Accumulate forces from all threads
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
        #pragma omp parallel for
        for (int i = 0; i < particles.size(); ++i) {
            particles[i].applyGravity(timeStep);
            box.handleWallCollisions(particles[i], timeStep);
        }

        box.handleParticleCollisions(particles, timeStep);

        #pragma omp parallel for
        for (int i = 0; i < particles.size(); ++i) {
            particles[i].updatePosition(timeStep);
        }

        vector<vector<float>> positions;
        for (auto &particle : particles) {
            positions.push_back({particle.x, particle.y});
        }

        return positions;
    }
};

namespace py = pybind11;

PYBIND11_MODULE(SEVENTH_TOY_PROBLEM, m) {
    py::class_<Particle>(m, "Particle")
        .def(py::init<float, float, float, float, float, float>())
        .def("updatePosition", &Particle::updatePosition)
        .def("applyGravity", &Particle::applyGravity)
        .def_readwrite("x", &Particle::x)
        .def_readwrite("y", &Particle::y)
        .def_readwrite("vx", &Particle::vx)
        .def_readwrite("vy", &Particle::vy)
        .def_readwrite("radius", &Particle::radius)
        .def_readwrite("mass", &Particle::mass);

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