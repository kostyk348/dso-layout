#!/usr/bin/env python3
"""
Simulated Annealing optimizer for Russian overlay on Colemak-DH positions.
"""

import random, math, json, sys, io

# =============================================================================
# DATA
# =============================================================================

KEY_COORD = {
    'q':(0,1),'w':(1,1),'e':(2,1),'r':(3,1),'t':(4,1),
    'y':(5,1),'u':(6,1),'i':(7,1),'o':(8,1),'p':(9,1),
    'a':(0,2),'s':(1,2),'d':(2,2),'f':(3,2),'g':(4,2),
    'h':(5,2),'j':(6,2),'k':(7,2),'l':(8,2),';':(9,2),
    'z':(0,3),'x':(1,3),'c':(2,3),'v':(3,3),'b':(4,3),
    'n':(5,3),'m':(6,3),',':(7,3),'.':(8,3),'/':(9,3),
}

FINGER = {}
for key, (c, r) in KEY_COORD.items():
    FINGER[key] = (c if c <= 4 else 9 - c, 0 if c <= 4 else 1)

FINGER_STRENGTH = {0: 0.5, 1: 0.8, 2: 1.0, 3: 0.9, 4: 0.7}

RUSSIAN_FREQ = {
    'о': 10.97, 'е': 8.45, 'а': 8.01, 'и': 7.35, 'н': 6.70,
    'т': 6.26, 'с': 5.47, 'л': 4.96, 'в': 4.54, 'р': 4.43,
    'к': 3.49, 'м': 3.21, 'д': 2.98, 'п': 2.81, 'у': 2.62,
    'я': 2.01, 'ы': 1.90, 'ь': 1.74, 'з': 1.65, 'б': 1.59,
    'ч': 1.44, 'г': 1.33, 'ф': 1.26, 'ж': 0.64, 'ш': 0.73,
    'х': 0.50, 'э': 0.32, 'ю': 0.22, 'ц': 0.04, 'щ': 0.03,
    'й': 0.01, 'ъ': 0.01,
}

RUSSIAN_BIGRAMS = [
    ('с','т',3.58),('н','о',3.21),('о','н',2.67),('е','н',2.10),
    ('н','и',2.00),('а','л',1.87),('к','о',1.74),('е','о',1.70),
    ('в','а',1.67),('и','с',1.61),('о','с',1.59),('н','а',1.55),
    ('а','о',1.52),('т','о',1.49),('ь','н',1.43),('р','о',1.39),
    ('н','е',1.31),('т','а',1.28),('о','в',1.25),('и','е',1.22),
    ('а','н',1.19),('л','и',1.16),('д','о',1.13),('а','с',1.10),
    ('к','а',1.07),('о','е',1.04),('в','о',1.01),('т','и',0.98),
    ('е','т',0.95),('с','о',0.92),('л','о',0.89),('и','л',0.86),
    ('р','а',0.83),('с','а',0.80),('н','у',0.77),('я','с',0.74),
]

# Keys we can use (27 letter keys + 3 punctuation = 30)
TARGET_KEYS = [
    'q','w','e','r','t','y','u','i','o','p',
    'a','s','d','f','g','h','j','k','l',';',
    'z','x','c','v','b','n','m',',',
    "'",'[',
]
# That's 30. Remaining 3 Russian letters (ц=0.04%, щ=0.03%, ъ=0.01%)
# can go on ] and compose sequences — they total 0.08% of text, negligible.

ALL_RUSSIAN = sorted(RUSSIAN_FREQ.keys(), key=lambda x: -RUSSIAN_FREQ[x])
TARGET_LETTERS = ALL_RUSSIAN[:30]

# =============================================================================
# SCORING
# =============================================================================

def score(mapping):
    travel = 0.0
    for key, letter in mapping.items():
        if letter not in RUSSIAN_FREQ or key not in KEY_COORD:
            continue
        f = RUSSIAN_FREQ[letter] / 100.0
        c, r = KEY_COORD[key]
        finger, hand = FINGER[key]
        strength = FINGER_STRENGTH[finger]
        row_dist = abs(r - 2) * 1.0
        col_dist = 0.3 if finger == 4 else (0.4 if finger == 0 and r != 2 else 0.0)
        travel += f * (row_dist + col_dist) / strength

    ltk = {}
    for key, letter in mapping.items():
        if letter not in ltk:
            ltk[letter] = key

    sfb = 0.0
    for l1, l2, freq in RUSSIAN_BIGRAMS:
        if l1 not in ltk or l2 not in ltk:
            continue
        k1, k2 = ltk[l1], ltk[l2]
        if k1 not in FINGER or k2 not in FINGER:
            continue
        if FINGER[k1] == FINGER[k2]:
            sfb += (freq / 100.0)

    total = sum(RUSSIAN_FREQ.get(l, 0) for l in mapping.values()) / 100.0
    home = sum(RUSSIAN_FREQ.get(l, 0) for k, l in mapping.items()
               if k in KEY_COORD and KEY_COORD[k][1] == 2) / 100.0
    home_pct = (home / total * 100) if total > 0 else 0

    pinky = sum(RUSSIAN_FREQ.get(l, 0) for k, l in mapping.items()
                if k in FINGER and FINGER[k][0] == 0) / 100.0
    pinky_pct = (pinky / total * 100) if total > 0 else 0

    return travel + sfb * 4.0 - home_pct * 0.05 + pinky_pct * 0.3

# =============================================================================
# SIMULATED ANNEALING
# =============================================================================

def random_mapping():
    keys = list(TARGET_KEYS)
    letters = list(TARGET_LETTERS)
    random.shuffle(keys)
    return dict(zip(keys, letters))

def neighbor(mapping):
    new_map = dict(mapping)
    keys = list(new_map.keys())
    k1, k2 = random.sample(keys, 2)
    new_map[k1], new_map[k2] = new_map[k2], new_map[k1]
    return new_map

def optimize(iterations=500000, initial_temp=5.0, cooling=0.99999):
    current = random_mapping()
    current_score = score(current)
    best = dict(current)
    best_score = current_score
    temp = initial_temp

    for i in range(iterations):
        new = neighbor(current)
        new_score = score(new)
        delta = new_score - current_score

        if delta < 0 or random.random() < math.exp(-delta / temp):
            current = new
            current_score = new_score
            if current_score < best_score:
                best = dict(current)
                best_score = current_score

        temp *= cooling

    return best, best_score

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("  RUSSIAN OVERLAY OPTIMIZER (Simulated Annealing)")
    print("=" * 60)
    print(f"  30 letters -> 30 keys, 5 trials x 500K iterations")
    print()

    overall_best = None
    overall_best_score = float('inf')

    for trial in range(5):
        random.seed(42 + trial)
        mapping, s = optimize()
        print(f"  Trial {trial+1}: score = {s:.5f}")
        if s < overall_best_score:
            overall_best = mapping
            overall_best_score = s

    print(f"\n  Best score: {overall_best_score:.5f}")

    print("\n  OPTIMIZED RUSSIAN LAYOUT:")
    print("  " + "-" * 45)
    for row_name, row_keys in [
        ("Top    ", ['q','w','e','r','t','y','u','i','o','p']),
        ("Home   ", ['a','s','d','f','g','h','j','k','l',';']),
        ("Bottom ", ['z','x','c','v','b','n','m',',']),
        ("Extra  ", ["'",'[']),
    ]:
        letters = '  '.join(f"{overall_best.get(k,'.'):>2}" for k in row_keys)
        print(f"  {row_name}: [{letters}]")

    covered = sum(RUSSIAN_FREQ.get(l, 0) for l in overall_best.values())
    print(f"\n  Coverage: {covered:.2f}% of Russian text")

    unmapped = [l for l in ALL_RUSSIAN if l not in overall_best.values()]
    if unmapped:
        print(f"  Unmapped (compose/dead key): {', '.join(unmapped)}")

    # Show what's where
    print("\n  Key -> Letter frequency mapping:")
    for key in TARGET_KEYS:
        letter = overall_best.get(key, '?')
        freq = RUSSIAN_FREQ.get(letter, 0)
        print(f"    {key:>2} -> {letter} ({freq:.2f}%)")

    # Save
    with open('optimized_ru_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(overall_best, f, ensure_ascii=False, indent=2)
    print("\n  Saved: optimized_ru_mapping.json")

if __name__ == '__main__':
    main()
