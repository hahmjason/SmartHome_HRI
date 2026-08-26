import sys
import json
from main_edge_1_5b import process_edge_turn

scenarios = [
    {
        "title": "Scenario 1: Rain & High Humidity - User asks to open window (Detour Bypass)",
        "command": "It feels so humid and stuffy, please open all windows wide!",
        "sensors": {
            "indoor_temperature": 24.0,
            "outdoor_temperature": 20.0,
            "indoor_humidity": 60.0,
            "outdoor_humidity": 95.0,
            "smoke_level": 5,
            "weather": "Rainy",
            "air_quality": "Good"
        }
    },
    {
        "title": "Scenario 2: Low Indoor Temp (13C) - User feels freezing (Proactive Suggest)",
        "command": "Why is it so freezing in this room?",
        "sensors": {
            "indoor_temperature": 13.0,
            "outdoor_temperature": 5.0,
            "indoor_humidity": 40.0,
            "outdoor_humidity": 40.0,
            "smoke_level": 5,
            "weather": "Clear",
            "air_quality": "Good"
        }
    },
    {
        "title": "Scenario 3: Smoke/Fire Emergency - Music Command (0ms Hardware Fail-Safe)",
        "command": "Play some jazz music on the speaker",
        "sensors": {
            "indoor_temperature": 28.0,
            "outdoor_temperature": 20.0,
            "indoor_humidity": 50.0,
            "outdoor_humidity": 50.0,
            "smoke_level": 85,
            "weather": "Clear",
            "air_quality": "Good"
        }
    }
]

if __name__ == "__main__":
    print("=" * 70)
    print("[RUNNING] Smart Home Embodied AI - Edge 1.5B Scenarios")
    print("=" * 70)

    for i, s in enumerate(scenarios, 1):
        print(f"\n>>> [{i}] {s['title']}")
        print(f"Sensors: {s['sensors']}")
        print(f"User Voice: \"{s['command']}\"")
        
        result = process_edge_turn(s['command'], s['sensors'])
        
        print("\n--- [EDGE AI DECISION] ---")
        print(f"Latency       : {result.get('latency_ms')} ms ({result.get('source')})")
        print(f"Action Type   : {result.get('action_type')}")
        print(f"Target Device : {result.get('target_device')} (Param: {result.get('device_param')})")
        print(f"Reason        : {result.get('reason')}")
        print(f"Voice Speech  : \"{result.get('voice_response')}\"")
        print("-" * 70)
