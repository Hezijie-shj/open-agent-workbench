$BackendPath = Join-Path $PSScriptRoot "backend"
$FrontendPath = Join-Path $PSScriptRoot "frontend"
$ConfigPath = Join-Path $PSScriptRoot "config\config.dev.toml"

Start-Process -FilePath powershell `
  -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "`$env:CONFIG_PATH='$ConfigPath'; uv run uvicorn app.main:app --host 127.0.0.1 --port 8001" `
  -WorkingDirectory $BackendPath `
  -WindowStyle Hidden

Start-Process -FilePath powershell `
  -ArgumentList "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "npm run dev" `
  -WorkingDirectory $FrontendPath `
  -WindowStyle Hidden

Write-Host "backend: http://127.0.0.1:8001"
Write-Host "frontend: http://localhost:5173"
