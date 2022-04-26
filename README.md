# webhook_demo
## Create Lambda
- Create new Lambda and check. Expand "Advanced settings" and check "Enable function URL"
- Locate and copy "Function URL" and save it for later
- Copy `lambda_function.py` file contents into the `lamdba_function` code window
- Click on "Deploy"
- Define Environment Variables 
 - TIMESTAMP_DIFF_TOLERANCE_SEC 
 - MY_SECRET

## Use the client
- create venv
- pip install requirements
- Define Environment Variables 
 - TIMESTAMP_DIFF_TOLERANCE_SEC (same as lambda)
 - MY_SECRET (same as lambda)
 - WEBHOOK_URL (use the lambda "Function URL")
- Run `python main.py`
