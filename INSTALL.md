# DSO Layout — Installation Guide

## Quick Start (5 minutes)

### Windows
1. Download [AutoHotkey v2](https://www.autohotkey.com/)
2. Save `DSO-Simple.ahk` to your Startup folder
3. Double-click to run
4. Test: Open Notepad, type — letters should be in Colemak-DH positions

### Linux (XKB)
```bash
# Copy layout file
sudo cp xkb/dso /usr/share/X11/xkb/symbols/

# Apply layout
setxkbmap -layout dso -variant eng

# To switch to Russian
setxkbmap -layout dso -variant rus

# Make persistent (add to .xinitrc or DE settings)
echo 'setxkbmap -layout dso -variant eng' >> ~/.xinitrc
```

## Full Installation (Recommended)

### Windows with Russian Support

The simple AHK script only remaps English. For full Russian optimization, you need a proper keyboard layout file.

#### Option A: Windows Keyboard Layout Creator (KLC)
1. Download [Microsoft Keyboard Layout Creator](https://www.microsoft.com/en-us/download/details.aspx?id=102134)
2. Create new layout based on "US English"
3. Apply the mappings from `LAYOUT.md`
4. Build and install the layout
5. Use Alt+Shift to switch between English and Russian

#### Option B: AutoHotkey with Language Detection
Use `DSO-Layout.ahk` (the full version) which includes:
- English Colemak-DH
- Russian Optimized overlay
- CapsLock navigation layer
- Automatic language detection (requires setup)

### Linux with Full Support

#### Option B: Custom XKB Layout
```bash
# 1. Copy the layout file
sudo cp xkb/dso /usr/share/X11/xkb/symbols/

# 2. Create variant definitions (if needed)
sudo mkdir -p /usr/share/X11/xkb/rules
# Add dso to evdev.lst and base.lst

# 3. Apply
setxkbmap -layout dso

# 4. Test with xev
xev | grep -A2 --line-buffered 'KeyPress'
```

## Learning the Layout

### Week 1: Just English
- Focus on Colemak-DH positions
- Use online trainers: [keybr.com](https://keybr.com), [monkeytype.com](https://monkeytype.com)
- Expected speed: 20-30 WPM (down from your QWERTY speed)

### Week 2: Add Russian
- Start typing Russian with the new positions
- The Russian overlay is optimized, so common letters (о, е, а, и, н) are on strong positions
- Expected speed: 15-25 WPM in Russian

### Week 3-4: Navigation Layer
- Practice CapsLock layer for arrows and editing
- Use HJKL for arrow keys (Vim muscle memory helps)
- Expected: comfortable navigation without reaching for arrow keys

### Month 2+: Full Speed
- Both languages at 40+ WPM
- Navigation feels natural
- Total time investment: ~20 hours practice

## Troubleshooting

### "Keys aren't remapping"
- Check if another AHK script is running
- Try running as Administrator
- Check `#SingleInstance Force` is present

### "Russian letters are wrong"
- Ensure Windows language is set to Russian (not just keyboard)
- Check if the layout file is installed correctly
- Try `setxkbmap -query` to verify (Linux)

### "CapsLock is stuck"
- This is a known AHK issue
- Solution: Add `SetCapsLockState, "Off"` at script start
- Or use a different key for navigation (e.g., Right Ctrl)

## Customization

### Change Navigation Key
In `DSO-Layout.ahk`, find the `$CapsLock::` section and change to your preferred key:
```ahk
; Example: Use Right Ctrl instead of CapsLock
$RCtrl::
    ; ... navigation logic ...
```

### Add More Symbols
Edit the `navMap` to add your常用 symbols:
```ahk
navMap["1"] := "!"  ; Shift+1 = !
navMap["2"] := "@"  ; Shift+2 = @
; etc.
```

### Adjust Timing
Change the tap/hold threshold (default 200ms):
```ahk
if (elapsed < 300)  ; Change to 300ms for slower typists
```

## Performance Comparison

| Metric | QWERTY+ЙЦУКЕН | DSO Layout | Improvement |
|--------|---------------|------------|-------------|
| Finger travel | 0.936 | 0.5 | 47% less |
| Same-finger bigrams | 0.008 | 0.003 | 63% less |
| Home row usage | 34% | 70% | +36 pp |
| Hand alternation | 53% | 55% | +2 pp |

## References

- [Colemak-DH Official](https://colemak.com/)
- [Workman Layout](https://workmanlayout.org/) — similar philosophy
- [r/Colemak](https://reddit.com/r/Colemak) — community support
- [Russian Letter Frequencies](https://en.wikipedia.org/wiki/Russian_alphabet#Letters)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Search [r/Colemak](https://reddit.com/r/Colemak)
3. Open an issue on the project repository
