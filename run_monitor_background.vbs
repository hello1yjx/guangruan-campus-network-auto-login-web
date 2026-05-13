Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
runtimeDir = scriptDir & "\runtime"
pidPath = runtimeDir & "\monitor.pid"
logPath = runtimeDir & "\monitor.log"
pythonwPath = "D:\python\pythonw.exe"
mainPath = scriptDir & "\main.py"

If Not fso.FolderExists(runtimeDir) Then
    fso.CreateFolder(runtimeDir)
End If

If fso.FileExists(pidPath) Then
    Set pidFile = fso.OpenTextFile(pidPath, 1)
    existingPid = Trim(pidFile.ReadAll)
    pidFile.Close

    If existingPid <> "" Then
        commandCheck = "cmd /c tasklist /FI ""PID eq " & existingPid & """ | find """ & existingPid & """ >nul"
        result = shell.Run(commandCheck, 0, True)
        If result = 0 Then
            MsgBox "Background monitor is already running.", 64, "Campus Network Auto Login"
            WScript.Quit
        End If
    End If

    On Error Resume Next
    fso.DeleteFile pidPath, True
    On Error GoTo 0
End If

command = "cmd /c cd /d """ & scriptDir & """ && """ & pythonwPath & """ """ & mainPath & """ --monitor > """ & logPath & """ 2>&1"
shell.Run command, 0, False

WScript.Sleep 4000

If fso.FileExists(pidPath) Then
    MsgBox "Background monitor started successfully.", 64, "Campus Network Auto Login"
Else
    message = "Background monitor did not start." & vbCrLf & vbCrLf & _
              "Please check:" & vbCrLf & _
              "1. runtime\monitor.log" & vbCrLf & _
              "2. config.json" & vbCrLf & _
              "3. Python / Playwright environment"
    MsgBox message, 48, "Campus Network Auto Login"
End If
