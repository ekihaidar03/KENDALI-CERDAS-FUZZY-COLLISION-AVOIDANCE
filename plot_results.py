import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from fuzzy_controller import FuzzyCollisionAvoidance


def buat_folder_gambar():
    os.makedirs("results", exist_ok=True)
    os.makedirs("results/figures", exist_ok=True)


def command_to_level(command):
    mapping = {
        "HOLD_COURSE": 0,
        "SLOW_DOWN": 1,
        "TURN_LEFT_SLOW": 2,
        "TURN_RIGHT_SLOW": 3,
        "STOP": 4,
    }
    return mapping.get(command, -1)


def plot_membership_function():
    fuzzy = FuzzyCollisionAvoidance()

    x_lateral = np.linspace(-1.0, 1.0, 501)
    kiri = [fuzzy.fuzz_lateral(v)["kiri"] for v in x_lateral]
    tengah = [fuzzy.fuzz_lateral(v)["tengah"] for v in x_lateral]
    kanan = [fuzzy.fuzz_lateral(v)["kanan"] for v in x_lateral]

    plt.figure(figsize=(8, 4.5))
    plt.plot(x_lateral, kiri, label="kiri")
    plt.plot(x_lateral, tengah, label="tengah")
    plt.plot(x_lateral, kanan, label="kanan")
    plt.title("Membership Function Input Lateral Position")
    plt.xlabel("lateral position")
    plt.ylabel("derajat keanggotaan")
    plt.ylim(-0.05, 1.05)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("results/figures/mf_lateral_position.png", dpi=200)
    plt.close()

    x_norm = np.linspace(0.0, 1.0, 501)
    jauh = [fuzzy.fuzz_proximity(v)["jauh"] for v in x_norm]
    sedang = [fuzzy.fuzz_proximity(v)["sedang"] for v in x_norm]
    dekat = [fuzzy.fuzz_proximity(v)["dekat"] for v in x_norm]

    plt.figure(figsize=(8, 4.5))
    plt.plot(x_norm, jauh, label="jauh")
    plt.plot(x_norm, sedang, label="sedang")
    plt.plot(x_norm, dekat, label="dekat")
    plt.title("Membership Function Input Visual Proximity")
    plt.xlabel("visual proximity")
    plt.ylabel("derajat keanggotaan")
    plt.ylim(-0.05, 1.05)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("results/figures/mf_visual_proximity.png", dpi=200)
    plt.close()

    rendah = [fuzzy.fuzz_urgency(v)["rendah"] for v in x_norm]
    sedang = [fuzzy.fuzz_urgency(v)["sedang"] for v in x_norm]
    tinggi = [fuzzy.fuzz_urgency(v)["tinggi"] for v in x_norm]

    plt.figure(figsize=(8, 4.5))
    plt.plot(x_norm, rendah, label="rendah")
    plt.plot(x_norm, sedang, label="sedang")
    plt.plot(x_norm, tinggi, label="tinggi")
    plt.title("Membership Function Input Approach Urgency")
    plt.xlabel("approach urgency")
    plt.ylabel("derajat keanggotaan")
    plt.ylim(-0.05, 1.05)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("results/figures/mf_approach_urgency.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 4.5))
    plt.plot(fuzzy.speed_x, fuzzy.mf_speed("stop"), label="stop")
    plt.plot(fuzzy.speed_x, fuzzy.mf_speed("slow"), label="slow")
    plt.plot(fuzzy.speed_x, fuzzy.mf_speed("normal"), label="normal")
    plt.title("Membership Function Output Speed Factor")
    plt.xlabel("speed factor")
    plt.ylabel("derajat keanggotaan")
    plt.ylim(-0.05, 1.05)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("results/figures/mf_speed_factor.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 4.5))
    plt.plot(fuzzy.turn_x, fuzzy.mf_turn("left"), label="left")
    plt.plot(fuzzy.turn_x, fuzzy.mf_turn("straight"), label="straight")
    plt.plot(fuzzy.turn_x, fuzzy.mf_turn("right"), label="right")
    plt.title("Membership Function Output Turn Bias")
    plt.xlabel("turn bias")
    plt.ylabel("derajat keanggotaan")
    plt.ylim(-0.05, 1.05)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig("results/figures/mf_turn_bias.png", dpi=200)
    plt.close()


def plot_skenario(df, nama_skenario):
    data = df[df["scenario"] == nama_skenario].copy()

    if data.empty:
        return

    t = data["time_s"].to_numpy()
    command_level = data["command"].apply(command_to_level).to_numpy()

    plt.figure(figsize=(9, 4.8))
    plt.plot(t, data["risk"], label="risk")
    plt.axhline(0.30, linestyle="--", linewidth=1.0, label="batas LOW-MEDIUM")
    plt.axhline(0.60, linestyle="--", linewidth=1.0, label="batas MEDIUM-HIGH")
    plt.title(f"Risk Score - {nama_skenario}")
    plt.xlabel("waktu (s)")
    plt.ylabel("risk score")
    plt.ylim(0.0, 1.0)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"results/figures/risk_{nama_skenario}.png", dpi=200)
    plt.close()

    plt.figure(figsize=(9, 4.8))
    plt.plot(t, data["speed"], label="speed factor")
    plt.plot(t, data["turn"], label="turn bias")
    plt.title(f"Output Fuzzy - {nama_skenario}")
    plt.xlabel("waktu (s)")
    plt.ylabel("nilai output")
    plt.ylim(-1.05, 1.05)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"results/figures/output_{nama_skenario}.png", dpi=200)
    plt.close()

    plt.figure(figsize=(9, 4.8))
    plt.step(t, command_level, where="post")
    plt.yticks(
        [0, 1, 2, 3, 4],
        ["HOLD", "SLOW", "LEFT", "RIGHT", "STOP"],
    )
    plt.title(f"Command Decision - {nama_skenario}")
    plt.xlabel("waktu (s)")
    plt.ylabel("command")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"results/figures/command_{nama_skenario}.png", dpi=200)
    plt.close()

    plt.figure(figsize=(9, 4.8))
    plt.plot(t, data["x"], label="x center")
    plt.plot(t, data["bot"], label="bbox bottom")
    plt.plot(t, data["area"], label="bbox area")
    plt.title(f"Visual Feature - {nama_skenario}")
    plt.xlabel("waktu (s)")
    plt.ylabel("nilai normalisasi")
    plt.ylim(0.0, 1.05)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"results/figures/visual_feature_{nama_skenario}.png", dpi=200)
    plt.close()


def plot_control_surface():
    fuzzy = FuzzyCollisionAvoidance()

    proximity = np.linspace(0.0, 1.0, 40)
    urgency = np.linspace(0.0, 1.0, 40)

    p_grid, u_grid = np.meshgrid(proximity, urgency)
    risk_grid = np.zeros_like(p_grid)
    speed_grid = np.zeros_like(p_grid)

    lateral_tengah = 0.0

    for i in range(p_grid.shape[0]):
        for j in range(p_grid.shape[1]):
            hasil = fuzzy.hitung(
                lateral=lateral_tengah,
                proximity=float(p_grid[i, j]),
                urgency=float(u_grid[i, j]),
            )
            risk_grid[i, j] = hasil["risk"]
            speed_grid[i, j] = hasil["speed"]

    fig = plt.figure(figsize=(8, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(p_grid, u_grid, risk_grid, linewidth=0, antialiased=True)
    ax.set_title("Control Surface Risk - Obstacle Tengah")
    ax.set_xlabel("visual proximity")
    ax.set_ylabel("approach urgency")
    ax.set_zlabel("risk")
    plt.tight_layout()
    plt.savefig("results/figures/surface_risk_center_obstacle.png", dpi=200)
    plt.close()

    fig = plt.figure(figsize=(8, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(p_grid, u_grid, speed_grid, linewidth=0, antialiased=True)
    ax.set_title("Control Surface Speed - Obstacle Tengah")
    ax.set_xlabel("visual proximity")
    ax.set_ylabel("approach urgency")
    ax.set_zlabel("speed factor")
    plt.tight_layout()
    plt.savefig("results/figures/surface_speed_center_obstacle.png", dpi=200)
    plt.close()


def main():
    buat_folder_gambar()

    csv_path = "results/simulation_log.csv"

    if not os.path.exists(csv_path):
        raise FileNotFoundError(
            "results/simulation_log.csv belum ada. Jalankan dulu: python scenario_generator.py"
        )

    df = pd.read_csv(csv_path)

    plot_membership_function()
    plot_control_surface()

    for nama_skenario in df["scenario"].unique():
        plot_skenario(df, nama_skenario)

    print("\nPlot selesai dibuat.")
    print("Folder output: results/figures")

    file_gambar = sorted(os.listdir("results/figures"))
    for nama_file in file_gambar:
        print("-", nama_file)


if __name__ == "__main__":
    main()