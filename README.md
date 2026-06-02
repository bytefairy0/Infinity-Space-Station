# 🚀 Infinity-Space-Station

A physics-based space station simulator where celestial bodies orbit, collide, and your station tries to keep the lights on while dealing with cosmic nonsense.

## What's This About? 🌌

Watch a little solar system spin while your space station (Infinity Station, fancy right?) manages its rooms, energy, and temperature. It's like SimCity but in space, with actual physics™.

### Features ✨
- **N-body gravity simulation** - Stars, planets, moons, and asteroids all pulling on each other
- **Smart room management** - Multiple rooms tracking temperature and energy usage
- **Cosmic environment** - Solar flux, radiation, eclipses, oh my!
- **Real-time visualization** - Watch it all happen with fancy orbit trails
- **Networking API** - Send commands to your station while it's running (because why not)
- **Data logging & analysis** - Pretty graphs to see where all your energy went

## How To Run 🎮

### Prerequisites
```bash
pip install numpy matplotlib pandas
```

### Let It Rip
```bash
python main.py
```

Watch the universe unfold! The simulation runs for 2000 frames with 3 physics steps per frame. Adjust in `main.py` if you want chaos or boredom.

### Just Want Pretty Graphs?
Run the simulation first, then:
```bash
python visualize_log.py
```

See temperature trends, energy usage per room, and how solar flux messes with everything.

## The Universe 🌍

Starting with:
- **1 Star** (yellow, very hot, very massive)
- **2 Planets** (cyan inner boi, blue outer boi)
- **1 Moon** (white friend orbiting the blue planet)
- **20 Asteroids** (orange chaos makers)

They all follow Kepler's laws-ish orbits. Occasionally asteroids smash into things and merge. It's dramatic.

## The Station 🏗️

Three rooms (you can add more):
- **R1** - Room One (blue vibes)
- **R2** - Room Two (orange vibes)
- **Control** - The nerve center (green vibes)

Each room:
- Monitors temperature (affected by external space cold)
- Tracks energy usage (based on how hard HVAC is working)
- Responds to solar flux changes
- Complains when things get toasty ☀️

## File Guide 📁

- **main.py** - The entry point, sets up universe + station + animation
- **universe/universe.py** - Physics engine and orbital dynamics
- **visualize_log.py** - Pandas + matplotlib magic for data porn
- **station/** - The station logic, rooms, networking, etc.

## Project Structure 🗂️
```
Infinity-Space-Station/
├── main.py                 # Run this!
├── visualize_log.py        # Then run this!
├── universe/
│   └── universe.py         # Gravity goes brrr
└── station/
    ├── space_station.py    # Station HQ
    ├── smart_room.py       # Individual rooms
    ├── adapter.py          # Universe ↔️ Station bridge
    └── networking.py       # Send commands to the station
```

## What Happens During Simulation 🎬

1. **Physics loop** - All bodies compute forces, update positions
2. **Collision detection** - When things touch, they merge (conservation of momentum ftw)
3. **Station updates** - Rooms react to cosmic conditions
4. **Networking** - Room status gets broadcast (if servers are running)
5. **Visualization** - Pretty dots and lines update on screen
6. **Logging** - Everything gets saved to `station_log.csv`

## Tweak It 🎛️

Want to change stuff? Go wild:

- **More rooms**: Add to `build_station()` in `main.py`
- **More asteroids**: Crank up the loop in `create_nice_orbits_system()`
- **Faster/slower sim**: Change `dt` or `steps_per_frame`
- **Different space weather**: Edit `_update_environment_fields()` in `universe.py`
- **Chaos mode**: Enable collisions with `handle_collisions=True`

## Outputs 📊

After running, you get:
- `station_log.csv` - All the juicy telemetry data
- Animated plot (while running)
- Graphs of temperature/energy trends (from `visualize_log.py`)

## Known Quirks 🤔

- Asteroids have a teeny radius to avoid too many collisions (space is big and empty, yo)
- Gravity constant is simplified to `G=1.0` (not Earth physics, but close enough for vibes)
- Networking is optional but cool if you want to mess with the station mid-sim
- Eclipse detection is "is solar flux low?" which is... accurate enough 🤷

## Future Ideas 💡

- Actual command protocol for controlling room systems
- More detailed station modules (life support, comms, etc.)
- 3D rendering (flex harder)
- Actual aliens 👽

---

**Made with ❤️ and a little bit of physics** ⚛️

Have fun launching your space station! 🛸
