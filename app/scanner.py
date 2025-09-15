import subprocess, tempfile, shutil, os, re
from fastapi import HTTPException
from collections import defaultdict

def safe_clone(repo_url):
    url_str = str(repo_url)
    if not url_str.startswith("https://github.com/"):
        raise HTTPException(status_code=400, detail="Only HTTPS GitHub URLs allowed")
    tmp_dir = tempfile.mkdtemp()
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", url_str, tmp_dir],
            check=True, timeout=30,
            env={"GIT_TERMINAL_PROMPT": "0"}
        )
        return tmp_dir
    except Exception:
        shutil.rmtree(tmp_dir)
        raise HTTPException(status_code=400, detail="Clone failed")

def cleanup_dir(path: str):
    shutil.rmtree(path, ignore_errors=True)

def prettify_findings(findings):
    grouped = defaultdict(set)
    for item in findings:
        grouped[item["file"]].update(item["matches"])
    pretty = [{"file": f, "matches": sorted(list(matches))} for f, matches in grouped.items()]
    return pretty

def scan_secrets(repo_path: str):
    secret_patterns = [
        r"api[_-]?key\s*=\s*[\"'].*?[\"']",  # non-greedy match
        r"secret\s*=\s*[\"'].*?[\"']",
        r"AWS_SECRET_ACCESS_KEY"
    ]
    findings = []
    for root, _, files in os.walk(repo_path):
        for fname in files:
            try:
                fpath = os.path.join(root, fname)
                with open(fpath, "r", errors="ignore") as f:
                    content = f.read()
                for pat in secret_patterns:
                    matches = re.findall(pat, content, flags=re.IGNORECASE)
                    if matches:
                        findings.append({"file": fpath, "matches": matches})
            except Exception:
                continue
    return prettify_findings(findings)

def scan_dangerous_functions(repo_path: str):
    func_patterns = [r"\beval\b", r"\bexec\b", r"\bpickle\.load\b"]
    findings = []
    for root, _, files in os.walk(repo_path):
        for fname in files:
            if fname.endswith(".py"):
                try:
                    fpath = os.path.join(root, fname)
                    with open(fpath, "r", errors="ignore") as f:
                        content = f.read()
                    for pat in func_patterns:
                        matches = re.findall(pat, content)
                        if matches:
                            findings.append({"file": fpath, "matches": matches})
                except Exception:
                    continue
    return prettify_findings(findings)
