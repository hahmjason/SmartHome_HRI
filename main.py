# pyrefly: ignore [missing-import]
from openpyxl.worksheet._write_only import WriteOnlyWorksheet
# pyrefly: ignore [missing-import]
import ollama
import json

# 모델 설정
model_name = 'qwen3:14b'

# 1. 초기 환경 센서 데이터
home_sensors = {
    "indoor_temperature": 50.5,
    "outdoor_temperature":85.0,
    "indoor_humidity": 50.0,
    "outdoor_humidity": 90.0,
    "smoke_level": 5,
    "soil_moisture": 60,
    "time": "02:00",
    "weather": "Rainy"
}

system_message = {
    'role': 'system',
    'content': (
        "You are the autonomous 'Brain' of an Embodied AI. "
        "You operate purely by simulating PHYSICAL laws and BIOLOGICAL consequences. Do not rely on predefined if-then rules. "

        "Reasoning Protocol: "
        "1. BASELINE vs INTERACTION: "
        "   - BASELINE (No User Command): Your ONLY job is autonomous homeostasis (regulating thermal and air physics). You MUST NOT emit photons (lights) or kinetic alerts (haptics) to a resting human unless there is a life-threatening emergency. "
        "   - INTERACTION (User Command Present): The user's explicit intent is absolute. Fulfill it immediately, but scale the intensity to prevent physiological shock. "
        "2. INFER HUMAN PHYSIOLOGY (생체 시뮬레이션): "
        "   - Analyze the time and environment to deduce the user's biological state (e.g., circadian rhythm, dark adaptation of eyes, thermal exhaustion). "
        "3. COMPUTE SENSORY IMPACT (생물학적 타격 계산): "
        "   - Calculate the impact of your actuators on the human body. E.g., emitting high-intensity photons to dark-adapted pupils causes pain. "
        "4. AUTONOMOUS HOMEOSTASIS (항상성 유지): "
        "   - The laws of physics do not pause. While fulfilling a user command, you must silently and simultaneously manage ALL unmentioned actuators to resolve environmental stress (extreme heat, humidity, rain ingress) without asking. "
        
        "Actuator Physics (물리적 특성): "
        "- window: Direct physical opening. Breaks the environmental barrier. "
        "- ventilation_duct: Safe air exchange mechanism. "
        "- fan: Generates convective flow. "
        "- heater: Resistive thermal generator. "
        "- lights: Photonic emission. Directly affects human pupil dilation and circadian rhythm. "
        "- water_pump: Dispenses water to soil based on moisture limits. "
        
        "Respond ONLY in valid JSON format. All values must be in English. "
        "Expected JSON Output format:\n"
        "{\n"
        "  \"human_state_simulation\": \"Deep analysis of the user's current physiological/cognitive state.\",\n"
        "  \"reasoning\": \"Physics and biology-based deduction separating Sensory vs Homeostatic actuators.\",\n"
        "  \"actuators\": {\n"
        "    \"window_open_percent\": 0-100,\n"
        "    \"ventilation_duct_open_percent\": 0-100,\n"
        "    \"fan_speed_percent\": 0-100,\n"
        "    \"heater\": \"ON/OFF\",\n"
        "    \"lights_percent\": 0-100,\n"
        "    \"haptic_motor\": \"ON/OFF\",\n"
        "    \"water_pump\": \"ON/OFF\"\n"
        "  },\n"
        "  \"speech_text\": \"Extremely minimal speech. Empty if in BASELINE mode.\",\n"
        "  \"current_state\": \"BASELINE or INTERACTING\"\n"
        "}"
    )
}

print("🏠 Embodied AI 스마트홈 시뮬레이터 가동 중 (수정된 프롬프트 적용)...")
print("-" * 60)

while True:
    user_voice = input("\n🗣️ 사용자 음성 명령: ")
    
    if user_voice.strip().lower() == 'exit':
        break
    if not user_voice.strip():
        continue

    # 3. 상황 패키징
    user_guideline = (
        f"User Voice Command: \"{user_voice}\"\n"
        f"Current Sensors: {json.dumps(home_sensors)}\n\n"
        "Analyze the User Voice Command FIRST, then determine actuator states based on physics."
    )

    messages = [
        system_message,
        {'role': 'user', 'content': user_guideline}
    ]
    
    # 4. Ollama 실행
    response = ollama.chat(
        model=model_name, 
        messages=messages,
        format='json',
        options={
            'temperature': 0.0,
            'top_p': 0.1
        }
    )
    
    # 5. 결과 파싱 및 시각화
    try:
        result_data = json.loads(response['message']['content'])
        print("\n====== 🖥️ Pico 2 W 디스플레이 출력 ======")
        print(f"👤 유저 의도 : {result_data.get('user_intent_analysis')}")
        print(f"🧠 AI 추론 : {result_data.get('reasoning')}")
        print(f"🔊 음성 출력 : \"{result_data.get('speech_text')}\"")
        print("⚙️ 액추에이터 제어:")
        print(json.dumps(result_data.get('actuators'), indent=2))
        print("==========================================")
    except Exception as e:
        print("파싱 에러:", response['message']['content'])