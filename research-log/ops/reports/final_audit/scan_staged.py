"""Bounded staged-delivery scan; no secret files or sensitive values printed."""
from pathlib import Path
import hashlib
import io
import json
import re
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
RULES = {
    "credential":re.compile(rb'\b(?:sk-(?:or-v1-)?[A-Za-z0-9_-]{28,}|gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[A-Z0-9]{16}|xox[baprs]-[A-Za-z0-9-]{20,}|AIza[A-Za-z0-9_-]{30,}|hf_[A-Za-z0-9]{25,})\b'),
    "private_key":re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    "bearer":re.compile(rb'\bBearer\s+[A-Za-z0-9_.-]{30,}'),
}
DOC = re.compile(rb'docs\.google\.com/(?:document|spreadsheets|presentation)/d/([A-Za-z0-9_-]{25,})')


def forbidden(name):
    p=Path(name)
    return p.name in {".env","compute.env"} or p.name.endswith(".local.json") or p.name.startswith(".env.")


def main():
    paths=subprocess.check_output(["git","diff","--cached","--name-only","-z"],cwd=ROOT).decode().split("\0")[:-1]
    hits=[];docs=[];secretpaths=[];textbytes=0;archive_members=0
    for name in paths:
        if forbidden(name):
            secretpaths.append(name);continue
        raw=subprocess.check_output(["git","show",":"+name],cwd=ROOT)
        blocks=[]
        if name.endswith(".tar.gz"):
            with tarfile.open(fileobj=io.BytesIO(raw),mode="r:gz") as tar:
                for member in tar:
                    if not member.isfile():continue
                    archive_members+=1
                    if forbidden(member.name):
                        secretpaths.append(name+"!"+member.name);continue
                    content=tar.extractfile(member).read()
                    if b"\0" not in content:blocks.append((name+"!"+member.name,content))
        elif Path(name).suffix not in {".png",".jpg",".jpeg",".pdf",".ttf",".gz"} and b"\0" not in raw:
            blocks=[(name,raw)]
        for location,content in blocks:
            textbytes+=len(content)
            for label,pattern in RULES.items():
                count=len(pattern.findall(content))
                if count:hits.append({"path":location,"rule":label,"count":count})
            docs.extend({"path":location,"id_fingerprint":hashlib.sha256(m[1]).hexdigest()[:16]} for m in DOC.finditer(content))
    assert not hits,hits
    assert not secretpaths,secretpaths
    assert all(x["id_fingerprint"]=="0a55e071e4a52347" for x in docs),docs
    result={"classification":"EXECUTED","scope":"all staged delivery text and audit snapshot tar text; binary fonts/images/PDF excluded from credential regex",
            "staged_paths":len(paths),"text_bytes":textbytes,"snapshot_archive_members":archive_members,
            "credential_matches":hits,"secret_file_paths":secretpaths,"doc_references":docs,"sensitive_values_printed":False,
            "limitations":"Bounded pattern scan; history is separate; source/PDF text independently checked. No secret values were read."}
    (OUT/"staged-release-scan.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ("staged_paths","credential_matches","secret_file_paths")}))


if __name__=="__main__":main()
