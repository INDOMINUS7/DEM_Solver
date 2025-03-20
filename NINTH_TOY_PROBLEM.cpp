#include <iostream>
#include <cmath>
#include <vector>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <omp.h>

using namespace std;

// === MODIFIED: Added new constants for vibration and analysis ===
const float GRAVITY = 9.81;
const float RESTITUTION_COEFF = 1.0;    // Reduced for stone-like materials
const float MU_S = 0.7;                 // Increased for stone on metal
const float MU_K = 0.5;                 // Increased for stone on metal
const float SPRING_CONSTANT = 10000.0;    // Kept same for rigid materials
const float DAMPING_COEFF = 90.0;        // Increased for faster energy dissipation
const float VELOCITY_THRESHOLD = 100.0;
const float MIN_SEPARATION = 0.01;
const float ROLL_FRICTION_COEFF = 0.05;
const float ROT_RESTITUTION_COEFF = 1.00; // Reduced for less spinning
const float ANGULAR_DAMPING = 0.25;      // Increased for stability
const float PI = 3.14159265359; // For settling time calculation

// === NEW: Added SimulationStats struct for data collection ===
struct SimulationStats {
    float maxHeight;
    float initialDropMaxHeight;  // To differentiate from post-drop height
    bool initialDropComplete;
    vector<float> heightHistory;
    vector<float> totalEnergyHistory;
    
    SimulationStats() : maxHeight(0.0f), initialDropMaxHeight(0.0f), 
                       initialDropComplete(false) {}
};

class Particle {
public:
    float x, y, vx, vy, radius, mass;
    float theta, omega, I;
    // === NEW: Added initial position tracking ===
    float initialY;

    // === MODIFIED: Constructor to track initial position ===
    Particle(float startX, float startY, float startVx, float startVy, float r, float m)
        : x(startX), y(startY), vx(startVx), vy(startVy), radius(r), mass(m), 
          theta(0.0f), omega(0.0f), initialY(startY) {
        calculateMomentOfInertia();
    }

    void calculateMomentOfInertia() {
        I = 0.5f * mass * radius * radius;
    }

    // === NEW: Added method to calculate particle energy ===
    float calculateEnergy(float baseHeight = 0.0f) const {
        float kineticEnergy = 0.5f * mass * (vx*vx + vy*vy);
        float rotationalEnergy = 0.5f * I * omega * omega;
        float potentialEnergy = mass * GRAVITY * (y - baseHeight);
        return kineticEnergy + rotationalEnergy + potentialEnergy;
    }

    // Rest of the Particle class remains unchanged
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
    // === NEW: Added vibration parameters ===
    float amplitude;
    float frequency;
    float currentTime;
    float baseHeight;

    // === MODIFIED: Constructor to include vibration parameters ===
    Box(float w, float h, float k, float amp = 0.0f, float freq = 0.0f) 
        : width(w), height(h), springConstant(k), 
          amplitude(amp), frequency(freq), currentTime(0.0f), baseHeight(0.0f) {}

    // === NEW: Method to get current bottom boundary position ===
    float getBottomBoundaryPosition() const {
        return baseHeight + amplitude * sin(2 * PI * frequency * currentTime);
    }

    // === NEW: Method to get bottom boundary velocity ===
    float getBottomBoundaryVelocity() const {
        return 2 * PI * frequency * amplitude * cos(2 * PI * frequency * currentTime);
    }

    // === MODIFIED: Wall collision handling to include vibrating bottom ===
    void handleWallCollisions(Particle &particle, float dt) {
        float overlap;
        float normalForce;
        
        // Left and right walls remain unchanged
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
            // ... (existing left wall collision code)
        }
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

        // === MODIFIED: Bottom wall with vibration ===
        float bottomY = getBottomBoundaryPosition();
        float bottomVel = getBottomBoundaryVelocity();
        
        if (particle.y - particle.radius < bottomY) {
            overlap = particle.radius - (particle.y - bottomY);
            normalForce = springConstant * overlap;
            float relativeVel = particle.vy - bottomVel;
            float dampingForce = DAMPING_COEFF * relativeVel;
            float totalNormalForce = normalForce - dampingForce;
            
            if (overlap > MIN_SEPARATION) {
                particle.y = bottomY + particle.radius + MIN_SEPARATION;
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
            
            if (relativeVel < 0) {
                particle.vy = bottomVel + RESTITUTION_COEFF * (bottomVel - particle.vy);
                particle.omega *= ROT_RESTITUTION_COEFF;
            }
        }

        // Top wall remains unchanged
        
    }

    float sign(float val) {
        return (val > 0) - (val < 0);
    }

    // Particle collision handling remains unchanged
    void handleParticleCollisions(vector<Particle>& particles, float dt) {
        int n = particles.size();
        vector<vector<float>> localFx(n, vector<float>(omp_get_max_threads(), 0.0f));
        vector<vector<float>> localFy(n, vector<float>(omp_get_max_threads(), 0.0f));
        vector<vector<float>> localTorque(n, vector<float>(omp_get_max_threads(), 0.0f));

        #pragma omp parallel for schedule(dynamic)
        for (int i = 0; i < n; ++i) {
            int tid = omp_get_thread_num();

            for (int j = i + 1; j < n; ++j) {
                float dx = particles[j].x - particles[i].x;
                float dy = particles[j].y - particles[i].y;
                float dist = sqrt(dx * dx + dy * dy);
                float overlap = particles[i].radius + particles[j].radius - dist;

                if (overlap > 0) {
                    float nx = dx / dist;
                    float ny = dy / dist;
                    float tx = -ny;
                    float ty = nx;
                    
                    // Relative velocity at contact point including rotation
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
                    
                    float forceFactor1 = 1.0f / m1;
                    float forceFactor2 = 1.0f / m2;
                    
                    // Calculate torques
                    float torque1 = (frictionForce * ri);
                    float torque2 = -(frictionForce * rj);
                    
                    localFx[i][tid] -= totalFx * forceFactor1;
                    localFy[i][tid] -= totalFy * forceFactor1;
                    localFx[j][tid] += totalFx * forceFactor2;
                    localFy[j][tid] += totalFy * forceFactor2;
                    
                    localTorque[i][tid] += torque1;
                    localTorque[j][tid] += torque2;
                    
                    if (normalVel < 0) {
                        float newNormalVel = -normalVel * RESTITUTION_COEFF;
                        float impulse = (newNormalVel - normalVel) * reducedMass;
                        
                        #pragma omp critical
                        {
                            particles[i].vx -= (impulse / m1) * nx;
                            particles[i].vy -= (impulse / m1) * ny;
                            particles[j].vx += (impulse / m2) * nx;
                            particles[j].vy += (impulse / m2) * ny;
                            
                            // Apply rotational impulse
                            float rotImpulse = impulse * ROT_RESTITUTION_COEFF;
                            particles[i].omega += (rotImpulse * ri) / particles[i].I;
                            particles[j].omega -= (rotImpulse * rj) / particles[j].I;
                        }
                    }
                }
            }
        }

        // Accumulate forces and torques
        for (int i = 0; i < n; ++i) {
            float totalFx = 0.0f, totalFy = 0.0f, totalTorque = 0.0f;
            
            #pragma omp parallel for reduction(+:totalFx,totalFy,totalTorque)
            for (int tid = 0; tid < omp_get_max_threads(); ++tid) {
                totalFx += localFx[i][tid];
                totalFy += localFy[i][tid];
                totalTorque += localTorque[i][tid];
            }
            
            particles[i].applyForce(totalFx, totalFy, dt);
            particles[i].applyTorque(totalTorque, dt);
        }
    }
};

class Simulation {
public:
    vector<Particle> particles;
    Box box;
    float timeStep;
    // === NEW: Added simulation statistics ===
    SimulationStats stats;
    float simulationTime;

    Simulation(vector<Particle> p, Box b, float dt) 
        : particles(move(p)), box(b), timeStep(dt), simulationTime(0.0f) {}

    // === MODIFIED: RunStep to include data collection ===
    vector<vector<float>> runStep() {
        simulationTime += timeStep;
        box.currentTime = simulationTime;

        #pragma omp parallel for
        for (int i = 0; i < particles.size(); ++i) {
            particles[i].applyGravity(timeStep);
            box.handleWallCollisions(particles[i], timeStep);
        }

        box.handleParticleCollisions(particles, timeStep);

        float maxHeightThisStep = 0.0f;
        float totalEnergy = 0.0f;

        #pragma omp parallel for reduction(max:maxHeightThisStep) reduction(+:totalEnergy)
        for (int i = 0; i < particles.size(); ++i) {
            particles[i].updatePosition(timeStep);
            maxHeightThisStep = max(maxHeightThisStep, particles[i].y);
            totalEnergy += particles[i].calculateEnergy(box.baseHeight);
            
            // Check if initial drop is complete (particle has hit bottom)
            if (!stats.initialDropComplete && 
                particles[i].y <= (box.getBottomBoundaryPosition() + particles[i].radius * 1.1)) {
                stats.initialDropComplete = true;
                stats.initialDropMaxHeight = stats.maxHeight;
                stats.maxHeight = 0.0f;  // Reset for post-drop tracking
            }
        }

        // Update statistics only after initial drop
        if (stats.initialDropComplete) {
            stats.maxHeight = max(stats.maxHeight, maxHeightThisStep);
        } else {
            stats.initialDropMaxHeight = max(stats.initialDropMaxHeight, maxHeightThisStep);
        }
        
        stats.heightHistory.push_back(maxHeightThisStep);
        stats.totalEnergyHistory.push_back(totalEnergy);

        // Prepare position data for visualization
        vector<vector<float>> positions;
        for (auto &particle : particles) {
            auto [markerX, markerY] = particle.getMarkerEndpoint();
            positions.push_back({
                particle.x, 
                particle.y, 
                particle.theta,
                markerX,
                markerY
            });
        }

        return positions;
    }

    // === NEW: Method to get current bottom boundary position for visualization ===
    float getCurrentBottomBoundaryPosition() const {
        return box.getBottomBoundaryPosition();
    }

    // === NEW: Method to get simulation statistics ===
    SimulationStats getSimulationStats() const {
        return stats;
    }
};

namespace py = pybind11;

PYBIND11_MODULE(NINTH_TOY_PROBLEM, m) {
    // === MODIFIED: Updated Python bindings to include new functionality ===
    py::class_<SimulationStats>(m, "SimulationStats")
        .def_readwrite("maxHeight", &SimulationStats::maxHeight)
        .def_readwrite("initialDropMaxHeight", &SimulationStats::initialDropMaxHeight)
        .def_readwrite("heightHistory", &SimulationStats::heightHistory)
        .def_readwrite("totalEnergyHistory", &SimulationStats::totalEnergyHistory);

    py::class_<Particle>(m, "Particle")
        .def(py::init<float, float, float, float, float, float>())
        .def_readwrite("x", &Particle::x)
        .def_readwrite("y", &Particle::y)
        .def_readwrite("vx", &Particle::vx)
        .def_readwrite("vy", &Particle::vy)
        .def_readwrite("radius", &Particle::radius)
        .def_readwrite("mass", &Particle::mass)
        .def_readwrite("theta", &Particle::theta)
        .def_readwrite("omega", &Particle::omega)
        .def_readwrite("initialY", &Particle::initialY);

    py::class_<Box>(m, "Box")
        .def(py::init<float, float, float, float, float>())
        .def_readwrite("width", &Box::width)
        .def_readwrite("height", &Box::height)
        .def_readwrite("springConstant", &Box::springConstant)
        .def_readwrite("amplitude", &Box::amplitude)
        .def_readwrite("frequency", &Box::frequency)
        .def("getBottomBoundaryPosition", &Box::getBottomBoundaryPosition);

    py::class_<Simulation>(m, "Simulation")
        .def(py::init<vector<Particle>, Box, float>())
        .def("runStep", &Simulation::runStep)
        .def("getCurrentBottomBoundaryPosition", &Simulation::getCurrentBottomBoundaryPosition)
        .def("getSimulationStats", &Simulation::getSimulationStats);
}