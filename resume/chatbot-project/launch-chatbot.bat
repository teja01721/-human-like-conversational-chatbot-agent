@echo off
echo 🚀 Launching Human-Like Conversational Chatbot...
echo ================================================

REM Check if Chrome is installed
where chrome >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Chrome not found in PATH. Trying alternative methods...
    
    REM Try common Chrome installation paths
    if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
        set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
    ) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
        set CHROME_PATH="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ) else (
        echo ❌ Chrome not found. Opening with default browser...
        start "" "standalone-chatbot.html"
        goto :end
    )
) else (
    set CHROME_PATH=chrome
)

echo ✅ Found Chrome browser
echo 🌐 Opening chatbot in Chrome...

REM Launch Chrome with the chatbot
%CHROME_PATH% --new-window --app="file:///%CD%\standalone-chatbot.html"

echo ✅ Chatbot launched successfully!
echo 💬 You can now test all STAN Challenge features:
echo    - Memory recall across conversations
echo    - Emotional tone adaptation  
echo    - Personalized responses
echo    - Natural conversation variety
echo.
echo 🧪 Try these test cases:
echo    1. "My name is [YourName]" then ask "What's my name?"
echo    2. "I'm feeling sad today" vs "I'm so excited!"
echo    3. "I love [hobby]" then mention that hobby later
echo    4. Say "hello" multiple times for variety
echo.

:end
pause
