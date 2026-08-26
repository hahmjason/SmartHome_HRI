"""
Dual Output Logger & Dispatcher for Smart Home Embodied AI
Separates:
1. Detailed JSON Log (Sensors, CoT Reasoning, Human State Simulation, Latency, Action Params)
2. Clean Human-Readable TXT Summary (Simple execution report, Device status, Spoken HRI text)
"""
import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Tuple

LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
JSON_DIR = os.path.join(LOGS_DIR, "json")
TXT_DIR = os.path.join(LOGS_DIR, "txt")

os.makedirs(JSON_DIR, exist_ok=True)
os.makedirs(TXT_DIR, exist_ok=True)

class DualOutputLogger:
    @staticmethod
    def save_turn_artifacts(user_voice: str,
                            sensors: Dict[str, Any],
                            decision: Dict[str, Any],
                            fsm_state: str,
                            prefix: str = "turn") -> Tuple[str, str]:
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
        
        # ---------------------------------------------------------------------
        # 1. Full Structured JSON Payload
        # ---------------------------------------------------------------------
        json_filename = f"{prefix}_{timestamp}.json"
        json_path = os.path.join(JSON_DIR, json_filename)
        latest_json_path = os.path.join(JSON_DIR, "latest_decision.json")

        full_payload = {
            "timestamp": datetime.now().isoformat(),
            "fsm_state": fsm_state,
            "latency_ms": decision.get("latency_ms", 0.0),
            "inference_source": decision.get("source", "UNKNOWN"),
            "input_context": {
                "user_voice": user_voice,
                "sensors": sensors
            },
            "ai_thinking_process": {
                "human_state_simulation": decision.get("human_state_simulation", "N/A"),
                "physical_reasoning": decision.get("physical_reasoning", "N/A"),
                "reason_code": decision.get("reason", "N/A")
            },
            "actuation_decision": {
                "action_type": decision.get("action_type"),
                "target_device": decision.get("target_device"),
                "device_param": decision.get("device_param"),
                "voice_response": decision.get("voice_response")
            }
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(full_payload, f, indent=2, ensure_ascii=False)
            
        with open(latest_json_path, "w", encoding="utf-8") as f:
            json.dump(full_payload, f, indent=2, ensure_ascii=False)

        # ---------------------------------------------------------------------
        # 2. Clean Human-Readable TXT Execution Summary
        # ---------------------------------------------------------------------
        txt_filename = f"{prefix}_{timestamp}.txt"
        txt_path = os.path.join(TXT_DIR, txt_filename)
        latest_txt_path = os.path.join(TXT_DIR, "latest_summary.txt")

        txt_content = []
        txt_content.append("=" * 70)
        txt_content.append(f" 스마트홈 Embodied AI 실행 요약 리포트 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
        txt_content.append("=" * 70)
        txt_content.append(f"■ 시스템 상태 (FSM)   : {fsm_state}")
        txt_content.append(f"■ 추론 엔진 및 지연시간 : {decision.get('source')} ({decision.get('latency_ms')} ms)")
        txt_content.append(f"■ 사용자 입력 발화     : \"{user_voice or '(외부 자극 없음 / 센서 이벤트)'}\"")
        txt_content.append("-" * 70)
        txt_content.append("🧠 [1. AI 사고 과정 및 생체/물리 분석 (Thinking Process)]")
        txt_content.append(f" • 생체/인지 분석 : {decision.get('human_state_simulation', '해당 없음')}")
        txt_content.append(f" • 물리/우회 추론 : {decision.get('physical_reasoning', '해당 없음')}")
        txt_content.append(f" • 판단 이유 코드 : {decision.get('reason', 'N/A')}")
        txt_content.append("-" * 70)
        txt_content.append("⚙️ [2. 물리 액추에이터 실행 결과 (Execution Output)]")
        txt_content.append(f" • 액션 타입     : {decision.get('action_type')}")
        txt_content.append(f" • 제어 기기     : {decision.get('target_device')} (설정값: {decision.get('device_param')})")
        txt_content.append(f" • 음성 피드백   : \"{decision.get('voice_response')}\"")
        txt_content.append("=" * 70)

        summary_text = "\n".join(txt_content)

        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(summary_text)

        with open(latest_txt_path, "w", encoding="utf-8") as f:
            f.write(summary_text)

        return json_path, txt_path
