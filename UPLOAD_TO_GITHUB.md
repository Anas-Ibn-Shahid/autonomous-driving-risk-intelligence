# Upload this project to GitHub (Windows)

This project is configured for:

<https://github.com/Anas-Ibn-Shahid/autonomous-driving-risk-intelligence>

## Easiest method

1. Download the project ZIP and choose **Extract All** in Windows.
2. Open the extracted `autonomous-driving-risk-intelligence` folder.
3. Double-click `publish_to_github.bat`.
4. If asked, enter the name and email you want attached to your Git commits.
5. Git may open a browser so you can sign in to GitHub and authorize the push.
6. When the script says **SUCCESS**, open the repository link above and refresh the page.

The script runs from its own folder, initializes Git, stages the project, commits the files, and pushes the `main` branch. It does not upload local files ignored by `.gitignore`, including raw ANAID data and generated model artifacts.

## Requirements

- Windows
- Git for Windows: <https://git-scm.com/download/win>
- Write access to the GitHub repository above
- Internet access and GitHub authentication

If Git was just installed, close and reopen File Explorer or Command Prompt before retrying.

## Troubleshooting

**`git is not recognized` or Git was not found**  
Install Git for Windows, then run the script again.

**GitHub sign-in or permission error**  
Complete the browser sign-in prompt and confirm that the signed-in GitHub account has write access to the target repository.

**`rejected` / `fetch first`**  
The remote repository may contain a commit that is not in this local folder. Do not force-push. Open a terminal in the project folder and run `git pull --rebase origin main`, resolve any reported conflicts, then run `git push -u origin main`.

**The project uploaded but the dashboard does not open**  
Uploading code does not install dependencies or run the app. To run it locally, follow the Quick Start commands in `README.md`.

## Before publishing

Review the staged file list if you add anything later. Never commit passwords, API keys, access tokens, private data, or raw datasets you do not have permission to redistribute. The included sample CSV is synthetic demonstration data, not genuine vehicle telemetry.
