Set WshShell = CreateObject("WScript.Shell")
WshShell.Run WScript.arguments.item(0), 0
Set WshShell = Nothing
