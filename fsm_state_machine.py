"""
4-State Finite State Machine (FSM) & FreeRTOS SMP Core Simulation
Implements Table 2 (State Management Logic) from the Project Proposal:
- IDLE: Sensor monitoring, background low-power mode
- OBSERVING: Threshold trigger, non-verbal social cue (gentle haptic), context caching
- INTERACTING: User responds to social cue -> sLLM proactive suggestion
- EMERGENCY: Smoke / critical trigger -> 0ms Hardware Preemption Interrupt
"""
import time
from enum import Enum
from typing import Dict, Any, Optional

class SystemState(Enum):
    IDLE = "IDLE"
    OBSERVING = "OBSERVING"
    INTERACTING = "INTERACTING"
    EMERGENCY = "EMERGENCY"

class SmartHomeFSM:
    def __init__(self):
        self.current_state = SystemState.IDLE
        self.cached_context: Optional[Dict[str, Any]] = None
        self.observing_timestamp = 0.0
        self.fallback_timeout_sec = 10.0  # If user doesn't respond within 10s, return to IDLE

    def evaluate_state_transition(self, sensors: Dict[str, Any], user_voice: Optional[str] = None) -> SystemState:
        now = time.time()
        smoke = sensors.get("smoke_level", 0)
        in_temp = sensors.get("indoor_temp", 22.0)
        voice_str = (user_voice or "").lower().strip()

        # 1. EMERGENCY (Highest Priority Interrupt)
        is_urgent_voice = any(w in voice_str for w in ["fire", "smoke", "emergency", "hurry", "quick", "빨리"])
        if smoke >= 50 or is_urgent_voice:
            self.current_state = SystemState.EMERGENCY
            self.cached_context = None
            return self.current_state

        # 2. EMERGENCY Recovery
        if self.current_state == SystemState.EMERGENCY:
            if smoke < 30 and not is_urgent_voice:
                self.current_state = SystemState.IDLE
            return self.current_state

        # 3. INTERACTING
        # Triggered when user asks a question while in OBSERVING, or speaks any explicit command
        if voice_str:
            self.current_state = SystemState.INTERACTING
            return self.current_state

        # 4. OBSERVING (Non-verbal Social Cue Mode)
        # Temperature drops below 15C or air is bad
        if in_temp < 15.0 or sensors.get("soil_moisture", 50) < 30:
            if self.current_state == SystemState.IDLE:
                self.current_state = SystemState.OBSERVING
                self.observing_timestamp = now
                self.cached_context = {
                    "reason": "LOW_TEMP" if in_temp < 15.0 else "DRY_SOIL",
                    "value": in_temp if in_temp < 15.0 else sensors.get("soil_moisture", 50),
                    "cue_type": "GENTLE_HAPTIC_PULSE"
                }
                return self.current_state

        # 5. OBSERVING Fallback Timer
        if self.current_state == SystemState.OBSERVING:
            if now - self.observing_timestamp > self.fallback_timeout_sec:
                # User did not react -> Fallback to IDLE (or quiet background regulation)
                self.current_state = SystemState.IDLE
                self.cached_context = None

        return self.current_state

    def get_state_summary(self) -> Dict[str, Any]:
        return {
            "state": self.current_state.value,
            "cached_context": self.cached_context,
            "observing_elapsed": round(time.time() - self.observing_timestamp, 1) if self.current_state == SystemState.OBSERVING else 0
        }
