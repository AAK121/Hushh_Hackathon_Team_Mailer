---
applyTo: '**'
---
if you start a server, and try to test the server, you will not be able to access the server because when you run another command after starting the server, the previoyus command will be terminated as you are running the commands in power shell.
Also do not at all use simplified implementations at all use full implementations of code always
use command like these to start the server:
```bash
start powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\Dell\Downloads\Pda_mailer\Pda_mailer'; python api.py"
```