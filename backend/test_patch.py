import re
with open("/usr/home/trusteei/flaskprojects/kspolonia/backend/app.py", "r") as f: content = f.read()

# Replace the whole admin function with a simple HTML string
new_func = """@app.get("/admin")
async def admin_dashboard(request: Request, team_id: Optional[str] = None):
    try:
        html_content = "<html><body><h1>Admin UI Test Successful!</h1></body></html>"
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content)
    except Exception as e:
        import traceback
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(traceback.format_exc())
"""
content = re.sub(r'@app\.get\("/admin"\).*', new_func, content, flags=re.DOTALL)
with open("/usr/home/trusteei/flaskprojects/kspolonia/backend/app.py", "w") as f: f.write(content)
