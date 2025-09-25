
<# ===============================================
 Vehicle Attendance (ANPR) – Deploy Script
 Author: Gaurish (AI-102) | Version: v1.0
================================================ #>

param(
  [string]$SubscriptionId = "<PUT-YOURS>",
  [string]$Location = "australiaeast",
  [string]$Env = "dev",
  [bool]$UseExistingResources = $false,

  # If using existing, fill these; otherwise ignored.
  [string]$ResourceGroup = "rg-veh-attendance",
  [string]$StorageAccountName = "stvehattnd",
  [string]$QueueName = "ingest",
  [string]$WebAppName = "veh-attendance-api",
  [string]$ContainerAppsEnv = "cae-veh-attendance"
)

$ErrorActionPreference = "Stop"

Write-Host ">>> Login & set subscription"
az account show 1>$null 2>$null; if ($LASTEXITCODE -ne 0) { az login | Out-Null }
az account set --subscription $SubscriptionId

if (-not $UseExistingResources) {
  $ResourceGroup      = "rg-veh-attendance-$Env"
  $StorageAccountName = "st$($Env)$(Get-Random)"
  $QueueName          = "ingest"
  $ContainerAppsEnv   = "cae-veh-$Env"
  $WebAppName         = "veh-att-api-$Env-$(Get-Random)"

  Write-Host ">>> Creating resource group and deploying Bicep..."
  az group create -n $ResourceGroup -l $Location | Out-Null

  az deployment group create `
    -g $ResourceGroup `
    -f ./deploy/main.bicep `
    -p location=$Location `
       storageAccountName=$StorageAccountName `
       queueName=$QueueName `
       containerAppsEnvName=$ContainerAppsEnv `
       webAppName=$WebAppName | Out-Null
}

Write-Host ">>> Fetching connection details"
$ST_CONN = az storage account show-connection-string -g $ResourceGroup -n $StorageAccountName --query connectionString -o tsv

# Save local app settings template
'{"AZURE_STORAGE_CONNECTION_STRING":"'+$ST_CONN+'","QUEUE_NAME":"'+$QueueName+'"}' | Out-File -Encoding utf8 ./deploy/local.settings.json

Write-Host "`n✅ Deployed resource group: $ResourceGroup"
Write-Host "   Storage account:      $StorageAccountName"
Write-Host "   Queue:                $QueueName"
Write-Host "   Web App (API):        $WebAppName"
Write-Host "`nNext steps:"
Write-Host "  1) Configure Event Grid (Blob Created -> Queue) OR run src/tools/backfill.py for local tests."
Write-Host "  2) Upload sample images to Storage containers: images-entry/ and images-exit/"
Write-Host "  3) Start processor locally:  python src/processor/main.py"
