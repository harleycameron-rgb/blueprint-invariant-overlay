"""End-to-end: synthetic/real field data -> IHB -> sealed release bundle."""
import json, hashlib, shutil, pathlib, numpy as np
from . import orrery, daemon_gate as g, differential_frame as d, invariant_hash as ih, sentinel_dot as sd, svc
def synthetic(n=4096, dt=60.0, drift=0.0, seed=0):
    r = np.random.default_rng(seed); s = np.arange(n)*dt
    v = np.c_[np.ones(n), 0.05*np.sin(2*np.pi*s/86400), 0.05*np.cos(2*np.pi*s/3600)]
    v[:, 1] += drift*s/s[-1]; return s, v + 0.01*r.standard_normal(v.shape)
def measure(s, v, device="device-A", ts="2026-01-01T00:00:00Z"):
    G = g.run_gate(v); T = orrery.tusi_trace(s); D = d.differential(G["coherence"], T)
    R = d.remove_periodic(s, D); f, P = d.residual_spectrum(R, s[1]-s[0])
    ihb = ih.build_ihb(T, G["coherence"], D, P, G["H"], G["closure"], len(G["rings"]), ts, device)
    return ihb, sd.seal(ihb), d.classify(s, R)
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
def build_release(out="release", root="."):
    out, root = pathlib.Path(out), pathlib.Path(root); out.mkdir(exist_ok=True)
    s, v = synthetic(); ihb, seal, cls = measure(s, v)
    render(out/"blueprint.jpeg"); img = (out/"blueprint.jpeg").read_bytes()
    (out/"invariant_hash_block.json").write_text(json.dumps(ihb, indent=2, sort_keys=True))
    (out/"sentinel_sha256.txt").write_text(seal+"\n")
    (out/"blueprint.svc").write_text(json.dumps(svc.build_svc(img, ihb, seal), indent=2))
    src = root/"src/blueprint_invariant"
    for f in ("orrery.py", "daemon_gate.py"): shutil.copy(src/f, out/f)
    shutil.copytree(root/"validation_suite", out/"validation_suite", dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("__pycache__"))
    for f in root.joinpath("docs").glob("*.md"): shutil.copy(f, out/f.name)
    shutil.copy(root/"README.md", out/"README.md")
    shutil.copy(root/"docs/compliance_report_template.json", out/"compliance_report_template.json")
    files = sorted(p for p in out.rglob("*") if p.is_file() and p.name not in ("manifest.json", "package_sha256.txt"))
    man = {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    (out/"manifest.json").write_text(json.dumps({"version": "1.0.0", "classification": cls, "files": man}, indent=2))
    pk = hashlib.sha256((out/"manifest.json").read_bytes()).hexdigest()
    (out/"package_sha256.txt").write_text(pk+"\n"); return out, seal, pk, cls
if __name__ == "__main__":
    o, s, p, c = build_release(); print(f"release={o} sentinel={s} package={p} classification={c}")
