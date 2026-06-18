<#
    run.ps1: convenience wrapper around docker compose for the VitiScience stack.

    Usage (from the dashboard/ folder):
        ./run.ps1 up        # create .env if missing, then start the stack
        ./run.ps1 down      # stop the stack (keeps data volumes)
        ./run.ps1 reset     # stop AND delete data volumes (fresh InfluxDB/Grafana)
        ./run.ps1 logs      # follow logs of all services
        ./run.ps1 ps        # show service status
        ./run.ps1 urls      # print the URLs to open
#>
param(
    [Parameter(Position = 0)]
    [ValidateSet('up', 'down', 'reset', 'logs', 'ps', 'urls')]
    [string]$Command = 'up'
)

$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot

function Ensure-Env {
    if (-not (Test-Path './.env')) {
        Copy-Item './.env.example' './.env'
        Write-Host "Created .env from .env.example. Review the passwords/token inside before exposing the stack." -ForegroundColor Yellow
    }
}

function Show-Urls {
    Write-Host ""
    Write-Host "  Grafana   : http://localhost:3000   (dashboard 'VitiScience Overview')" -ForegroundColor Cyan
    Write-Host "  InfluxDB  : http://localhost:8086   (admin UI)" -ForegroundColor Cyan
    Write-Host "  MQTT TCP  : localhost:1883          (publishers connect here)" -ForegroundColor Cyan
    Write-Host ""
}

switch ($Command) {
    'up' {
        Ensure-Env
        docker compose up -d
        Show-Urls
    }
    'down' { docker compose down }
    'reset' { docker compose down -v }
    'logs' { docker compose logs -f }
    'ps' { docker compose ps }
    'urls' { Show-Urls }
}
