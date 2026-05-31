import os
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def clamp(x, batas_bawah, batas_atas):
    return max(batas_bawah, min(batas_atas, x))


def buat_folder_output():
    os.makedirs("results", exist_ok=True)
    os.makedirs("results/figures", exist_ok=True)


def buat_posisi_obstacle(nama_skenario, t):
    t = np.asarray(t, dtype=float)
    durasi = max(t[-1] - t[0], 1e-6)
    s = t / durasi

    if nama_skenario == "frontal_static_obstacle":
        obs_x = np.zeros_like(t)
        obs_y = np.full_like(t, 9.0)
        ada_obstacle = np.ones_like(t, dtype=bool)

    elif nama_skenario == "crossing_left_to_right":
        obs_x = -5.0 + 10.0 * s
        obs_y = np.full_like(t, 8.0)
        ada_obstacle = np.ones_like(t, dtype=bool)

    elif nama_skenario == "crossing_right_to_left":
        obs_x = 5.0 - 10.0 * s
        obs_y = np.full_like(t, 8.0)
        ada_obstacle = np.ones_like(t, dtype=bool)

    elif nama_skenario == "side_safe_obstacle":
        obs_x = np.full_like(t, -5.0)
        obs_y = 4.0 + 5.0 * s
        ada_obstacle = np.ones_like(t, dtype=bool)

    else:
        obs_x = np.full_like(t, np.nan)
        obs_y = np.full_like(t, np.nan)
        ada_obstacle = np.zeros_like(t, dtype=bool)

    return obs_x, obs_y, ada_obstacle


def simulasi_lintasan_skenario(df_skenario):
    nama_skenario = df_skenario["scenario"].iloc[0]

    t = df_skenario["time_s"].to_numpy(dtype=float)
    dt = float(np.median(np.diff(t))) if len(t) > 1 else 0.2

    obs_x, obs_y, ada_obstacle = buat_posisi_obstacle(nama_skenario, t)

    x = 0.0
    y = 0.0
    heading = 0.0

    base_speed = 1.10
    max_yaw_rate = math.radians(28.0)

    kp_heading = 0.90
    kp_cross_track = 0.10

    hasil = []

    for i, row in df_skenario.iterrows():
        speed_factor = float(row["speed"])
        turn_bias = float(row["turn"])
        command = row["command"]
        risk_class = row["risk_class"]

        speed = base_speed * speed_factor

        if command == "STOP":
            speed = 0.0

        if command in ["TURN_RIGHT_SLOW", "TURN_LEFT_SLOW"]:
            yaw_rate = max_yaw_rate * turn_bias

        else:
            yaw_rate = (-kp_heading * heading) + (-kp_cross_track * x)
            yaw_rate += 0.25 * max_yaw_rate * turn_bias

        yaw_rate = clamp(yaw_rate, -max_yaw_rate, max_yaw_rate)

        heading = heading + yaw_rate * dt
        heading = clamp(heading, math.radians(-55.0), math.radians(55.0))

        x = x + speed * math.sin(heading) * dt
        y = y + speed * math.cos(heading) * dt

        if ada_obstacle[len(hasil)]:
            jarak_obstacle = math.sqrt((x - obs_x[len(hasil)]) ** 2 + (y - obs_y[len(hasil)]) ** 2)
        else:
            jarak_obstacle = np.nan

        hasil.append(
            {
                "scenario": nama_skenario,
                "time_s": round(float(row["time_s"]), 3),
                "usv_x_m": round(float(x), 4),
                "usv_y_m": round(float(y), 4),
                "heading_deg": round(math.degrees(heading), 4),
                "speed_mps": round(float(speed), 4),
                "yaw_rate_dps": round(math.degrees(yaw_rate), 4),
                "obstacle_x_m": round(float(obs_x[len(hasil)]), 4) if ada_obstacle[len(hasil)] else np.nan,
                "obstacle_y_m": round(float(obs_y[len(hasil)]), 4) if ada_obstacle[len(hasil)] else np.nan,
                "distance_to_obstacle_m": round(float(jarak_obstacle), 4) if ada_obstacle[len(hasil)] else np.nan,
                "risk": round(float(row["risk"]), 4),
                "risk_class": risk_class,
                "command": command,
            }
        )

    return pd.DataFrame(hasil)


def hitung_ringkasan_lintasan(df):
    ringkasan = []

    for nama, grup in df.groupby("scenario"):
        jarak_valid = grup["distance_to_obstacle_m"].dropna()

        if len(jarak_valid) > 0:
            min_distance = round(float(jarak_valid.min()), 4)
        else:
            min_distance = np.nan

        command_series = grup["command"].tolist()
        jumlah_switch = 0

        for i in range(1, len(command_series)):
            if command_series[i] != command_series[i - 1]:
                jumlah_switch += 1

        ringkasan.append(
            {
                "scenario": nama,
                "final_x_m": round(float(grup["usv_x_m"].iloc[-1]), 4),
                "final_y_m": round(float(grup["usv_y_m"].iloc[-1]), 4),
                "max_abs_cross_track_m": round(float(grup["usv_x_m"].abs().max()), 4),
                "mean_speed_mps": round(float(grup["speed_mps"].mean()), 4),
                "min_speed_mps": round(float(grup["speed_mps"].min()), 4),
                "min_distance_to_obstacle_m": min_distance,
                "command_switch_count": jumlah_switch,
            }
        )

    return pd.DataFrame(ringkasan)


def plot_lintasan(df_skenario):
    nama = df_skenario["scenario"].iloc[0]

    plt.figure(figsize=(7.5, 6.0))

    plt.plot(
        df_skenario["usv_x_m"],
        df_skenario["usv_y_m"],
        linewidth=2.0,
        label="USV trajectory",
    )

    if df_skenario["obstacle_x_m"].notna().any():
        plt.plot(
            df_skenario["obstacle_x_m"],
            df_skenario["obstacle_y_m"],
            linestyle="--",
            linewidth=1.8,
            label="obstacle path",
        )

        awal = df_skenario.iloc[0]
        akhir = df_skenario.iloc[-1]

        plt.scatter(
            [awal["obstacle_x_m"]],
            [awal["obstacle_y_m"]],
            marker="x",
            s=70,
            label="obstacle start",
        )

        plt.scatter(
            [akhir["obstacle_x_m"]],
            [akhir["obstacle_y_m"]],
            marker="o",
            s=50,
            label="obstacle end",
        )

    plt.scatter(
        [df_skenario["usv_x_m"].iloc[0]],
        [df_skenario["usv_y_m"].iloc[0]],
        marker="o",
        s=50,
        label="USV start",
    )

    plt.scatter(
        [df_skenario["usv_x_m"].iloc[-1]],
        [df_skenario["usv_y_m"].iloc[-1]],
        marker="s",
        s=50,
        label="USV end",
    )

    plt.axvline(0.0, linestyle=":", linewidth=1.0, label="mission line")
    plt.title(f"Simulasi Lintasan USV - {nama}")
    plt.xlabel("posisi lateral x (m)")
    plt.ylabel("posisi maju y (m)")
    plt.grid(True)
    plt.axis("equal")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"results/figures/trajectory_{nama}.png", dpi=200)
    plt.close()


def plot_heading_speed(df_skenario):
    nama = df_skenario["scenario"].iloc[0]

    plt.figure(figsize=(9, 4.8))
    plt.plot(df_skenario["time_s"], df_skenario["heading_deg"], label="heading")
    plt.plot(df_skenario["time_s"], df_skenario["speed_mps"], label="speed")
    plt.title(f"Heading dan Speed - {nama}")
    plt.xlabel("waktu (s)")
    plt.ylabel("nilai")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"results/figures/usv_heading_speed_{nama}.png", dpi=200)
    plt.close()


def plot_distance(df_skenario):
    nama = df_skenario["scenario"].iloc[0]

    if not df_skenario["distance_to_obstacle_m"].notna().any():
        return

    plt.figure(figsize=(9, 4.8))
    plt.plot(
        df_skenario["time_s"],
        df_skenario["distance_to_obstacle_m"],
        label="distance to obstacle",
    )
    plt.title(f"Jarak Simulatif USV-Obstacle - {nama}")
    plt.xlabel("waktu (s)")
    plt.ylabel("jarak simulatif (m)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"results/figures/distance_{nama}.png", dpi=200)
    plt.close()


def main():
    buat_folder_output()

    path_log = "results/simulation_log.csv"

    if not os.path.exists(path_log):
        raise FileNotFoundError(
            "File results/simulation_log.csv belum ada. Jalankan dulu: python scenario_generator.py"
        )

    df = pd.read_csv(path_log)

    semua_hasil = []

    for nama_skenario, grup in df.groupby("scenario"):
        grup = grup.sort_values("time_s").reset_index(drop=True)
        hasil = simulasi_lintasan_skenario(grup)

        semua_hasil.append(hasil)

        hasil.to_csv(f"results/usv_trajectory_{nama_skenario}.csv", index=False)

        plot_lintasan(hasil)
        plot_heading_speed(hasil)
        plot_distance(hasil)

    df_all = pd.concat(semua_hasil, ignore_index=True)
    df_all.to_csv("results/usv_trajectory_log.csv", index=False)

    df_summary = hitung_ringkasan_lintasan(df_all)
    df_summary.to_csv("results/usv_trajectory_summary.csv", index=False)

    print("\nSimulasi lintasan selesai.")
    print("File utama:")
    print("- results/usv_trajectory_log.csv")
    print("- results/usv_trajectory_summary.csv")
    print("- results/figures/trajectory_*.png")
    print("- results/figures/usv_heading_speed_*.png")
    print("- results/figures/distance_*.png")

    print("\nRingkasan lintasan:")
    print(df_summary.to_string(index=False))


if __name__ == "__main__":
    main()