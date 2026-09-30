import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# CONSTANTS
# ============================================================

G = 6.67430e-11          # Gravitational constant (m^3 kg^-1 s^-2)
M_EARTH = 5.97219e24     # Mass of Earth (kg)
R_EARTH = 6.371e6        # Radius of Earth (m)

MU = G * M_EARTH         # Earth's gravitational parameter


# ============================================================
# PHYSICS FUNCTIONS
# ============================================================

def acceleration(position):
    """
    Calculate gravitational acceleration at a given position.
    """
    r = np.linalg.norm(position)

    return -MU * position / r**3


def simulate(initial_position, initial_velocity, dt=5.0, duration=30000.0):
    """
    Numerically simulate spacecraft motion using
    velocity-Verlet integration.
    """

    steps = int(duration / dt)

    positions = np.zeros((steps + 1, 2))
    velocities = np.zeros((steps + 1, 2))
    times = np.arange(steps + 1) * dt

    positions[0] = initial_position
    velocities[0] = initial_velocity

    acceleration_now = acceleration(positions[0])

    for i in range(steps):

        # Update position
        positions[i + 1] = (
            positions[i]
            + velocities[i] * dt
            + 0.5 * acceleration_now * dt**2
        )

        # Calculate new acceleration
        acceleration_new = acceleration(positions[i + 1])

        # Update velocity
        velocities[i + 1] = (
            velocities[i]
            + 0.5 * (acceleration_now + acceleration_new) * dt
        )

        acceleration_now = acceleration_new

    return times, positions, velocities


def circular_velocity(radius):
    """
    Calculate circular orbital velocity.
    """
    return np.sqrt(MU / radius)


def escape_velocity(radius):
    """
    Calculate escape velocity.
    """
    return np.sqrt(2 * MU / radius)


def specific_energy(position, velocity):
    """
    Calculate specific orbital energy.

    Negative  -> bound orbit
    Zero      -> escape threshold
    Positive  -> escape trajectory
    """

    r = np.linalg.norm(position)
    v = np.linalg.norm(velocity)

    return 0.5 * v**2 - MU / r


def eccentricity(position, velocity):
    """
    Calculate orbital eccentricity.
    """

    r = np.linalg.norm(position)
    v = np.linalg.norm(velocity)

    energy = specific_energy(position, velocity)

    angular_momentum = np.linalg.norm(
        np.cross(
            np.append(position, 0),
            np.append(velocity, 0)
        )
    )

    e_squared = 1 + (2 * energy * angular_momentum**2) / MU**2

    return np.sqrt(max(e_squared, 0))


# ============================================================
# INITIAL CONDITIONS
# ============================================================

ALTITUDE = 400e3

INITIAL_RADIUS = R_EARTH + ALTITUDE

V_CIRCULAR = circular_velocity(INITIAL_RADIUS)
V_ESCAPE = escape_velocity(INITIAL_RADIUS)

print()
print("==========================================")
print("       ORBITAL MECHANICS SIMULATION")
print("==========================================")
print()

print(f"Altitude:              {ALTITUDE / 1000:.0f} km")
print(f"Circular velocity:     {V_CIRCULAR / 1000:.3f} km/s")
print(f"Escape velocity:       {V_ESCAPE / 1000:.3f} km/s")
print(f"Escape/circular ratio: {V_ESCAPE / V_CIRCULAR:.4f}")
print()


# ============================================================
# RUN EXPERIMENTS
# ============================================================

velocity_multipliers = [
    1.00,
    1.05,
    1.10,
    1.20,
    1.30,
    1.40,
    1.42
]

results = []

for multiplier in velocity_multipliers:

    initial_position = np.array([
        INITIAL_RADIUS,
        0.0
    ])

    initial_velocity = np.array([
        0.0,
        V_CIRCULAR * multiplier
    ])

    times, positions, velocities = simulate(
        initial_position,
        initial_velocity
    )

    energy = specific_energy(
        initial_position,
        initial_velocity
    )

    e = eccentricity(
        initial_position,
        initial_velocity
    )

    radius_history = np.linalg.norm(
        positions,
        axis=1
    )

    maximum_radius = radius_history.max()

    if energy < -1e-5:

        if e < 0.01:
            orbit_type = "Circular"
        else:
            orbit_type = "Elliptical"

    else:
        orbit_type = "Escape"

    results.append({
        "multiplier": multiplier,
        "velocity": V_CIRCULAR * multiplier,
        "energy": energy,
        "eccentricity": e,
        "max_radius": maximum_radius,
        "orbit_type": orbit_type
    })


# ============================================================
# PRINT RESULTS TABLE
# ============================================================

print("RESULTS")
print("------------------------------------------")

print(
    f"{'Multiplier':<12}"
    f"{'Velocity':<15}"
    f"{'Energy':<15}"
    f"{'Eccentricity':<15}"
    f"{'Orbit'}"
)

print("------------------------------------------")

for result in results:

    print(
        f"{result['multiplier']:<12.2f}"
        f"{result['velocity'] / 1000:<15.3f}"
        f"{result['energy']:<15.2e}"
        f"{result['eccentricity']:<15.3f}"
        f"{result['orbit_type']}"
    )

print()


# ============================================================
# GRAPH 1: ORBITAL TRAJECTORIES
# ============================================================

plt.figure(figsize=(9, 9))

# Draw Earth
theta = np.linspace(0, 2 * np.pi, 500)

earth_x = R_EARTH * np.cos(theta) / 1000
earth_y = R_EARTH * np.sin(theta) / 1000

plt.plot(
    earth_x,
    earth_y,
    label="Earth"
)

# Plot selected trajectories
trajectory_multipliers = [
    1.00,
    1.05,
    1.10,
    1.20,
    1.30
]   

for multiplier in trajectory_multipliers:

    initial_position = np.array([
        INITIAL_RADIUS,
        0.0
    ])

    initial_velocity = np.array([
        0.0,
        V_CIRCULAR * multiplier
    ])

    times, positions, velocities = simulate(
        initial_position,
        initial_velocity
    )

    plt.plot(
        positions[:, 0] / 1000,
        positions[:, 1] / 1000,
        label=f"{multiplier:.2f} × circular velocity"
    )

plt.xlabel("x (km)")
plt.ylabel("y (km)")

plt.title(
    "Effect of Initial Velocity on Spacecraft Trajectory"
)

plt.axis("equal")
plt.legend()
plt.xlim(-20000, 15000)
plt.ylim(-20000, 15000)
plt.tight_layout()

plt.savefig(
    "trajectory_comparison.png",
    dpi=300
)

plt.show()


# ============================================================
# GRAPH 2: ORBITAL ENERGY
# ============================================================

multipliers = np.array([
    result["multiplier"]
    for result in results
])

energies = np.array([
    result["energy"]
    for result in results
])

plt.figure(figsize=(9, 6))

plt.plot(
    multipliers,
    energies,
    marker="o"
)

plt.axhline(
    0,
    linestyle="--",
    label="Escape threshold"
)

plt.xlabel(
    "Initial velocity / circular velocity"
)

plt.ylabel(
    "Specific orbital energy (J/kg)"
)

plt.title(
    "Specific Orbital Energy vs Initial Velocity"
)

plt.legend()

plt.grid(True)

plt.tight_layout()

plt.savefig(
    "orbital_energy.png",
    dpi=300
)

plt.show()


# ============================================================
# GRAPH 3: ECCENTRICITY
# ============================================================

eccentricities = np.array([
    result["eccentricity"]
    for result in results
])

plt.figure(figsize=(9, 6))

plt.plot(
    multipliers,
    eccentricities,
    marker="o"
)

plt.axhline(
    1,
    linestyle="--",
    label="Escape boundary (e = 1)"
)

plt.xlabel(
    "Initial velocity / circular velocity"
)

plt.ylabel(
    "Orbital eccentricity"
)

plt.title(
    "Orbital Eccentricity vs Initial Velocity"
)

plt.legend()

plt.grid(True)

plt.tight_layout()

plt.savefig(
    "eccentricity.png",
    dpi=300
)

plt.show()

# ============================================================
# SAVE RESULTS TO CSV
# ============================================================

import csv

with open("orbital_results.csv", "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Velocity multiplier",
        "Velocity (km/s)",
        "Specific energy (J/kg)",
        "Eccentricity",
        "Maximum radius (km)",
        "Orbit type"
    ])

    for result in results:

        writer.writerow([
            result["multiplier"],
            result["velocity"] / 1000,
            result["energy"],
            result["eccentricity"],
            result["max_radius"] / 1000,
            result["orbit_type"]
        ])

print("  orbital_results.csv")
# ============================================================
# FINAL SUMMARY
# ============================================================

print("==========================================")
print("SUMMARY")
print("==========================================")

print(
    f"Theoretical escape velocity: "
    f"{V_ESCAPE / 1000:.3f} km/s"
)

print(
    f"Theoretical velocity ratio: "
    f"{V_ESCAPE / V_CIRCULAR:.4f}"
)

print()

print(
    "The simulation demonstrates that increasing "
    "initial velocity changes the spacecraft's "
    "orbital energy and trajectory."
)

print()
print("Figures saved:")
print("  trajectory_comparison.png")
print("  orbital_energy.png")
print("  eccentricity.png")