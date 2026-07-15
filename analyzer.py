#!/usr/bin/env python3
"""
Keyboard Layout Optimizer for Russian + English
================================================
Evaluates letter placement, computes ergonomic metrics.
Each layout stores BOTH english and russian mappings per physical key.
"""

import json, math
from typing import Dict, List, Tuple

# =============================================================================
# KEYBOARD GEOMETRY — (column_index, row_index), approximate cm from home
# Columns: 0-4 = left hand (pinky..inner), 5-9 = right hand (inner..pinky)
# Rows: 0=number, 1=top, 2=home, 3=bottom
# =============================================================================

KEY_POS = {}
ROW_NAMES = {0: 'num', 1: 'top', 2: 'home', 3: 'bot'}

LEFT_KEYS  = ['q','w','e','r','t','a','s','d','f','g','z','x','c','v','b']
RIGHT_KEYS = ['y','u','i','o','p','h','j','k','l',';','n','m',',','.','/']

def _pos(col, row):
    return (col, row)

# Physical layout: key -> (col, row)
KEY_COORD = {
    # Top row (row 1)
    'q': _pos(0,1), 'w': _pos(1,1), 'e': _pos(2,1), 'r': _pos(3,1), 't': _pos(4,1),
    'y': _pos(5,1), 'u': _pos(6,1), 'i': _pos(7,1), 'o': _pos(8,1), 'p': _pos(9,1),
    # Home row (row 2)
    'a': _pos(0,2), 's': _pos(1,2), 'd': _pos(2,2), 'f': _pos(3,2), 'g': _pos(4,2),
    'h': _pos(5,2), 'j': _pos(6,2), 'k': _pos(7,2), 'l': _pos(8,2), ';': _pos(9,2),
    # Bottom row (row 3)
    'z': _pos(0,3), 'x': _pos(1,3), 'c': _pos(2,3), 'v': _pos(3,3), 'b': _pos(4,3),
    'n': _pos(5,3), 'm': _pos(6,3), ',': _pos(7,3), '.': _pos(8,3), '/': _pos(9,3),
}

# Finger: 0=pinky 1=ring 2=middle 3=index 4=inner-index
# Hand: 0=left 1=right
FINGER = {
    'q':(0,0),'a':(0,0),'z':(0,0),   # left pinky
    'w':(1,0),'s':(1,0),'x':(1,0),   # left ring
    'e':(2,0),'d':(2,0),'c':(2,0),   # left middle
    'r':(3,0),'f':(3,0),'v':(3,0),   # left index
    't':(4,0),'g':(4,0),'b':(4,0),   # left inner
    'y':(4,1),'h':(4,1),'n':(4,1),   # right inner
    'u':(3,1),'j':(3,1),'m':(3,1),   # right index
    'i':(2,1),'k':(2,1),',':(2,1),   # right middle
    'o':(8-7,1),'l':(8-7,1),'.':(8-7,1),  # right ring — fix below
    'p':(9-7,1),';':(9-7,1),'/':(9-7,1),  # right pinky — fix below
}

# Rewrite finger map cleanly
FINGER = {}
# Left hand: cols 0-4
for key, (c, r) in KEY_COORD.items():
    if c <= 4:
        if c == 0:   FINGER[key] = (0, 0)  # pinky
        elif c == 1: FINGER[key] = (1, 0)  # ring
        elif c == 2: FINGER[key] = (2, 0)  # middle
        elif c == 3: FINGER[key] = (3, 0)  # index
        elif c == 4: FINGER[key] = (4, 0)  # inner index
    else:
        if c == 5:   FINGER[key] = (4, 1)  # right inner index
        elif c == 6: FINGER[key] = (3, 1)  # right index
        elif c == 7: FINGER[key] = (2, 1)  # right middle
        elif c == 8: FINGER[key] = (1, 1)  # right ring
        elif c == 9: FINGER[key] = (0, 1)  # right pinky

FINGER_STRENGTH = {0: 0.5, 1: 0.8, 2: 1.0, 3: 0.9, 4: 0.7}

# =============================================================================
# FREQUENCY DATA
# =============================================================================

RUSSIAN_FREQ = {
    'о': 10.97, 'е': 8.45, 'а': 8.01, 'и': 7.35, 'н': 6.70,
    'т': 6.26, 'с': 5.47, 'л': 4.96, 'в': 4.54, 'р': 4.43,
    'к': 3.49, 'м': 3.21, 'д': 2.98, 'п': 2.81, 'у': 2.62,
    'я': 2.01, 'ы': 1.90, 'ь': 1.74, 'з': 1.65, 'б': 1.59,
    'ч': 1.44, 'г': 1.33, 'ф': 1.26, 'ж': 0.64, 'ш': 0.73,
    'х': 0.50, 'э': 0.32, 'ю': 0.22, 'ц': 0.04, 'щ': 0.03,
    'й': 0.01, 'ъ': 0.01,
}

ENGLISH_FREQ = {
    'e': 12.70, 't': 9.06, 'a': 8.17, 'o': 7.51, 'i': 6.97,
    'n': 6.75, 's': 6.33, 'h': 6.09, 'r': 5.99, 'd': 4.25,
    'l': 4.03, 'c': 2.78, 'u': 2.76, 'm': 2.41, 'w': 2.36,
    'f': 2.23, 'g': 2.02, 'y': 1.97, 'p': 1.93, 'b': 1.49,
    'v': 0.98, 'k': 0.77, 'j': 0.15, 'x': 0.15, 'q': 0.10,
    'z': 0.07,
}

ENGLISH_BIGRAMS = [
    ('t','h',3.56),('h','e',3.07),('i','n',2.43),('e','r',2.05),
    ('a','n',1.99),('r','e',1.85),('o','n',1.76),('a','t',1.49),
    ('e','n',1.45),('b','e',1.44),('t','e',1.35),('a','l',1.31),
    ('h','a',1.28),('o','r',1.24),('n','t',1.21),('l','i',1.18),
    ('s','t',1.15),('n','g',1.12),('a','r',1.09),('i','o',1.06),
    ('s','e',1.03),('r','i',1.00),('c','t',0.97),('g','h',0.94),
    ('l','e',0.91),('t','o',0.88),('f','o',0.85),('r','s',0.82),
    ('w','h',0.79),('o','u',0.76),('l','l',0.75),('e','s',0.73),
    ('o','f',0.71),('t','o',0.69),('n','d',0.67),('i','t',0.65),
]

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

# =============================================================================
# CANDIDATE LAYOUTS — each has {key: en_letter} and {key: ru_letter}
# =============================================================================

LAYOUTS = {}

# --- QWERTY + ЙЦУКЕН ---
LAYOUTS['QWERTY+ЙЦУКЕН'] = {
    'en': {
        'q':'q','w':'w','e':'e','r':'r','t':'t','y':'y','u':'u','i':'i','o':'o','p':'p',
        'a':'a','s':'s','d':'d','f':'f','g':'g','h':'h','j':'j','k':'k','l':'l',
        'z':'z','x':'x','c':'c','v':'v','b':'b','n':'n','m':'m',
    },
    'ru': {
        'q':'й','w':'ц','e':'у','r':'к','t':'е','y':'н','u':'г','i':'ш','o':'щ','p':'з',
        'a':'ф','s':'ы','d':'в','f':'а','g':'п','h':'р','j':'о','k':'л','l':'д',
        'z':'я','x':'ч','c':'с','v':'м','b':'и','n':'т','m':'ь',
        ';':'ж',"'":'э',',':'б','.':'ю','[':'х',']':'ъ',
    },
}

# --- Colemak-DH + Russian overlay (freq-matched to same physical positions) ---
LAYOUTS['Colemak-DH+RU'] = {
    'en': {
        'q':'q','w':'w','e':'f','r':'p','t':'g','y':'j','u':'l','i':'u','o':'y','p':';',
        'a':'a','s':'r','d':'s','f':'t','g':'d','h':'h','j':'n','k':'e','l':'i',';':'o',
        'z':'z','x':'x','c':'c','v':'v','b':'b','n':'k','m':'m',
    },
    'ru': {
        # Russian freq: о>е>а>и>н>т>с>л>в>р>к>м>д>п>у>я>ы>ь>з>б>ч>г>ф>ж>ш>х>э>ю>ц>щ>й>ъ
        # Map to Colemak-DH physical positions by frequency
        'q':'к','w':'м','e':'д','r':'п','t':'у','y':'я','u':'ы','i':'ь','o':'з','p':'б',
        'a':'о','s':'е','d':'а','f':'и','g':'н','h':'т','j':'с','k':'л','l':'в',';':'р',
        'z':'ч','x':'г','c':'ф','v':'ш','b':'ж','n':'х','m':'э',
        ',':'й','.':'ъ',"'":'щ',
    },
}

# --- OPTIMIZED: my design ---
# Philosophy:
#   1. Home row = 10 most frequent letters in BOTH languages
#   2. Strong fingers (middle, index) for highest frequency
#   3. Maximize hand alternation in common bigrams
#   4. Russian gets extra keys: ; ' , . [ ] for rare letters

# Russian top 10:  о е а и н т с л в р  (total ~67%)
# English top 10:  e t a o i n s h r d  (total ~79%)
#
# Home row assignment (physical keys):
#   Left:  a s d f g    Right: h j k l ;
#
# I need to find a compromise where BOTH languages put their top letters on home row.
# The best compromise for overlapping frequency:
#   о/e:  both #1 in their language — give strongest home position
#   е/t:  both very high — second strongest
#   а/a:  identical letter! — easy win
#   и/i:  both top 5 — middle finger
#   н/n:  both top 6 — middle finger opposite hand
#   т/h:  high in both — index
#   с/s:  high in both — ring finger
#   л/l:  moderate-high — ring finger
#   в/r:  moderate — inner index
#   р/d:  moderate — inner index

LAYOUTS['Optimized'] = {
    'en': {
        # Home row: e t a o i n s h r d (10 most frequent English)
        'a':'e','s':'t','d':'a','f':'o','g':'i',
        'h':'n','j':'s','k':'h','l':'r',';':'d',
        # Top row: l c u m w f g y p b (next tier)
        'q':'l','w':'c','e':'u','r':'m','t':'w',
        'y':'f','u':'g','i':'y','o':'p','p':'b',
        # Bottom row: v k j x q z
        'z':'v','x':'k','c':'j','v':'x','b':'q',
        'n':'z',
    },
    'ru': {
        # Home row: о е а и н т с л в р (10 most frequent Russian)
        'a':'о','s':'е','d':'а','f':'и','g':'н',
        'h':'т','j':'с','k':'л','l':'в',';':'р',
        # Top row: к м д п у я ы ь з б
        'q':'к','w':'м','e':'д','r':'п','t':'у',
        'y':'я','u':'ы','i':'ь','o':'з','p':'б',
        # Bottom row: ч г ф ш ж х э + extra rare on punctuation
        'z':'ч','x':'г','c':'ф','v':'ш','b':'ж',
        'n':'х','m':'э',
        ',':'ю','.':'ц',"'":'щ','[':'й',']':'ъ',
    },
}

# --- OPTIMIZED v2: shift-heavy optimization ---
# Same home row, but different top/bottom to reduce same-finger bigrams
# Key change: swap some top-row pairs to break up common SFBs

LAYOUTS['Optimized-v2'] = {
    'en': {
        # Home: e t a o i n s h r d
        'a':'e','s':'t','d':'a','f':'o','g':'i',
        'h':'n','j':'s','k':'h','l':'r',';':'d',
        # Top: restructured to reduce SFBs
        'q':'l','w':'u','e':'c','r':'m','t':'f',
        'y':'g','u':'w','i':'y','o':'p','p':'b',
        # Bottom
        'z':'v','x':'k','c':'j','v':'x','b':'q',
        'n':'z',
    },
    'ru': {
        # Home: о е а и н т с л в р
        'a':'о','s':'е','d':'а','f':'и','g':'н',
        'h':'т','j':'с','k':'л','l':'в',';':'р',
        # Top: restructured
        'q':'к','w':'у','e':'м','r':'д','t':'п',
        'y':'я','u':'ы','i':'ь','o':'з','p':'б',
        # Bottom
        'z':'ч','x':'г','c':'ф','v':'ш','b':'ж',
        'n':'х','m':'э',
        ',':'ю','.':'ц',"'":'щ','[':'й',']':'ъ',
    },
}

# --- ALT: completely new approach ---
# Put the MOST overlapping letters on the strongest finger positions
# и/i and н/n overlap perfectly — both are frequent, put them on middle fingers
# а/a overlaps perfectly — index finger
# с/s overlaps — ring finger

LAYOUTS['Alt-Overlap'] = {
    'en': {
        # Home: prioritize overlap first, then English-only optimization
        'a':'a','s':'s','d':'o','f':'e','g':'i',
        'h':'n','j':'t','k':'h','l':'r',';':'d',
        # Top
        'q':'l','w':'c','e':'u','r':'m','t':'w',
        'y':'f','u':'g','i':'y','o':'p','p':'b',
        # Bottom
        'z':'v','x':'k','c':'j','v':'x','b':'q',
        'n':'z',
    },
    'ru': {
        'a':'а','s':'с','d':'о','f':'е','g':'и',
        'h':'н','j':'т','k':'л','l':'в',';':'р',
        'q':'к','w':'м','e':'д','r':'п','t':'у',
        'y':'я','u':'ы','i':'ь','o':'з','p':'б',
        'z':'ч','x':'г','c':'ф','v':'ш','b':'ж',
        'n':'х','m':'э',
        ',':'ю','.':'ц',"'":'щ','[':'й',']':'ъ',
    },
}

# =============================================================================
# EVALUATION
# =============================================================================

def finger_travel(mapping: Dict[str,str], freq: Dict[str,float]) -> float:
    """Weighted finger travel distance. Lower = better."""
    total = 0.0
    for key, letter in mapping.items():
        if letter not in freq or key not in KEY_COORD or key not in FINGER:
            continue
        f = freq[letter] / 100.0
        c, r = KEY_COORD[key]
        finger, hand = FINGER[key]
        strength = FINGER_STRENGTH[finger]

        # Distance from home: row distance + column stretch
        row_dist = abs(r - 2) * 1.0  # home row = 0
        col_dist = 0.0
        if finger == 4:  # inner index stretch
            col_dist = 0.3
        elif finger == 0 and r != 2:  # pinky off home
            col_dist = 0.4

        distance = row_dist + col_dist
        total += f * distance / strength

    return total


def same_finger_bigrams(mapping: Dict[str,str], bigrams: List[Tuple[str,str,float]]) -> float:
    """Penalty for same-finger same-hand bigrams. Lower = better."""
    letter_to_key = {}
    for key, letter in mapping.items():
        if letter not in letter_to_key:
            letter_to_key[letter] = key

    penalty = 0.0
    for l1, l2, freq in bigrams:
        if l1 not in letter_to_key or l2 not in letter_to_key:
            continue
        k1, k2 = letter_to_key[l1], letter_to_key[l2]
        if k1 not in FINGER or k2 not in FINGER:
            continue
        f1, h1 = FINGER[k1]
        f2, h2 = FINGER[k2]
        if f1 == f2 and h1 == h2:
            penalty += (freq / 100.0)
    return penalty


def hand_alternation(mapping: Dict[str,str], bigrams: List[Tuple[str,str,float]]) -> float:
    """Ratio of hand alternations. Higher = better."""
    letter_to_key = {}
    for key, letter in mapping.items():
        if letter not in letter_to_key:
            letter_to_key[letter] = key

    alt = 0.0
    total = 0.0
    for l1, l2, freq in bigrams:
        if l1 not in letter_to_key or l2 not in letter_to_key:
            continue
        k1, k2 = letter_to_key[l1], letter_to_key[l2]
        if k1 not in FINGER or k2 not in FINGER:
            continue
        _, h1 = FINGER[k1]
        _, h2 = FINGER[k2]
        total += freq
        if h1 != h2:
            alt += freq
    return (alt / total * 100) if total > 0 else 0


def home_row_pct(mapping: Dict[str,str], freq: Dict[str,float]) -> float:
    """Percentage of typing on home row. Higher = better."""
    total = 0.0
    home = 0.0
    for key, letter in mapping.items():
        if letter not in freq or key not in KEY_COORD:
            continue
        f = freq[letter] / 100.0
        total += f
        _, r = KEY_COORD[key]
        if r == 2:
            home += f
    return (home / total * 100) if total > 0 else 0


def pinky_pct(mapping: Dict[str,str], freq: Dict[str,float]) -> float:
    """Percentage on pinky. Lower = better."""
    total = 0.0
    pinky = 0.0
    for key, letter in mapping.items():
        if letter not in freq or key not in FINGER:
            continue
        f = freq[letter] / 100.0
        total += f
        finger, _ = FINGER[key]
        if finger == 0:
            pinky += f
    return (pinky / total * 100) if total > 0 else 0


def inner_stretch_pct(mapping: Dict[str,str], freq: Dict[str,float]) -> float:
    """Percentage on inner index (stretch). Lower = better."""
    total = 0.0
    stretch = 0.0
    for key, letter in mapping.items():
        if letter not in freq or key not in FINGER:
            continue
        f = freq[letter] / 100.0
        total += f
        finger, _ = FINGER[key]
        if finger == 4:
            stretch += f
    return (stretch / total * 100) if total > 0 else 0


def evaluate(mapping: Dict[str,str], freq: Dict[str,float],
             bigrams: List[Tuple[str,str,float]], lang: str) -> dict:
    ft  = finger_travel(mapping, freq)
    sfb = same_finger_bigrams(mapping, bigrams)
    ha  = hand_alternation(mapping, bigrams)
    hr  = home_row_pct(mapping, freq)
    pp  = pinky_pct(mapping, freq)
    ist = inner_stretch_pct(mapping, freq)

    # Composite: lower = better
    # travel: weight 1.0, sfb: weight 4.0 (very bad), ha: bonus (-2.0),
    # home row: bonus (-0.1 per %), pinky: penalty 0.3
    composite = ft + sfb * 4.0 - ha * 0.02 - hr * 0.05 + pp * 0.3 + ist * 0.1

    return {
        'lang': lang,
        'travel': round(ft, 5),
        'sfb': round(sfb, 5),
        'alt_pct': round(ha, 1),
        'home_pct': round(hr, 1),
        'pinky_pct': round(pp, 1),
        'stretch_pct': round(ist, 1),
        'composite': round(composite, 5),
    }


# =============================================================================
# PRINT HELPERS
# =============================================================================

def print_keyboard(mapping: Dict[str,str], label: str = ""):
    """Visual keyboard."""
    if label:
        print(f"  {label}")
    rows = [
        ('  ', ['q','w','e','r','t','y','u','i','o','p']),
        ('  ', ['a','s','d','f','g','h','j','k','l',';']),
        ('  ', ['z','x','c','v','b','n','m',',','.','/']),
    ]
    for prefix, keys in rows:
        letters = '  '.join(f'{mapping.get(k,"?"):>2}' for k in keys)
        print(f"  {letters}")


def print_finger_map():
    """Show finger assignments."""
    print("  Finger map:")
    print("    LP  LM  LI  LI+  |  RI+  RI  RM  RP")
    print("    Q   E   R   T    |  Y   U   I   O   P")
    print("    A   D   F   G    |  H   J   K   L   ;")
    print("    Z   C   V   B    |  N   M   ,   .   /")
    print("   (pinky)           |          (pinky)")


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 72)
    print("  KEYBOARD LAYOUT OPTIMIZER — Russian + English")
    print("=" * 72)

    all_results = {}

    for lang, freq, bigrams in [
        ('en', ENGLISH_FREQ, ENGLISH_BIGRAMS),
        ('ru', RUSSIAN_FREQ, RUSSIAN_BIGRAMS),
    ]:
        print(f"\n{'─' * 72}")
        print(f"  {lang} EVALUATION")
        print(f"{'─' * 72}")
        header = f"{'Layout':<22} {'Travel':>7} {'SFB':>7} {'Alt%':>6} {'Home%':>6} {'Pinky%':>6} {'Stretch%':>7} {'Score':>8}"
        print(header)
        print("─" * 72)

        for name, layout in LAYOUTS.items():
            r = evaluate(layout[lang], freq, bigrams, lang)
            all_results[f"{name}_{lang}"] = r
            print(f"  {name:<20} {r['travel']:>7.4f} {r['sfb']:>7.4f} {r['alt_pct']:>5.1f}% "
                  f"{r['home_pct']:>5.1f}% {r['pinky_pct']:>5.1f}% {r['stretch_pct']:>6.1f}% "
                  f"{r['composite']:>8.5f}")

    # Combined
    print(f"\n{'═' * 72}")
    print("  COMBINED SCORE (avg of EN + RU, lower = better)")
    print(f"{'═' * 72}")
    print(f"  {'Layout':<22} {'EN':>10} {'RU':>10} {'Combined':>10}")
    print(f"  {'─' * 55}")

    best_name, best_score = None, float('inf')
    for name in LAYOUTS:
        en = all_results[f"{name}_en"]
        ru = all_results[f"{name}_ru"]
        combined = (en['composite'] + ru['composite']) / 2
        marker = ""
        if combined < best_score:
            best_score = combined
            best_name = name
        print(f"  {name:<22} {en['composite']:>10.5f} {ru['composite']:>10.5f} {combined:>10.5f}")

    print(f"\n  ★ Best: {best_name} (score: {best_score:.5f})")

    # Print best layout
    print(f"\n{'═' * 72}")
    print(f"  WINNING LAYOUT: {best_name}")
    print(f"{'═' * 72}")
    print_finger_map()
    print()
    print_keyboard(LAYOUTS[best_name]['en'], "English:")
    print()
    print_keyboard(LAYOUTS[best_name]['ru'], "Russian:")
    print()

    # Save
    output = {
        'best': best_name,
        'results': all_results,
        'layouts': {name: {'en': LAYOUTS[name]['en'], 'ru': LAYOUTS[name]['ru']}
                    for name in LAYOUTS},
    }
    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("  Saved: results.json")


if __name__ == '__main__':
    main()
