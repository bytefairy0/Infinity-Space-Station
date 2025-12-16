import time
import numpy as np
import pandas as pd
from typing import Dict, Optional
from station.smart_room import SmartRoom

FILE_PATH = "station_log.csv"

class SpaceStation:
    def __init__(self, name: str):
        self.name = name
        self.rooms: Dict[str, SmartRoom] = {}
        self.sim_time = 0.0
        self.last_external_temp: Optional[float] = None
        self.last_solar_flux: Optional[float] = None
        self.log_df = pd.DataFrame(columns=[
            "time", "room_id", "temperature", "target_temperature",
            "occupied", "light_level", "energy_usage_kw",
            "heater_on", "cooler_on", "lights_on",
            "external_temp", "solar_flux"
        ])

    def add_room(self, room: SmartRoom):
        self.rooms[room.room_id] = room

    def get_room(self, room_id: str) -> Optional[SmartRoom]:
        return self.rooms.get(room_id, None)
    
    def step(self, external_temp: float, solar_flux: float, dt: float = 1.0, env_time: Optional[float] = None):
        # track sim time so we can coordinate schedules with the universe clock
        self.sim_time = env_time if env_time is not None else self.sim_time + dt
        self.last_external_temp = external_temp
        self.last_solar_flux = solar_flux

        for room in self.rooms.values():
            self._update_room_schedule(room, solar_flux, dt)
            room.update_from_environment(external_temp, solar_flux, dt)
            room.apply_automation_rules()

        self._log_state()

    def _update_room_schedule(self, room: SmartRoom, solar_flux: float, dt: float):
        """
        Simple schedule model:
        - Brighter solar_flux => higher chance of someone being around.
        - Occupancy has persistence so it doesn't flip every frame.
        - Target temps relax when empty to save energy.
        """
        day_factor = float(np.clip(solar_flux / 2.0, 0.0, 1.0))
        stay_prob = 0.97 if room.occupied else 0.0
        arrive_prob = 0.02 + 0.35 * day_factor

        if room.occupied:
            room.occupied = np.random.rand() < stay_prob
        else:
            room.occupied = np.random.rand() < arrive_prob

        # ambient light driven by solar flux with a pinch of noise
        ambient_light = np.clip(day_factor + np.random.normal(0, 0.05), 0.0, 1.0)
        room.light_level = float(ambient_light)

        if room.occupied:
            room.target_temperature = 22.5
            room.comfort_min = 21.0
            room.comfort_max = 24.0
        else:
            room.target_temperature = 19.0
            room.comfort_min = 18.0
            room.comfort_max = 24.0

    def _log_state(self):
        timestamp = self.sim_time if self.sim_time is not None else time.time()
        records = []
        for room in self.rooms.values():
            r = room.to_dict()
            r["time"] = timestamp
            r["external_temp"] = None if self.last_external_temp is None else round(self.last_external_temp, 2)
            r["solar_flux"] = None if self.last_solar_flux is None else round(self.last_solar_flux, 3)

            # round noisy floats for clean logs
            r["temperature"] = round(r["temperature"], 2)
            r["target_temperature"] = round(r["target_temperature"], 2)
            r["energy_usage_kw"] = round(r["energy_usage_kw"], 3)
            records.append(r)

        df_new = pd.DataFrame(records)
        self.log_df = pd.concat([self.log_df, df_new], ignore_index=True)

    def total_energy_usage(self) -> float:
        return float(np.array([r.energy_usage_kw for r in self.rooms.values()]).sum())
    
    def summary(self) -> pd.DataFrame:
        if self.log_df.empty:
            print("No log yet.")
            return pd.DataFrame()
        
        return self.log_df.groupby("room_id").agg(
            avg_temp = ("temperature", "mean"),
            avg_energy = ("energy_usage_kw", "mean"),
            max_temp = ("temperature", "max"),
            min_temp = ("temperature", "min")
        )
    
    def save_log(self, FILE_PATH: str):
        self.log_df.to_csv(FILE_PATH, index=False, float_format="%.2f")
        print(f"Log saved to {FILE_PATH}")
       
