"""
Human-in-the-Loop Feedback & Annotation Tool for Embodied AI
Allows researchers to:
1. Review generated JSON/TXT logs
2. Mark decisions as [Y] Approved (Good) or [N] Rejected (Bad) with optional human corrections
3. Automatically export to DPO (Direct Preference Optimization) & LoRA fine-tuning datasets
4. Instantly update dynamic Few-Shot memory for immediate runtime improvement
"""
import os
import glob
import json
from typing import Dict, Any, List

LOGS_JSON_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs", "json")
DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
os.makedirs(DATASET_DIR, exist_ok=True)

DPO_DATASET_FILE = os.path.join(DATASET_DIR, "dpo_preference_pairs.jsonl")
LORA_SFT_FILE = os.path.join(DATASET_DIR, "lora_sft_dataset.jsonl")
DYNAMIC_MEMORY_FILE = os.path.join(DATASET_DIR, "dynamic_verified_fewshots.json")

class HumanFeedbackManager:
    def __init__(self):
        pass

    @staticmethod
    def list_unreviewed_logs() -> List[str]:
        files = glob.glob(os.path.join(LOGS_JSON_DIR, "*.json"))
        return [f for f in files if "latest" not in os.path.basename(f)]

    @staticmethod
    def record_feedback(log_filepath: str, is_approved: bool, human_corrected_json: Dict[str, Any] = None):
        with open(log_filepath, "r", encoding="utf-8") as f:
            log_data = json.load(f)

        prompt = (
            f"User Voice: \"{log_data['input_context']['user_voice']}\"\n"
            f"Sensors: {json.dumps(log_data['input_context']['sensors'])}\n"
            f"FSM State: {log_data['fsm_state']}"
        )

        model_output = json.dumps(log_data["actuation_decision"], ensure_ascii=False)

        # 1. If Approved -> Add to LoRA SFT and Dynamic Memory
        if is_approved:
            sft_entry = {
                "instruction": "You are an active Smart Home HRI control agent. Respond in strict JSON.",
                "input": prompt,
                "output": model_output
            }
            with open(LORA_SFT_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(sft_entry, ensure_ascii=False) + "\n")

            HumanFeedbackManager._append_to_dynamic_memory({
                "command": log_data["input_context"]["user_voice"],
                "sensors": log_data["input_context"]["sensors"],
                "decision": log_data["actuation_decision"]
            })
            return "APPROVED_AND_SAVED"

        # 2. If Rejected with Correction -> Create DPO Pair (Chosen vs Rejected)
        else:
            if human_corrected_json:
                chosen_output = json.dumps(human_corrected_json, ensure_ascii=False)
                dpo_entry = {
                    "prompt": prompt,
                    "chosen": chosen_output,
                    "rejected": model_output
                }
                with open(DPO_DATASET_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(dpo_entry, ensure_ascii=False) + "\n")

                sft_entry = {
                    "instruction": "You are an active Smart Home HRI control agent. Respond in strict JSON.",
                    "input": prompt,
                    "output": chosen_output
                }
                with open(LORA_SFT_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(sft_entry, ensure_ascii=False) + "\n")

                return "CORRECTED_AND_SAVED_DPO"
            return "REJECTED_DISCARDED"

    @staticmethod
    def _append_to_dynamic_memory(example: Dict[str, Any]):
        memory = []
        if os.path.exists(DYNAMIC_MEMORY_FILE):
            try:
                with open(DYNAMIC_MEMORY_FILE, "r", encoding="utf-8") as f:
                    memory = json.load(f)
            except Exception:
                memory = []
        memory.append(example)
        with open(DYNAMIC_MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)

def interactive_cli_annotator():
    manager = HumanFeedbackManager()
    unreviewed = manager.list_unreviewed_logs()
    
    print("=" * 70)
    print(f"[Human-in-the-Loop] Smart Home AI Decision Feedback Tool")
    print(f"Discovered Log Files: {len(unreviewed)} files")
    print("=" * 70)

    if not unreviewed:
        print("No log files found for review.")
        return

    for i, filepath in enumerate(unreviewed, 1):
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"\n[{i}/{len(unreviewed)}] File: {filename}")
        print(f"- User Voice  : \"{data['input_context']['user_voice']}\"")
        print(f"- AI Reasoning: {data['ai_thinking_process'].get('physical_reasoning')}")
        print(f"- AI Action   : {data['actuation_decision'].get('action_type')} -> {data['actuation_decision'].get('target_device')} ({data['actuation_decision'].get('device_param')})")
        print(f"- Voice Speech: \"{data['actuation_decision'].get('voice_response')}\"")
        print("-" * 50)

        choice = input("Is this decision CORRECT? (Y: Yes / N: No / S: Skip / Q: Quit): ").strip().upper()
        if choice == 'Q':
            break
        elif choice == 'S':
            continue
        elif choice == 'Y':
            res = manager.record_feedback(filepath, is_approved=True)
            print(f"[APPROVED] Added to LoRA dataset & Dynamic Few-Shot Memory. ({res})")
        elif choice == 'N':
            print("Human Correction (press Enter to skip):")
            corr_action = input(" - Correct action_type (e.g. DETOUR_BYPASS): ").strip()
            corr_device = input(" - Correct target_device (e.g. DUCT_FAN): ").strip()
            corr_speech = input(" - Correct voice speech response: ").strip()

            if corr_action and corr_device:
                corrected_json = {
                    "action_type": corr_action,
                    "target_device": corr_device,
                    "device_param": 100,
                    "reason": "HUMAN_SUPERVISED_CORRECTION",
                    "voice_response": corr_speech
                }
                res = manager.record_feedback(filepath, is_approved=False, human_corrected_json=corrected_json)
                print(f"[CORRECTED] Registered in DPO preference dataset (Chosen vs Rejected)! ({res})")
            else:
                res = manager.record_feedback(filepath, is_approved=False)
                print(f"[REJECTED] Recorded. ({res})")

    print("\n" + "=" * 70)
    print("Feedback complete! Dataset files saved at:")
    print(f" - DPO Preference Dataset : {DPO_DATASET_FILE}")
    print(f" - LoRA Fine-Tune Dataset : {LORA_SFT_FILE}")
    print(f" - Dynamic Few-Shot Memory: {DYNAMIC_MEMORY_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    interactive_cli_annotator()
