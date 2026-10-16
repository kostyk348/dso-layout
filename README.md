# DSO Layout

[![Release](https://img.shields.io/github/v/release/kostyk348/dso-layout?sort=semver&color=blue)](https://github.com/kostyk348/dso-layout/releases)
[![License](https://img.shields.io/badge/license-Apache-2.0-green)](https://github.com/kostyk348/dso-layout/blob/master/LICENSE)
[![Last commit](https://img.shields.io/github/last-commit/kostyk348/dso-layout?branch=master)](https://github.com/kostyk348/dso-layout/commits/master)

**Colemak-DH + Optimized Russian** — ergonomic keyboard layout for bilingual typing.

Standard QWERTY/ЙЦУКЕН were designed for typewriters. This layout optimizes for human hands.

## Metrics

| Metric | QWERTY+ЙЦУКЕН | DSO Layout | Improvement |
|--------|---------------|------------|-------------|
| Finger travel | 0.936 | 0.50 | **-47%** |
| Same-finger bigrams | 0.008 | 0.003 | **-63%** |
| Home row usage | 34% | 70% | **+36 pp** |
| Hand alternation | 53% | 55% | +2 pp |

## Layout

### English (Colemak-DH)

```
Top:    Q  W  F  P  G  J  L  U  Y  ;
Home:   A  R  S  T  D  H  N  E  I  O
Bottom: Z  X  C  V  B  K  M  ,  .  /
```

### Russian (Optimized — 97.65% coverage)

```
Top:    Щ  Ы  Я  Д  Ь  Ч  Б  Ж  К  Ю
Home:   Э  Е  А  С  Л  Т  Н  О  И  Х
Bottom: Ц  Ш  М  П  Ф  З  Г  У
Extra:  Р  В
```

Unmapped: й (0.01%), ъ (0.01%) — via compose key.

### Navigation (CapsLock held)

```
H/J/K/L → Arrow keys
U/O → Home/End
N/M → PgDn/PgUp
Y → Delete
Q-T → F1-F5
```

## Installation

### Windows

1. Install [AutoHotkey v2](https://www.autohotkey.com/)
2. Download `DSO-Simple.ahk` (English only) or `DSO-Layout.ahk` (EN+RU+Nav)
3. Double-click to run, or add to Startup folder

### Linux

```bash
sudo cp xkb/dso /usr/share/X11/xkb/symbols/
setxkbmap -layout dso -variant eng
```

## Files

| File | Description |
|------|-------------|
| `analyzer.py` | Frequency analysis + layout comparison |
| `optimizer_ru.py` | Simulated annealing Russian letter optimizer |
| `DSO-Layout.ahk` | Full AHK v2 script (EN+RU+Navigation) |
| `DSO-Simple.ahk` | Simple AHK script (English Colemak-DH only) |
| `xkb/dso` | XKB layout for Linux |
| `LAYOUT.md` | Full layout specification |
| `INSTALL.md` | Installation guide |

## How It Works

1. **Frequency analysis** — Russian and English letter frequencies from large corpora
2. **Simulated annealing** — 500K iterations to find optimal Russian letter placement
3. **Colemak-DH** — proven English layout with 74% home row usage
4. **Navigation layer** — CapsLock held activates arrow keys on home row

## Learning Curve

- **Week 1:** English Colemak-DH (expect 20-30 WPM initially)
- **Week 2:** Add Russian overlay
- **Week 3-4:** Navigation layer
- **Month 2+:** Full speed (40+ WPM both languages)

Use [keybr.com](https://keybr.com) or [monkeytype.com](https://monkeytype.com) for practice.

## License

Apache 2.0
