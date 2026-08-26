"""
Interactive Smart Home Embodied AI 1.5B Test Runner
Features:
- Infinite interactive loop until 'exit'
- Voice Command input (Normal text)
- Dynamic Environmental Variable Manipulation (using '*' prefix)
- Autonomous Auto-Trigger upon Critical Environmental Change (e.g. *smoke 80 -> 0ms Emergency)
- Dual Output Logging (logs/json and logs/txt) + 3-Split XAI Display
"""
import os
import sys
import json
from embodied_brain import EmbodiedSmartHomeBrain

def print_help_menu():
    print("\n" + "=" * 70)
    print("[* Variable Command Guide]")
    print(" - *temp <value>       : Set Indoor Temperature (e.g. *temp 12.5)")
    print(" - *out_temp <value>   : Set Outdoor Temperature (e.g. *out_temp 3.0)")
    print(" - *humidity <value>   : Set Outdoor Humidity (e.g. *humidity 95)")
    print(" - *in_humidity <val>  : Set Indoor Humidity (e.g. *in_humidity 50)")
    print(" - *weather <value>    : Set Weather (e.g. *weather Rainy, *weather Clear)")
    print(" - *air <value>        : Set Air Quality (e.g. *air YellowDust, *air Good)")
    print(" - *smoke <value>      : Set Smoke/Gas Level (e.g. *smoke 85 -> 0ms Emergency)")
    print(" - *soil <value>       : Set Soil Moisture (e.g. *soil 15 -> Silent Water Pump)")
    print(" - *time <value>       : Set Time (e.g. *time 03:00, *time 14:00)")
    print(" - *user <value>       : Set User State (e.g. *user SLEEPING, *user ACTIVE)")
    print(" - *status            : Show Current Sensors & Actuators Snapshot")
    print(" - exit / quit         : Exit Program")
    print("=" * 70)

def main():
    print("=" * 75)
    print("[Embodied AI] Smart Home 1.5B Interactive Terminal Console")
    print("Model: qwen2.5:1.5b | 4-State FSM | 3-Layer Defense | 0ms Fail-Safe")
    print("=" * 75)
    print(">> Type normal speech commands (e.g. 'Open window', 'Why is it cold?')")
    print(">> Type *<cmd> to change environment variables (e.g. *smoke 85, *temp 12)")
    print(">> Type *help for full list of variable commands, or 'exit' to quit.")
    print("=" * 75)

    brain = EmbodiedSmartHomeBrain(model_name="qwen2.5:1.5b")

    while True:
        try:
            user_input = input("\n[INPUT / *ENV] >> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting program...")
            break

        if not user_input:
            continue

        if user_input.lower() in ["exit", "quit", "q"]:
            print("\n[EXIT] Smart Home Embodied AI session ended.")
            break

        # =====================================================================
        # 1. Environmental Variable Control (Prefix: '*')
        # =====================================================================
        if user_input.startswith("*"):
            parts = user_input[1:].strip().split()
            cmd = parts[0].lower() if parts else ""
            arg = parts[1] if len(parts) > 1 else ""

            if cmd == "help":
                print_help_menu()
                continue
            elif cmd == "status":
                print("\n--- [Sensors Snapshot] ---")
                print(json.dumps(brain.hal.sensors, indent=2, ensure_ascii=False))
                print("--- [Actuators Snapshot] ---")
                print(json.dumps(brain.hal.actuators, indent=2, ensure_ascii=False))
                continue
            elif cmd == "temp" and arg:
                brain.hal.sensors["indoor_temp"] = float(arg)
                print(f"[UPDATED] Indoor Temperature set to {arg} C")
            elif cmd == "out_temp" and arg:
                brain.hal.sensors["outdoor_temp"] = float(arg)
                print(f"[UPDATED] Outdoor Temperature set to {arg} C")
            elif cmd == "humidity" and arg:
                brain.hal.sensors["outdoor_humidity"] = float(arg)
                print(f"[UPDATED] Outdoor Humidity set to {arg}%")
            elif cmd == "in_humidity" and arg:
                brain.hal.sensors["indoor_humidity"] = float(arg)
                print(f"[UPDATED] Indoor Humidity set to {arg}%")
            elif cmd == "weather" and arg:
                brain.hal.sensors["weather"] = arg
                print(f"[UPDATED] Weather set to '{arg}'")
            elif cmd == "air" and arg:
                brain.hal.sensors["air_quality"] = arg
                print(f"[UPDATED] Air Quality set to '{arg}'")
            elif cmd == "smoke" and arg:
                brain.hal.sensors["smoke_level"] = int(arg)
                print(f"[ALERT] Smoke Level set to {arg}")
            elif cmd == "soil" and arg:
                brain.hal.sensors["soil_moisture"] = int(arg)
                print(f"[UPDATED] Soil Moisture set to {arg}%")
            elif cmd == "time" and arg:
                brain.hal.sensors["time_str"] = arg
                print(f"[UPDATED] Time set to '{arg}'")
            elif cmd == "user" and arg:
                brain.hal.sensors["user_state"] = arg.upper()
                print(f"[UPDATED] User State set to '{arg.upper()}'")
            else:
                print(f"[ERROR] Unknown variable command: {user_input} (Type *help for guide)")
                continue

            # Check if variable change triggers automatic background action (Emergency / Social Cue / Plant Care)
            print("\n[EVALUATING FSM TRIGGER] Checking environmental safety...")
            dec, frame, j_path, t_path = brain.process_turn(user_voice=None)
            print(frame)
            if dec.get("action_type") in ["FAIL_SAFE_EMERGENCY", "BACKGROUND_AUTONOMOUS", "PROACTIVE_SUGGEST"]:
                print(f"\n[AUTONOMOUS INTERVENTION TRIGGERED]: {dec.get('action_type')} -> {dec.get('target_device')} ({dec.get('device_param')})")
                if dec.get("voice_response"):
                    print(f"Speech: \"{dec.get('voice_response')}\"")
                print(f"Logs Saved: {os.path.basename(t_path)}")
            continue

        # =====================================================================
        # 2. Voice Command Interaction (sLLM Processing)
        # =====================================================================
        print(f"\n[PROCESSING HRI INFERENCE] Voice: \"{user_input}\" ...")
        dec, frame, j_path, t_path = brain.process_turn(user_voice=user_input)
        print("\n" + frame)
        print(f"Latency : {dec.get('latency_ms')} ms ({dec.get('source')})")
        print(f"Decision: {dec.get('action_type')} -> {dec.get('target_device')} (Param: {dec.get('device_param')})")
        if dec.get("voice_response"):
            print(f"Speech  : \"{dec.get('voice_response')}\"")
        print(f"Logs    : JSON({os.path.basename(j_path)}) | TXT({os.path.basename(t_path)})")

if __name__ == "__main__":
    main()
