set /p reviewer=Who would you like to review your code?
"C:\Program Files\codereview\upload.py" --cc sucy-uci-code-reviews@googlegroups.com --reviewers %reviewer% --send_mail --server codereview.appspot.com
