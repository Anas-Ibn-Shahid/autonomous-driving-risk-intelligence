@echo off
setlocal
cd /d "%~dp0"
set "REPO_URL=https://github.com/Anas-Ibn-Shahid/autonomous-driving-risk-intelligence.git"

echo ======================================================
echo  Publish Autonomous Driving Risk Intelligence to GitHub
echo ======================================================
echo.

where git >nul 2>nul
if errorlevel 1 goto :no_git

if not exist ".git" (
  echo Initializing local Git repository...
  git init
  if errorlevel 1 goto :failed
)

git branch -M main
if errorlevel 1 goto :failed

rem Configure commit identity locally if it is not already set.
git config user.name >nul 2>nul
if errorlevel 1 goto :configure_name
goto :check_email

:configure_name
echo Enter the name to show on your Git commits.
set /p "GIT_NAME=Name: "
git config user.name "%GIT_NAME%"
if errorlevel 1 goto :failed

:check_email
git config user.email >nul 2>nul
if errorlevel 1 goto :configure_email
goto :set_remote

:configure_email
echo Enter your GitHub email or GitHub noreply email.
set /p "GIT_EMAIL=Email: "
git config user.email "%GIT_EMAIL%"
if errorlevel 1 goto :failed

:set_remote

rem Point origin to the intended public repository.
git remote get-url origin >nul 2>nul
if errorlevel 1 (
  git remote add origin "%REPO_URL%"
) else (
  git remote set-url origin "%REPO_URL%"
)
if errorlevel 1 goto :failed

echo.
echo Staging project files...
git add -A
if errorlevel 1 goto :failed

git diff --cached --quiet
if errorlevel 1 goto :make_commit
if errorlevel 2 goto :failed
echo No file changes to commit.
goto :push

:make_commit
git commit -m "Add autonomous driving risk intelligence project"
if errorlevel 1 goto :failed

:push
echo.
echo Pushing project to GitHub...
echo GitHub may open a browser for sign-in on the first push.
git push -u origin main
if errorlevel 1 goto :failed

echo.
echo SUCCESS: Project uploaded to:
echo https://github.com/Anas-Ibn-Shahid/autonomous-driving-risk-intelligence
echo.
pause
exit /b 0

:no_git
echo Git was not found on this computer.
echo Install Git for Windows from https://git-scm.com/download/win
 echo Then close and reopen this window and run this file again.
echo.
pause
exit /b 1

:failed
echo.
echo Upload did not finish. Read the Git error above.
echo Common causes: GitHub sign-in is incomplete or the remote repository is not empty.
echo See UPLOAD_TO_GITHUB.md for troubleshooting.
echo.
pause
exit /b 1
