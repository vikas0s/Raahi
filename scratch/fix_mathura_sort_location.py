with open("backend/router.py", "r", encoding="utf-8") as f:
    text = f.read()

import re

# 1. Restore Delhi sort in plan_journey
delhi_wrong_sort = """            def _mathura_rank(r):
                prio = 2
                if "Goverdhan Chauraha" in r.title or "Goverdhan Chauraha" in r.tag:
                    prio = 0
                elif r.route_type in ["mathura_shared", "mathura_ebus", "mathura_tempo"]:
                    prio = 1
                return (_avail_key(r), prio, r.total_duration_minutes, r.total_fare_inr)
            routes.sort(key=_mathura_rank)"""

delhi_correct_sort = "            routes.sort(key=lambda r: (_avail_key(r), r.total_duration_minutes, r.total_fare_inr))"

if delhi_wrong_sort in text:
    text = text.replace(delhi_wrong_sort, delhi_correct_sort, 1)
    print("Restored Delhi sort in plan_journey!")

# 2. Put _mathura_rank in _plan_mathura_journey
m = re.search(r'def _plan_mathura_journey', text)
if m:
    start = m.start()
    m_end = re.search(r'\n    def ', text[start+20:])
    end = start + 20 + m_end.start() if m_end else len(text)
    sub = text[start:end]

    old_target = "routes.sort(key=lambda r: (_avail_key(r), r.total_duration_minutes, r.total_fare_inr))"
    mathura_sort = """def _mathura_rank(r):
            prio = 2
            if "Goverdhan Chauraha" in r.title or "Goverdhan Chauraha" in r.tag:
                prio = 0
            elif r.route_type in ["mathura_shared", "mathura_ebus", "mathura_tempo"]:
                prio = 1
            return (_avail_key(r), prio, r.total_duration_minutes, r.total_fare_inr)
        routes.sort(key=_mathura_rank)"""

    # Check indentation of old_target in sub
    pos = sub.find(old_target)
    if pos != -1:
        # Find leading spaces before old_target
        line_start = sub.rfind('\n', 0, pos) + 1
        indent = sub[line_start:pos]
        # Build properly indented block
        mathura_sort_indented = f"""def _mathura_rank(r):
{indent}    prio = 2
{indent}    if "Goverdhan Chauraha" in r.title or "Goverdhan Chauraha" in r.tag:
{indent}        prio = 0
{indent}    elif r.route_type in ["mathura_shared", "mathura_ebus", "mathura_tempo"]:
{indent}        prio = 1
{indent}    return (_avail_key(r), prio, r.total_duration_minutes, r.total_fare_inr)
{indent}routes.sort(key=_mathura_rank)"""
        sub_new = sub[:pos] + mathura_sort_indented + sub[pos+len(old_target):]
        text = text[:start] + sub_new + text[end:]
        print("Updated _mathura_rank inside _plan_mathura_journey with indent:", repr(indent))

compile(text, "backend/router.py", "exec")
with open("backend/router.py", "w", encoding="utf-8") as f:
    f.write(text)
print("Saved backend/router.py successfully!")
