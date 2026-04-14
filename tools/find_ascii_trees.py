"""
Find E-trees (only E and 1) whose eval'd values round to target ASCII codes.

E(x, y) = exp(x) - ln(y)
Leaf = 1

BFS over tree depth, tracking all reachable values and their expressions.
"""

import math
from collections import defaultdict

def e_op(x, y):
    if y <= 0:
        return None
    try:
        val = math.exp(x) - math.log(y)
        if not math.isfinite(val) or abs(val) > 1e6:
            return None
        return val
    except (OverflowError, ValueError):
        return None

# Target ASCII codes for "Hello, World!"
TARGETS = {
    'H': 72, 'e': 101, 'l': 108, 'o': 111,
    ',': 44, ' ': 32, 'W': 87, 'r': 114,
    'd': 100, '!': 33,
}

# BFS: enumerate all (value, expression) pairs by depth
# values[depth] = list of (float_value, expr_string)
found = {}  # rounded_int -> (expr, actual_value, depth)

# Depth 0: just the constant 1
by_depth = {0: [(1.0, "1")]}
all_vals = [(1.0, "1")]

print("Searching for E-trees that evaluate to ASCII codes...")
print(f"Targets: {sorted(set(TARGETS.values()))}\n")

MAX_DEPTH = 10

for depth in range(1, MAX_DEPTH + 1):
    new_entries = []

    # Combine all pairs (a, b) where max(depth_a, depth_b) = depth - 1
    # i.e., at least one operand is from the previous depth
    prev_depth_vals = by_depth.get(depth - 1, [])

    pairs_to_try = []
    # New left × all right
    for lv, le in prev_depth_vals:
        for rv, re in all_vals:
            pairs_to_try.append((lv, le, rv, re))
    # All left × new right (avoid duplicates where both are prev_depth)
    for lv, le in all_vals:
        for rv, re in prev_depth_vals:
            if (lv, le) not in prev_depth_vals or True:  # allow all
                pairs_to_try.append((lv, le, rv, re))

    seen_vals = set()
    for lv, le, rv, re in pairs_to_try:
        val = e_op(lv, rv)
        if val is None:
            continue

        # Deduplicate by rounded value (keep shortest expression)
        rounded = round(val)
        val_key = round(val * 1000)  # deduplicate to 3 decimal places
        if val_key in seen_vals:
            continue
        seen_vals.add(val_key)

        expr = f"(E {le} {re})"
        new_entries.append((val, expr))

        # Check if this hits a target
        if abs(val - rounded) < 0.5 and rounded in TARGETS.values():
            if rounded not in found or depth < found[rounded][2]:
                chars = [c for c, code in TARGETS.items() if code == rounded]
                found[rounded] = (expr, val, depth)
                print(f"  FOUND: {chars} = {rounded} ≈ {val:.6f} (depth {depth})")
                print(f"         {expr}")

    by_depth[depth] = new_entries
    all_vals.extend(new_entries)

    print(f"Depth {depth}: {len(new_entries)} new values, {len(all_vals)} total, {len(found)}/{len(set(TARGETS.values()))} targets found")

    if len(found) >= len(set(TARGETS.values())):
        print("\nAll targets found!")
        break

print("\n=== Results ===\n")
for char in "Hello, World!":
    code = ord(char)
    if code in found:
        expr, val, depth = found[code]
        print(f"'{char}' = {code} ≈ {val:.6f} (depth {depth})")
        print(f"  {expr}\n")
    else:
        print(f"'{char}' = {code} — NOT FOUND\n")
