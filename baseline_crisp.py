import os
from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd


OUTPUT_DIR = "results"
FIGURE_DIR = "results/figures_report"


def buat_folder():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(FIGURE_DIR, exist_ok=True)


def clamp(nilai, batas_bawah, batas_atas):
    return max(batas_bawah, min(batas_atas, nilai))


def hitung_proximity_visual(bot, area):
    area_norm = clamp(area / 0.45, 0.0, 1.0)
    proximity = (0.65 * bot) + (0.35 * area_norm)
    return clamp(proximity, 0.0, 1.0)


def hitung_urgency_visual(vttc, dlog, corridor):
    if pd.isna(vttc) or vttc <= 0:
        vttc_norm = 0.0
    elif vttc <= 1.5:
        vttc_norm = 1.0
    elif vttc >= 6.0:
        vttc_norm = 0.0
    else:
        vttc_norm = (6.0 - vttc) / 4.5

    dlog_norm = clamp(dlog / 0.18, 0.0, 1.0)
    urgency = (0.70 * vttc_norm) + (0.30 * dlog_norm)

    if corridor:
        urgency += 0.10

    return clamp(urgency, 0.0, 1.0)


def pilih_command_crisp(x, proximity, urgency, corridor):
    """
    Baseline crisp dibuat sebagai pembanding sederhana terhadap fuzzy controller.

    Prinsip:
    - LOW     : HOLD_COURSE
    - MEDIUM  : SLOW_DOWN atau TURN_SLOW
    - HIGH    : STOP
    """

    if proximity < 0.35 and urgency < 0.35:
        return 0.15, "LOW", "HOLD_COURSE"

    if corridor and proximity >= 0.82 and urgency >= 0.65:
        return 0.85, "HIGH", "STOP"

    if corridor and urgency >= 0.85:
        return 0.75, "HIGH", "STOP"

    if corridor and proximity >= 0.50:
        if x < 0.42:
            return 0.45, "MEDIUM", "SLOW_DOWN"

        if x > 0.58:
            return 0.45, "MEDIUM", "SLOW_DOWN"

        return 0.50, "MEDIUM", "TURN_RIGHT_SLOW"

    if corridor and urgency >= 0.45:
        return 0.45, "MEDIUM", "SLOW_DOWN"

    if proximity >= 0.75 and urgency >= 0.50:
        return 0.45, "MEDIUM", "SLOW_DOWN"

    return 0.15, "LOW", "HOLD_COURSE"


def proses_baseline(df):
    hasil = []

    for _, row in df.iterrows():
        x = float(row["x"])
        bot = float(row["bot"])
        area = float(row["area"])
        vttc = float(row["vttc_s"])
        dlog = float(row["dlog"])
        corridor = bool(row["corridor"])

        proximity = hitung_proximity_visual(bot, area)
        urgency = hitung_urgency_visual(vttc, dlog, corridor)

        crisp_risk, crisp_class, crisp_command = pilih_command_crisp(
            x=x,
            proximity=proximity,
            urgency=urgency,
            corridor=corridor,
        )

        hasil.append(
            {
                "scenario": row["scenario"],
                "time_s": row["time_s"],
                "x": x,
                "bot": bot,
                "area": area,
                "vttc_s": vttc,
                "corridor": corridor,
                "fuzzy_risk": row["risk"],
                "fuzzy_risk_class": row["risk_class"],
                "fuzzy_command": row["command"],
                "crisp_risk": crisp_risk,
                "crisp_risk_class": crisp_class,
                "crisp_command": crisp_command,
                "same_risk_class": row["risk_class"] == crisp_class,
                "same_command": row["command"] == crisp_command,
            }
        )

    return pd.DataFrame(hasil)


def ringkas_perbandingan(df):
    rows = []

    for scenario, group in df.groupby("scenario"):
        jumlah_data = len(group)

        fuzzy_command = Counter(group["fuzzy_command"])
        crisp_command = Counter(group["crisp_command"])

        class_match = group["same_risk_class"].mean() * 100.0
        command_match = group["same_command"].mean() * 100.0

        rows.append(
            {
                "scenario": scenario,
                "jumlah_data": jumlah_data,
                "risk_class_match_percent": round(class_match, 2),
                "command_match_percent": round(command_match, 2),
                "fuzzy_command_count": dict(fuzzy_command),
                "crisp_command_count": dict(crisp_command),
                "fuzzy_risk_max": round(float(group["fuzzy_risk"].max()), 4),
                "crisp_risk_max": round(float(group["crisp_risk"].max()), 4),
            }
        )

    return pd.DataFrame(rows)


def command_level(command):
    mapping = {
        "HOLD_COURSE": 0,
        "SLOW_DOWN": 1,
        "TURN_LEFT_SLOW": 2,
        "TURN_RIGHT_SLOW": 3,
        "STOP": 4,
    }

    return mapping.get(command, -1)


def plot_perbandingan_command(df, scenario):
    data = df[df["scenario"] == scenario].copy()

    if data.empty:
        return

    t = data["time_s"]

    fuzzy_level = data["fuzzy_command"].apply(command_level)
    crisp_level = data["crisp_command"].apply(command_level)

    plt.figure(figsize=(9, 4.8))
    plt.step(t, fuzzy_level, where="post", linewidth=2.0, label="Fuzzy")
    plt.step(t, crisp_level, where="post", linewidth=1.8, linestyle="--", label="Crisp baseline")

    plt.yticks(
        [0, 1, 2, 3, 4],
        ["HOLD", "SLOW", "LEFT", "RIGHT", "STOP"],
    )

    plt.title(f"Perbandingan Command Fuzzy dan Crisp - {scenario}")
    plt.xlabel("Waktu (s)")
    plt.ylabel("Command")
    plt.ylim(-0.3, 4.3)
    plt.grid(True, alpha=0.35)
    plt.legend()
    plt.tight_layout()

    path = os.path.join(FIGURE_DIR, f"G70_baseline_command_{scenario}.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_perbandingan_risk(df, scenario):
    data = df[df["scenario"] == scenario].copy()

    if data.empty:
        return

    t = data["time_s"]

    plt.figure(figsize=(9, 4.8))
    plt.plot(t, data["fuzzy_risk"], linewidth=2.2, label="Fuzzy risk")
    plt.plot(t, data["crisp_risk"], linewidth=1.8, linestyle="--", label="Crisp baseline risk")
    plt.axhline(0.30, linestyle=":", linewidth=1.2, label="Batas LOW-MEDIUM")
    plt.axhline(0.60, linestyle=":", linewidth=1.2, label="Batas MEDIUM-HIGH")

    plt.title(f"Perbandingan Risk Fuzzy dan Crisp - {scenario}")
    plt.xlabel("Waktu (s)")
    plt.ylabel("Risk score")
    plt.ylim(0.0, 1.0)
    plt.grid(True, alpha=0.35)
    plt.legend()
    plt.tight_layout()

    path = os.path.join(FIGURE_DIR, f"G71_baseline_risk_{scenario}.png")
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def main():
    buat_folder()

    path = "results/simulation_log.csv"

    if not os.path.exists(path):
        raise FileNotFoundError(
            "File results/simulation_log.csv belum ada. "
            "Jalankan dulu: python scenario_generator.py"
        )

    df = pd.read_csv(path)

    df_baseline = proses_baseline(df)
    df_summary = ringkas_perbandingan(df_baseline)

    df_baseline.to_csv("results/baseline_crisp_log.csv", index=False)
    df_summary.to_csv("results/baseline_crisp_summary.csv", index=False)

    for scenario in df_baseline["scenario"].unique():
        plot_perbandingan_command(df_baseline, scenario)
        plot_perbandingan_risk(df_baseline, scenario)

    print("\nBaseline crisp selesai dibuat.")
    print("File output:")
    print("- results/baseline_crisp_log.csv")
    print("- results/baseline_crisp_summary.csv")
    print("- results/figures_report/G70_baseline_command_*.png")
    print("- results/figures_report/G71_baseline_risk_*.png")

    print("\nRingkasan perbandingan:")
    print(df_summary.to_string(index=False))


if __name__ == "__main__":
    main()