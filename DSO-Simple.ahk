; DSO Layout — Simple AHK v2 Script
; Just does English Colemak-DH remapping
; Russian: use Windows language switch (Alt+Shift) + standard ЙЦУКЕН
; 
; This is the simplest approach: remap English only, let Windows handle Russian
; The Russian overlay will need a separate .KLC layout for full optimization

#Requires AutoHotkey v2.0
#SingleInstance Force

; Colemak-DH English remapping
; Physical key -> Colemak-DH letter
remaps := Map()
remaps["e"] := "f"
remaps["r"] := "p"
remaps["t"] := "g"
remaps["y"] := "j"
remaps["u"] := "l"
remaps["i"] := "u"
remaps["o"] := "y"
remaps["p"] := ";"
remaps["s"] := "r"
remaps["d"] := "s"
remaps["f"] := "t"
remaps["g"] := "d"
remaps["j"] := "n"
remaps["k"] := "e"
remaps["l"] := "i"
remaps[";"] := "o"
remaps["n"] := "k"

; Create remappings
for from, to in remaps
{
    ; Only remap lowercase (AHK will handle uppercase automatically)
    Hotkey "$" from, MakeHandler(to)
}

MakeHandler(output) {
    return (*) => Send(output)
}

; CapsLock -> Escape (simple version)
$CapsLock::Send("{Esc}")

; Notification
ToolTip("DSO Layout (Colemak-DH) active`nCapsLock -> Esc`nWin+Alt+Q to exit")
SetTimer(() => ToolTip(), -2000)

!#q::ExitApp
