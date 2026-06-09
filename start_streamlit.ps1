$logFile = "$env:TEMP\streamlit_log.txt"
$env:STREAMLIT_EMAIL = ""
$env:STREAMLIT_CONSUMER_EMAIL = ""
$env:STREAMLIT_NO_EMAIL = "true"
$env:HOME = $env:USERPROFILE

$proc = Start-Process -WindowStyle Hidden -FilePath "streamlit" -ArgumentList "run app.py --server.headless true" -WorkingDirectory "C:\Users\Admin\Desktop\Graph-Models" -RedirectStandardOutput $logFile -RedirectStandardError "$env:TEMP\streamlit_err.txt" -PassThru

$proc.Id | Out-File "$env:TEMP\streamlit_pid.txt"
Write-Output "Streamlit started with PID $($proc.Id)"
