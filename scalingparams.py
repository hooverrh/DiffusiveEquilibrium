from math import sin, radians
gravity = 1.62        # m/s2
strength = 1.0e4     # Pa
target_density = 1500.0  #kg/m3 (rho)
impactor_density = 2500.0   #kg/m3 (delta)
velocity = 20000.0    # m/s    COULD choose a distribution?
alpha = 45.0          # impact angle degrees
effective_velocity = velocity * sin(radians(alpha))
nu = (1.0/3.0)           # ~1/3 to 0.4
mu = 0.43             # ~0.4 to 0.55    Varying mu makes a big difference in scaling, 0.41 from Williams et al. would predict lower fluxes / longer equilibrium times and a discontinuity with Neukum
K1 = 0.132
K2 = 0.26
Kr = 1.1*1.3  # Kr and KrRim
density_ratio = (target_density / impactor_density)

# km^2
surface_area = 1.0

