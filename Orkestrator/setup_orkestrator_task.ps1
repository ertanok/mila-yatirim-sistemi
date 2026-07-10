# Orkestrator - Task Scheduler kurulumu (surekli/otonom surec)
# VPS'te yonetici olarak calistir: powershell -ExecutionPolicy Bypass -File setup_orkestrator_task.ps1

$TaskName   = "MilaGold Orkestrator"
$NodeExe    = "C:\Program Files\nodejs\node.exe"
$ScriptPath = "C:\MilaYatirim\mila-yatirim-sistemi\Orkestrator\orkestrator_dongu.mjs"
$WorkDir    = "C:\MilaYatirim\mila-yatirim-sistemi\Orkestrator"

# Mevcut gorevi kaldir (varsa)
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "Eski gorev silindi (varsa)."

# Eylem: node.exe ile Orkestrator donguyu calistir
$Action = New-ScheduledTaskAction `
    -Execute $NodeExe `
    -Argument "`"$ScriptPath`"" `
    -WorkingDirectory $WorkDir

# Tetikleyici: kullanici oturum acinca baslat
$Trigger = New-ScheduledTaskTrigger -AtLogOn

# Ayarlar - sinirsiz calisma suresi (persistent loop), hata durumunda otomatik yeniden baslama
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -ExecutionTimeLimit ([TimeSpan]::Zero) `
    -RestartCount 5 `
    -RestartInterval (New-TimeSpan -Minutes 2) `
    -StartWhenAvailable

# Principal: mevcut kullanici, interactive session (Session 0 izolasyonuna karsi kritik)
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
    -Description "Orkestrator - Yol1 pipeline devamliligi (Arastirmaci->Stratejist->Backtest Muhendisi->Risk Analisti), surekli/otonom" `
    -Force

Write-Host ""
Write-Host "Task Scheduler gorevi olusturuldu: '$TaskName'"
Write-Host "  Script  : $ScriptPath"
Write-Host "  Tetikci : Oturum acilinca (AtLogOn)"
Write-Host "  Kullanici: $env:USERNAME (Interactive/RDP)"
Write-Host "  Hata durumunda: 5 kez, 2dk aralikla yeniden baslatilir"
Write-Host ""
Write-Host "NOT: Gorev kaydedildi ama BASLATILMADI. Baslatmak icin:"
Write-Host "  Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "Durum kontrol: Get-ScheduledTask -TaskName '$TaskName' | Select-Object TaskName, State"
