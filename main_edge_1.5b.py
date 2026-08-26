"""
[Edge 1.5B Optimized Version]
Smart Home Embodied AI - Edge sLLM Controller (Raspberry Pi 4 / Embedded Linux)
- Model: qwen2.5:1.5b (or 0.5b / llama.cpp / Q4_K_M)
- Architecture: Brain-Cerebellum 분리, Context Enrichment, Few-Shot Detour HRI, 0ms Fail-Safe
- Output: Strict JSON schema (Adhering to schema.gbnf)
"""
import json
import time
import ollama

# ==============================================================================
# 1. Configuration & Schema Definition
# ==============================================================================
MODEL_NAME = 'qwen2.5:1.5b'

ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "action_type": {
            "type": "string",
            "enum": ["EXECUTE_ORIGINAL", "DETOUR_BYPASS", "PROACTIVE_SUGGEST"]
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

# ==============================================================================
# 2. High-Density English Few-Shot System Prompt
# ==============================================================================
SYSTEM_PROMPT = (
    "You are an active Smart Home HRI (Human-Robot Interaction) control agent.\n"
    "Analyze user commands against environmental constraints to determine the optimal action.\n"
    "Respond ONLY with a valid JSON adhering to the specified schema.\n"
    "Action types: [\"EXECUTE_ORIGINAL\", \"DETOUR_BYPASS\", \"PROACTIVE_SUGGEST\"]\n"
    "Target devices: [\"WINDOW\", \"DUCT_FAN\", \"HEATER\", \"AIR_PURIFIER\", \"LIGHT_DIMMER\", \"NONE\"]\n\n"
    "[Example 1]\n"
    "- User Command: \"Open the windows wide\"\n"
    "- Environment State: [OUTDOOR_HEAVY_RAIN, OUTDOOR_HUMIDITY_92%]\n"
    "- Conflict Element: High humidity and rainwater ingress risk\n"
    "- Available Alternative: DUCT_FAN\n"
    "[Result]\n"
    "{\n"
    "  \"action_type\": \"DETOUR_BYPASS\",\n"
    "  \"target_device\": \"DUCT_FAN\",\n"
    "  \"device_param\": 100,\n"
    "  \"reason\": \"RAIN_AND_HIGH_HUMIDITY\",\n"
    "  \"voice_response\": \"It is raining heavily outside. Opening the window will increase humidity. I will run the ventilation fan at max instead.\"\n"
    "}\n\n"
    "[Example 2]\n"
    "- User Command: \"Why is it buzzing?\"\n"
    "- Environment State: [INDOOR_COLD_14C, Haptic knock standby]\n"
    "- Conflict Element: Low indoor temperature detected\n"
    "- Available Alternative: HEATER\n"
    "[Result]\n"
    "{\n"
    "  \"action_type\": \"PROACTIVE_SUGGEST\",\n"
    "  \"target_device\": \"HEATER\",\n"
    "  \"device_param\": 24,\n"
    "  \"reason\": \"LOW_TEMPERATURE_ALERT\",\n"
    "  \"voice_response\": \"The room temperature is 14 degrees Celsius, which is quite chilly. Would you like me to turn on the heater to 24 degrees?\"\n"
    "}"
)

# ==============================================================================
# 3. Context Enrichment & Fail-Safe Module
# ==============================================================================
def check_fail_safe_emergency(sensors: dict) -> dict:
    """0ms Hardware Fail-Safe Interrupt (Bypasses LLM completely for smoke/fire)"""
    if sensors.get("smoke_level", 0) >= 50:
        return {
            "action_type": "FAIL_SAFE_EMERGENCY",
            "target_device": "DUCT_FAN",
            "device_param": 100,
            "reason": "CRITICAL_SMOKE_FIRE_DETECTED",
            "voice_response": "Emergency: Smoke detected. Maximum ventilation activated immediately.",
            "latency_ms": 0.01,
            "source": "0ms_HW_FAIL_SAFE_INTERRUPT"
        }
    return None

def enrich_context(sensors: dict) -> tuple:
    """Preprocesses raw sensor telemetry into semantic tags to reduce sLLM reasoning load"""
    env_tags = []
    conflict_tags = []
    
    out_hum = sensors.get("outdoor_humidity", 50)
    weather = sensors.get("weather", "Clear")
    air_quality = sensors.get("air_quality", "Good")
    in_temp = sensors.get("indoor_temperature", 22.0)

    if weather in ["Rainy", "Storm"] or out_hum >= 85:
        env_tags.append(f"OUTDOOR_RAIN_OR_HIGH_HUMIDITY({out_hum}%)")
        conflict_tags.append("RISK_OF_RAIN_AND_MOISTURE_INGRESS")

    if air_quality in ["Poor", "Hazardous", "YellowDust"]:
        env_tags.append(f"OUTDOOR_AIR_HAZARDOUS({air_quality})")
        conflict_tags.append("RISK_OF_FINE_DUST_INGRESS")

    if in_temp < 16.0:
        env_tags.append(f"INDOOR_COLD({in_temp}C)")
        conflict_tags.append("LOW_INDOOR_TEMPERATURE")
    elif in_temp > 28.0:
        env_tags.append(f"INDOOR_OVERHEATED({in_temp}C)")
        conflict_tags.append("HIGH_INDOOR_TEMPERATURE")

    env_str = "[" + ", ".join(env_tags) + "]" if env_tags else "[NORMAL_CONDITIONS]"
    conflict_str = ", ".join(conflict_tags) if conflict_tags else "NONE"
    available_devices = "WINDOW, DUCT_FAN, HEATER, AIR_PURIFIER, LIGHT_DIMMER"

    return env_str, conflict_str, available_devices

# ==============================================================================
# 4. Core Edge Inference Pipeline
# ==============================================================================
def process_edge_turn(user_voice: str, sensors: dict, model: str = MODEL_NAME) -> dict:
    # Step 1: 0ms Emergency check
    emergency = check_fail_safe_emergency(sensors)
    if emergency:
        return emergency

    # Step 2: Context Enrichment
    env_state, conflict_elem, available_devs = enrich_context(sensors)
    user_prompt = (
        f"[Actual Input]\n"
        f"- User Command: \"{user_voice}\"\n"
        f"- Environment State: {env_state}\n"
        f"- Conflict Element: {conflict_elem}\n"
        f"- Available Alternative: {available_devs}\n"
        f"[Result]"
    )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    # Step 3: Fast constrained inference (Optimized for RPi ARM CPU)
    t0 = time.perf_counter()
    try:
        response = ollama.chat(
            model=model,
            messages=messages,
            format=ACTION_SCHEMA,
            options={
                'temperature': 0.0,
                'top_p': 0.1,
                'num_ctx': 512,        # Minimal context for fast prefill
                'num_predict': 120,     # Strict output length cap
                'num_thread': 4         # Quad-core utilization
            }
        )
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        result = json.loads(response['message']['content'])
        result["latency_ms"] = latency_ms
        result["source"] = f"sLLM_{model}"
        return result
    except Exception as e:
        return {
            "error": str(e),
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
        }

# ==============================================================================
# 5. Interactive Execution
# ==============================================================================
if __name__ == "__main__":
    print("=" * 65)
    print("🚀 [Edge 1.5B] Smart Home Embodied AI - Edge Controller Active")
    print(f"📌 Model: {MODEL_NAME} | Optimization: Strict JSON + RPi Tuned")
    print("=" * 65)

    # Current Sensor Snapshot
    current_sensors = {
        "indoor_temperature": 23.0,
        "outdoor_temperature": 18.0,
        "indoor_humidity": 45.0,
        "outdoor_humidity": 50.0,
        "smoke_level": 5,
        "weather": "Clear",
        "air_quality": "YellowDust"
    }

    print(f"\n📡 Current Sensor Context: {current_sensors}")

    while True:
        user_voice = input("\n🗣️ User Voice Command (exit to quit): ")
        if user_voice.strip().lower() == 'exit':
            break
        if not user_voice.strip():
            continue

        result = process_edge_turn(user_voice, current_sensors)
        
        print("\n" + "=" * 45)
        print("🖥️ [Pico 2 W / Edge Decision Output]")
        print(f"⏱️ Latency       : {result.get('latency_ms')} ms ({result.get('source')})")
        print(f"🎯 Action Type  : {result.get('action_type')}")
        print(f"🔌 Target Device: {result.get('target_device')} (Param: {result.get('device_param')})")
        print(f"💡 Reason       : {result.get('reason')}")
        print(f"🔊 Voice Speech : \"{result.get('voice_response')}\"")
        print("=" * 45)
