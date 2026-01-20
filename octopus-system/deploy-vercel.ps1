# Octopus Architecture - Vercel Deployment Script
# Run this from PowerShell on Windows

Write-Host "🐙 Octopus Architecture - Vercel Deployment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Load environment variables from master.env
$masterEnvPath = "E:\THE PAULI FILES\master.env"

if (Test-Path $masterEnvPath) {
    Write-Host "✓ Found master.env file" -ForegroundColor Green

    # Parse master.env file
    Get-Content $masterEnvPath | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()

            # Set environment variable
            [Environment]::SetEnvironmentVariable($name, $value, "Process")

            # Show loaded vars (hide secrets)
            if ($name -like "*KEY*" -or $name -like "*TOKEN*" -or $name -like "*SECRET*") {
                $maskedValue = $value.Substring(0, [Math]::Min(10, $value.Length)) + "..."
                Write-Host "  Loaded: $name = $maskedValue" -ForegroundColor Gray
            } else {
                Write-Host "  Loaded: $name = $value" -ForegroundColor Gray
            }
        }
    }
} else {
    Write-Host "✗ master.env not found at: $masterEnvPath" -ForegroundColor Red
    Write-Host "Please update the path in this script or paste your secrets below" -ForegroundColor Yellow
    Write-Host ""

    # Prompt for required variables
    $env:NEXT_PUBLIC_SUPABASE_URL = Read-Host "Enter SUPABASE_URL"
    $env:NEXT_PUBLIC_SUPABASE_ANON_KEY = Read-Host "Enter SUPABASE_ANON_KEY"
}

Write-Host ""
Write-Host "Deploying to Vercel..." -ForegroundColor Cyan

# Change to frontend directory
$frontendPath = Join-Path $PSScriptRoot "frontend"
Set-Location $frontendPath

# Check if Vercel CLI is installed
if (!(Get-Command vercel -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Vercel CLI..." -ForegroundColor Yellow
    npm install -g vercel
}

# Deploy to Vercel
if ($env:VERCEL_TOKEN) {
    Write-Host "Using Vercel token from environment..." -ForegroundColor Green
    vercel --prod --yes --token $env:VERCEL_TOKEN `
        -e NEXT_PUBLIC_SUPABASE_URL="$env:NEXT_PUBLIC_SUPABASE_URL" `
        -e NEXT_PUBLIC_SUPABASE_ANON_KEY="$env:NEXT_PUBLIC_SUPABASE_ANON_KEY"
} else {
    Write-Host "No VERCEL_TOKEN found. Running interactive login..." -ForegroundColor Yellow
    vercel login
    vercel --prod --yes `
        -e NEXT_PUBLIC_SUPABASE_URL="$env:NEXT_PUBLIC_SUPABASE_URL" `
        -e NEXT_PUBLIC_SUPABASE_ANON_KEY="$env:NEXT_PUBLIC_SUPABASE_ANON_KEY"
}

Write-Host ""
Write-Host "✓ Deployment complete!" -ForegroundColor Green
Write-Host "Check your Vercel dashboard for the live URL" -ForegroundColor Cyan
