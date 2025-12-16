from .environment import EnvironmentState


class UniverseAdapter:
    """
    Wraps your existing universe simulation object.

    You must edit the attribute names inside step() to match your universe code.
    Example mapping:
      self.u.time -> t
      self.u.T_space -> external_temp
      self.u.sun_intensity -> solar_flux
    """

    def __init__(self, universe_sim):
        self.u = universe_sim

    def step(self, dt: float = 1.0, advance_universe: bool = True) -> EnvironmentState:
        """
        Build an EnvironmentState from the universe.
        Set advance_universe=False when the simulation already advanced
        (e.g., inside matplotlib animation) to avoid double-stepping.
        """
        if advance_universe:
            # Advance the universe if requested.
            self.u.step(dt)

        # Map your universe variables -> EnvironmentState fields
        # Change these attribute names to match YOUR code:
        t = getattr(self.u, "t", getattr(self.u, "time", 0.0))
        external_temp = getattr(self.u, "external_temp", getattr(self.u, "space_temp", -80.0))
        solar_flux = getattr(self.u, "solar_flux", getattr(self.u, "sun_intensity", 0.0))

        radiation = getattr(self.u, "radiation", 0.0)
        eclipse = getattr(self.u, "eclipse", False)
        meteor_alert = getattr(self.u, "meteor_alert", False)

        return EnvironmentState(
            t=t,
            external_temp=external_temp,
            solar_flux=solar_flux,
            radiation=radiation,
            eclipse=eclipse,
            meteor_alert=meteor_alert,
        )
