"""EXP-003 Modal app: gemma4:26b served by Ollama behind a bearer-authenticated proxy.

Design (cost-bounded):
* one GPU container max (``max_containers=1``), hard function timeout (default 2 h, never more),
  short ``scaledown_window``; the app is *ephemeral* (see modal_ctl.py) so it dies with its owner process;
* weights live in a Modal Volume (populated once by the CPU-only ``prefetch`` function);
* the per-session bearer token is passed to the container via an in-memory ``modal.Secret.from_dict``
  and is never printed or written to the repo;
* the web endpoint is ``https://*.modal.run`` (required by BudgetGuard's modal backend).

Config is read from environment at *definition* time on the local side (EXP003_GPU, EXP003_PARALLEL,
EXP003_TIMEOUT_S, EXP003_SCALEDOWN_S) and shipped to the container through the secret dict.
"""
import os
import subprocess
import time

import modal

MODEL = "gemma4:26b"
OLLAMA_VERSION = "0.32.5"          # same server version as the local EXP-002 host
EXPECTED_DIGEST = "5571076f3d70050487b26b341705799e0ab29b808164f90d20d4cf84f699d251"
# Exact EXP-002 weights (uploaded from the local Ollama store; the registry tag has since moved to another blob).
MODELS_DIR = "/models/legacy"
VOLUME_NAME = "exp003-ollama-models"
APP_NAME = "exp003-ollama-gemma4-26b"
GPU = os.environ.get("EXP003_GPU", "L40S")
PARALLEL = os.environ.get("EXP003_PARALLEL", "1")
TIMEOUT_S = min(int(os.environ.get("EXP003_TIMEOUT_S", "7200")), 7200)   # hard ceiling 2 h
SCALEDOWN_S = int(os.environ.get("EXP003_SCALEDOWN_S", "180"))
CPU = float(os.environ.get("EXP003_CPU", "8" if GPU == "none" else "4"))
MEM_MIB = int(os.environ.get("EXP003_MEM_MIB", "32768" if GPU == "none" else "16384"))
GPU_ARG = None if GPU == "none" else GPU   # "none" = CPU-only plumbing test, never for the experiment

image = (modal.Image.from_registry(f"ollama/ollama:{OLLAMA_VERSION}", add_python="3.12")
         .entrypoint([])
         .pip_install("fastapi==0.115.6", "httpx==0.28.1"))
volume = modal.Volume.from_name(VOLUME_NAME, create_if_missing=True)
app = modal.App(APP_NAME)
prefetch_app = modal.App(APP_NAME + "-prefetch")   # CPU-only, separate so it loads without any GPU entitlement

if modal.is_local():
    _cfg = {"EXP003_SERVER_TOKEN": os.environ.get("EXP003_MODAL_TOKEN", ""),
            "EXP003_DEADLINE_EPOCH": os.environ.get("EXP003_DEADLINE_EPOCH", "0"),
            "OLLAMA_NUM_PARALLEL": PARALLEL, "EXP003_MODELS_DIR": MODELS_DIR}
    secret = modal.Secret.from_dict(_cfg)
else:  # inside the container the secret is already injected into the environment
    secret = modal.Secret.from_dict({})


def _ollama_env():
    env = dict(os.environ)
    env.update(OLLAMA_MODELS=os.environ.get("EXP003_MODELS_DIR", MODELS_DIR), OLLAMA_HOST="127.0.0.1:11434", OLLAMA_KEEP_ALIVE="-1",
               OLLAMA_CONTEXT_LENGTH="32768", OLLAMA_NUM_PARALLEL=os.environ.get("OLLAMA_NUM_PARALLEL", "1"))
    env.pop("EXP003_SERVER_TOKEN", None)
    return env


def _start_ollama():
    import httpx
    proc = subprocess.Popen(["ollama", "serve"], env=_ollama_env(), stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)
    for _ in range(120):
        try:
            if httpx.get("http://127.0.0.1:11434/api/version", timeout=2).status_code == 200:
                return proc
        except Exception:
            time.sleep(1)
    raise RuntimeError("ollama serve did not become ready")


@prefetch_app.function(image=image, volumes={"/models": volume}, cpu=CPU, memory=MEM_MIB, timeout=3600,
              max_containers=1, secrets=[secret])
def prefetch(ref: str = MODEL):
    """CPU-only: pull ``ref`` into the Volume (no GPU billing) and alias it to MODEL. Returns identity facts.

    If ``ref`` differs from MODEL (e.g. ``gemma4:26b@sha256:<manifest digest>``), any existing MODEL entry is
    first preserved under an ``-registry-latest`` alias, then MODEL is re-pointed at the pulled ref."""
    import httpx
    base = "http://127.0.0.1:11434"
    proc = _start_ollama()
    try:
        t0 = time.time()
        tags0 = httpx.get(base + "/api/tags").json().get("models", [])
        before = [{"name": m["name"], "digest": m["digest"], "size": m["size"]} for m in tags0]
        if ref != MODEL and any(m["name"] == MODEL for m in tags0):
            httpx.post(base + "/api/copy", json={"source": MODEL, "destination": MODEL + "-registry-latest"}).raise_for_status()
            httpx.request("DELETE", base + "/api/delete", json={"model": MODEL}).raise_for_status()
        err = None
        with httpx.stream("POST", base + "/api/pull", json={"model": ref}, timeout=3300) as r:
            for line in r.iter_lines():
                if '"error"' in line:
                    err = line[:300]
        if err:
            return {"error": err, "before": before}
        if ref != MODEL:
            httpx.post(base + "/api/copy", json={"source": ref, "destination": MODEL}).raise_for_status()
        volume.commit()
        tags = httpx.get(base + "/api/tags").json()
        ver = httpx.get(base + "/api/version").json()
        ents = [{k: m[k] for k in ("name", "digest", "size", "modified_at")} | {"details": m.get("details")}
                for m in tags.get("models", [])]
        return {"pull_seconds": round(time.time() - t0, 1), "ref": ref, "server_version": ver, "before": before,
                "tag_entries": ents, "expected_digest": EXPECTED_DIGEST}
    finally:
        proc.terminate()


@prefetch_app.function(image=image, volumes={"/models": volume}, cpu=CPU, memory=MEM_MIB, timeout=900,
                       max_containers=1)
def identity_check(models_dir: str = MODELS_DIR):
    """CPU-only: start Ollama on ``models_dir`` and report the tag digest/size/details (no GPU, no load)."""
    import httpx
    os.environ["EXP003_MODELS_DIR"] = models_dir
    proc = _start_ollama()
    try:
        tags = httpx.get("http://127.0.0.1:11434/api/tags").json()
        ver = httpx.get("http://127.0.0.1:11434/api/version").json()
        ents = [{k: m[k] for k in ("name", "digest", "size")} | {"details": m.get("details")}
                for m in tags.get("models", [])]
        return {"server_version": ver, "models_dir": models_dir, "tag_entries": ents,
                "equals_expected": any(e["digest"].removeprefix("sha256:") == EXPECTED_DIGEST for e in ents)}
    finally:
        proc.terminate()


@app.cls(image=image, gpu=GPU_ARG, volumes={"/models": volume}, cpu=CPU, memory=MEM_MIB,
         timeout=TIMEOUT_S, startup_timeout=1800, scaledown_window=SCALEDOWN_S, max_containers=1,
         secrets=[secret])
@modal.concurrent(max_inputs=32)
class Server:
    @modal.enter()
    def boot(self):
        import httpx
        import threading
        deadline = float(os.environ.get("EXP003_DEADLINE_EPOCH", "0"))
        if deadline <= time.time():
            raise RuntimeError("controller absolute deadline missing or expired")
        def absolute_shutdown():
            # Kill Ollama as well as the proxy, independently of an in-flight request.
            if hasattr(self, "proc"):
                self.proc.kill()
            os._exit(0)
        timer = threading.Timer(max(.001, deadline-time.time()), absolute_shutdown)
        timer.daemon = True
        timer.start()
        self.t_boot = time.time()
        self.proc = _start_ollama()
        tags = httpx.get("http://127.0.0.1:11434/api/tags").json()
        if not any(m.get("name") == MODEL for m in tags.get("models", [])):
            raise RuntimeError("model missing from Volume; run `modal_ctl.py prefetch` first (refusing GPU pull)")
        # load and pin the model (keep_alive=-1, num_ctx from OLLAMA_CONTEXT_LENGTH)
        httpx.post("http://127.0.0.1:11434/api/generate",
                   json={"model": MODEL, "prompt": "ok", "stream": False, "keep_alive": -1,
                         "options": {"num_ctx": 32768, "num_predict": 1}}, timeout=900)
        # second warm-up through the exact endpoint/options the runner uses, so the first real request cannot
        # trigger a model re-load (the runner treats any reload as invalid)
        httpx.post("http://127.0.0.1:11434/v1/chat/completions",
                   json={"model": MODEL, "messages": [{"role": "user", "content": "ok"}], "max_tokens": 1,
                         "keep_alive": -1, "options": {"num_ctx": 32768}}, timeout=900)
        self.t_ready = time.time()
        self.n_requests = 0
        self.last_request = self.t_ready

    @modal.exit()
    def shutdown(self):
        try:
            self.proc.terminate()
        except Exception:
            pass

    @modal.asgi_app()
    def web(self):
        import httpx
        from fastapi import FastAPI, Request, Response
        token = os.environ.get("EXP003_SERVER_TOKEN", "")
        api = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
        client = httpx.AsyncClient(base_url="http://127.0.0.1:11434", timeout=900)
        import hmac

        def authed(request: Request) -> bool:
            got = request.headers.get("authorization", "")
            return bool(token) and hmac.compare_digest(got, f"Bearer {token}")

        @api.get("/exp003/info")
        async def info(request: Request):
            if not authed(request):
                return Response(status_code=401)
            ps = subprocess.run(["ps", "-axo", "pid=,ppid=,etimes=,command="], capture_output=True, text=True).stdout
            runner = [l.split(None, 3) for l in ps.splitlines() if "ollama runner" in l or "llama-server" in l]
            try:
                smi = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,memory.used,driver_version",
                                      "--format=csv,noheader"], capture_output=True, text=True).stdout.strip()
            except OSError:
                smi = "no-gpu"
            import json
            return Response(json.dumps({
                "task_id": os.environ.get("MODAL_TASK_ID"), "ollama_pid": self.proc.pid,
                "runner_pids": [r[0] for r in runner], "boot_epoch": self.t_boot, "ready_epoch": self.t_ready,
                "now_epoch": time.time(), "uptime_s": round(time.time() - self.t_boot, 1),
                "n_requests": self.n_requests, "last_request_epoch": self.last_request, "gpu": smi,
                "num_parallel": os.environ.get("OLLAMA_NUM_PARALLEL")}), media_type="application/json")

        @api.api_route("/{path:path}", methods=["GET", "POST"])
        async def proxy(path: str, request: Request):
            if not authed(request):
                return Response(status_code=401)
            self.n_requests += 1
            self.last_request = time.time()
            body = await request.body()
            r = await client.request(request.method, "/" + path, params=request.query_params, content=body,
                                     headers={"content-type": request.headers.get("content-type", "application/json")})
            self.last_request = time.time()
            return Response(content=r.content, status_code=r.status_code,
                            media_type=r.headers.get("content-type", "application/json"))

        return api
