"""End-to-end: synthetic/real field data -> IHB -> sealed release bundle."""
import json, hashlib, shutil, pathlib, numpy as np
from . import orrery, daemon_gate as g, differential_frame as d, invariant_hash as ih, sentinel_dot as sd, svc
def synthetic(n=4096, dt=60.0, drift=0.0, seed=0):
    r = np.random.default_rng(seed); s = np.arange(n)*dt
    v = np.c_[np.ones(n), 0.05*np.sin(2*np.pi*s/86400), 0.05*np.cos(2*np.pi*s/3600)]
    v[:, 1] += drift*s/s[-1]; return s, v + 0.01*r.standard_normal(v.shape)
def measure(s, v, device="device-A", ts="2026-01-01T00:00:00Z"):
    d.validate(s, v)
    G = g.run_gate(v); T = orrery.tusi_trace(s); D = d.differential(G["coherence"], T)
    R = d.remove_periodic(s, D, list(d.FACILITY_PERIODS.values()) + [86400.0/orrery.RATIO]); f, P = d.residual_spectrum(R, s[1]-s[0])
    ihb = ih.build_ihb(T, G["coherence"], D, P, G["H"], G["closure"], len(G["rings"]), ts, device)
    det = d.classify_drift(s, v, list(d.FACILITY_PERIODS.values()))
    return ihb, sd.seal(ihb), det["classification"]
def measure_detail(s, v, **kw):
    """Like measure() but also returns the per-channel drift statistics."""
    ihb, seal, _ = measure(s, v, **kw); return ihb, seal, d.classify_drift(s, v, list(d.FACILITY_PERIODS.values()))
def render(path):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 8), facecolor="#0b1020"); ax.set_facecolor("#0b1020"); ax.axis("off")
    t = np.linspace(0, 2*np.pi, 800)
    ax.plot(2.1*np.cos(t), 2.1*np.sin(t), color="#ffd484", lw=1.2, ls="--")
    for k, rr in enumerate(orrery.radial_partitions()):
        ax.plot(2*rr*np.cos(t), 2*rr*np.sin(t), color="#8a93b8", lw=.6, alpha=.6-k*.06)
    for i, a in enumerate(np.linspace(0, 2*np.pi, 12, endpoint=False)):
        ax.plot([0, 2*np.cos(a)], [0, 2*np.sin(a)], color="#8a93b8", lw=.4, alpha=.4)
        ax.text(2.25*np.cos(a), 2.25*np.sin(a), f"{i:02d}", color="#ffd484", family="monospace", ha="center", va="center", fontsize=9)
    for a in np.linspace(0, 2*np.pi, orrery.DIALS, endpoint=False):
        ax.plot([1.92*np.cos(a), 2*np.cos(a)], [1.92*np.sin(a), 2*np.sin(a)], color="#9fd0ff", lw=.3)
    # Tusi couples: inner circle r=1 rolling inside R=2 (A), second couple at ratio 1.37 (B)
    for k, ph in enumerate([0.6, 0.6*orrery.RATIO]):
        cx, cy = np.cos(ph), np.sin(ph); col = "#d4b8ff" if k == 0 else "#ffd484"
        ax.plot(cx+np.cos(t), cy+np.sin(t), color=col, lw=1.6)
        x, _ = orrery.tusi_position(ph); ax.plot(x, 0, "o", color=col, ms=7)
        ax.plot([-2, 2], [0, 0], color=col, lw=1.2, alpha=.7) if k == 0 else None
        ax.plot([0, cx], [0, cy], color=col, lw=1.0)
    ax.set_aspect("equal"); fig.savefig(path, dpi=150, facecolor=fig.get_facecolor()); plt.close(fig)
def _load_signer():
    """Signer from SENTINEL_DOT_SIGNING_KEY (PEM path); otherwise None (unsigned build)."""
    import os
    p = os.environ.get("SENTINEL_DOT_SIGNING_KEY")
    if not p: return None
    from sentinel_dot.signing import Signer
    pw = os.environ.get("SENTINEL_DOT_SIGNING_PASSWORD"); return Signer.from_file(p, pw.encode() if pw else None)
def _anchor(path):
    """OpenTimestamps-stamp a file (pending proof). Requires `ots` and network; opt-in via BLUEPRINT_ANCHOR=1."""
    import os, shutil as sh, subprocess
    if os.environ.get("BLUEPRINT_ANCHOR") != "1" or not sh.which("ots"): return None
    r = subprocess.run(["ots", "stamp", str(path)], capture_output=True, text=True, timeout=120)
    return str(path)+".ots" if r.returncode == 0 else None
def build_release(out="release", root=".", signer=None):
    out, root = pathlib.Path(out), pathlib.Path(root); out.mkdir(exist_ok=True)
    s, v = synthetic(); ihb, seal, cls = measure(s, v)
    render(out/"blueprint.jpeg"); img = (out/"blueprint.jpeg").read_bytes()
    (out/"invariant_hash_block.json").write_text(json.dumps(ihb, indent=2, sort_keys=True))
    (out/"sentinel_sha256.txt").write_text(seal+"\n")  # digest of canonical JSON, not file bytes
    signer = signer or _load_signer(); sig = None
    if signer is not None:
        _, sig = sd.sign(ihb, signer)
        (out/"sentinel_sig.txt").write_text(sig+"\n"); (out/"signer.pub").write_bytes(signer.public_pem())
    (out/"blueprint.svc").write_text(json.dumps(svc.build_svc(img, ihb, seal, signature=sig,
        public_key=signer.public_pem().decode() if signer else None), indent=2))
    src = root/"src/blueprint_invariant"
    for f in ("orrery.py", "daemon_gate.py"): shutil.copy(src/f, out/f)
    shutil.copytree(src, out/"src/blueprint_invariant", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for f in ("pyproject.toml", "LICENSE", "CITATION.cff"):
        if (root/f).exists(): shutil.copy(root/f, out/f)
    (out/"docs").mkdir(exist_ok=True)
    for f in root.joinpath("docs").iterdir(): shutil.copy(f, out/"docs"/f.name)
    shutil.copytree(root/"validation_suite", out/"validation_suite", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"))
    for f in root.joinpath("docs").glob("*.md"): shutil.copy(f, out/f.name)
    shutil.copy(root/"README.md", out/"README.md")
    shutil.copy(root/"docs/compliance_report_template.json", out/"compliance_report_template.json")
    files = sorted(p for p in out.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.name not in ("manifest.json", "package_sha256.txt"))
    man = {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (out/"manifest.json").write_text(json.dumps({"version": "1.0.2", "classification": cls, "files": man}, indent=2))
    pk = hashlib.sha256((out/"manifest.json").read_bytes()).hexdigest()
    (out/"package_sha256.txt").write_text(f"{pk}  manifest.json\n"); _anchor(out/"manifest.json")
    return out, seal, pk, cls
if __name__ == "__main__":
    o, s, p, c = build_release(); print(f"release={o} sentinel={s} package={p} classification={c}")
