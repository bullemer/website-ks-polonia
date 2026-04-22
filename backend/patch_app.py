import re
with open("backend/app.py", "r") as f: content = f.read()
repl = """    try:
        return templates.TemplateResponse(
            request=request, 
            name="admin.html", 
            context={
                "teams": teams, 
                "players": players, 
                "selected_team_id": team_id or ""
            }
        )
    except Exception as e:
        import traceback
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": "traceback", "trace": traceback.format_exc()})"""
content = re.sub(r'    return templates\.TemplateResponse\(\s+request=request,\s+name="admin\.html",\s+context=\{[^{}]+\}\s+\)', repl, content, re.DOTALL)
with open("backend/app.py", "w") as f: f.write(content)
