# Weight calculation coefficients
ALPHA_DENSITY = 0.4      # importance of vehicle density
BETA_SPEED = 0.4        # importance of speed reduction
GAMMA_QUEUE = 0.2       # importance of queue buildup

# Weight smoothing
WEIGHT_DECAY = 0.8      # memory of old weight
WEIGHT_UPDATE = 0.2    # contribution of new observation

# Safety bounds
MIN_WEIGHT = 0.0
MAX_WEIGHT = 1.0

# Time configuration
TIME_STEP_SECONDS = 60

# Simulation control
DEFAULT_SIMULATION_STEPS = 10