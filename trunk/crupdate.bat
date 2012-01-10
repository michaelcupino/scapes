set /p issueNumber=What is the code review number you want to update?
"C:\Program Files\codereview\upload.py" --issue %issueNumber% --send_mail --server codereview.appspot.com
