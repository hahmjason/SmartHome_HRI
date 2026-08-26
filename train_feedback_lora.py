"""
LoRA / DPO Fine-Tuning Script & Guide (Unsloth / HuggingFace & Ollama Modelfile)
Uses datasets generated from feedback_annotator.py:
- dataset/lora_sft_dataset.jsonl (Supervised Fine-Tuning)
- dataset/dpo_preference_pairs.jsonl (Direct Preference Optimization)
"""
import os
import json

DATASET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset")
DPO_FILE = os.path.join(DATASET_DIR, "dpo_preference_pairs.jsonl")
SFT_FILE = os.path.join(DATASET_DIR, "lora_sft_dataset.jsonl")

def inspect_feedback_dataset():
    print("=" * 70)
    print("[HUMAN FEEDBACK DATASET STATUS]")
    print("=" * 70)

    sft_count = 0
    if os.path.exists(SFT_FILE):
        with open(SFT_FILE, "r", encoding="utf-8") as f:
            sft_count = len(f.readlines())

    dpo_count = 0
    if os.path.exists(DPO_FILE):
        with open(DPO_FILE, "r", encoding="utf-8") as f:
            dpo_count = len(f.readlines())

    print(f"- Approved & Corrected SFT Samples : {sft_count} pairs")
    print(f"- DPO Preference (Chosen/Rejected) : {dpo_count} pairs")
    print("-" * 70)
    print("[HOW TO TRAIN YOUR CUSTOM 1.5B MODEL]:")
    print("1. Fast LoRA Fine-Tuning (via Unsloth / HuggingFace):")
    print("   pip install unsloth")
    print("   python -m unsloth.train --model Qwen/Qwen2.5-1.5B-Instruct --dataset dataset/lora_sft_dataset.jsonl")
    print("\n2. Direct Preference Optimization (DPO):")
    print("   trl dpo --model_name Qwen/Qwen2.5-1.5B-Instruct --dataset dataset/dpo_preference_pairs.jsonl")
    print("\n3. Ollama Export:")
    print("   ollama create qwen2.5:1.5b-custom -f Modelfile")
    print("=" * 70)

if __name__ == "__main__":
    inspect_feedback_dataset()
