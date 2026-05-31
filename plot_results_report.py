import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from fuzzy_controller import FuzzyCollisionAvoidance


FIG_DIR = "results/figures_report"


def buat_folder():
    os.makedirs(FIG_DIR, exist_ok=True)


def simpan_gambar(nama_file):
    path = os.path.join(FIG_DIR, nama_file)
    plt.tight_layout()
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()


def command_to_level(command):
    mapping = {
        "HOLD_COURSE": 0,
        "SLOW_DOWN": 1,
        "TURN_LEFT_SLOW": 2,
        "TURN_RIGHT_SLOW": 3,
        "STOP": 4,
    }
    return mapping.get(command, -1)


def style_umum():
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "legend.fontsize": 9,
            "xtick.labelsize": 10,
            "ytick.labelsize": 10,
            "figure.titlesize": 13,
        }
    )


def plot_membership_input():
    fuzzy = FuzzyCollisionAvoidance()

    x_lateral = np.linspace(-1.0, 1.0, 501)
    kiri = [fuzzy.fuzz_lateral(v)["kiri"] for v in x_lateral]
    tengah = [fuzzy.fuzz_lateral(v)["tengah"] for v in x_lateral]
    kanan = [fuzzy.fuzz_lateral(v)["kanan"] for v in x_lateral]

    plt.figure(figsize=(8.0, 4.6))
    plt.plot(x_lateral, kiri, linewidth=2.0, label="Kiri")
    plt.plot(x_lateral, tengah, linewidth=2.0, label="Tengah / Corridor")
    plt.plot(x_lateral, kanan, linewidth=2.0, label="Kanan")
    plt.title("Fungsi Keanggotaan Input Posisi Lateral Obstacle")
    plt.xlabel("Posisi lateral ternormalisasi")
    plt.ylabel("Derajat keanggotaan")
    plt.ylim(-0.05, 1.05)
    plt.grid(True, alpha=0.35)
    plt.legend(loc="upper center", ncol=3)
    simpan_gambar("G01_membership_lateral_position.png")

    x = np.linspace(0.0, 1.0, 501)
    jauh = [fuzzy.fuzz_proximity(v)["jauh"] for v in x]
    sedang = [fuzzy.fuzz_proximity(v)["sedang"] for v in x]
    dekat = [fuzzy.fuzz_proximity(v)["dekat"] for v in x]

    plt.figure(figsize=(8.0, 4.6))
    plt.plot(x, jauh, linewidth=2.0, label="Jauh")
    plt.plot(x, sedang, linewidth=2.0, label="Sedang")
    plt.plot(x, dekat, linewidth=2.0, label="Dekat")
    plt.title("Fungsi Keanggotaan Input Kedekatan Visual")
    plt.xlabel("Kedekatan visual ternormalisasi")
    plt.ylabel("Derajat keanggotaan")
    plt.ylim(-0.05, 1.05)
    plt.grid(True, alpha=0.35)
    plt.legend(loc="upper center", ncol=3)
    simpan_gambar("G02_membership_visual_proximity.png")

    rendah = [fuzzy.fuzz_urgency(v)["rendah"] for v in x]
    sedang = [fuzzy.fuzz_urgency(v)["sedang"] for v in x]
    tinggi = [fuzzy.fuzz_urgency(v)["tinggi"] for v in x]

    plt.figure(figsize=(8.0, 4.6))
    plt.plot(x, rendah, linewidth=2.0, label="Rendah")
    plt.plot(x, sedang, linewidth=2.0, label="Sedang")
    plt.plot(x, tinggi, linewidth=2.0, label="Tinggi")
    plt.title("Fungsi Keanggotaan Input Urgensi Pendekatan")
    plt.xlabel("Urgensi pendekatan ternormalisasi")
    plt.ylabel("Derajat keanggotaan")
    plt.ylim(-0.05, 1.05)
    plt.grid(True, alpha=0.35)
    plt.legend(loc="upper center", ncol=3)
    simpan_gambar("G03_membership_approach_urgency.png")


def plot_skenario_utama(df):
    skenario_pilihan = [
        "frontal_static_obstacle",
        "crossing_left_to_right",
        "crossing_right_to_left",
        "side_safe_obstacle",
        "no_obstacle",
    ]

    nama_rapih = {
        "frontal_static_obstacle": "Obstacle Frontal Statis",
        "crossing_left_to_right": "Crossing Kiri ke Kanan",
        "crossing_right_to_left": "Crossing Kanan ke Kiri",
        "side_safe_obstacle": "Obstacle Samping Aman",
        "no_obstacle": "Tanpa Obstacle",
    }

    for skenario in skenario_pilihan:
        data = df[df["scenario"] == skenario].copy()

        if data.empty:
            continue

        t = data["time_s"].to_numpy()
        command_level = data["command"].apply(command_to_level).to_numpy()

        plt.figure(figsize=(8.6, 4.8))
        plt.plot(t, data["risk"], linewidth=2.2, label="Risk score")
        plt.axhline(0.30, linestyle="--", linewidth=1.4, label="Batas LOW-MEDIUM")
        plt.axhline(0.60, linestyle="--", linewidth=1.4, label="Batas MEDIUM-HIGH")
        plt.fill_between(t, 0.0, 0.30, alpha=0.08)
        plt.fill_between(t, 0.30, 0.60, alpha=0.08)
        plt.fill_between(t, 0.60, 1.0, alpha=0.08)
        plt.title(f"Perubahan Risk Score - {nama_rapih[skenario]}")
        plt.xlabel("Waktu (s)")
        plt.ylabel("Risk score")
        plt.ylim(0.0, 1.0)
        plt.grid(True, alpha=0.35)
        plt.legend(loc="upper left")
        simpan_gambar(f"G10_risk_{skenario}.png")

        plt.figure(figsize=(8.6, 4.8))
        plt.plot(t, data["speed"], linewidth=2.2, label="Speed factor")
        plt.plot(t, data["turn"], linewidth=2.2, label="Turn bias")
        plt.axhline(0.0, linewidth=1.0, alpha=0.6)
        plt.title(f"Output Fuzzy Controller - {nama_rapih[skenario]}")
        plt.xlabel("Waktu (s)")
        plt.ylabel("Nilai output")
        plt.ylim(-1.05, 1.05)
        plt.grid(True, alpha=0.35)
        plt.legend(loc="best")
        simpan_gambar(f"G20_output_{skenario}.png")

        plt.figure(figsize=(8.6, 4.8))
        plt.step(t, command_level, where="post", linewidth=2.2)
        plt.yticks(
            [0, 1, 2, 3, 4],
            ["HOLD", "SLOW", "LEFT", "RIGHT", "STOP"],
        )
        plt.title(f"Keputusan Command - {nama_rapih[skenario]}")
        plt.xlabel("Waktu (s)")
        plt.ylabel("Command")
        plt.ylim(-0.3, 4.3)
        plt.grid(True, alpha=0.35)
        simpan_gambar(f"G30_command_{skenario}.png")


def plot_lintasan_rapih():
    path = "results/usv_trajectory_log.csv"

    if not os.path.exists(path):
        print("Lewati plot lintasan: results/usv_trajectory_log.csv belum ada.")
        return

    df = pd.read_csv(path)

    nama_rapih = {
        "frontal_static_obstacle": "Obstacle Frontal Statis",
        "crossing_left_to_right": "Crossing Kiri ke Kanan",
        "crossing_right_to_left": "Crossing Kanan ke Kiri",
        "side_safe_obstacle": "Obstacle Samping Aman",
        "no_obstacle": "Tanpa Obstacle",
    }

    for skenario, data in df.groupby("scenario"):
        data = data.sort_values("time_s").copy()

        plt.figure(figsize=(7.2, 6.0))
        plt.plot(
            data["usv_x_m"],
            data["usv_y_m"],
            linewidth=2.4,
            label="Lintasan USV",
        )

        if data["obstacle_x_m"].notna().any():
            plt.plot(
                data["obstacle_x_m"],
                data["obstacle_y_m"],
                linestyle="--",
                linewidth=2.0,
                label="Lintasan obstacle",
            )

            plt.scatter(
                data["obstacle_x_m"].iloc[0],
                data["obstacle_y_m"].iloc[0],
                marker="x",
                s=80,
                label="Obstacle awal",
            )

            plt.scatter(
                data["obstacle_x_m"].iloc[-1],
                data["obstacle_y_m"].iloc[-1],
                marker="o",
                s=55,
                label="Obstacle akhir",
            )

        plt.scatter(
            data["usv_x_m"].iloc[0],
            data["usv_y_m"].iloc[0],
            marker="o",
            s=60,
            label="USV awal",
        )

        plt.scatter(
            data["usv_x_m"].iloc[-1],
            data["usv_y_m"].iloc[-1],
            marker="s",
            s=60,
            label="USV akhir",
        )

        plt.axvline(0.0, linestyle=":", linewidth=1.3, label="Garis misi")
        plt.title(f"Simulasi Lintasan - {nama_rapih.get(skenario, skenario)}")
        plt.xlabel("Posisi lateral x (m)")
        plt.ylabel("Posisi maju y (m)")
        plt.grid(True, alpha=0.35)
        plt.axis("equal")
        plt.legend(loc="best")
        simpan_gambar(f"G40_trajectory_{skenario}.png")

        if data["distance_to_obstacle_m"].notna().any():
            plt.figure(figsize=(8.6, 4.8))
            plt.plot(
                data["time_s"],
                data["distance_to_obstacle_m"],
                linewidth=2.2,
                label="Jarak simulatif USV-obstacle",
            )
            plt.title(f"Jarak Simulatif terhadap Obstacle - {nama_rapih.get(skenario, skenario)}")
            plt.xlabel("Waktu (s)")
            plt.ylabel("Jarak simulatif (m)")
            plt.grid(True, alpha=0.35)
            plt.legend(loc="best")
            simpan_gambar(f"G50_distance_{skenario}.png")


def plot_surface_rapih():
    fuzzy = FuzzyCollisionAvoidance()

    proximity = np.linspace(0.0, 1.0, 45)
    urgency = np.linspace(0.0, 1.0, 45)

    p_grid, u_grid = np.meshgrid(proximity, urgency)
    risk_grid = np.zeros_like(p_grid)
    speed_grid = np.zeros_like(p_grid)

    for i in range(p_grid.shape[0]):
        for j in range(p_grid.shape[1]):
            hasil = fuzzy.hitung(
                lateral=0.0,
                proximity=float(p_grid[i, j]),
                urgency=float(u_grid[i, j]),
            )
            risk_grid[i, j] = hasil["risk"]
            speed_grid[i, j] = hasil["speed"]

    fig = plt.figure(figsize=(8.0, 6.0))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(p_grid, u_grid, risk_grid, linewidth=0, antialiased=True)
    ax.set_title("Surface Risk untuk Obstacle di Tengah")
    ax.set_xlabel("Visual proximity")
    ax.set_ylabel("Approach urgency")
    ax.set_zlabel("Risk")
    simpan_gambar("G60_surface_risk_center_obstacle.png")

    fig = plt.figure(figsize=(8.0, 6.0))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(p_grid, u_grid, speed_grid, linewidth=0, antialiased=True)
    ax.set_title("Surface Speed untuk Obstacle di Tengah")
    ax.set_xlabel("Visual proximity")
    ax.set_ylabel("Approach urgency")
    ax.set_zlabel("Speed factor")
    simpan_gambar("G61_surface_speed_center_obstacle.png")


def main():
    buat_folder()
    style_umum()

    path_log = "results/simulation_log.csv"

    if not os.path.exists(path_log):
        raise FileNotFoundError(
            "results/simulation_log.csv belum ada. Jalankan dulu: python scenario_generator.py"
        )

    df = pd.read_csv(path_log)

    plot_membership_input()
    plot_skenario_utama(df)
    plot_lintasan_rapih()
    plot_surface_rapih()

    print("\nGrafik laporan selesai dibuat.")
    print(f"Folder output: {FIG_DIR}")

    for file in sorted(os.listdir(FIG_DIR)):
        print("-", file)


if __name__ == "__main__":
    main()