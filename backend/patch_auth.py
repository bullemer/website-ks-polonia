import re
with open("/usr/home/trusteei/flaskprojects/kspolonia/backend/app.py", "r") as f: content = f.read()

# Replace the signature to remove Depends(get_current_username)
old_sig = 'async def admin_dashboard(request: Request, team_id: Optional[str] = None, username: str = Depends(get_current_username)):'
new_sig = 'async def admin_dashboard(request: Request, team_id: Optional[str] = None):'
content = content.replace(old_sig, new_sig)

with open("/usr/home/trusteei/flaskprojects/kspolonia/backend/app.py", "w") as f: f.write(content)
