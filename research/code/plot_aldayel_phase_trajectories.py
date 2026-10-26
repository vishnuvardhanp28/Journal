"""Reintegrate the Al-Dayel et al. 4-D ODE for a disclosed phase-portrait figure.

This is a numerical trajectory illustration, not a reproduction of the image
encryption implementation or a proof of chaos/security. The source article
does not specify its solver step/tolerances; these are therefore disclosed
independent choices in this script.
"""
from pathlib import Path
import json
import platform
import sys

import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "manuscript" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

INITIAL = np.array([19.0, 37.0, 113.0, 12.0])
PARAMS = {"p": -7.0, "q": 3.0, "r": -1.2, "s": -2.0,
          "c1": 2.0, "c2": -1.0, "c3": 1.0, "c4": 1.0}
T0, T1, TRANSIENT = 0.0, 100.0, 10.0
SAMPLES = 45_001  # equally spaced samples over [10, 100]


def system(_t: float, state: np.ndarray) -> np.ndarray:
    x, y, z, w = state
    p, q, r, s = PARAMS["p"], PARAMS["q"], PARAMS["r"], PARAMS["s"]
    c1, c2, c3, c4 = PARAMS["c1"], PARAMS["c2"], PARAMS["c3"], PARAMS["c4"]
    return np.array([
        p * x - c1 * y * z * w,
        q * y - c2 * x * z * w,
        r * z - c3 * x * y * w,
        s * w - c4 * x * y * z,
    ])


def main() -> None:
    t_eval = np.linspace(TRANSIENT, T1, SAMPLES)
    sol = solve_ivp(
        system, (T0, T1), INITIAL, method="DOP853", t_eval=t_eval,
        rtol=1e-6, atol=1e-8,
    )
    if not sol.success or sol.y.shape != (4, SAMPLES) or not np.isfinite(sol.y).all():
        raise RuntimeError(f"ODE integration failed: {sol.message}")
    x, y, z, w = sol.y

    plt.rcParams.update({"font.size": 9, "axes.labelsize": 9,
                         "xtick.labelsize": 8, "ytick.labelsize": 8,
                         "font.family": "serif"})
    fig = plt.figure(figsize=(10.4, 6.5), constrained_layout=True)
    ax_xy = fig.add_subplot(2, 3, 1)
    ax_xz = fig.add_subplot(2, 3, 2)
    ax_xw = fig.add_subplot(2, 3, 3)
    ax_yz = fig.add_subplot(2, 3, 4)
    ax_xyz = fig.add_subplot(2, 3, 5, projection="3d")
    ax_yzw = fig.add_subplot(2, 3, 6, projection="3d")
    color = "#1675b9"
    lw = 0.42
    for ax, a, b, xlabel, ylabel in [
        (ax_xy, x, y, "$x$", "$y$"),
        (ax_xz, x, z, "$x$", "$z$"),
        (ax_xw, x, w, "$x$", "$w$"),
        (ax_yz, y, z, "$y$", "$z$"),
    ]:
        ax.plot(a, b, color=color, linewidth=lw, alpha=0.8)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.grid(True, linewidth=0.35, alpha=0.35)
        ax.ticklabel_format(style="sci", axis="both", scilimits=(-3, 4))

    ax_xyz.plot(x, y, z, color=color, linewidth=lw, alpha=0.8)
    ax_xyz.set_xlabel("$x$")
    ax_xyz.set_ylabel("$y$")
    ax_xyz.set_zlabel("$z$")
    ax_xyz.tick_params(labelsize=7, pad=0)
    ax_yzw.plot(y, z, w, color=color, linewidth=lw, alpha=0.8)
    ax_yzw.set_xlabel("$y$")
    ax_yzw.set_ylabel("$z$")
    ax_yzw.set_zlabel("$w$")
    ax_yzw.tick_params(labelsize=7, pad=0)
    fig.suptitle("Phase-space projections of the reported four-state system", fontsize=12)
    fig.savefig(FIGURES / "aldayel_4d_phase_portrait.pdf", bbox_inches="tight")
    fig.savefig(FIGURES / "aldayel_4d_phase_portrait.png", dpi=300, bbox_inches="tight")
    plt.close(fig)

    report = {
        "scope": "ODE trajectory illustration only; not a full image-cipher reproduction or security result",
        "source": "Al-Dayel et al., Scientific Reports (2025), DOI 10.1038/s41598-025-95511-y",
        "initial_state": INITIAL.tolist(),
        "parameters": PARAMS,
        "solver": "DOP853",
        "relative_tolerance": 1e-6,
        "absolute_tolerance": 1e-8,
        "integration_interval": [T0, T1],
        "plotted_interval": [TRANSIENT, T1],
        "plotted_samples": SAMPLES,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "matplotlib": plt.matplotlib.__version__,
        "min_state_values": np.min(sol.y, axis=1).tolist(),
        "max_state_values": np.max(sol.y, axis=1).tolist(),
        "final_state": sol.y[:, -1].tolist(),
        "finite_solution": bool(np.isfinite(sol.y).all()),
    }
    (ROOT / "results" / "aldayel_phase_portrait_run.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Saved projections using DOP853 over [{T0}, {T1}], transient [0, {TRANSIENT}) omitted.")
    print(f"rtol=1e-6, atol=1e-8, samples={SAMPLES}; finite={np.isfinite(sol.y).all()}")
    print("This figure alone does not establish chaos, hyperchaos, or cryptographic security.")


if __name__ == "__main__":
    main()
