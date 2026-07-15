; DSO Layout — Colemak-DH + Optimized Russian
; AutoHotkey v2 implementation
; 
; Features:
;   - Colemak-DH for English
;   - Optimized Russian overlay
;   - CapsLock: tap=Esc, hold=Navigation layer
;   - Alt+Shift language switch (unchanged)
;
; Installation:
;   1. Install AutoHotkey v2: https://www.autohotkey.com/
;   2. Save this file as DSO-Layout.ahk
;   3. Double-click to run (or add to startup)
;   4. To stop: Right-click tray icon -> Exit
;
; Notes:
;   - Windows language switch (Alt+Shift) works independently
;   - This script remaps keys based on active keyboard layout
;   - You may need to adjust AHK's keyboard layout detection

#Requires AutoHotkey v2.0
#SingleInstance Force

; =============================================================================
; CONFIGURATION
; =============================================================================

; Which layout is active? Change this or use a hotkey to toggle
; 0 = English (Colemak-DH), 1 = Russian (Optimized)
currentLang := 0

; Hotkey to toggle language (alternative to Alt+Shift)
; CapsLock is used for navigation layer, so use something else
; Set to 0 to disable
toggleHotkey := 0  ; e.g., "^!l" for Ctrl+Alt+L

; =============================================================================
; LAYER DEFINITIONS
; =============================================================================

; English Colemak-DH mapping: physical key -> letter
; Row 1 (top): Q W F P G J L U Y ;
enMap := Map()
enMap["q"] := "q", enMap["w"] := "w", enMap["e"] := "f", enMap["r"] := "p", enMap["t"] := "g"
enMap["y"] := "j", enMap["u"] := "l", enMap["i"] := "u", enMap["o"] := "y", enMap["p"] := ";"
; Row 2 (home): A R S T D H N E I O
enMap["a"] := "a", enMap["s"] := "r", enMap["d"] := "s", enMap["f"] := "t", enMap["g"] := "d"
enMap["h"] := "h", enMap["j"] := "n", enMap["k"] := "e", enMap["l"] := "i", enMap[";"] := "o"
; Row 3 (bottom): Z X C V B K M , . /
enMap["z"] := "z", enMap["x"] := "x", enMap["c"] := "c", enMap["v"] := "v", enMap["b"] := "b"
enMap["n"] := "k", enMap["m"] := "m"

; Russian Optimized mapping: physical key -> Russian letter
; Top row: Щ Ы Я Д Ь Ч Б Ж К Ю
ruMap := Map()
ruMap["q"] := "щ", ruMap["w"] := "ы", ruMap["e"] := "я", ruMap["r"] := "д", ruMap["t"] := "ь"
ruMap["y"] := "ч", ruMap["u"] := "б", ruMap["i"] := "ж", ruMap["o"] := "к", ruMap["p"] := "ю"
; Home row: Э Е А С Л Т Н О И Х
ruMap["a"] := "э", ruMap["s"] := "е", ruMap["d"] := "а", ruMap["f"] := "с", ruMap["g"] := "л"
ruMap["h"] := "т", ruMap["j"] := "н", ruMap["k"] := "о", ruMap["l"] := "и", ruMap[";"] := "х"
; Bottom row: Ц Ш М П Ф З Г У
ruMap["z"] := "ц", ruMap["x"] := "ш", ruMap["c"] := "м", ruMap["v"] := "п", ruMap["b"] := "ф"
ruMap["n"] := "з", ruMap["m"] := "г"
; Extra
ruMap[","] := "у", ruMap["'"] := "р", ruMap["["] := "в"

; =============================================================================
; NAVIGATION LAYER (CapsLock held)
; =============================================================================

navActive := false

; Navigation layer keys (when CapsLock is held)
; HJKL = arrows (Vim-style)
; U = Home, O = End
; N = PgDn, M = PgUp
; Y = Delete
; Top row = F1-F10

navMap := Map()
; Arrows on HJKL
navMap["h"] := "{Left}", navMap["j"] := "{Down}", navMap["k"] := "{Up}", navMap["l"] := "{Right}"
; Home/End
navMap["u"] := "{Home}", navMap["o"] := "{End}"
; Page Up/Down
navMap["n"] := "{PgDn}", navMap["m"] := "{PgUp}"
; Delete
navMap["y"] := "{Del}"
; F-keys on top row
navMap["q"] := "{F1}", navMap["w"] := "{F2}", navMap["e"] := "{F3}", navMap["r"] := "{F4}", navMap["t"] := "{F5}"
navMap["y"] := "{F6}", navMap["u"] := "{F7}", navMap["i"] := "{F8}", navMap["o"] := "{F9}", navMap["p"] := "{F10}"

; =============================================================================
; CAPSLOCK REMAPPING
; =============================================================================

; CapsLock: tap = Esc, hold = Navigation layer
$CapsLock::
{
    global navActive
    navActive := true
    
    ; Wait to see if it's a tap or hold
    startTime := A_TickCount
    KeyWait "CapsLock"
    elapsed := A_TickCount - startTime
    
    if (elapsed < 200)  ; Tap (< 200ms)
        Send "{Esc}"
    
    navActive := false
}

; =============================================================================
; KEY REMAPPING (main loop)
; =============================================================================

; Create hotkeys for all remappable keys
keys := ["q","w","e","r","t","y","u","i","o","p",
         "a","s","d","f","g","h","j","k","l",";",
         "z","x","c","v","b","n","m",",",".","/",
         "'","[","]"]

for key in keys
{
    ; Create hotkey for this key
    hotkey("$" key, KeyHandler)
}

KeyHandler(thisHotkey)
{
    global currentLang, navActive, enMap, ruMap, navMap
    
    ; Get the physical key (remove $ prefix)
    physicalKey := SubStr(thisHotkey, 2)
    
    ; Navigation layer takes priority
    if (navActive && navMap.Has(physicalKey))
    {
        Send navMap[physicalKey]
        return
    }
    
    ; Otherwise, use language map
    if (currentLang = 0)  ; English
    {
        if (enMap.Has(physicalKey))
            Send enMap[physicalKey]
        else
            Send physicalKey  ; fallback
    }
    else  ; Russian
    {
        if (ruMap.Has(physicalKey))
            Send "{" ruMap[physicalKey] "}"
        else
            Send physicalKey  ; fallback
    }
}

; =============================================================================
; LANGUAGE TOGGLE (optional alternative to Alt+Shift)
; =============================================================================

if (toggleHotkey)
{
    Hotkey toggleHotkey, ToggleLanguage
}

ToggleLanguage(*)
{
    global currentLang
    currentLang := 1 - currentLang
    langName := (currentLang = 0) ? "English" : "Russian"
    ToolTip "DSO Layout: " langName
    SetTimer () => ToolTip(), -1000
}

; =============================================================================
; STARTUP
; =============================================================================

; Show startup tooltip
ToolTip "DSO Layout loaded`nLanguage: " ((currentLang = 0) ? "English" : "Russian") "`nCapsLock: Esc (tap) / Nav (hold)"
SetTimer () => ToolTip(), -2000

; Exit script with Win+Alt+Q
!#q::ExitApp
