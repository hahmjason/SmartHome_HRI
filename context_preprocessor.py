"""
Cerebellum-to-Brain Context Enrichment & Fail-Safe Layer
Preprocesses raw sensor data into high-density semantic tags and handles 0ms emergency interrupts.
"""
from typing import Dict, Any, Tuple, Optional

class EdgeContextPreprocessor:
    def __init__(self):
        pass

    def check_fail_safe_emergency(self, sensors: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        0ms Hardware Fail-Safe Interrupt:
        Emergency situations (e.g. smoke/fire) bypass LLM completely for instantaneous actuation.
        """
        smoke = sensors.get("smoke_level", 0)
        if smoke >= 50:
            return {
                "action_type": "FAIL_SAFE_EMERGENCY",
                "target_device": "DUCT_FAN",
                "device_param": 100,
                "reason": "CRITICAL_SMOKE_FIRE_DETECTED",
                "voice_response": "Emergency warning: Smoke detected. Activating ventilation immediately."
            }
        return None

    def enrich_context(self, sensors: Dict[str, Any]) -> Tuple[str, str, str]:
        """
        Transforms raw sensor numbers into semantic tags for the sLLM:
        Returns: (env_state_tag, conflict_tag, available_devices_tag)
        """
        in_temp = sensors.get("indoor_temperature", 22.0)
        out_temp = sensors.get("outdoor_temperature", 20.0)
        in_humidity = sensors.get("indoor_humidity", 50.0)
        out_humidity = sensors.get("outdoor_humidity", 50.0)
        weather = sensors.get("weather", "Clear")
        air_quality = sensors.get("air_quality", "Good")

        env_tags = []
        conflict_tags = []
        available_devices = ["WINDOW", "DUCT_FAN", "HEATER", "AIR_PURIFIER", "LIGHT_DIMMER"]

        # Weather & Rain / Humidity analysis
        if weather in ["Rainy", "Storm"] or out_humidity >= 85:
            env_tags.append(f"OUTDOOR_RAIN_OR_HIGH_HUMIDITY({out_humidity}%)")
            conflict_tags.append("RISK_OF_RAIN_AND_MOISTURE_INGRESS")

        # Air Quality analysis
        if air_quality in ["Poor", "Hazardous", "YellowDust"]:
            env_tags.append(f"OUTDOOR_AIR_HAZARDOUS({air_quality})")
            conflict_tags.append("RISK_OF_FINE_DUST_INGRESS")

        # Temperature analysis
        if in_temp < 16.0:
            env_tags.append(f"INDOOR_COLD({in_temp}C)")
            conflict_tags.append("LOW_INDOOR_TEMPERATURE")
        elif in_temp > 28.0:
            env_tags.append(f"INDOOR_OVERHEATED({in_temp}C)")
            conflict_tags.append("HIGH_INDOOR_TEMPERATURE")

        env_str = "[" + ", ".join(env_tags) + "]" if env_tags else "[NORMAL_CONDITIONS]"
        conflict_str = ", ".join(conflict_tags) if conflict_tags else "NONE"
        devices_str = ", ".join(available_devices)

        return env_str, conflict_str, devices_str
