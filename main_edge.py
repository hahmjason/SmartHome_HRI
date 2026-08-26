"""
Smart Home Embodied AI - Edge sLLM Controller (Raspberry Pi & Desktop Compatible)
"""
import json
import time
import ollama
from context_preprocessor import EdgeContextPreprocessor
from prompt_engine import SYSTEM_PROMPT, build_actual_input

# Default lightweight model suitable for Raspberry Pi
# (e.g., 'qwen2.5:1.5b', 'qwen2.5:0.5b', or 'qwen2.5:7b')
MODEL_NAME = 'qwen2.5:1.5b'

# Strict JSON Schema for Ollama / llama.cpp
ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "action_type": {
            "type": "string",
            "enum": ["EXECUTE_ORIGINAL", "DETOUR_BYPASS", "PROACTIVE_SUGGEST", "FAIL_SAFE_EMERGENCY"]
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

def run_embodied_ai_turn(user_voice: str, sensors: dict, model: str = MODEL_NAME) -> dict:
    preprocessor = EdgeContextPreprocessor()
    
    # 1. 0ms Fast-Path Fail-Safe Check (Hardware Interrupt level)
    emergency = preprocessor.check_fail_safe_emergency(sensors)
    if emergency:
        emergency["latency_ms"] = 0.01
        emergency["source"] = "HW_FAIL_SAFE_INTERRUPT"
        return emergency

    # 2. Context Enrichment
    env_state, conflict_elem, available_devs = preprocessor.enrich_context(sensors)
    user_prompt = build_actual_input(user_voice, env_state, conflict_elem, available_devs)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    # 3. sLLM Inference with RPi Edge Optimized Options
    t0 = time.perf_counter()
    try:
        response = ollama.chat(
            model=model,
            messages=messages,
            format=ACTION_SCHEMA,
            options={
                'temperature': 0.0,
                'top_p': 0.1,
                'num_ctx': 512,        # Ultra-compact context for low RAM & high speed
                'num_predict': 120,     # Max token cap for fast JSON generation
                'num_thread': 4         # Quad-core RPi optimization
            }
        )
        t1 = time.perf_counter()
        elapsed_ms = round((t1 - t0) * 1000, 2)

        content = response['message']['content']
        parsed_result = json.loads(content)
        parsed_result["latency_ms"] = elapsed_ms
        parsed_result["source"] = f"sLLM_{model}"
        return parsed_result
    except Exception as e:
        return {
            "error": str(e),
            "raw_response": response.get('message', {}).get('content') if 'response' in locals() else None,
            "latency_ms": round((time.perf_counter() - t0) * 1000, 2)
        }

if __name__ == "__main__":
    print("=" * 60)
    print("🏠 Embodied AI Smart Home Brain (Edge sLLM Optimized)")
    print("=" * 60)

    # Test Scenario: Dust & Poor air quality outside, user asks to open window
    sample_sensors = {
        "indoor_temperature": 23.5,
        "outdoor_temperature": 20.0,
        "indoor_humidity": 45.0,
        "outdoor_humidity": 45.0,
        "smoke_level": 5,
        "weather": "Clear",
        "air_quality": "YellowDust"
    }

    test_commands = [
        "It feels stuffy in here, should I open the window?",
        "Turn on the heater please",
        "Why is it vibrating?"
    ]

    for cmd in test_commands:
        print(f"\n🗣️ Voice Input: \"{cmd}\"")
        result = run_embodied_ai_turn(cmd, sample_sensors)
        print("🤖 Decision Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
