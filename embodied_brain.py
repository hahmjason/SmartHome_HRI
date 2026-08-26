"""
Unified Master Embodied AI Brain Engine (with Strict Directive Adherence & Dual Output Logging)
"""
import json
import time
import ollama
from typing import Dict, Any, Tuple
from physical_world_sim import MiniatureSmartHomeHAL
from fsm_state_machine import SmartHomeFSM, SystemState
from xai_display_renderer import XAIDisplayRenderer
from dual_output_logger import DualOutputLogger

MODEL_NAME = 'qwen2.5:1.5b'

ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "human_state_simulation": {
            "type": "string",
            "description": "Biological and cognitive state analysis of the human (circadian rhythm, dark adaptation, thermal comfort)."
        },
        "physical_reasoning": {
            "type": "string",
            "description": "First-principles deduction of environmental physics and detour mechanics."
        },
        "action_type": {
            "type": "string",
            "enum": ["DETOUR_BYPASS", "PROACTIVE_SUGGEST", "EXECUTE_ORIGINAL", "FAIL_SAFE_EMERGENCY", "BACKGROUND_AUTONOMOUS"]
        },
        "target_device": {
            "type": "string",
            "enum": ["WINDOW", "DUCT_FAN", "HEATER", "AIR_PURIFIER", "LIGHT_DIMMER", "WATER_PUMP", "HAPTIC_MOTOR", "NONE"]
        },
        "device_param": {
            "type": "integer"
        },
        "reason": {
            "type": "string"
        },
        "voice_response": {
            "type": "string"
        }
    },
    "required": [
        "human_state_simulation",
        "physical_reasoning",
        "action_type",
        "target_device",
        "device_param",
        "reason",
        "voice_response"
    ]
}

SYSTEM_PROMPT = (
    "You are an active Smart Home HRI Embodied AI Brain.\n"
    "You must perform two cognitive steps before actuating:\n"
    "1. Infer Human Physiology (human_state_simulation): Analyze circadian rhythm, dark adaptation, or thermal discomfort.\n"
    "2. Physical & Biology Deduction (physical_reasoning): Deduce aerodynamics, rainwater ingress, or thermal transfer.\n\n"
    "IMPORTANT: You MUST strictly set action_type and target_device to match the Action Directive given in the input.\n\n"
    "[Example 1 - Rain Detour]\n"
    "- User Command: \"Open all windows wide\"\n"
    "- Environment State: [OUTDOOR_RAIN, HUMIDITY_95%]\n"
    "- Action Directive: DETOUR_BYPASS (Target: DUCT_FAN, Forbidden: WINDOW)\n"
    "- Reason Hint: RISK_OF_RAIN_INGRESS\n"
    "[Result]\n"
    "{\n"
    "  \"human_state_simulation\": \"User seeks fresh air due to stuffiness, unaware of heavy rain outside.\",\n"
    "  \"physical_reasoning\": \"Opening window breaks physical barrier causing immediate rain ingress. Forced convection via Duct Fan safely ventilates.\",\n"
    "  \"action_type\": \"DETOUR_BYPASS\",\n"
    "  \"target_device\": \"DUCT_FAN\",\n"
    "  \"device_param\": 100,\n"
    "  \"reason\": \"RAIN_AND_HIGH_HUMIDITY\",\n"
    "  \"voice_response\": \"It is raining heavily outside. Opening the window will let rain in. I will run the ventilation fan at max instead.\"\n"
    "}\n\n"
    "[Example 2 - Cold Proactive HRI]\n"
    "- User Command: \"Why did you vibrate?\"\n"
    "- Environment State: [INDOOR_COLD_13C]\n"
    "- Action Directive: PROACTIVE_SUGGEST (Target: HEATER)\n"
    "- Reason Hint: LOW_TEMPERATURE_ALERT\n"
    "[Result]\n"
    "{\n"
    "  \"human_state_simulation\": \"User noticed the non-verbal haptic social cue. Room at 13C risks hypothermia.\",\n"
    "  \"physical_reasoning\": \"Resistive heating to 24C restores human thermal comfort without sudden startling alarms.\",\n"
    "  \"action_type\": \"PROACTIVE_SUGGEST\",\n"
    "  \"target_device\": \"HEATER\",\n"
    "  \"device_param\": 24,\n"
    "  \"reason\": \"LOW_TEMPERATURE_ALERT\",\n"
    "  \"voice_response\": \"The room temperature is 13 degrees Celsius, which is quite chilly. Would you like me to turn on the heater to 24 degrees?\"\n"
    "}\n\n"
    "[Example 3 - Dawn Dimming Adaptation]\n"
    "- User Command: \"Turn on the lights\"\n"
    "- Environment State: [TIME_03:00, COMPLETE_DARKNESS, DARK_ADAPTED_PUPILS]\n"
    "- Action Directive: EXECUTE_ORIGINAL (Target: LIGHT_DIMMER, MaxParam: 20)\n"
    "- Reason Hint: DARK_ADAPTATION_PROTECTION\n"
    "[Result]\n"
    "{\n"
    "  \"human_state_simulation\": \"User awakened during circadian rest. Pupils are fully dilated in 0 Lux darkness; 100% light causes retinal pain.\",\n"
    "  \"physical_reasoning\": \"Soft photon emission capped at 20% with PID fade-in protects rhodopsin photopigments.\",\n"
    "  \"action_type\": \"EXECUTE_ORIGINAL\",\n"
    "  \"target_device\": \"LIGHT_DIMMER\",\n"
    "  \"device_param\": 20,\n"
    "  \"reason\": \"NIGHT_SOFT_FADE_IN\",\n"
    "  \"voice_response\": \"Fading in the light gently to 20% brightness to protect your eyes.\"\n"
    "}"
)

class EmbodiedSmartHomeBrain:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self.hal = MiniatureSmartHomeHAL()
        self.fsm = SmartHomeFSM()
        self.renderer = XAIDisplayRenderer()
        self.logger = DualOutputLogger()

    def process_turn(self, user_voice: str = None, save_logs: bool = True) -> Tuple[Dict[str, Any], str, str, str]:
        sensors = self.hal.sensors

        # 1. Update FSM State
        state = self.fsm.evaluate_state_transition(sensors, user_voice)

        # 2. Scenario C-1: 0ms EMERGENCY Hardware Fast-Path
        if state == SystemState.EMERGENCY:
            decision = {
                "human_state_simulation": "Critical hazard detected. Immediate risk of smoke inhalation and asphyxiation.",
                "physical_reasoning": "Toxic combustion gas density rising rapidly. 0ms preemption bypasses LLM to evacuate smoke and unlock escape path.",
                "action_type": "FAIL_SAFE_EMERGENCY",
                "target_device": "DUCT_FAN",
                "device_param": 100,
                "reason": "CRITICAL_SMOKE_FIRE_DETECTED",
                "voice_response": "Emergency warning: Smoke detected. Max ventilation activated, windows opened, door unlocked.",
                "latency_ms": 0.01,
                "source": "0ms_FreeRTOS_Interrupt"
            }
            self.hal.apply_actuators({
                "duct_fan_pwm": 100,
                "window_angle": 90,
                "blind_open_percent": 100,
                "doorlock_unlocked": True
            })
            cot = ["Emergency Trigger", "Smoke Sensor Critical", "Danger Level 100", "0ms HW Bypass", "All Open"]
            frame = self.renderer.render_frame(sensors, self.hal.actuators, cot, decision, state.value)
            
            json_path, txt_path = "", ""
            if save_logs:
                json_path, txt_path = self.logger.save_turn_artifacts(user_voice, sensors, decision, state.value, prefix="emergency")
            return decision, frame, json_path, txt_path

        # 3. Scenario D: Background Autonomous Plant Care
        if not user_voice and sensors.get("soil_moisture", 50) < 30 and sensors.get("user_state") in ["SLEEPING", "RESTING", "AWAY"]:
            decision = {
                "human_state_simulation": "User is currently resting or sleeping. Auditory alerts must be suppressed to avoid disrupting sleep cycle.",
                "physical_reasoning": "Soil volumetric water content is below 30% wilting point. 5V diaphragm pump provides silent micro-irrigation.",
                "action_type": "BACKGROUND_AUTONOMOUS",
                "target_device": "WATER_PUMP",
                "device_param": 100,
                "reason": "SOIL_MOISTURE_BELOW_THRESHOLD",
                "voice_response": "",
                "latency_ms": 0.05,
                "source": "Background_Homeostasis_Daemon"
            }
            self.hal.apply_actuators({"water_pump_on": True})
            self.hal.sensors["soil_moisture"] = 65
            cot = ["Low Soil Moisture (<30%)", "User Resting/Sleeping", "Silent Background Homeostasis", "No Speech Alert", "Pump Activated"]
            frame = self.renderer.render_frame(sensors, self.hal.actuators, cot, decision, state.value)
            
            json_path, txt_path = "", ""
            if save_logs:
                json_path, txt_path = self.logger.save_turn_artifacts(user_voice, sensors, decision, state.value, prefix="plant")
            return decision, frame, json_path, txt_path

        # 4. Scenario B-1: OBSERVING State (Social Cue Generation)
        if state == SystemState.OBSERVING:
            decision = {
                "human_state_simulation": "User is active or focused. A sudden high-volume voice alert causes cognitive startle reflex.",
                "physical_reasoning": "Emitting low-frequency kinetic haptic pulse (100Hz) establishes non-verbal contact without verbal intrusion.",
                "action_type": "PROACTIVE_SUGGEST",
                "target_device": "HAPTIC_MOTOR",
                "device_param": 1,
                "reason": "NON_VERBAL_SOCIAL_CUE_EMISSION",
                "voice_response": "",
                "latency_ms": 0.05,
                "source": "FSM_Social_Cue_Engine"
            }
            self.hal.apply_actuators({
                "haptic_vibration_active": True,
                "haptic_pattern": "GENTLE_PULSE"
            })
            cot = ["Indoor Temp < 15C", "User Concentrating/Resting", "Avoid Startle Response", "Emit Gentle Haptic Pulse", "Await User Cue Response"]
            frame = self.renderer.render_frame(sensors, self.hal.actuators, cot, decision, state.value)
            
            json_path, txt_path = "", ""
            if save_logs:
                json_path, txt_path = self.logger.save_turn_artifacts(user_voice, sensors, decision, state.value, prefix="social_cue")
            return decision, frame, json_path, txt_path

        # 5. sLLM Inference (INTERACTING / IDLE with user command)
        voice_str = (user_voice or "").strip()
        voice_lower = voice_str.lower()

        env_tags = []
        is_rain = sensors.get("weather") == "Rainy" or sensors.get("outdoor_humidity", 50) >= 85
        is_dust = sensors.get("air_quality") in ["Poor", "Hazardous", "YellowDust"]
        is_cold = sensors.get("indoor_temp", 22.0) < 16.0
        is_dawn = sensors.get("time_str", "12:00") in ["02:00", "03:00", "04:00"] and sensors.get("lux", 50) < 15

        if is_rain:
            env_tags.append(f"OUTDOOR_RAIN({sensors.get('outdoor_humidity')}%)")
        if is_dust:
            env_tags.append(f"OUTDOOR_AIR_HAZARDOUS({sensors.get('air_quality')})")
        if is_cold:
            env_tags.append(f"INDOOR_COLD({sensors.get('indoor_temp')}C)")
        if is_dawn:
            env_tags.append("TIME_03:00, DARK_ADAPTED_PUPILS")

        if any(w in voice_lower for w in ["window", "open", "stuffy"]) and (is_rain or is_dust):
            directive = "DETOUR_BYPASS (Target: DUCT_FAN, Param: 100, Forbidden: WINDOW)"
            reason_hint = "RISK_OF_RAIN_INGRESS" if is_rain else "RISK_OF_FINE_DUST_INGRESS"
            cot_risk = "Rain / Dust ingress if window opened"
            cot_detour = "Detour to Duct Fan (100%)"
        elif any(w in voice_lower for w in ["why", "vibrate", "buzzing", "cold", "freeze"]) and is_cold:
            directive = "PROACTIVE_SUGGEST (Target: HEATER, Param: 24)"
            reason_hint = "LOW_TEMPERATURE_ALERT"
            cot_risk = "User acknowledges social cue (Low Temp)"
            cot_detour = "Suggest Heater at 24C"
        elif any(w in voice_lower for w in ["light", "turn on light", "불"]) and is_dawn:
            directive = "EXECUTE_ORIGINAL (Target: LIGHT_DIMMER, MaxParam: 20)"
            reason_hint = "DARK_ADAPTATION_PROTECTION"
            cot_risk = "Sudden 100% light causes pupil shock"
            cot_detour = "PID Soft Fade-in to 20%"
        else:
            directive = "EXECUTE_ORIGINAL"
            reason_hint = "NORMAL_OPERATION"
            cot_risk = "No conflict detected"
            cot_detour = "Direct Execution"

        env_str = "[" + ", ".join(env_tags) + "]" if env_tags else "[NORMAL_CONDITIONS]"
        
        user_prompt = (
            f"[Actual Input]\n"
            f"- User Command: \"{voice_str}\"\n"
            f"- Environment State: {env_str}\n"
            f"- Action Directive: {directive}\n"
            f"- Reason Hint: {reason_hint}\n"
            f"[Result]"
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        t0 = time.perf_counter()
        response = ollama.chat(
            model=self.model_name,
            messages=messages,
            format=ACTION_SCHEMA,
            options={
                'temperature': 0.0,
                'top_p': 0.1,
                'num_ctx': 512,
                'num_predict': 180,
                'num_thread': 4
            }
        )
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        decision = json.loads(response['message']['content'])
        decision["latency_ms"] = latency_ms
        decision["source"] = f"sLLM_{self.model_name}"

        target = decision.get("target_device")
        param = decision.get("device_param", 0)

        if target == "DUCT_FAN":
            self.hal.apply_actuators({"duct_fan_pwm": param})
        elif target == "HEATER":
            self.hal.apply_actuators({"heater_on": True, "heater_target_temp": param})
        elif target == "LIGHT_DIMMER":
            if is_dawn and param <= 25:
                fade_steps = self.hal.simulate_pid_light_fade_in(target_brightness=param)
                decision["pid_fade_steps"] = fade_steps
            else:
                self.hal.apply_actuators({"light_brightness": param})

        cot = [
            f"Voice: \"{voice_str[:20]}...\"",
            env_str[:25],
            cot_risk[:25],
            cot_detour[:25],
            decision.get("action_type", "")
        ]

        frame = self.renderer.render_frame(sensors, self.hal.actuators, cot, decision, state.value)
        
        json_path, txt_path = "", ""
        if save_logs:
            json_path, txt_path = self.logger.save_turn_artifacts(user_voice, sensors, decision, state.value, prefix="turn")

        return decision, frame, json_path, txt_path
