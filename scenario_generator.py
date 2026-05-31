import os
import numpy as np
import pandas as pd

from fuzzy_controller import (
    FuzzyCollisionAvoidance,
    ubah_fitur_visual_ke_input_fuzzy,
)


def buat_folder_results():
    os.makedirs("results", exist_ok=True)


def hitung_dlog(area, dt):
    area = np.asarray(area, dtype=float)
    area_aman = np.maximum(area, 1e-4)

    log_area = np.log(area_aman)
    dlog = np.gradient(log_area, dt)

    dlog = np.clip(dlog, -0.20, 0.20)
    return dlog


def skenario_obstacle_depan(t):
    durasi = t[-1] - t[0]
    s = t / durasi

    x = 0.50 + 0.02 * np.sin(2.0 * np.pi * s)
    bot = 0.25 + 0.70 * s
    area = 0.03 + 0.35 * (s ** 1.35)

    vttc = 8.0 - 7.0 * s
    vttc = np.maximum(vttc, 1.0)

    corridor = bot > 0.40

    return x, bot, area, vttc, corridor


def skenario_crossing_kiri_ke_kanan(t):
    durasi = t[-1] - t[0]
    s = t / durasi

    x = 0.12 + 0.76 * s
    bot = 0.42 + 0.22 * np.sin(np.pi * s)
    area = 0.07 + 0.13 * np.sin(np.pi * s)

    vttc = 7.0 - 3.8 * np.sin(np.pi * s)
    vttc = np.maximum(vttc, 2.6)

    corridor = (x > 0.38) & (x < 0.62) & (bot > 0.48)

    return x, bot, area, vttc, corridor


def skenario_crossing_kanan_ke_kiri(t):
    durasi = t[-1] - t[0]
    s = t / durasi

    x = 0.88 - 0.76 * s
    bot = 0.42 + 0.22 * np.sin(np.pi * s)
    area = 0.07 + 0.13 * np.sin(np.pi * s)

    vttc = 7.0 - 3.8 * np.sin(np.pi * s)
    vttc = np.maximum(vttc, 2.6)

    corridor = (x > 0.38) & (x < 0.62) & (bot > 0.48)

    return x, bot, area, vttc, corridor


def skenario_samping_aman(t):
    s = t / t[-1]

    x = 0.14 + 0.03 * np.sin(2.0 * np.pi * s)
    bot = 0.50 + 0.04 * np.sin(2.0 * np.pi * s)
    area = 0.08 + 0.02 * np.sin(2.0 * np.pi * s)

    vttc = np.full_like(t, 9.0)
    corridor = np.full_like(t, False, dtype=bool)

    return x, bot, area, vttc, corridor


def skenario_tanpa_obstacle(t):
    x = np.full_like(t, 0.50)
    bot = np.full_like(t, 0.05)
    area = np.full_like(t, 0.00)

    vttc = np.full_like(t, 99.0)
    corridor = np.full_like(t, False, dtype=bool)

    return x, bot, area, vttc, corridor


def proses_skenario(nama_skenario, t, x, bot, area, vttc, corridor):
    fuzzy = FuzzyCollisionAvoidance()

    dt = t[1] - t[0]
    dlog = hitung_dlog(area, dt)

    data = []

    for i in range(len(t)):
        lateral, proximity, urgency = ubah_fitur_visual_ke_input_fuzzy(
            x=float(x[i]),
            bot=float(bot[i]),
            area=float(area[i]),
            vttc=float(vttc[i]),
            dlog=float(dlog[i]),
            corridor=bool(corridor[i]),
        )

        hasil = fuzzy.hitung(lateral, proximity, urgency)

        data.append(
            {
                "scenario": nama_skenario,
                "time_s": round(float(t[i]), 3),
                "x": round(float(x[i]), 4),
                "bot": round(float(bot[i]), 4),
                "area": round(float(area[i]), 4),
                "vttc_s": round(float(vttc[i]), 4),
                "dlog": round(float(dlog[i]), 4),
                "corridor": bool(corridor[i]),
                "lateral": round(float(lateral), 4),
                "proximity": round(float(proximity), 4),
                "urgency": round(float(urgency), 4),
                "speed": round(float(hasil["speed"]), 4),
                "turn": round(float(hasil["turn"]), 4),
                "risk": round(float(hasil["risk"]), 4),
                "risk_class": hasil["risk_class"],
                "command": hasil["command"],
            }
        )

    return pd.DataFrame(data)


def ringkas_skenario(df):
    ringkasan = []

    for nama, grup in df.groupby("scenario"):
        command_count = grup["command"].value_counts().to_dict()
        risk_count = grup["risk_class"].value_counts().to_dict()

        ringkasan.append(
            {
                "scenario": nama,
                "jumlah_data": len(grup),
                "risk_min": round(float(grup["risk"].min()), 4),
                "risk_max": round(float(grup["risk"].max()), 4),
                "risk_mean": round(float(grup["risk"].mean()), 4),
                "speed_mean": round(float(grup["speed"].mean()), 4),
                "command_count": str(command_count),
                "risk_class_count": str(risk_count),
            }
        )

    return pd.DataFrame(ringkasan)


def main():
    buat_folder_results()

    dt = 0.2
    t = np.arange(0.0, 20.0 + dt, dt)

    daftar_skenario = [
        ("frontal_static_obstacle", skenario_obstacle_depan),
        ("crossing_left_to_right", skenario_crossing_kiri_ke_kanan),
        ("crossing_right_to_left", skenario_crossing_kanan_ke_kiri),
        ("side_safe_obstacle", skenario_samping_aman),
        ("no_obstacle", skenario_tanpa_obstacle),
    ]

    semua_data = []

    for nama, fungsi_skenario in daftar_skenario:
        x, bot, area, vttc, corridor = fungsi_skenario(t)
        df = proses_skenario(nama, t, x, bot, area, vttc, corridor)

        semua_data.append(df)

        path_skenario = os.path.join("results", f"{nama}.csv")
        df.to_csv(path_skenario, index=False)

    df_all = pd.concat(semua_data, ignore_index=True)
    df_all.to_csv(os.path.join("results", "simulation_log.csv"), index=False)

    df_summary = ringkas_skenario(df_all)
    df_summary.to_csv(os.path.join("results", "simulation_summary.csv"), index=False)

    print("\nSimulasi selesai.")
    print("File hasil:")
    print("- results/simulation_log.csv")
    print("- results/simulation_summary.csv")
    print("- results/frontal_static_obstacle.csv")
    print("- results/crossing_left_to_right.csv")
    print("- results/crossing_right_to_left.csv")
    print("- results/side_safe_obstacle.csv")
    print("- results/no_obstacle.csv")

    print("\nRingkasan:")
    print(df_summary.to_string(index=False))


if __name__ == "__main__":
    main()