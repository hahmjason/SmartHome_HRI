"""
Empirical Verification & Demonstration Suite with Dual Output Logging (JSON & TXT)
"""
import time
import json
from embodied_brain import EmbodiedSmartHomeBrain

def run_empirical_validation():
    print("=" * 80)
    print("[ACADEMIC EMPIRICAL VERIFICATION] Embodied AI Smart Home System")
    print("Proposal: Smart Home Embodied AI Proactive HRI System (Physical AI)")
    print("Features: Separate CoT Thinking Process + Dual File Logging (JSON & TXT)")
    print("=" * 80)

    brain = EmbodiedSmartHomeBrain(model_name="qwen2.5:1.5b")
    results = []

    # =========================================================================
    # Experiment 1: Scenario A - Context-based Detour
    # =========================================================================
    print("\n" + "#" * 80)
    print("[EXPERIMENT 1: SCENARIO A] Context-based Detour (Rain/Moisture)")
    print("#" * 80)
    brain.hal.update_environment({
        "indoor_temp": 24.0,
        "outdoor_temp": 20.0,
        "indoor_humidity": 60.0,
        "outdoor_humidity": 95.0,
        "smoke_level": 5,
        "weather": "Rainy",
        "air_quality": "Good",
        "time_str": "14:00"
    })
    cmd1 = "Open all windows wide please"
    print(f"User Voice: \"{cmd1}\"")
    dec1, frame1, j1, t1 = brain.process_turn(user_voice=cmd1)
    print(frame1)
    print(f"-> Full Structured JSON : {j1}")
    print(f"-> Clean Summary TXT    : {t1}")
    results.append(("Scenario A (Rain Detour)", dec1.get("action_type") == "DETOUR_BYPASS" and dec1.get("target_device") == "DUCT_FAN", dec1.get("latency_ms")))

    # =========================================================================
    # Experiment 2: Scenario B - Proactive HRI & Non-verbal Social Cue Loop
    # =========================================================================
    print("\n" + "#" * 80)
    print("[EXPERIMENT 2: SCENARIO B] Proactive HRI 2-Step Social Cue Loop")
    print("#" * 80)
    brain.hal.update_environment({
        "indoor_temp": 13.5,
        "outdoor_temp": 4.0,
        "indoor_humidity": 45.0,
        "outdoor_humidity": 45.0,
        "weather": "Clear",
        "air_quality": "Good",
        "smoke_level": 5,
        "time_str": "20:00"
    })
    print("[Phase 1] Sensor detects Indoor Temp = 13.5C (< 15C threshold). No voice command.")
    dec2_1, frame2_1, j2_1, t2_1 = brain.process_turn(user_voice=None)
    print(frame2_1)
    
    cmd2 = "Why did you vibrate just now?"
    print(f"\n[Phase 2] User Voice: \"{cmd2}\"")
    dec2_2, frame2_2, j2_2, t2_2 = brain.process_turn(user_voice=cmd2)
    print(frame2_2)
    print(f"-> Full Structured JSON : {j2_2}")
    print(f"-> Clean Summary TXT    : {t2_2}")
    results.append(("Scenario B (Social Cue -> Proactive)", dec2_2.get("action_type") == "PROACTIVE_SUGGEST" and dec2_2.get("target_device") == "HEATER", dec2_2.get("latency_ms")))

    # =========================================================================
    # Experiment 3: Scenario C-1 - Emergency 0ms Hardware Preemption
    # =========================================================================
    print("\n" + "#" * 80)
    print("[EXPERIMENT 3: SCENARIO C-1] 0ms Hardware Preemption Fail-Safe (Smoke)")
    print("#" * 80)
    brain.hal.update_environment({
        "smoke_level": 85,
        "indoor_temp": 32.0
    })
    cmd3 = "Play some relaxing music"
    print(f"User Voice: \"{cmd3}\" (Smoke level = 85)")
    dec3, frame3, j3, t3 = brain.process_turn(user_voice=cmd3)
    print(frame3)
    print(f"-> Full Structured JSON : {j3}")
    print(f"-> Clean Summary TXT    : {t3}")
    results.append(("Scenario C-1 (0ms Fail-Safe)", dec3.get("action_type") == "FAIL_SAFE_EMERGENCY" and dec3.get("latency_ms") < 1.0, dec3.get("latency_ms")))

    # =========================================================================
    # Experiment 4: Scenario C-2 - Dawn 03:00 Dark-Adaptation PID Dimming
    # =========================================================================
    print("\n" + "#" * 80)
    print("[EXPERIMENT 4: SCENARIO C-2] Dawn 03:00 Dark-Adaptation PID Light Fade-In")
    print("#" * 80)
    brain.hal.update_environment({
        "smoke_level": 2,
        "time_str": "03:00",
        "lux": 1.0,
        "indoor_temp": 21.0,
        "weather": "Clear",
        "air_quality": "Good"
    })
    cmd4 = "Turn on the lights"
    print(f"User Voice: \"{cmd4}\" at 03:00 AM in total darkness")
    dec4, frame4, j4, t4 = brain.process_turn(user_voice=cmd4)
    print(frame4)
    print(f"-> Full Structured JSON : {j4}")
    print(f"-> Clean Summary TXT    : {t4}")
    results.append(("Scenario C-2 (Dawn PID Light)", dec4.get("target_device") == "LIGHT_DIMMER" and dec4.get("device_param") <= 25, dec4.get("latency_ms")))

    # =========================================================================
    # Experiment 5: Scenario D - Silent Background Plant Homeostasis
    # =========================================================================
    print("\n" + "#" * 80)
    print("[EXPERIMENT 5: SCENARIO D] Silent Background Plant Watering Homeostasis")
    print("#" * 80)
    brain.hal.update_environment({
        "soil_moisture": 18,
        "user_state": "SLEEPING",
        "time_str": "04:00"
    })
    print("[Background Event] Soil Moisture drops to 18%. User is SLEEPING. No voice command.")
    dec5, frame5, j5, t5 = brain.process_turn(user_voice=None)
    print(frame5)
    print(f"-> Full Structured JSON : {j5}")
    print(f"-> Clean Summary TXT    : {t5}")
    results.append(("Scenario D (Plant Homeostasis)", dec5.get("action_type") == "BACKGROUND_AUTONOMOUS" and dec5.get("target_device") == "WATER_PUMP", dec5.get("latency_ms")))

    # =========================================================================
    # Final Empirical Validation Summary
    # =========================================================================
    print("\n" + "=" * 80)
    print("[FINAL EMPIRICAL VALIDATION MATRIX]")
    print("=" * 80)
    passed_cnt = 0
    for name, ok, lat in results:
        status = "PASSED [OK]" if ok else "FAILED [X]"
        if ok: passed_cnt += 1
        print(f" - {name:<35}: {status} | Latency: {lat:6.2f} ms")
    
    print("-" * 80)
    print(f"Overall Academic Feasibility Score: {passed_cnt}/{len(results)} ({(passed_cnt/len(results))*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    run_empirical_validation()
