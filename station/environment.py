from dataclasses import dataclass

@dataclass
class EnvironmentState:
    t: float
    external_temp: float
    solar_flux: float
    radiation: float
    eclipse: bool = False
    meteor_alert: bool = False
