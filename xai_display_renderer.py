"""
Explainable AI (XAI) 3-Split Display Interface (Pico 2 W / 3.5" 320x480 TFT LCD)
Implements Section 8 of the Project Proposal:
- Left: Hardware Telemetry & Actuator Gauges
- Center: AI Chain of Thought (CoT) Reasoning Pipeline
- Top Right: System Vitals, Inference Latency, and FSM State Indicator
"""
from typing import Dict, Any, List

class XAIDisplayRenderer:
    def __init__(self):
        self.state_colors = {
            "IDLE": "\033[92m[IDLE]\033[0m",
            "OBSERVING": "\033[96m[OBSERVING - Social Cue Active]\033[0m",
            "INTERACTING": "\033[93m[INTERACTING - Active HRI]\033[0m",
            "EMERGENCY": "\033[91m[EMERGENCY - FAIL-SAFE]\033[0m"
        }

    def render_frame(self, 
                     sensors: Dict[str, Any], 
                     actuators: Dict[str, Any], 
                     cot_steps: List[str], 
                     decision: Dict[str, Any], 
                     fsm_state: str) -> str:
        
        state_tag = self.state_colors.get(fsm_state, f"[{fsm_state}]")
        latency = decision.get("latency_ms", 0.0)
        source = decision.get("source", "sLLM_1.5b")

        # Visual gauges
        win_deg = actuators.get("window_angle", 0)
        fan_pwm = actuators.get("duct_fan_pwm", 0)
        light_pct = actuators.get("light_brightness", 0)
        soil_pct = sensors.get("soil_moisture", 50)
        in_temp = sensors.get("indoor_temp", 22.0)
        out_temp = sensors.get("outdoor_temp", 18.0)
        in_hum = sensors.get("indoor_humidity", 50.0)
        out_hum = sensors.get("outdoor_humidity", 50.0)
        smoke = sensors.get("smoke_level", 0)

        gauge_fan = "#" * (fan_pwm // 10) + "-" * (10 - (fan_pwm // 10))
        gauge_light = "#" * (light_pct // 10) + "-" * (10 - (light_pct // 10))
        gauge_soil = "#" * (soil_pct // 10) + "-" * (10 - (soil_pct // 10))

        frame = []
        frame.append("+" + "=" * 76 + "+")
        frame.append(f"|  [Pico 2 W XAI 3.5\" TFT Display]  State: {state_tag:<32} Latency: {latency:6.2f}ms |")
        frame.append("+" + "-" * 76 + "+")
        frame.append(f"| [1. HARDWARE GAUGES]          | [2. AI CHAIN OF THOUGHT (CoT) REASONING]  |")
        frame.append(f"| - In/Out Temp: {in_temp:4.1f}C / {out_temp:4.1f}C | 1. Input  : {cot_steps[0] if len(cot_steps)>0 else 'None':<33} |")
        frame.append(f"| - In/Out Hum : {in_hum:4.1f}% / {out_hum:4.1f}% | 2. Context: {cot_steps[1] if len(cot_steps)>1 else 'None':<33} |")
        frame.append(f"| - Smoke Level: {smoke:4d} / 100       | 3. Risk   : {cot_steps[2] if len(cot_steps)>2 else 'None':<33} |")
        frame.append(f"| - Soil Moist : [{gauge_soil}] {soil_pct:3d}% | 4. Detour : {cot_steps[3] if len(cot_steps)>3 else 'None':<33} |")
        frame.append(f"| - Window     : {win_deg:3d} deg         | 5. Action : {decision.get('action_type', 'NONE'):<33} |")
        frame.append(f"| - Duct Fan   : [{gauge_fan}] {fan_pwm:3d}% | 6. Target : {decision.get('target_device', 'NONE')} ({decision.get('device_param', 0)}) {'':<18} |")
        frame.append(f"| - Light Dim  : [{gauge_light}] {light_pct:3d}% | 7. Speech : \"{decision.get('voice_response', '')[:30]}...\" |")
        frame.append("+" + "=" * 76 + "+")
        return "\n".join(frame)
