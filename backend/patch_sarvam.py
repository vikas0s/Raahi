with open("Raahi/backend/sarvam_service.py", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("DEFAULT_TIMEOUT_SEC = 25.0", "DEFAULT_TIMEOUT_SEC = 45.0")
text = text.replace("max_tokens: int = 1024", "max_tokens: int = 1500")

old_part = """            content = choices[0].get("message", {}).get("content", "")
            return content.strip()"""

new_part = """            msg = choices[0].get("message", {})
            content = (msg.get("content") or "").strip()
            if not content and msg.get("reasoning_content"):
                content = (msg.get("reasoning_content") or "").strip()
            return content"""

text = text.replace(old_part, new_part)

with open("Raahi/backend/sarvam_service.py", "w", encoding="utf-8") as f:
    f.write(text)

print("PATCHED_SARVAM_SERVICE")

