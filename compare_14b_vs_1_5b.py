"""
Comparative Benchmark: 14B vs 1.5B on Intel Core Ultra 5 225H
Measures empirical latency, token count, and memory/throughput.
"""
import time
import json
import ollama

test_prompt = (
    "[Actual Input]\n"
    "- User Command: \"Open all windows wide please\"\n"
    "- Environment State: [OUTDOOR_RAIN(95.0%)]\n"
    "- Action Directive: DETOUR_BYPASS (Target: DUCT_FAN, Forbidden: WINDOW)\n"
    "- Reason Hint: RISK_OF_RAIN_INGRESS\n"
    "[Result]"
)

system_prompt = (
    "You are an active Smart Home HRI control agent. Respond in strict JSON adhering to schema."
)

schema = {
    "type": "object",
    "properties": {
        "action_type": {"type": "string"},
        "target_device": {"type": "string"},
        "device_param": {"type": "integer"},
        "reason": {"type": "string"},
        "voice_response": {"type": "string"}
    },
    "required": ["action_type", "target_device", "device_param", "reason", "voice_response"]
}

def benchmark_model(model_name: str):
    print(f"\n[BENCHMARK] Testing {model_name}...")
    t0 = time.perf_counter()
    try:
        res = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": test_prompt}
            ],
            format=schema,
            options={"temperature": 0.0, "top_p": 0.1, "num_ctx": 512, "num_predict": 120}
        )
        elapsed = round((time.perf_counter() - t0) * 1000, 2)
        eval_count = res.get("eval_count", 0)
        eval_duration = res.get("eval_duration", 1) / 1e9 # seconds
        tps = round(eval_count / eval_duration, 2) if eval_duration > 0 else 0
        
        return {
            "model": model_name,
            "status": "SUCCESS",
            "latency_ms": elapsed,
            "tokens_generated": eval_count,
            "tokens_per_sec": tps,
            "output": res["message"]["content"]
        }
    except Exception as e:
        return {"model": model_name, "status": "ERROR", "error": str(e), "latency_ms": round((time.perf_counter() - t0)*1000, 2)}

if __name__ == "__main__":
    res_1_5b = benchmark_model("qwen2.5:1.5b")
    print(f"1.5B Result: {res_1_5b}")
    res_14b = benchmark_model("qwen3:14b")
    print(f"14B Result: {res_14b}")
