import os
import numpy as np
import matplotlib.pyplot as plt


OUTPUT_DIR = "results/figures_report"
TABLE_DIR = "results/report_tables"


def trimf(x, a, b, c):
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x, dtype=float)

    idx = (a < x) & (x <= b)
    y[idx] = (x[idx] - a) / (b - a)

    idx = (b < x) & (x < c)
    y[idx] = (c - x[idx]) / (c - b)

    y[x == b] = 1.0
    return np.clip(y, 0.0, 1.0)


def trapmf(x, a, b, c, d):
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x, dtype=float)

    if a == b:
        y[x <= b] = 1.0
    else:
        idx = (a < x) & (x < b)
        y[idx] = (x[idx] - a) / (b - a)

    idx = (b <= x) & (x <= c)
    y[idx] = 1.0

    if c == d:
        y[x >= c] = 1.0
    else:
        idx = (c < x) & (x < d)
        y[idx] = (d - x[idx]) / (d - c)

    if a != b:
        y[x <= a] = 0.0

    if c != d:
        y[x >= d] = 0.0

    return np.clip(y, 0.0, 1.0)


def centroid(x, mu):
    luas = np.sum(mu)
    if luas <= 1e-12:
        return 0.0
    return float(np.sum(x * mu) / luas)


def hitung_manual():
    x_c = 0.50
    bbox_bottom = 0.80
    bbox_area = 0.23
    visual_ttc = 2.80
    dlog_area = 0.11
    corridor_bonus = 0.10

    lateral = 2.0 * (x_c - 0.50)

    area_norm = bbox_area / 0.45
    area_norm = min(max(area_norm, 0.0), 1.0)

    proximity = 0.65 * bbox_bottom + 0.35 * area_norm
    proximity = min(max(proximity, 0.0), 1.0)

    if visual_ttc <= 1.5:
        ttc_norm = 1.0
    elif visual_ttc >= 6.0:
        ttc_norm = 0.0
    else:
        ttc_norm = (6.0 - visual_ttc) / 4.5

    dlog_norm = dlog_area / 0.18
    dlog_norm = min(max(dlog_norm, 0.0), 1.0)

    urgency = 0.70 * ttc_norm + 0.30 * dlog_norm + corridor_bonus
    urgency = min(max(urgency, 0.0), 1.0)

    mu_l_center = float(trimf(np.array([lateral]), -0.35, 0.00, 0.35)[0])
    mu_p_medium = float(trimf(np.array([proximity]), 0.30, 0.55, 0.80)[0])
    mu_p_near = float(trapmf(np.array([proximity]), 0.65, 0.82, 1.00, 1.00)[0])
    mu_u_medium = float(trimf(np.array([urgency]), 0.30, 0.55, 0.80)[0])
    mu_u_high = float(trapmf(np.array([urgency]), 0.75, 0.90, 1.00, 1.00)[0])

    alpha_1 = min(mu_l_center, mu_p_medium, mu_u_medium)
    alpha_2 = min(mu_l_center, mu_p_medium, mu_u_high)
    alpha_3 = min(mu_l_center, mu_p_near, mu_u_medium)
    alpha_4 = min(mu_l_center, mu_p_near, mu_u_high)

    risk_medium_level = alpha_1
    risk_high_level = max(alpha_2, alpha_3, alpha_4)

    speed_slow_level = max(alpha_1, alpha_2)
    speed_stop_level = max(alpha_3, alpha_4)

    turn_right_level = max(alpha_1, alpha_2, alpha_3, alpha_4)

    x_risk = np.linspace(0.0, 1.0, 2500)
    risk_low = trapmf(x_risk, 0.00, 0.00, 0.18, 0.35)
    risk_medium = trimf(x_risk, 0.25, 0.45, 0.65)
    risk_high = trapmf(x_risk, 0.62, 0.78, 1.00, 1.00)

    risk_medium_clip = np.minimum(risk_medium_level, risk_medium)
    risk_high_clip = np.minimum(risk_high_level, risk_high)
    risk_agg = np.maximum(risk_medium_clip, risk_high_clip)
    risk_crisp = centroid(x_risk, risk_agg)

    x_speed = np.linspace(0.0, 1.0, 2500)
    speed_stop = trapmf(x_speed, 0.00, 0.00, 0.05, 0.18)
    speed_slow = trimf(x_speed, 0.12, 0.35, 0.58)
    speed_normal = trapmf(x_speed, 0.50, 0.72, 1.00, 1.00)

    speed_stop_clip = np.minimum(speed_stop_level, speed_stop)
    speed_slow_clip = np.minimum(speed_slow_level, speed_slow)
    speed_agg = np.maximum(speed_stop_clip, speed_slow_clip)
    speed_crisp = centroid(x_speed, speed_agg)

    x_turn = np.linspace(-1.0, 1.0, 2500)
    turn_left = trapmf(x_turn, -1.00, -1.00, -0.75, -0.22)
    turn_straight = trimf(x_turn, -0.30, 0.00, 0.30)
    turn_right = trapmf(x_turn, 0.22, 0.75, 1.00, 1.00)

    turn_right_clip = np.minimum(turn_right_level, turn_right)
    turn_agg = turn_right_clip
    turn_crisp = centroid(x_turn, turn_agg)

    return {
        "x_c": x_c,
        "bbox_bottom": bbox_bottom,
        "bbox_area": bbox_area,
        "visual_ttc": visual_ttc,
        "dlog_area": dlog_area,
        "corridor_bonus": corridor_bonus,
        "lateral": lateral,
        "area_norm": area_norm,
        "proximity": proximity,
        "ttc_norm": ttc_norm,
        "dlog_norm": dlog_norm,
        "urgency": urgency,
        "mu_l_center": mu_l_center,
        "mu_p_medium": mu_p_medium,
        "mu_p_near": mu_p_near,
        "mu_u_medium": mu_u_medium,
        "mu_u_high": mu_u_high,
        "alpha_1": alpha_1,
        "alpha_2": alpha_2,
        "alpha_3": alpha_3,
        "alpha_4": alpha_4,
        "risk_medium_level": risk_medium_level,
        "risk_high_level": risk_high_level,
        "speed_slow_level": speed_slow_level,
        "speed_stop_level": speed_stop_level,
        "turn_right_level": turn_right_level,
        "x_risk": x_risk,
        "risk_low": risk_low,
        "risk_medium": risk_medium,
        "risk_high": risk_high,
        "risk_medium_clip": risk_medium_clip,
        "risk_high_clip": risk_high_clip,
        "risk_agg": risk_agg,
        "risk_crisp": risk_crisp,
        "x_speed": x_speed,
        "speed_stop": speed_stop,
        "speed_slow": speed_slow,
        "speed_normal": speed_normal,
        "speed_stop_clip": speed_stop_clip,
        "speed_slow_clip": speed_slow_clip,
        "speed_agg": speed_agg,
        "speed_crisp": speed_crisp,
        "x_turn": x_turn,
        "turn_left": turn_left,
        "turn_straight": turn_straight,
        "turn_right": turn_right,
        "turn_right_clip": turn_right_clip,
        "turn_agg": turn_agg,
        "turn_crisp": turn_crisp,
    }


def simpan_ringkasan(data):
    os.makedirs(TABLE_DIR, exist_ok=True)
    path = os.path.join(TABLE_DIR, "perhitungan_manual_mamdani_transisi.txt")

    isi = f"""PERHITUNGAN MANUAL MAMDANI FUZZY LOGIC CONTROLLER
Kasus: obstacle depan transisi

Data visual:
x_c = {data["x_c"]:.2f}
B = {data["bbox_bottom"]:.2f}
A = {data["bbox_area"]:.2f}
T_vTTC = {data["visual_ttc"]:.2f} s
dlog(A) = {data["dlog_area"]:.2f}
C = {data["corridor_bonus"]:.2f}

Normalisasi:
L = {data["lateral"]:.3f}
A_n = {data["area_norm"]:.3f}
P = {data["proximity"]:.3f}
T_n = {data["ttc_norm"]:.3f}
D_n = {data["dlog_norm"]:.3f}
U = {data["urgency"]:.3f}

Fuzzifikasi:
mu CENTER(L) = {data["mu_l_center"]:.3f}
mu MEDIUM(P) = {data["mu_p_medium"]:.3f}
mu NEAR(P) = {data["mu_p_near"]:.3f}
mu MEDIUM(U) = {data["mu_u_medium"]:.3f}
mu HIGH(U) = {data["mu_u_high"]:.3f}

Rule aktif:
Rule 1: CENTER, MEDIUM, MEDIUM -> RISK MEDIUM, SPEED SLOW, TURN RIGHT
alpha_1 = {data["alpha_1"]:.3f}

Rule 2: CENTER, MEDIUM, HIGH -> RISK HIGH, SPEED SLOW, TURN RIGHT
alpha_2 = {data["alpha_2"]:.3f}

Rule 3: CENTER, NEAR, MEDIUM -> RISK HIGH, SPEED STOP, TURN RIGHT
alpha_3 = {data["alpha_3"]:.3f}

Rule 4: CENTER, NEAR, HIGH -> RISK HIGH, SPEED STOP, TURN RIGHT
alpha_4 = {data["alpha_4"]:.3f}

Agregasi:
RISK MEDIUM = {data["risk_medium_level"]:.3f}
RISK HIGH = {data["risk_high_level"]:.3f}
SPEED SLOW = {data["speed_slow_level"]:.3f}
SPEED STOP = {data["speed_stop_level"]:.3f}
TURN RIGHT = {data["turn_right_level"]:.3f}

Defuzzifikasi:
Risk Score = {data["risk_crisp"]:.3f}
Speed Factor = {data["speed_crisp"]:.3f}
Turn Bias = {data["turn_crisp"]:.3f}

Risk Class = HIGH
Command = STOP
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(isi)

    return path


def plot_grafik_manual_risk(data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    plt.figure(figsize=(11, 6))

    plt.plot(data["x_risk"], data["risk_low"], linewidth=2.0, label="LOW")
    plt.plot(data["x_risk"], data["risk_medium"], linewidth=2.0, label="MEDIUM")
    plt.plot(data["x_risk"], data["risk_high"], linewidth=2.0, label="HIGH")

    plt.fill_between(
        data["x_risk"],
        0,
        data["risk_medium_clip"],
        alpha=0.35,
        label=f"clipping MEDIUM = {data['risk_medium_level']:.2f}",
    )

    plt.fill_between(
        data["x_risk"],
        0,
        data["risk_high_clip"],
        alpha=0.35,
        label=f"clipping HIGH = {data['risk_high_level']:.2f}",
    )

    plt.plot(data["x_risk"], data["risk_agg"], linewidth=2.4, label="agregasi output")
    plt.axvline(
        data["risk_crisp"],
        linestyle="--",
        linewidth=2.0,
        label=f"centroid R = {data['risk_crisp']:.3f}",
    )

    plt.title("Grafik Mamdani Output Risk Score", fontsize=16, fontweight="bold")
    plt.xlabel("Risk Score")
    plt.ylabel("Derajat keanggotaan")
    plt.xlim(0.0, 1.0)
    plt.ylim(-0.05, 1.10)
    plt.grid(True, alpha=0.35)
    plt.legend(loc="upper left")

    path = os.path.join(OUTPUT_DIR, "G16_manual_mamdani_risk_score_transisi.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()

    return path


def plot_grafik_manual_tiga_output(data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fig, axes = plt.subplots(3, 1, figsize=(11, 13))

    axes[0].plot(data["x_risk"], data["risk_low"], linewidth=1.6, label="LOW")
    axes[0].plot(data["x_risk"], data["risk_medium"], linewidth=1.6, label="MEDIUM")
    axes[0].plot(data["x_risk"], data["risk_high"], linewidth=1.6, label="HIGH")
    axes[0].fill_between(data["x_risk"], 0, data["risk_medium_clip"], alpha=0.35)
    axes[0].fill_between(data["x_risk"], 0, data["risk_high_clip"], alpha=0.35)
    axes[0].plot(data["x_risk"], data["risk_agg"], linewidth=2.2, label="agregasi")
    axes[0].axvline(data["risk_crisp"], linestyle="--", linewidth=1.8)
    axes[0].set_title(f"Risk Score = {data['risk_crisp']:.3f}")
    axes[0].set_xlabel("Risk Score")
    axes[0].set_ylabel("Derajat keanggotaan")
    axes[0].grid(True, alpha=0.35)
    axes[0].legend(loc="upper left")

    axes[1].plot(data["x_speed"], data["speed_stop"], linewidth=1.6, label="STOP")
    axes[1].plot(data["x_speed"], data["speed_slow"], linewidth=1.6, label="SLOW")
    axes[1].plot(data["x_speed"], data["speed_normal"], linewidth=1.6, label="NORMAL")
    axes[1].fill_between(data["x_speed"], 0, data["speed_stop_clip"], alpha=0.35)
    axes[1].fill_between(data["x_speed"], 0, data["speed_slow_clip"], alpha=0.35)
    axes[1].plot(data["x_speed"], data["speed_agg"], linewidth=2.2, label="agregasi")
    axes[1].axvline(data["speed_crisp"], linestyle="--", linewidth=1.8)
    axes[1].set_title(f"Speed Factor = {data['speed_crisp']:.3f}")
    axes[1].set_xlabel("Speed Factor")
    axes[1].set_ylabel("Derajat keanggotaan")
    axes[1].grid(True, alpha=0.35)
    axes[1].legend(loc="upper right")

    axes[2].plot(data["x_turn"], data["turn_left"], linewidth=1.6, label="LEFT")
    axes[2].plot(data["x_turn"], data["turn_straight"], linewidth=1.6, label="STRAIGHT")
    axes[2].plot(data["x_turn"], data["turn_right"], linewidth=1.6, label="RIGHT")
    axes[2].fill_between(data["x_turn"], 0, data["turn_right_clip"], alpha=0.35)
    axes[2].plot(data["x_turn"], data["turn_agg"], linewidth=2.2, label="agregasi")
    axes[2].axvline(data["turn_crisp"], linestyle="--", linewidth=1.8)
    axes[2].set_title(f"Turn Bias = {data['turn_crisp']:.3f}")
    axes[2].set_xlabel("Turn Bias")
    axes[2].set_ylabel("Derajat keanggotaan")
    axes[2].grid(True, alpha=0.35)
    axes[2].legend(loc="upper left")

    fig.suptitle("Grafik Clipping, Agregasi, dan Defuzzifikasi Mamdani", fontsize=16, fontweight="bold")
    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, "G17_manual_mamdani_tiga_output_transisi.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()

    return path


def main():
    data = hitung_manual()

    txt_path = simpan_ringkasan(data)
    risk_graph = plot_grafik_manual_risk(data)
    output_graph = plot_grafik_manual_tiga_output(data)

    print("Grafik perhitungan manual Mamdani selesai dibuat.")
    print("")
    print("Hasil perhitungan:")
    print(f"L = {data['lateral']:.3f}")
    print(f"P = {data['proximity']:.3f}")
    print(f"U = {data['urgency']:.3f}")
    print(f"alpha_1 = {data['alpha_1']:.3f}")
    print(f"alpha_2 = {data['alpha_2']:.3f}")
    print(f"alpha_3 = {data['alpha_3']:.3f}")
    print(f"alpha_4 = {data['alpha_4']:.3f}")
    print(f"Risk Score = {data['risk_crisp']:.3f}")
    print(f"Speed Factor = {data['speed_crisp']:.3f}")
    print(f"Turn Bias = {data['turn_crisp']:.3f}")
    print("Risk Class = HIGH")
    print("Command = STOP")
    print("")
    print("File output:")
    print(f"- {txt_path}")
    print(f"- {risk_graph}")
    print(f"- {output_graph}")


if __name__ == "__main__":
    main()