from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from fastapi.responses import JSONResponse
from app.scanner import scan_secrets, scan_dangerous_functions, safe_clone, cleanup_dir
import json

app = FastAPI(title="Secure Repo Scanner", version="1.0.0")

class RepoRequest(BaseModel):
    repo_url: HttpUrl

@app.post("/scan/secrets")
async def scan_secrets_endpoint(request: RepoRequest):
    repo_path = safe_clone(request.repo_url)
    try:
        findings = scan_secrets(repo_path)
        return JSONResponse(content={"report": findings}, media_type="application/json")
    finally:
        cleanup_dir(repo_path)

@app.post("/scan/code")
async def scan_code_endpoint(request: RepoRequest):
    repo_path = safe_clone(request.repo_url)
    try:
        findings = scan_dangerous_functions(repo_path)
        return JSONResponse(content={"report": findings}, media_type="application/json")
    finally:
        cleanup_dir(repo_path)
