import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from typing import Optional

from station.adapter import UniverseAdapter
from station.space_station import SpaceStation

class Body:
    def __init__(self, name, mass, position, velocity, radius=0.1, color="white"):
        self.name = name
        self.mass = mass
        self.position = np.array(position, dtype=float)  # [x, y]
        self.velocity = np.array(velocity, dtype=float)  # [vx, vy]
        self.radius = radius
        self.color = color

    def __repr__(self):
        return f"Body(name={self.name}, mass={self.mass}, position={self.position}, velocity={self.velocity}, radius={self.radius}, color={self.color})"
    


class Universe:
    def __init__(self, G=1.0):
        self.bodies = []
        self.G = G  # Gravitational constant
        self.time = 0.0
        # environment fields used by the station adapter
        self.external_temp = -80.0
        self.solar_flux = 0.0
        self.radiation = 0.0
        self.eclipse = False
        self.meteor_alert = False

    def add_body(self, body: Body):
        self.bodies.append(body)

    # ------- Gravity Calculation -------
    def compute_forces(self):
        n = len(self.bodies)
        forces = [np.zeros(2, dtype=float) for _ in range(n)]

        # between every body
        for i in range(n):
            for j in range(i+1, n):
                bi = self.bodies[i]
                bj = self.bodies[j]

                # Vector from bi to bj
                r_vec = bj.position - bi.position
                r_mag = np.linalg.norm(r_vec)
                if r_mag == 0:
                    continue  # avoid crash

                dist = r_mag # distance b/w 2 bodies
                # Gravitational force 
                force_mag = self.G * bi.mass * bj.mass / (dist ** 2)
                force_dir = r_vec / r_mag  # unit vector
                force = force_mag * force_dir

                forces[i] += force
                forces[j] -= force  # equal and opposite

        return forces
    
    # ------- Collision Handling -------
    def handle_collisions(self):
        """ Merge bodies that are overlapping (distance < r1 + r2)"""
        merged = set()
        new_bodies = []

        n = len(self.bodies)

        for i in range(n):
            if i in merged:
                continue

            bi = self.bodies[i]
            current_group = [i]

            for j in range(i+1, n):
                if j in merged:
                    continue

                bj = self.bodies[j]
                r_vec = bj.position - bi.position
                dist = np.linalg.norm(r_vec)

                if dist < (bi.radius + bj.radius):
                    # Merge bi and bj
                    current_group.append(j)
                    merged.add(j)

            if len(current_group) == 1:
                # no collision
                new_bodies.append(bi)
            else:
                # merge all in current_group
                merged.add(i)
                bodies_to_merge = [self.bodies[k] for k in current_group]

                total_mass = sum(b.mass for b in bodies_to_merge)

                # center of mass position
                pos = sum(b.mass*b.position for b in bodies_to_merge) / total_mass
                # momentum conservation for velocity
                vel = sum(b.mass*b.velocity for b in bodies_to_merge) / total_mass

                # approximate radius : scale with mass^(1/3)
                base_radius = max(b.radius for b in bodies_to_merge)
                radius = base_radius * (total_mass / bodies_to_merge[0].mass) ** (1/3)

                # choose color of most massive
                biggest = max(bodies_to_merge, key=lambda b: b.mass)
                color = biggest.color

                merged_body = Body(
                    name="Merged(" + "+".join(b.name for b in bodies_to_merge) + ")",
                    mass=total_mass,
                    position=pos,
                    velocity=vel,
                    radius=radius,
                    color=color
                )
                new_bodies.append(merged_body)
            
        self.bodies = new_bodies

    #------- Energy -------
    def total_energy(self):
        ke = 0.0  # kinetic energy
        for b in self.bodies:
            v_mag = np.linalg.norm(b.velocity)
            ke += 0.5 * b.mass * v_mag**2

        pe = 0.0  # potential energy
        n = len(self.bodies)
        for i in range(n):
            for j in range(i+1, n):
                bi = self.bodies[i]
                bj = self.bodies[j]
                r_vec = bj.position - bi.position
                dist = np.linalg.norm(r_vec)
                if dist == 0:
                    continue
                pe -= self.G * bi.mass * bj.mass / dist
        return ke + pe
    
    # ------- Time Step -------
    def step(self, dt, handle_collisions=True):
        forces = self.compute_forces()
        
        for body, F in zip(self.bodies, forces):
            a = F / body.mass
            body.velocity += a * dt
            body.position += body.velocity * dt

        if handle_collisions:
            self.handle_collisions()

        self.time += dt
        self._update_environment_fields()

    def _update_environment_fields(self):
        """
        Simple space weather model to drive the station.
        Tweak these functions freely to match your scenario.
        """
        # External temperature oscillates between roughly -230C and -70C
        self.external_temp = -150.0 + 80.0 * np.sin(self.time / 50.0)
        # Solar flux peaks when "in sunlight"
        self.solar_flux = max(0.0, 1.2 + 0.8 * np.cos(self.time / 40.0))
        # Mild radiation drift
        self.radiation = 0.1 + 0.05 * np.sin(self.time / 30.0)
        # Treat low flux as eclipse
        self.eclipse = self.solar_flux < 0.3
        # Keep meteor_alert simple/deterministic for now
        self.meteor_alert = False

    
# ---------- SYSTEM WITH NICE ORBITS ----------

def create_nice_orbits_system():
    """
    Clean system: 1 star, 2 planets, 1 moon.
    Planet speeds chosen for almost circular orbits.
    """
    universe = Universe(G=1.0)

    # Central star
    star = Body(
        name="Star",
        mass=1500.0,
        position=[0.0, 0.0],
        velocity=[0.0, 0.0],
        radius=0.4,
        color="yellow",
    )
    universe.add_body(star)

    # --- Inner planet (circular orbit) ---
    r_inner = 3.0
    v_inner = np.sqrt(universe.G * star.mass / r_inner)  # circular speed
    inner = Body(
        name="InnerPlanet",
        mass=1.0,
        position=[r_inner, 0.0],    # on +x axis
        velocity=[0.0, v_inner],    # pure +y direction
        radius=0.15,
        color="cyan",
    )
    universe.add_body(inner)

    # --- Outer planet (larger orbit, slower) ---
    r_outer = 7.0
    v_outer = np.sqrt(universe.G * star.mass / r_outer)
    outer = Body(
        name="OuterPlanet",
        mass=3.0,
        position=[r_outer, 0.0],
        velocity=[0.0, v_outer],
        radius=0.22,
        color="blue",
    )
    universe.add_body(outer)

    # --- Moon around outer planet ---
    # Put moon slightly "above" the planet
    moon_offset = np.array([0.0, 1.0])  # 1 unit above
    moon_pos = outer.position + moon_offset
    r_moon = np.linalg.norm(moon_offset)

    # orbital speed around planet:
    v_moon_rel = np.sqrt(universe.G * outer.mass / r_moon)

    # direction perpendicular to offset (offset is [0,1] so perpendicular is [1,0])
    moon_velocity = outer.velocity + np.array([v_moon_rel, 0.0])

    moon = Body(
        name="Moon",
        mass=0.2,
        position=moon_pos,
        velocity=moon_velocity,
        radius=0.08,
        color="white",
    )
    universe.add_body(moon)

    # --- small asteroid belt (for occasional collisions) ---
    rng = np.random.default_rng(7)
    for i in range(20):
        r = rng.uniform(8.5, 10.5)
        theta = rng.uniform(0, 2 * np.pi)

        x = r * np.cos(theta)
        y = r * np.sin(theta)

        # near-circular orbit around star
        speed = np.sqrt(universe.G * star.mass / r) * rng.uniform(0.97, 1.03)
        vx = -speed * np.sin(theta)
        vy = speed * np.cos(theta)

        asteroid = Body(
            name=f"A{i}",
            mass=rng.uniform(0.01, 0.05),
            position=[x, y],
            velocity=[vx, vy],
            radius=0.04,          # 👈 small radius = fewer collisions
            color="orange",
        )
        universe.add_body(asteroid)


    return universe


# ---------- ANIMATION WITH ORBIT TRAILS ----------
def animate_universe(
    universe: Universe,
    station: Optional[SpaceStation] = None,
    adapter: Optional[UniverseAdapter] = None,
    dt=0.01,
    steps_per_frame=3,
    frames=2000,
    show_trails=True,
    handle_collisions=False,
):
    fig, ax = plt.subplots()
    ax.set_aspect("equal", "box")

    ax.set_xlim(-12, 12)
    ax.set_ylim(-12, 12)
    ax.set_facecolor("black")

    scatters = []
    for body in universe.bodies:
        scatter = ax.scatter(
            body.position[0],
            body.position[1],
            s=(body.radius * 200) ** 2,
            c=body.color,
            label=body.name,
        )
        scatters.append((scatter, body))

    # orbit trails
    trails_x = [[] for _ in universe.bodies]
    trails_y = [[] for _ in universe.bodies]
    lines = []

    if show_trails:
        for body in universe.bodies:
            (line,) = ax.plot([], [], linewidth=0.7, alpha=0.7, c=body.color)
            lines.append(line)

    # text overlays
    energy_text = ax.text(0.02, 0.95, "", transform=ax.transAxes, fontsize=8, color="white")
    station_text = ax.text(0.02, 0.90, "", transform=ax.transAxes, fontsize=8, color="white")

    def update(frame):
        # --- universe physics ---
        for _ in range(steps_per_frame):
            universe.step(dt, handle_collisions=handle_collisions)

        # --- station update if provided ---
        if station is not None and adapter is not None:
            # We already advanced the universe above, so only read its state.
            env = adapter.step(dt, advance_universe=False)
            station.step(env.external_temp, env.solar_flux, dt, env.t)

        # --- update body drawings ---
        for idx, (scatter, body) in enumerate(scatters):
            scatter.set_offsets(body.position)

            if show_trails:
                trails_x[idx].append(body.position[0])
                trails_y[idx].append(body.position[1])

                # Keep trails short
                max_pts = 250
                if len(trails_x[idx]) > max_pts:
                    trails_x[idx].pop(0)
                    trails_y[idx].pop(0)

                lines[idx].set_data(trails_x[idx], trails_y[idx])

        # --- UI text ---
        energy_text.set_text(f"t={universe.time:.2f}")
        if station is not None:
            station_text.set_text(f"station energy={station.total_energy_usage():.2f} kW")
        else:
            station_text.set_text("")

        artists = [s for s, _ in scatters] + [energy_text, station_text]
        if show_trails:
            artists += lines

        return artists

    ani = FuncAnimation(fig, update, frames=frames, interval=20, blit=True)
    plt.show()

    # Save station log at end if available
    if station is not None:
        from station.space_station import FILE_PATH
        station.save_log(FILE_PATH)
        print("Station log saved:", FILE_PATH)

if __name__ == "__main__":
    uni = create_nice_orbits_system()
    # collisions off + trails on for clean orbits
    animate_universe(
        uni,
        station=None,
        adapter=None,
        dt=0.01,
        steps_per_frame=3,
        frames=2000,
        show_trails=True,
        handle_collisions=False,
    )
