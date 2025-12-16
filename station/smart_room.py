import time
import threading
import socket
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# Smart Room Data Model
@dataclass
class SmartRoom:
    room_id: str

    # --- sensor values ---
    temperature: float = 20.0  # in C
    target_temperature: float = 22.0  # desired temp
    occupied: bool = False
    light_level: float = 0.5  # 0.0 (dark) to 1.0 (bright)
    energy_usage_kw: float = 0.0  # current energy usage in kW

    # --- Actuator states ---
    heater_on: bool = False
    cooler_on: bool = False
    lights_on: bool = False

    # --- config thresholds ---
    comfort_min : float = 21.0
    comfort_max : float = 24.0

    def update_from_environment(self, external_temp: float, solar_flux: float, dt: float = 1.0):
        """
        Simple temperature model:
        - Room temp moves towards external_temp
        - If solar_flux > 0, room temp increases (warms up)
        """

        # passive heat exchange with outside
        alpha = 0.05 # how quickly room tends to outside
        self.temperature += alpha * (external_temp - self.temperature) * dt

        # solar heating
        self.temperature += 0.02 * solar_flux * dt

        # active heater/cooler effect
        # scale boost based on how far we are from the target
        temp_gap = self.target_temperature - self.temperature
        heater_boost = min(0.6, 0.1 * max(temp_gap, 0))
        cooler_pull = min(0.6, 0.1 * max(-temp_gap, 0))

        if self.heater_on:
            self.temperature += heater_boost * dt
        if self.cooler_on:
            self.temperature -= cooler_pull * dt

        # small random wobble keeps the signal from being perfectly flat
        self.temperature += np.random.normal(0, 0.005)

        # energy usage model
        base_usage = 0.1  # in kW

        # thermal load grows with the gap to target temp
        thermal_load_kw = min(2.5, 0.35 * abs(temp_gap))
        heater_usage = thermal_load_kw if self.heater_on else 0.0
        cooler_usage = min(2.0, 0.25 * abs(temp_gap)) if self.cooler_on else 0.0
        lights_usage = 0.2 if self.lights_on else (0.05 if self.occupied else 0.0)

        self.energy_usage_kw = base_usage + heater_usage + cooler_usage + lights_usage


    def apply_automation_rules(self):
        """
        Local automation rules:
        - Keep temperature within comfort range
        - If no one is in the room, turn off lights and relax temp control
        """
        lower = self.comfort_min
        upper = self.comfort_max

        if self.temperature < lower:
            self.heater_on = True
            self.cooler_on = False
        elif self.temperature > upper:
            self.heater_on = False
            self.cooler_on = True
        else:
            self.heater_on = False
            self.cooler_on = False

        # lights only when someone is inside and it is dark enough
        self.lights_on = self.occupied and self.light_level < 0.6

    def to_dict(self) -> Dict:
        return {
            "room_id": self.room_id,
            "temperature": self.temperature,
            "target_temperature": self.target_temperature,
            "occupied": self.occupied,
            "light_level": self.light_level,
            "energy_usage_kw": self.energy_usage_kw,
            "heater_on": self.heater_on,
            "cooler_on": self.cooler_on,
            "lights_on": self.lights_on
        }


       
