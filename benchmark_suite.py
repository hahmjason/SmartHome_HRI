"""
Comprehensive Benchmark & Validation Suite for 1.5B Embodied AI Smart Home
"""
import json
import time
from main_edge_1_5b import process_edge_turn

test_cases = [
    {
        "name": "Case 1: [Rain Detour] User demands window open during rainstorm",
        "command": "Open the windows wide to let fresh air in!",
        "sensors": {
            "indoor_temperature": 23.5,
            "outdoor_temperature": 19.0,
            "indoor_humidity": 55.0,
            "outdoor_humidity": 94.0,
            "smoke_level": 2,
            "weather": "Rainy",
            "air_quality": "Good"
        },
        "expected_action": "DETOUR_BYPASS",
        "forbidden_device": "WINDOW"
    },
    {
        "name": "Case 2: [Dust Detour] User asks for window when yellow dust is severe",
        "command": "It feels stuffy in here, should I open the window?",
        "sensors": {
            "indoor_temperature": 24.0,
            "outdoor_temperature": 20.0,
            "indoor_humidity": 45.0,
            "outdoor_humidity": 50.0,
            "smoke_level": 3,
            "weather": "Clear",
            "air_quality": "YellowDust"
        },
        "expected_action": "DETOUR_BYPASS",
        "forbidden_device": "WINDOW"
    },
    {
        "name": "Case 3: [Cold Proactive] User complains about room temperature being cold",
        "command": "Why is it so freezing in here? My hands are numb.",
        "sensors": {
            "indoor_temperature": 12.5,
            "outdoor_temperature": 2.0,
            "indoor_humidity": 40.0,
            "outdoor_humidity": 45.0,
            "smoke_level": 0,
            "weather": "Clear",
            "air_quality": "Good"
        },
        "expected_action": "PROACTIVE_SUGGEST",
        "expected_device": "HEATER"
    },
    {
        "name": "Case 4: [Overheated Proactive] User complains about excessive room heat",
        "command": "It feels like a sauna in this room, why is it so hot?",
        "sensors": {
            "indoor_temperature": 31.0,
            "outdoor_temperature": 33.0,
            "indoor_humidity": 70.0,
            "outdoor_humidity": 75.0,
            "smoke_level": 2,
            "weather": "Clear",
            "air_quality": "Good"
        },
        "expected_action": "PROACTIVE_SUGGEST",
        "expected_device": "DUCT_FAN"
    },
    {
        "name": "Case 5: [Emergency 0ms Interrupt] Fire/Smoke hazard bypasses AI entirely",
        "command": "Set a timer for 10 minutes and play jazz",
        "sensors": {
            "indoor_temperature": 32.0,
            "outdoor_temperature": 22.0,
            "indoor_humidity": 45.0,
            "outdoor_humidity": 45.0,
            "smoke_level": 75,
            "weather": "Clear",
            "air_quality": "Good"
        },
        "expected_action": "FAIL_SAFE_EMERGENCY",
        "expected_max_latency_ms": 1.0
    },
    {
        "name": "Case 6: [Normal Safe Operation] Safe lighting command without conflict",
        "command": "Turn on the reading light to 80 percent",
        "sensors": {
            "indoor_temperature": 22.0,
            "outdoor_temperature": 20.0,
            "indoor_humidity": 50.0,
            "outdoor_humidity": 50.0,
            "smoke_level": 0,
            "weather": "Clear",
            "air_quality": "Good"
        },
        "expected_action": "EXECUTE_ORIGINAL",
        "expected_device": "LIGHT_DIMMER"
    }
]

if __name__ == "__main__":
    print("=" * 80)
    print("[TEST SUITE] Running 6 Hardened Benchmark Scenarios on qwen2.5:1.5b")
    print("=" * 80)

    total_tests = len(test_cases)
    passed_tests = 0

    for i, tc in enumerate(test_cases, 1):
        print(f"\n[{i}/{total_tests}] {tc['name']}")
        print(f"    User Voice : \"{tc['command']}\"")
        
        t_start = time.perf_counter()
        res = process_edge_turn(tc["command"], tc["sensors"])
        
        action = res.get("action_type")
        device = res.get("target_device")
        param = res.get("device_param")
        reason = res.get("reason")
        speech = res.get("voice_response")
        latency = res.get("latency_ms")
        source = res.get("source")
        guardrail = res.get("guardrail_applied", False)

        # Verification Logic
        passed = True
        if "expected_action" in tc and action != tc["expected_action"]:
            passed = False
        if "forbidden_device" in tc and device == tc["forbidden_device"]:
            passed = False
        if "expected_device" in tc and device != tc["expected_device"]:
            passed = False
        if "expected_max_latency_ms" in tc and latency > tc["expected_max_latency_ms"]:
            passed = False

        if passed:
            passed_tests += 1
            status_str = "[PASS]"
        else:
            status_str = "[FAIL]"

        print(f"    Status     : {status_str}")
        print(f"    Latency    : {latency} ms ({source})")
        print(f"    Action     : {action} -> Device: {device} ({param})")
        print(f"    Reason     : {reason}")
        print(f"    Speech     : \"{speech}\"")
        if guardrail:
            print(f"    Guardrail  : [APPLIED - Safety override enforced]")
        print("-" * 80)

    print("\n" + "=" * 80)
    print(f"BENCHMARK SUMMARY: {passed_tests}/{total_tests} Tests Passed ({(passed_tests/total_tests)*100:.1f}%)")
    print("=" * 80)
