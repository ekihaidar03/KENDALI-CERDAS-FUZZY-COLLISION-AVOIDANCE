import os
import numpy as np
import matplotlib.pyplot as plt


OUTPUT_DIR = "results/figures_report"


def trimf(x, a, b, c):
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

    y[x <= a] = 0.0 if a != b else y[x <= a]
    y[x >= d] = 0.0 if c != d else y[x >= d]

    return np.clip(y, 0.0, 1.0)


def plot_membership_graph(
    file_name,
    title,
    x_label,
    x_min,
    x_max,
    functions,
    source_text=None,
):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    x = np.linspace(x_min, x_max, 1000)

    plt.figure(figsize=(10, 6))

    for item in functions:
        name = item["name"]
        mf_type = item["type"]
        params = item["params"]

        if mf_type == "trimf":
            y = trimf(x, *params)
        elif mf_type == "trapmf":
            y = trapmf(x, *params)
        else:
            raise ValueError(f"Tipe membership function tidak dikenal: {mf_type}")

        plt.plot(x, y, linewidth=2.2)

        label_x = item.get("label_x", params[len(params) // 2])
        label_y = item.get("label_y", 1.08)

        plt.text(
            label_x,
            label_y,
            name,
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.title(title, fontsize=18, fontweight="bold", pad=18)
    plt.xlabel(x_label, fontsize=12)
    plt.ylabel("Derajat keanggotaan", fontsize=12)

    plt.xlim(x_min, x_max)
    plt.ylim(-0.05, 1.20)

    plt.grid(True, linewidth=0.6, alpha=0.45)
    plt.tight_layout()

    if source_text:
        plt.figtext(
            0.12,
            0.01,
            source_text,
            ha="left",
            fontsize=11,
        )
        plt.subplots_adjust(bottom=0.14)

    output_path = os.path.join(OUTPUT_DIR, file_name)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    return output_path


def plot_lateral_position():
    return plot_membership_graph(
        file_name="G01_membership_lateral_position_report.png",
        title="Input 1: Lateral Position",
        x_label="Input Variable LATERAL POSITION",
        x_min=-1.0,
        x_max=1.0,
        functions=[
            {
                "name": "LEFT",
                "type": "trapmf",
                "params": [-1.00, -1.00, -0.60, -0.15],
                "label_x": -0.75,
            },
            {
                "name": "CENTER",
                "type": "trimf",
                "params": [-0.35, 0.00, 0.35],
                "label_x": 0.00,
            },
            {
                "name": "RIGHT",
                "type": "trapmf",
                "params": [0.15, 0.60, 1.00, 1.00],
                "label_x": 0.75,
            },
        ],
        source_text="Sumber: parameter posisi lateral obstacle dari bounding box kamera.",
    )


def plot_visual_proximity():
    return plot_membership_graph(
        file_name="G02_membership_visual_proximity_report.png",
        title="Input 2: Visual Proximity",
        x_label="Input Variable VISUAL PROXIMITY",
        x_min=0.0,
        x_max=1.0,
        functions=[
            {
                "name": "FAR",
                "type": "trapmf",
                "params": [0.00, 0.00, 0.25, 0.45],
                "label_x": 0.16,
            },
            {
                "name": "MEDIUM",
                "type": "trimf",
                "params": [0.30, 0.55, 0.80],
                "label_x": 0.55,
            },
            {
                "name": "NEAR",
                "type": "trapmf",
                "params": [0.65, 0.82, 1.00, 1.00],
                "label_x": 0.88,
            },
        ],
        source_text="Sumber: posisi bawah bounding box dan rasio area bounding box.",
    )


def plot_approach_urgency():
    return plot_membership_graph(
        file_name="G03_membership_approach_urgency_report.png",
        title="Input 3: Approach Urgency",
        x_label="Input Variable APPROACH URGENCY",
        x_min=0.0,
        x_max=1.0,
        functions=[
            {
                "name": "LOW",
                "type": "trapmf",
                "params": [0.00, 0.00, 0.25, 0.45],
                "label_x": 0.16,
            },
            {
                "name": "MEDIUM",
                "type": "trimf",
                "params": [0.30, 0.55, 0.80],
                "label_x": 0.55,
            },
            {
                "name": "HIGH",
                "type": "trapmf",
                "params": [0.75, 0.90, 1.00, 1.00],
                "label_x": 0.90,
            },
        ],
        source_text="Sumber: visual time-to-collision dan perubahan log area bounding box.",
    )


def plot_speed_factor():
    return plot_membership_graph(
        file_name="G04_membership_speed_factor_report.png",
        title="Output 1: Speed Factor",
        x_label="Output Variable SPEED FACTOR",
        x_min=0.0,
        x_max=1.0,
        functions=[
            {
                "name": "STOP",
                "type": "trapmf",
                "params": [0.00, 0.00, 0.05, 0.18],
                "label_x": 0.08,
            },
            {
                "name": "SLOW",
                "type": "trimf",
                "params": [0.12, 0.35, 0.58],
                "label_x": 0.35,
            },
            {
                "name": "NORMAL",
                "type": "trapmf",
                "params": [0.50, 0.72, 1.00, 1.00],
                "label_x": 0.85,
            },
        ],
        source_text="Sumber: output fuzzy untuk faktor kecepatan USV.",
    )


def plot_turn_bias():
    return plot_membership_graph(
        file_name="G05_membership_turn_bias_report.png",
        title="Output 2: Turn Bias",
        x_label="Output Variable TURN BIAS",
        x_min=-1.0,
        x_max=1.0,
        functions=[
            {
                "name": "LEFT",
                "type": "trapmf",
                "params": [-1.00, -1.00, -0.75, -0.22],
                "label_x": -0.82,
            },
            {
                "name": "STRAIGHT",
                "type": "trimf",
                "params": [-0.30, 0.00, 0.30],
                "label_x": 0.00,
            },
            {
                "name": "RIGHT",
                "type": "trapmf",
                "params": [0.22, 0.75, 1.00, 1.00],
                "label_x": 0.82,
            },
        ],
        source_text="Sumber: output fuzzy untuk kecenderungan arah belok USV.",
    )


def plot_risk_score():
    return plot_membership_graph(
        file_name="G06_membership_risk_score_report.png",
        title="Output 3: Risk Score",
        x_label="Output Variable RISK SCORE",
        x_min=0.0,
        x_max=1.0,
        functions=[
            {
                "name": "LOW",
                "type": "trapmf",
                "params": [0.00, 0.00, 0.18, 0.35],
                "label_x": 0.12,
            },
            {
                "name": "MEDIUM",
                "type": "trimf",
                "params": [0.25, 0.45, 0.65],
                "label_x": 0.45,
            },
            {
                "name": "HIGH",
                "type": "trapmf",
                "params": [0.62, 0.78, 1.00, 1.00],
                "label_x": 0.87,
            },
        ],
        source_text="Sumber: output fuzzy untuk klasifikasi risiko collision avoidance.",
    )


def main():
    print("Membuat grafik membership function versi laporan...")

    output_files = [
        plot_lateral_position(),
        plot_visual_proximity(),
        plot_approach_urgency(),
        plot_speed_factor(),
        plot_turn_bias(),
        plot_risk_score(),
    ]

    print("\nGrafik berhasil dibuat:")
    for path in output_files:
        print(f"- {path}")


if __name__ == "__main__":
    main()