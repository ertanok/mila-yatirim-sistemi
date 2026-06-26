# MilaGold Watchdog - Task Scheduler kurulumu
# VPS'te yonetici olarak calistir: powershell -ExecutionPolicy Bypass -File setup_watchdog_task.ps1

$TaskName   = "MilaGold Watchdog"
$ScriptPath = "C:\MilaYatirim\mila-yatirim-sistemi\MilaGold\milagold_watchdog.py"
$WorkDir    = "C:\MilaYatirim\mila-yatirim-sistemi\MilaGold"
$PyExe      = (Get-Command py.exe -ErrorAction SilentlyContinue).Source
if (-not $PyExe) { $PyExe = "py.exe" }

# Mevcut gorevi kaldir (varsa)
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "Eski gorev silindi (varsa)."

# Eylem: py.exe ile watchdog calistir
$Action = New-ScheduledTaskAction `
    -Execute $PyExe `
    -Argument $ScriptPath `
    -WorkingDirectory $WorkDir

# Tetikleyici: kullanici oturum acinca baslat
$Trigger = New-ScheduledTaskTrigger -AtLogOn

# Ayarlar
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 5 `
    -RestartInterval (New-TimeSpan -Minutes 2) `
    -StartWhenAvailable

# Principal: mevcut kullanici, interactive session (RDP icin kritik)
$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Highest

# Gorevi kaydet
Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "MilaGold OCR ve MT5 agent gozetleme - otomatik yeniden baslama" `
    -Force

Write-Host ""
Write-Host "Task Scheduler gorevi olusturuldu: '$TaskName'"
Write-Host "  Script  : $ScriptPath"
Write-Host "  Tetikci : Oturum acilinca (AtLogOn)"
Write-Host "  Kullanici: $env:USERNAME (Interactive/RDP)"
Write-Host "  Hata durumunda: 5 kez, 2dk aralikla yeniden baslatilir"
Write-Host ""

# Simdi baslat
Start-ScheduledTask -TaskName $TaskName
Write-Host "Gorev simdi baslatildi."
Write-Host "Durum kontrol: Get-ScheduledTask -TaskName '$TaskName' | Select-Object TaskName, State"
