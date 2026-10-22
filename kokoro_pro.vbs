' Kokoro Studio Pro — silent launcher
' Hides the CMD window; runs kokoro_pro.bat completely in the background.
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh  = CreateObject("WScript.Shell")
here = fso.GetParentFolderName(WScript.ScriptFullName)
sh.CurrentDirectory = here
sh.Run """" & here & "\kokoro_pro.bat""", 0, False