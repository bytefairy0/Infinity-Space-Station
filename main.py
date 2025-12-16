from universe.universe import create_nice_orbits_system, animate_universe
from station.adapter import UniverseAdapter
from station.space_station import SpaceStation, FILE_PATH
from station.smart_room import SmartRoom
from station.networking import StationServer, RoomNode

# Expose the server so commands can be sent while the sim runs.
network_server = None


def build_station() -> SpaceStation:
    station = SpaceStation(name="Infinity Station")

    # Add a few rooms (you can change IDs / count)
    station.add_room(SmartRoom(room_id="R1"))
    station.add_room(SmartRoom(room_id="R2"))
    station.add_room(SmartRoom(room_id="Control"))

    return station


def run_simulation(frames: int = 2000, dt: float = 0.01, steps_per_frame: int = 3):
    # Networking setup (optional but enabled by default here)
    global network_server
    network_server = StationServer()
    network_server.start()

    # 1) Build universe
    universe = create_nice_orbits_system()

    # 2) Wrap with adapter (so we get EnvironmentState) without double-stepping in animation
    adapter = UniverseAdapter(universe)

    # 3) Build space station
    station = build_station()

    # 4) Create a RoomNode per room to send status + receive commands
    room_nodes = []
    for room in station.rooms.values():
        node = RoomNode(room)
        node.connect()
        room_nodes.append(node)

    print(f"Running animated simulation for {frames} frames, dt={dt}, steps_per_frame={steps_per_frame}...\n")

    animate_universe(
        universe,
        station=station,
        adapter=adapter,
        room_nodes=room_nodes,
        dt=dt,
        steps_per_frame=steps_per_frame,
        frames=frames,
        show_trails=True,
        handle_collisions=True,
    )


if __name__ == "__main__":
    run_simulation(frames=2000, dt=0.01, steps_per_frame=3)
