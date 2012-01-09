set /p issueNumber=What is the code review number you want to update?
"D:\Program Files\CodeReview\upload.py" --issue %issueNumber% --send_mail