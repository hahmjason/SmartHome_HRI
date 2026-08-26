"""
Physical Hardware HAL & Simulation Layer (Miniature Smart Home Physical Twin)
Covers all 6 subsystems defined in Table 1 of the Project Proposal:
1. Lights: BH1750 Lux, RGB LED, PID Fade-in/Fade-out Module
2. Ventilation: MQ-2 Gas/Smoke, MQ135 Air Quality, 12V Duct Cooling Fan, Relay
3. Openings: SG90 Servos (Window, Blind), 28BYJ-48 Stepper, 12V Solenoid Doorlock
4. Plant Care: Soil Moisture Sensor, 5V Mini Water Pump
5. Environment: Dual SHT31 (Indoor & Outdoor Temp/Humidity)
6. HRI Feedback: Coin Haptic Motor, I2S Audio Audio/TTS
"""
import time
import math
from typing import Dict, Any

class MiniatureSmartHomeHAL:
    def __init__(self):
        # 1. Environment & Sensor Telemetry
        self.sensors = {
            "indoor_temp": 22.0,
            "outdoor_temp": 18.0,
            "indoor_humidity": 50.0,
            "outdoor_humidity": 92.0,
            "lux": 10.0,
            "smoke_level": 5,        # 0 - 100 (Safe < 30, Warning 30-50, Danger >= 50)
            "soil_moisture": 45,     # 0 - 100% (Dry < 30%)
            "air_quality": "Good",
            "weather": "Rainy",
            "time_str": "03:00",     # 24H clock
            "user_present": True,
            "user_state": "RESTING"  # SLEEPING, RESTING, ACTIVE, AWAY
        }

        # 2. Actuator States
        self.actuators = {
            "window_angle": 0,       # 0 - 90 degrees
            "blind_open_percent": 0, # 0 - 100%
            "doorlock_unlocked": False,
            "duct_fan_pwm": 0,       # 0 - 100%
            "heater_on": False,
            "heater_target_temp": 20,
            "air_purifier_pwm": 0,
            "water_pump_on": False,
            "light_brightness": 0,   # 0 - 100%
            "light_color_temp": 3000,# Kelvin
            "haptic_vibration_active": False,
            "haptic_pattern": "NONE" # NONE, GENTLE_PULSE, RAPID_BUZZ
        }

    def update_environment(self, updates: Dict[str, Any]):
        self.sensors.update(updates)

    def apply_actuators(self, command: Dict[str, Any]):
        """Applies PID or direct actuation commands to physical devices"""
        for k, v in command.items():
            if k in self.actuators:
                self.actuators[k] = v

    def simulate_pid_light_fade_in(self, target_brightness: int = 20, duration_sec: float = 1.0) -> list:
        """Simulates soft PID fade-in curve to protect dark-adapted human pupils"""
        steps = []
        current = 0.0
        kp, ki, kd = 0.6, 0.05, 0.1
        dt = 0.1
        error_integral = 0.0
        last_error = float(target_brightness)

        t = 0.0
        while t < duration_sec and current < target_brightness - 0.5:
            error = float(target_brightness) - current
            error_integral += error * dt
            derivative = (error - last_error) / dt
            control = kp * error + ki * error_integral + kd * derivative
            current = min(float(target_brightness), current + control * dt)
            steps.append((round(t, 2), round(current, 1)))
            last_error = error
            t += dt

        self.actuators["light_brightness"] = target_brightness
        return steps

    def get_telemetry_snapshot(self) -> Dict[str, Any]:
        return {
            "sensors": dict(self.sensors),
            "actuators": dict(self.actuators)
        }
