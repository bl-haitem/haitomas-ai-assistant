"""Find currently available free models on OpenRouter."""
import sys, os, requests, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config.settings as settings

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_results.txt")
lines = []

def log(msg):
    lines.append(str(msg))

log("=== FINDING AVAILABLE FREE MODELS ===")
try:
    resp = requests.get("https://openrouter.ai/api/v1/models", timeout=20)
    data = resp.json()
    models = data.get("data", [])
    
    free_models = []
    for m in models:
        mid = m.get("id", "")
        pricing = m.get("pricing", {})
        prompt_price = pricing.get("prompt", "1")
        completion_price = pricing.get("completion", "1") 
        
        if str(prompt_price) == "0" and str(completion_price) == "0":
            free_models.append({
                "id": mid,
                "name": m.get("name", ""),
                "context": m.get("context_length", 0),
            })
    
    log("Total free models: " + str(len(free_models)))
    log("")
    
    # Filter for quality models (Google, Meta, DeepSeek, Mistral)
    priority_brands = ["google", "meta", "deepseek", "mistral", "qwen"]
    priority_models = []
    other_models = []
    
    for fm in free_models:
        fid = fm["id"].lower()
        is_priority = any(b in fid for b in priority_brands)
        if is_priority:
            priority_models.append(fm)
        else:
            other_models.append(fm)
    
    log("PRIORITY FREE MODELS:")
    for m in sorted(priority_models, key=lambda x: x["context"], reverse=True):
        log("  " + m["id"] + " (ctx: " + str(m["context"]) + ")")
    
    log("")
    log("OTHER FREE MODELS:")
    for m in sorted(other_models, key=lambda x: x["context"], reverse=True)[:20]:
        log("  " + m["id"] + " (ctx: " + str(m["context"]) + ")")
        
    # Test top candidates
    log("")
    log("=== TESTING TOP CANDIDATES ===")
    candidates = [m["id"] for m in priority_models if "gemini" in m["id"].lower() or "gemma" in m["id"].lower() or "llama" in m["id"].lower()]
    candidates = candidates[:10]
    
    for mid in candidates:
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": "Bearer " + settings.OPENROUTER_API_KEY, "Content-Type": "application/json"},
                json={"model": mid, "messages": [{"role": "user", "content": "hi"}]},
                timeout=15,
            )
            d = r.json()
            if "choices" in d:
                log("  OK: " + mid)
            elif "error" in d:
                log("  ERR: " + mid + " -> " + str(d["error"].get("message", ""))[:80])
            else:
                log("  ???: " + mid + " -> " + str(r.status_code))
        except Exception as e:
            log("  FAIL: " + mid + " -> " + str(e)[:60])

except Exception as e:
    log("ERROR: " + str(e))

log("")
log("=== DONE ===")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("Done.")
