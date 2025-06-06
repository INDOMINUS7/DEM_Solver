# === Config ===
CXX = nvc++
PYTHON = python3
EXT = $(shell $(PYTHON)-config --extension-suffix)

# Common include paths
PYINCLUDE = -I/usr/include/python3.10 -I/usr/local/include/pybind11

# Flags
CXXFLAGS_COMMON = -O3 -shared -std=c++11 -fPIC
CXXFLAGS_OMP = $(CXXFLAGS_COMMON) -mp
CXXFLAGS_ACC = $(CXXFLAGS_COMMON) -acc -gpu=mem:managed

# === Source files ===
SIM1_SRC = industrial_simulations/NINTH_TOY_PROBLEM.cpp
SIM2_SRC = industrial_simulations/ELEVENTH_TOY_PROBLEM.cpp

# === Targets ===
SIM1_TARGET = industrial_simulations/NINTH_TOY_PROBLEM$(EXT)
SIM2_TARGET = industrial_simulations/ELEVENTH_TOY_PROBLEM$(EXT)

# === Default: build both ===
all: $(SIM1_TARGET) $(SIM2_TARGET)

# === Build rules ===
$(SIM1_TARGET): $(SIM1_SRC)
	$(CXX) $(CXXFLAGS_OMP) $(PYINCLUDE) $< -o $@

$(SIM2_TARGET): $(SIM2_SRC)
	$(CXX) $(CXXFLAGS_ACC) $(PYINCLUDE) $< -o $@

# === Run commands for industrial_simulation1 ===
run_sim1:
	$(PYTHON) industrial_simulations/simulation9_plot.py

# === Run commands for industrial_simulation2 ===
run_sim2_plot:
	$(PYTHON) industrial_simulations/sim_nut1.py

run_sim2_freq_amp_maxheight:
	$(PYTHON) industrial_simulations/result3.py

run_sim2_freq_amp_timereach:
	$(PYTHON) industrial_simulations/results12.py

run_sim2_sizeratio_maxheight:
	$(PYTHON) industrial_simulations/result5.py

run_sim2_sizeratio_rise:
	$(PYTHON) industrial_simulations/results15.py

# === Clean ===
clean:
	rm -f industrial_simulations*$(EXT)

