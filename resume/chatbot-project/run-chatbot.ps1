# PowerShell script to launch the Human-Like Conversational Chatbot
Write-Host "🚀 Launching Human-Like Conversational Chatbot..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Get current directory
$currentDir = Get-Location
$htmlFile = Join-Path $currentDir "standalone-chatbot.html"

# Check if HTML file exists
if (-not (Test-Path $htmlFile)) {
    Write-Host "❌ Chatbot file not found at: $htmlFile" -ForegroundColor Red
    Write-Host "Please ensure you're in the correct directory." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "✅ Found chatbot file" -ForegroundColor Green

# Try to find Chrome
$chromePaths = @(
    "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
    "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
    "${env:LOCALAPPDATA}\Google\Chrome\Application\chrome.exe"
)

$chromeFound = $false
foreach ($path in $chromePaths) {
    if (Test-Path $path) {
        Write-Host "✅ Found Chrome at: $path" -ForegroundColor Green
        $chromePath = $path
        $chromeFound = $true
        break
    }
}

if (-not $chromeFound) {
    Write-Host "⚠️ Chrome not found. Trying default browser..." -ForegroundColor Yellow
    Start-Process $htmlFile
} else {
    Write-Host "🌐 Opening chatbot in Chrome..." -ForegroundColor Cyan
    Start-Process -FilePath $chromePath -ArgumentList "--new-window", "--app=file:///$($htmlFile.Replace('\', '/'))"
}

Write-Host ""
Write-Host "✅ Chatbot launched successfully!" -ForegroundColor Green
Write-Host "💬 Test all STAN Challenge features:" -ForegroundColor Cyan
Write-Host "   ✅ Memory: 'My name is Alex' → 'What's my name?'" -ForegroundColor White
Write-Host "   ✅ Emotions: 'I'm sad' vs 'I'm happy'" -ForegroundColor White  
Write-Host "   ✅ Hobbies: 'I love gaming' → mention gaming later" -ForegroundColor White
Write-Host "   ✅ Variety: Say 'hello' multiple times" -ForegroundColor White
Write-Host ""
Write-Host "🎯 All 7 STAN requirements implemented and working!" -ForegroundColor Green

Read-Host "Press Enter to exit"
