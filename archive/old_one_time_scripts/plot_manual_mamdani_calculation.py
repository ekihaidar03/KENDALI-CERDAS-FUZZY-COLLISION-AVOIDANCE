import os
import numpy as np
import matplotlib.pyplot as plt


OUTPUT_DIR = "results/figures_report"
TEXT_DIR = "results/report_tables"


def trimf(x, a, b, c):
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x, dtype=float)

    if b != a:
        idx = (a < x) & (x <= b)
        y[idx] = (x[idx] - a) / (b - a)

    if c != b:
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
    area = np.sum(mu)
    if area <= 1e-12:
        return float(np.mean(x))
    return float(np.sum(x * mu) / area)


def eval_trimf(value, a, b, c):
    return float(trimf(np.array([value]), a, b, c)[0])


def eval_trapmf(value, a, b, c, d):
    return float(trapmf(np.array([value]), a, b, c, d)[0])


def hitung_contoh_manual():
    x_c = 0.50
    bbox_bottom = 0.70
    area = 0.15
    visual_ttc = 3.0
    dlog_area = 0.08
    corridor_bonus = 0.10

    lateral = 2.0 * (x_c - 0.50)

    area_norm = area / 0.45
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

    mu_l_left = eval_trapmf(lateral, -1.00, -1.00, -0.60, -0.15)
    mu_l_center = eval_trimf(lateral, -0.35, 0.00, 0.35)
    mu_l_right = eval_trapmf(lateral, 0.15, 0.60, 1.00, 1.00)

    mu_p_far = eval_trapmf(proximity, 0.00, 0.00, 0.25, 0.45)
    mu_p_medium = eval_trimf(proximity, 0.30, 0.55, 0.80)
    mu_p_near = eval_trapmf(proximity, 0.65, 0.82, 1.00, 1.00)

    mu_u_low = eval_trapmf(urgency, 0.00, 0.00, 0.25, 0.45)
    mu_u_medium = eval_trimf(urgency, 0.30, 0.55, 0.80)
    mu_u_high = eval_trapmf(urgency, 0.75, 0.90, 1.00, 1.00)

    alpha = min(mu_l_center, mu_p_medium, mu_u_medium)

    x_risk = np.linspace(0.0, 1.0, 2000)
    risk_medium = trimf(x_risk, 0.25, 0.45, 0.65)
    risk_clipped = np.minimum(alpha, risk_medium)
    risk_crisp = centroid(x_risk, risk_clipped)

    x_speed = np.linspace(0.0, 1.0, 2000)
    speed_slow = trimf(x_speed, 0.12, 0.35, 0.58)
    speed_clipped = np.minimum(alpha, speed_slow)
    speed_crisp = centroid(x_speed, speed_clipped)

    x_turn = np.linspace(-1.0, 1.0, 2000)
    turn_right = trapmf(x_turn, 0.22, 0.75, 1.00, 1.00)
    turn_clipped = np.minimum(alpha, turn_right)
    turn_crisp = centroid(x_turn, turn_clipped)

    return {
        "x_c": x_c,
        "bbox_bottom": bbox_bottom,
        "area": area,
        "visual_ttc": visual_ttc,
        "dlog_area": dlog_area,
        "corridor_bonus": corridor_bonus,
        "lateral": lateral,
        "area_norm": area_norm,
        "proximity": proximity,
        "ttc_norm": ttc_norm,
        "dlog_norm": dlog_norm,
        "urgency": urgency,
        "mu_l_left": mu_l_left,
        "mu_l_center": mu_l_center,
        "mu_l_right": mu_l_right,
        "mu_p_far": mu_p_far,
        "mu_p_medium": mu_p_medium,
        "mu_p_near": mu_p_near,
        "mu_u_low": mu_u_low,
        "mu_u_medium": mu_u_medium,
        "mu_u_high": mu_u_high,
        "alpha": alpha,
        "risk_crisp": risk_crisp,
        "speed_crisp": speed_crisp,
        "turn_crisp": turn_crisp,
        "x_risk": x_risk,
        "risk_medium": risk_medium,
        "risk_clipped": risk_clipped,
        "x_speed": x_speed,
        "speed_slow": speed_slow,
        "speed_clipped": speed_clipped,
        "x_turn": x_turn,
        "turn_right": turn_right,
        "turn_clipped": turn_clipped,
    }


def simpan_ringkasan_txt(data):
    os.makedirs(TEXT_DIR, exist_ok=True)
    path = os.path.join(TEXT_DIR, "perhitungan_manual_mamdani_obstacle_depan_sedang.txt")

    lines = [
        "PERHITUNGAN MANUAL MAMDANI FUZZY LOGIC CONTROLLER",
        "Kasus: obstacle depan sedang",
        "",
        "Data input visual:",
        f"x_c = {data['x_c']:.2f}",
        f"B = {data['bbox_bottom']:.2f}",
        f"A = {data['area']:.2f}",
        f"T_vTTC = {data['visual_ttc']:.2f} s",
        f"dlog(A) = {data['dlog_area']:.2f}",
        f"C = {data['corridor_bonus']:.2f}",
        "",
        "Hasil normalisasi:",
        f"L = {data['lateral']:.3f}",
        f"A_n = {data['area_norm']:.3f}",
        f"P = {data['proximity']:.3f}",
        f"T_n = {data['ttc_norm']:.3f}",
        f"D_n = {data['dlog_norm']:.3f}",
        f"U = {data['urgency']:.3f}",
        "",
        "Fuzzifikasi:",
        f"mu LEFT(L) = {data['mu_l_left']:.3f}",
        f"mu CENTER(L) = {data['mu_l_center']:.3f}",
        f"mu RIGHT(L) = {data['mu_l_right']:.3f}",
        f"mu FAR(P) = {data['mu_p_far']:.3f}",
        f"mu MEDIUM(P) = {data['mu_p_medium']:.3f}",
        f"mu NEAR(P) = {data['mu_p_near']:.3f}",
        f"mu LOW(U) = {data['mu_u_low']:.3f}",
        f"mu MEDIUM(U) = {data['mu_u_medium']:.3f}",
        f"mu HIGH(U) = {data['mu_u_high']:.3f}",
        "",
        "Rule aktif:",
        "IF LATERAL is CENTER AND PROXIMITY is MEDIUM AND URGENCY is MEDIUM",
        "THEN RISK is MEDIUM, SPEED is SLOW, TURN is RIGHT",
        "",
        f"alpha = min(1.000, {data['mu_p_medium']:.3f}, {data['mu_u_medium']:.3f}) = {data['alpha']:.3f}",
        "",
        "Hasil defuzzifikasi:",
        f"Risk Score = {data['risk_crisp']:.3f}",
        f"Speed Factor = {data['speed_crisp']:.3f}",
        f"Turn Bias = {data['turn_crisp']:.3f}",
        "Risk Class = MEDIUM",
        "Command = TURN_RIGHT_SLOW",
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return path


def plot_fuzzifikasi(data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))

    x_l = np.linspace(-1.0, 1.0, 1000)
    axes[0].plot(x_l, trapmf(x_l, -1.00, -1.00, -0.60, -0.15), label="LEFT")
    axes[0].plot(x_l, trimf(x_l, -0.35, 0.00, 0.35), label="CENTER")
    axes[0].plot(x_l, trapmf(x_l, 0.15, 0.60, 1.00, 1.00), label="RIGHT")
    axes[0].axvline(data["lateral"], linestyle="--", linewidth=1.4)
    axes[0].set_title("Fuzzifikasi Lateral Position")
    axes[0].set_xlabel("Lateral Position")
    axes[0].set_ylabel("Derajat keanggotaan")
    axes[0].grid(True, alpha=0.4)
    axes[0].legend()

    x_p = np.linspace(0.0, 1.0, 1000)
    axes[1].plot(x_p, trapmf(x_p, 0.00, 0.00, 0.25, 0.45), label="FAR")
    axes[1].plot(x_p, trimf(x_p, 0.30, 0.55, 0.80), label="MEDIUM")
    axes[1].plot(x_p, trapmf(x_p, 0.65, 0.82, 1.00, 1.00), label="NEAR")
    axes[1].axvline(data["proximity"], linestyle="--", linewidth=1.4)
    axes[1].set_title("Fuzzifikasi Visual Proximity")
    axes[1].set_xlabel("Visual Proximity")
    axes[1].grid(True, alpha=0.4)
    axes[1].legend()

    x_u = np.linspace(0.0, 1.0, 1000)
    axes[2].plot(x_u, trapmf(x_u, 0.00, 0.00, 0.25, 0.45), label="LOW")
    axes[2].plot(x_u, trimf(x_u, 0.30, 0.55, 0.80), label="MEDIUM")
    axes[2].plot(x_u, trapmf(x_u, 0.75, 0.90, 1.00, 1.00), label="HIGH")
    axes[2].axvline(data["urgency"], linestyle="--", linewidth=1.4)
    axes[2].set_title("Fuzzifikasi Approach Urgency")
    axes[2].set_xlabel("Approach Urgency")
    axes[2].grid(True, alpha=0.4)
    axes[2].legend()

    fig.suptitle("Fuzzifikasi Input Crisp Obstacle Depan Sedang", fontsize=15, fontweight="bold")
    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, "G13_fuzzifikasi_manual_obstacle_depan_sedang.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()

    return path


def plot_output_risk_seperti_manual(data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    x = np.linspace(0.0, 1.0, 1000)

    risk_low = trapmf(x, 0.00, 0.00, 0.18, 0.35)
    risk_medium = trimf(x, 0.25, 0.45, 0.65)
    risk_high = trapmf(x, 0.62, 0.78, 1.00, 1.00)

    clipped_medium = np.minimum(data["alpha"], risk_medium)

    plt.figure(figsize=(10, 5.8))

    plt.plot(x, risk_low, linewidth=2.0, label="LOW")
    plt.plot(x, risk_medium, linewidth=2.0, label="MEDIUM")
    plt.plot(x, risk_high, linewidth=2.0, label="HIGH")

    plt.fill_between(x, 0, clipped_medium, alpha=0.35, label="Clipped output MEDIUM")
    plt.axhline(data["alpha"], linestyle="--", linewidth=1.4, label=f"firing strength = {data['alpha']:.2f}")
    plt.axvline(data["risk_crisp"], linestyle="-", linewidth=1.6, label=f"centroid R = {data['risk_crisp']:.3f}")

    plt.title("Output Mamdani Risk Score - Obstacle Depan Sedang", fontsize=15, fontweight="bold")
    plt.xlabel("Risk Score")
    plt.ylabel("Derajat keanggotaan")
    plt.ylim(-0.05, 1.10)
    plt.xlim(0.0, 1.0)
    plt.grid(True, alpha=0.4)
    plt.legend(loc="upper right")

    path = os.path.join(OUTPUT_DIR, "G14_output_mamdani_risk_manual_obstacle_depan_sedang.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()

    return path


def plot_output_tiga_variabel(data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    fig, axes = plt.subplots(3, 1, figsize=(10, 12))

    axes[0].plot(data["x_risk"], data["risk_medium"], linewidth=2.0, label="RISK MEDIUM")
    axes[0].fill_between(data["x_risk"], 0, data["risk_clipped"], alpha=0.35)
    axes[0].axhline(data["alpha"], linestyle="--", linewidth=1.2)
    axes[0].axvline(data["risk_crisp"], linewidth=1.5)
    axes[0].set_title(f"Risk Score = {data['risk_crisp']:.3f}")
    axes[0].set_xlabel("Risk Score")
    axes[0].set_ylabel("Derajat keanggotaan")
    axes[0].grid(True, alpha=0.4)
    axes[0].legend()

    axes[1].plot(data["x_speed"], data["speed_slow"], linewidth=2.0, label="SPEED SLOW")
    axes[1].fill_between(data["x_speed"], 0, data["speed_clipped"], alpha=0.35)
    axes[1].axhline(data["alpha"], linestyle="--", linewidth=1.2)
    axes[1].axvline(data["speed_crisp"], linewidth=1.5)
    axes[1].set_title(f"Speed Factor = {data['speed_crisp']:.3f}")
    axes[1].set_xlabel("Speed Factor")
    axes[1].set_ylabel("Derajat keanggotaan")
    axes[1].grid(True, alpha=0.4)
    axes[1].legend()

    axes[2].plot(data["x_turn"], data["turn_right"], linewidth=2.0, label="TURN RIGHT")
    axes[2].fill_between(data["x_turn"], 0, data["turn_clipped"], alpha=0.35)
    axes[2].axhline(data["alpha"], linestyle="--", linewidth=1.2)
    axes[2].axvline(data["turn_crisp"], linewidth=1.5)
    axes[2].set_title(f"Turn Bias = {data['turn_crisp']:.3f}")
    axes[2].set_xlabel("Turn Bias")
    axes[2].set_ylabel("Derajat keanggotaan")
    axes[2].grid(True, alpha=0.4)
    axes[2].legend()

    fig.suptitle("Clipping Output Mamdani dan Defuzzifikasi Centroid", fontsize=15, fontweight="bold")
    plt.tight_layout()

    path = os.path.join(OUTPUT_DIR, "G15_output_mamdani_tiga_variabel_obstacle_depan_sedang.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()

    return path


def main():
    data = hitung_contoh_manual()

    txt_path = simpan_ringkasan_txt(data)
    fig_fuzzifikasi = plot_fuzzifikasi(data)
    fig_risk = plot_output_risk_seperti_manual(data)
    fig_tiga_output = plot_output_tiga_variabel(data)

    print("Perhitungan manual Mamdani selesai.")
    print("")
    print("Ringkasan hasil:")
    print(f"L = {data['lateral']:.3f}")
    print(f"P = {data['proximity']:.3f}")
    print(f"U = {data['urgency']:.3f}")
    print(f"alpha = {data['alpha']:.3f}")
    print(f"Risk Score = {data['risk_crisp']:.3f}")
    print(f"Speed Factor = {data['speed_crisp']:.3f}")
    print(f"Turn Bias = {data['turn_crisp']:.3f}")
    print("Risk Class = MEDIUM")
    print("Command = TURN_RIGHT_SLOW")
    print("")
    print("File output:")
    print(f"- {txt_path}")
    print(f"- {fig_fuzzifikasi}")
    print(f"- {fig_risk}")
    print(f"- {fig_tiga_output}")


if __name__ == "__main__":
    main()