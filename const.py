IS_CONTAINER=1
VERSION="v1.0.6"
SLEEP_INTERVAL=60

ENTITIES =  {
    "grid-tied_active_power": {"type": "energy", "unit": "kWh"},
    "grid-tied_reactive_power": {"type": "power", "unit": "kW"},
    "load_power": {"type": "power", "unit": "kW"},
    "active_power": {"type": "power", "unit": "kW"},
    "reactive_power": {"type": "power", "unit": "kW"},
    "todays_power_supply_from_grid": {"type": "energy", "unit": "kWh"},
    "current_day_supply_from_grid": {"type": "energy", "unit": "kWh"},
    "current_day_feed-in_to_grid": {"type": "energy", "unit": "kWh"},
    "current_day_consumption": {"type": "energy", "unit": "kWh"},
    "total_power_supply_from_grid": {"type": "energy", "unit": "kWh"},
    "total_supply_from_grid": {"type": "energy", "unit": "kWh"},
    "total_feed-in_to_grid": {"type": "energy", "unit": "kWh", "attribute": "total_increasing"},
    "total_power_consumption": {"type": "energy", "unit": "kWh"},
    "pv_output_power": {"type": "power", "unit": "kW"},
    "battery_charge_discharge_power": {"type": "power", "unit": "kW"},
    "reactive_pv_power": {"type": "power", "unit": "kW"},
    "reactive_ess_power": {"type": "power", "unit": "kW"},
    "soc": {"type": "battery", "unit": "%"},
    "current-day_charge_capacity": {"type": "energy", "unit": "kWh"},
    "current-day_discharge_capacity": {"type": "energy", "unit": "kWh"},
    "total_charge": {"type": "energy", "unit": "kWh"},
    "total_discharge": {"type": "energy", "unit": "kWh"},
    "rated_ess_power": {"type": "power", "unit": "kW"}
}