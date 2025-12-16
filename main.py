from universe.universe import create_nice_orbits_system, animate_universe
from station.adapter import UniverseAdapter
from station.space_station import SpaceStation, FILE_PATH
from station.smart_room import SmartRoom


def build_station() -> SpaceStation:
    station = SpaceStation(name="Infinity Station")

    # Add a few rooms (you can change IDs / count)
    station.add_room(SmartRoom(room_id="R1"))
    station.add_room(SmartRoom(room_id="R2"))
    station.add_room(SmartRoom(room_id="Control"))

    return station


def run_simulation(frames: int = 2000, dt: float = 0.01, steps_per_frame: int = 3):
    # 1) Build universe
    universe = create_nice_orbits_system()

    # 2) Wrap with adapter (so we get EnvironmentState) without double-stepping in animation
    adapter = UniverseAdapter(universe)

    # 3) Build space station
    station = build_station()

    print(f"Running animated simulation for {frames} frames, dt={dt}, steps_per_frame={steps_per_frame}...\n")

    animate_universe(
        universe,
        station=station,
        adapter=adapter,
        dt=dt,
        steps_per_frame=steps_per_frame,
        frames=frames,
        show_trails=True,
        handle_collisions=True,
    )


if __name__ == "__main__":
    run_simulation(frames=2000, dt=0.01, steps_per_frame=3)
