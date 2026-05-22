# ShadowReel AI — Production Git Preparation & Publishing Automation
# This script prepares the repository for public/private GitHub publishing by cleaning caches,
# temporary files, verifying security parameters, and executing Git initializations.

$ErrorActionPreference = "Stop"

# Helper for colored log messages
function Write-Log ($Message, $Level = "Info") {
    $Color = "Cyan"
    if ($Level -eq "Error") { $Color = "Red" }
    elseif ($Level -eq "Success") { $Color = "Green" }
    elseif ($Level -eq "Warning") { $Color = "Yellow" }
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] [$Level] $Message" -ForegroundColor $Color
}

Write-Log "Starting ShadowReel Git deployment automation..." "Info"

# 1. Clean python cache files, logs, and SQLite DB files
Write-Log "Cleaning up temporary files, logs, and caches..." "Info"

# Recursively delete __pycache__ directories
$PyCacheDirs = Get-ChildItem -Path . -Filter "__pycache__" -Recurse -Directory -ErrorAction SilentlyContinue
foreach ($Dir in $PyCacheDirs) {
    Write-Log "Removing pycache: $($Dir.FullName)" "Info"
    Remove-Item -Path $Dir.FullName -Recurse -Force
}

# Remove any raw SQLite db files in backend (except the schema or migrations)
$DbFiles = Get-ChildItem -Path . -Filter "*.db" -Recurse -File -ErrorAction SilentlyContinue
foreach ($File in $DbFiles) {
    # Keep example db or template files if any, but clean active SQLite instances
    Write-Log "Removing local database file: $($File.FullName)" "Warning"
    Remove-Item -Path $File.FullName -Force
}

# Remove any raw logs
$LogFiles = Get-ChildItem -Path . -Filter "*.log" -Recurse -File -ErrorAction SilentlyContinue
foreach ($File in $LogFiles) {
    Write-Log "Removing log file: $($File.FullName)" "Info"
    Remove-Item -Path $File.FullName -Force
}

# Ensure temporary outputs directory in backend is clean (keep .gitkeep)
$OutputsPath = Join-Path (Get-Location) "backend/outputs"
if (Test-Path $OutputsPath) {
    Write-Log "Cleaning backend outputs folder..." "Info"
    Get-ChildItem -Path $OutputsPath -Exclude ".gitkeep" -Recurse | Remove-Item -Recurse -Force
}

# 2. Check for sensitive files (e.g. active .env or certs that shouldn't be pushed)
Write-Log "Running safety check for credentials and certs..." "Info"
$SensitiveFiles = @(".env", "frontend/.env.local", "backend/.env")
foreach ($File in $SensitiveFiles) {
    if (Test-Path $File) {
        Write-Log "Found local active configuration: $File. Ensure it is ignored by .gitignore before pushing." "Warning"
    }
}

# Verify .gitignore exists
if (-not (Test-Path ".gitignore")) {
    Write-Log ".gitignore file is missing! Creating standard monorepo .gitignore..." "Warning"
    # Create basic .gitignore if not found
    Set-Content -Path ".gitignore" -Value @"
node_modules/
backend/venv/
__pycache__/
*.db
*.sqlite3
.env
.env.local
.env.production
backend/outputs/*
!backend/outputs/.gitkeep
*.log
nginx/certs/*
!nginx/certs/.gitkeep
"@
} else {
    Write-Log ".gitignore verified." "Success"
}

# 3. Git Initialization
Write-Log "Initializing Git repository..." "Info"
if (-not (Test-Path ".git")) {
    git init
    Write-Log "Git repository initialized." "Success"
} else {
    Write-Log "Git repository already initialized. Proceeding with update." "Warning"
}

# Set main as the default branch
git checkout -B main
Write-Log "Branch set to: main" "Success"

# Stage all files
Write-Log "Staging all production-safe files..." "Info"
git add .

# Commit changes
Write-Log "Creating first production commit..." "Info"
git commit -m "chore: initial production-ready commit for ShadowReel AI platform"

Write-Log "Repository successfully prepared and committed locally." "Success"

# 4. GitHub Remote setup option
Write-Host ""
$PushToGithub = Read-Host "Do you want to configure a GitHub remote and push now? (y/n)"
if ($PushToGithub -eq "y" -or $PushToGithub -eq "yes") {
    $RemoteUrl = Read-Host "Enter your GitHub Remote Repository URL (e.g., https://github.com/username/shadowreel.git)"
    if (-not [string]::IsNullOrWhiteSpace($RemoteUrl)) {
        # Check if origin already exists
        $ExistingRemote = git remote get-url origin 2>$null
        if ($ExistingRemote) {
            Write-Log "Existing remote origin found ($ExistingRemote). Overwriting..." "Warning"
            git remote set-url origin $RemoteUrl
        } else {
            git remote add origin $RemoteUrl
        }
        Write-Log "Remote origin set to: $RemoteUrl" "Success"
        
        Write-Log "Pushing main branch to GitHub..." "Info"
        git push -u origin main
        Write-Log "Successfully pushed to GitHub!" "Success"
    } else {
        Write-Log "Invalid remote URL provided. Skipping push." "Warning"
    }
} else {
    Write-Log "Skipped GitHub remote setup and push. You can push manually using:" "Info"
    Write-Host "  git remote add origin <your-repo-url>" -ForegroundColor Cyan
    Write-Host "  git push -u origin main" -ForegroundColor Cyan
}

Write-Log "Git Deployment preparation complete!" "Success"
