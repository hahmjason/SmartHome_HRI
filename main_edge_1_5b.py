"""
[Edge 1.5B Production-Grade Hardened Version]
Smart Home Embodied AI - Edge sLLM Controller (Raspberry Pi 4 / Embedded Linux)
- Architecture: Brain-Cerebellum Division with Semantic Action Hints
"""
import json
import time
import ollama

MODEL_NAME = 'qwen2.5:1.5b'

ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "action_type": {
            "type": "string",
            "enum": ["DETOUR_BYPASS", "PROACTIVE_SUGGEST", "EXECUTE_ORIGINAL", "FAIL_SAFE_EMERGENCY"]
        },
        "target_device": {
            "type": "string",
            "enum": ["WINDOW", "DUCT_FAN", "HEATER", "AIR_PURIFIER", "LIGHT_DIMMER", "NONE"]
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
    "required": ["action_type", "target_device", "device_param", "reason", "voice_response"]
}

SYSTEM_PROMPT = (
    "You are an active Smart Home HRI (Human-Robot Interaction) agent.\n"
    "Your job is to generate a polite, concise voice response and strict JSON control according to the Action Directive.\n"
    "Respond ONLY with valid JSON matching the schema.\n\n"
    "[Example 1 - Rain Detour]\n"
    "- User Command: \"Open all windows\"\n"
    "- Environment State: [OUTDOOR_RAIN, HUMIDITY_92%]\n"
    "- Action Directive: DETOUR_BYPASS (Target: DUCT_FAN, Forbidden: WINDOW)\n"
    "- Reason Hint: RISK_OF_RAIN_INGRESS\n"
    "[Result]\n"
    "{\n"
    "  \"action_type\": \"DETOUR_BYPASS\",\n"
    "  \"target_device\": \"DUCT_FAN\",\n"
    "  \"device_param\": 100,\n"
    "  \"reason\": \"RAIN_AND_HIGH_HUMIDITY\",\n"
    "  \"voice_response\": \"It is raining outside. Opening the window will let rain in. I am running the ventilation fan at max instead.\"\n"
    "}\n\n"
    "[Example 2 - Cold Suggestion]\n"
    "- User Command: \"Why is it so freezing in here?\"\n"
    "- Environment State: [INDOOR_COLD_13C]\n"
    "- Action Directive: PROACTIVE_SUGGEST (Target: HEATER)\n"
    "- Reason Hint: LOW_TEMPERATURE_ALERT\n"
    "[Result]\n"
    "{\n"
    "  \"action_type\": \"PROACTIVE_SUGGEST\",\n"
    "  \"target_device\": \"HEATER\",\n"
    "  \"device_param\": 24,\n"
    "  \"reason\": \"LOW_TEMPERATURE_ALERT\",\n"
    "  \"voice_response\": \"The room temperature is 13 degrees Celsius. Would you like me to turn on the heater to 24 degrees?\"\n"
    "}\n\n"
    "[Example 3 - Normal Execution]\n"
    "- User Command: \"Turn on reading light to 80 percent\"\n"
    "- Environment State: [NORMAL_CONDITIONS]\n"
    "- Action Directive: EXECUTE_ORIGINAL (Target: LIGHT_DIMMER)\n"
    "- Reason Hint: NORMAL_OPERATION\n"
    "[Result]\n"
    "{\n"
    "  \"action_type\": \"EXECUTE_ORIGINAL\",\n"
    "  \"target_device\": \"LIGHT_DIMMER\",\n"
    "  \"device_param\": 80,\n"
    "  \"reason\": \"NORMAL_OPERATION\",\n"
    "  \"voice_response\": \"Setting the reading light brightness to 80%.\"\n"
    "}"
)

def check_fail_safe_emergency(sensors: dict) -> dict:
    """0ms Hardware Fail-Safe Interrupt"""
    if sensors.get("smoke_level", 0) >= 50:
        return {
            "action_type": "FAIL_SAFE_EMERGENCY",
            "target_device": "DUCT_FAN",
            "device_param": 100,
            "reason": "CRITICAL_SMOKE_FIRE_DETECTED",
            "voice_response": "Emergency warning: Smoke detected. Activating ventilation immediately.",
            "latency_ms": 0.01,
            "source": "0ms_HW_FAIL_SAFE_INTERRUPT"
        }
    return None

def analyze_context_directives(user_voice: str, sensors: dict) -> tuple:
    """
    Context Enrichment & Directive Synthesizer:
    Calculates physical rules and constructs explicit action directives for the 1.5B sLLM.
    """
    env_tags = []
    
    out_hum = sensors.get("outdoor_humidity", 50)
    weather = sensors.get("weather", "Clear")
    air_quality = sensors.get("air_quality", "Good")
    in_temp = sensors.get("indoor_temperature", 22.0)

    is_rain = weather in ["Rainy", "Storm"] or out_hum >= 85
    is_dust = air_quality in ["Poor", "Hazardous", "YellowDust"]
    is_cold = in_temp < 16.0
    is_hot = in_temp > 28.0

    voice_lower = user_voice.lower()
    asks_window = any(w in voice_lower for w in ["window", "open", "stuffy", "fresh air"])
    asks_discomfort = any(w in voice_lower for w in ["why", "freezing", "cold", "hot", "sauna", "warm", "shivering"])

    if is_rain:
        env_tags.append(f"OUTDOOR_RAIN({out_hum}%)")
    if is_dust:
        env_tags.append(f"OUTDOOR_AIR_HAZARDOUS({air_quality})")
    if is_cold:
        env_tags.append(f"INDOOR_COLD({in_temp}C)")
    if is_hot:
        env_tags.append(f"INDOOR_HOT({in_temp}C)")

    # Compute Action Directive
    if asks_window and (is_rain or is_dust):
        directive = "DETOUR_BYPASS (Target: DUCT_FAN if rain else AIR_PURIFIER, Forbidden: WINDOW)"
        reason_hint = "RISK_OF_RAIN_INGRESS" if is_rain else "RISK_OF_FINE_DUST_INGRESS"
    elif asks_discomfort and is_cold:
        directive = "PROACTIVE_SUGGEST (Target: HEATER, Param: 24)"
        reason_hint = "LOW_TEMPERATURE_ALERT"
    elif asks_discomfort and is_hot:
        directive = "PROACTIVE_SUGGEST (Target: DUCT_FAN, Param: 100)"
        reason_hint = "HIGH_TEMPERATURE_ALERT"
    else:
        directive = "EXECUTE_ORIGINAL"
        reason_hint = "NORMAL_OPERATION"

    env_str = "[" + ", ".join(env_tags) + "]" if env_tags else "[NORMAL_CONDITIONS]"
    return env_str, directive, reason_hint, is_rain, is_dust

def apply_safety_guardrail(result: dict, is_rain: bool, is_dust: bool) -> dict:
    """Post-inference hardware sanity guardrail"""
    target = result.get("target_device", "")
    if (is_rain or is_dust) and target == "WINDOW":
        result["action_type"] = "DETOUR_BYPASS"
        result["target_device"] = "AIR_PURIFIER" if is_dust else "DUCT_FAN"
        result["device_param"] = 100
        result["reason"] = "SAFETY_GUARDRAIL_OVERRIDE"
        result["guardrail_applied"] = True
    else:
        result["guardrail_applied"] = False
    return result

def process_edge_turn(user_voice: str, sensors: dict, model: str = MODEL_NAME) -> dict:
    # 1. 0ms Emergency Fast-Path
    emergency = check_fail_safe_emergency(sensors)
    if emergency:
        return emergency

    # 2. Context Enrichment & Directive Synthesis
    env_state, directive, reason_hint, is_rain, is_dust = analyze_context_directives(user_voice, sensors)
    
    user_prompt = (
        f"[Actual Input]\n"
        f"- User Command: \"{user_voice}\"\n"
        f"- Environment State: {env_state}\n"
        f"- Action Directive: {directive}\n"
        f"- Reason Hint: {reason_hint}\n"
        f"[Result]"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    t0 = time.perf_counter()
    try:
        response = ollama.chat(
            model=model,
            messages=messages,
            format=ACTION_SCHEMA,
            options={
                'temperature': 0.0,
                'top_p': 0.1,
                'num_ctx': 512,
                'num_predict': 120,
                'num_thread': 4
            }
        )
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        raw_result = json.loads(response['message']['content'])
        raw_result["latency_ms"] = latency_ms
        raw_result["source"] = f"sLLM_{model}"
        
        final_result = apply_safety_guardrail(raw_result, is_rain, is_dust)
        return final_result

    except Exception as e:
        return {
            "error": str(e),
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
        }

if __name__ == "__main__":
    print("=" * 65)
    print("[Edge 1.5B] Production Hardened Controller")
    print("=" * 65)
