import os
import csv
import numpy as np
import matplotlib.pyplot as plt


OUTPUT_DIR = "results/figures_report"
TABLE_DIR = "results/report_tables"


CASE_NAME = "obstacle_depan_sedang"

INPUT_VALUE = {
    "lateral": 0.00,
    "proximity": 0.57,
    "urgency": 0.70,
}


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


def eval_mf(value, mf_def):
    x = np.array([value], dtype=float)
    if mf_def["type"] == "trimf":
        return float(trimf(x, *mf_def["params"])[0])
    if mf_def["type"] == "trapmf":
        return float(trapmf(x, *mf_def["params"])[0])
    raise ValueError(f"Tipe membership function tidak dikenal: {mf_def['type']}")


def curve(x, mf_def):
    if mf_def["type"] == "trimf":
        return trimf(x, *mf_def["params"])
    if mf_def["type"] == "trapmf":
        return trapmf(x, *mf_def["params"])
    raise ValueError(f"Tipe membership function tidak dikenal: {mf_def['type']}")


def centroid(x, mu):
    area = np.sum(mu)
    if area <= 1e-12:
        return float(np.mean(x))
    return float(np.sum(x * mu) / area)


INPUT_MF = {
    "lateral": {
        "range": (-1.0, 1.0),
        "label": "LATERAL",
        "value_label": "L = 0.00",
        "sets": {
            "LEFT": {
                "type": "trapmf",
                "params": [-1.00, -1.00, -0.60, -0.15],
            },
            "CENTER": {
                "type": "trimf",
                "params": [-0.35, 0.00, 0.35],
            },
            "RIGHT": {
                "type": "trapmf",
                "params": [0.15, 0.60, 1.00, 1.00],
            },
        },
    },
    "proximity": {
        "range": (0.0, 1.0),
        "label": "PROXIMITY",
        "value_label": "P = 0.57",
        "sets": {
            "FAR": {
                "type": "trapmf",
                "params": [0.00, 0.00, 0.25, 0.45],
            },
            "MEDIUM": {
                "type": "trimf",
                "params": [0.30, 0.55, 0.80],
            },
            "NEAR": {
                "type": "trapmf",
                "params": [0.65, 0.82, 1.00, 1.00],
            },
        },
    },
    "urgency": {
        "range": (0.0, 1.0),
        "label": "URGENCY",
        "value_label": "U = 0.70",
        "sets": {
            "LOW": {
                "type": "trapmf",
                "params": [0.00, 0.00, 0.25, 0.45],
            },
            "MEDIUM": {
                "type": "trimf",
                "params": [0.30, 0.55, 0.80],
            },
            "HIGH": {
                "type": "trapmf",
                "params": [0.75, 0.90, 1.00, 1.00],
            },
        },
    },
}


OUTPUT_MF = {
    "risk": {
        "range": (0.0, 1.0),
        "label": "RISK SCORE",
        "sets": {
            "LOW": {
                "type": "trapmf",
                "params": [0.00, 0.00, 0.18, 0.35],
            },
            "MEDIUM": {
                "type": "trimf",
                "params": [0.25, 0.45, 0.65],
            },
            "HIGH": {
                "type": "trapmf",
                "params": [0.62, 0.78, 1.00, 1.00],
            },
        },
    },
    "speed": {
        "range": (0.0, 1.0),
        "label": "SPEED FACTOR",
        "sets": {
            "STOP": {
                "type": "trapmf",
                "params": [0.00, 0.00, 0.05, 0.18],
            },
            "SLOW": {
                "type": "trimf",
                "params": [0.12, 0.35, 0.58],
            },
            "NORMAL": {
                "type": "trapmf",
                "params": [0.50, 0.72, 1.00, 1.00],
            },
        },
    },
    "turn": {
        "range": (-1.0, 1.0),
        "label": "TURN BIAS",
        "sets": {
            "LEFT": {
                "type": "trapmf",
                "params": [-1.00, -1.00, -0.75, -0.22],
            },
            "STRAIGHT": {
                "type": "trimf",
                "params": [-0.30, 0.00, 0.30],
            },
            "RIGHT": {
                "type": "trapmf",
                "params": [0.22, 0.75, 1.00, 1.00],
            },
        },
    },
}


RULES = [
    {
        "no": 1,
        "lateral": "CENTER",
        "proximity": "FAR",
        "urgency": "LOW",
        "risk": "LOW",
        "speed": "NORMAL",
        "turn": "STRAIGHT",
    },
    {
        "no": 2,
        "lateral": "CENTER",
        "proximity": "FAR",
        "urgency": "MEDIUM",
        "risk": "LOW",
        "speed": "NORMAL",
        "turn": "STRAIGHT",
    },
    {
        "no": 3,
        "lateral": "CENTER",
        "proximity": "FAR",
        "urgency": "HIGH",
        "risk": "MEDIUM",
        "speed": "SLOW",
        "turn": "RIGHT",
    },
    {
        "no": 4,
        "lateral": "CENTER",
        "proximity": "MEDIUM",
        "urgency": "LOW",
        "risk": "LOW",
        "speed": "NORMAL",
        "turn": "STRAIGHT",
    },
    {
        "no": 5,
        "lateral": "CENTER",
        "proximity": "MEDIUM",
        "urgency": "MEDIUM",
        "risk": "MEDIUM",
        "speed": "SLOW",
        "turn": "RIGHT",
    },
    {
        "no": 6,
        "lateral": "CENTER",
        "proximity": "MEDIUM",
        "urgency": "HIGH",
        "risk": "HIGH",
        "speed": "SLOW",
        "turn": "RIGHT",
    },
    {
        "no": 7,
        "lateral": "CENTER",
        "proximity": "NEAR",
        "urgency": "LOW",
        "risk": "MEDIUM",
        "speed": "SLOW",
        "turn": "STRAIGHT",
    },
    {
        "no": 8,
        "lateral": "CENTER",
        "proximity": "NEAR",
        "urgency": "MEDIUM",
        "risk": "HIGH",
        "speed": "STOP",
        "turn": "RIGHT",
    },
    {
        "no": 9,
        "lateral": "CENTER",
        "proximity": "NEAR",
        "urgency": "HIGH",
        "risk": "HIGH",
        "speed": "STOP",
        "turn": "RIGHT",
    },
]


def calculate_rule_strength(rule):
    mu_lateral = eval_mf(
        INPUT_VALUE["lateral"],
        INPUT_MF["lateral"]["sets"][rule["lateral"]],
    )
    mu_proximity = eval_mf(
        INPUT_VALUE["proximity"],
        INPUT_MF["proximity"]["sets"][rule["proximity"]],
    )
    mu_urgency = eval_mf(
        INPUT_VALUE["urgency"],
        INPUT_MF["urgency"]["sets"][rule["urgency"]],
    )

    alpha = min(mu_lateral, mu_proximity, mu_urgency)

    return {
        "mu_lateral": mu_lateral,
        "mu_proximity": mu_proximity,
        "mu_urgency": mu_urgency,
        "alpha": alpha,
    }


def calculate_output(output_name):
    out_def = OUTPUT_MF[output_name]
    x_out = np.linspace(out_def["range"][0], out_def["range"][1], 1200)
    aggregate = np.zeros_like(x_out)

    rows = []

    for rule in RULES:
        strength = calculate_rule_strength(rule)
        alpha = strength["alpha"]

        output_set = rule[output_name]
        output_curve = curve(x_out, out_def["sets"][output_set])
        clipped_output = np.minimum(alpha, output_curve)

        aggregate = np.maximum(aggregate, clipped_output)

        rows.append(
            {
                "rule": rule,
                "strength": strength,
                "x_out": x_out,
                "output_curve": output_curve,
                "clipped_output": clipped_output,
            }
        )

    crisp_value = centroid(x_out, aggregate)

    return {
        "x_out": x_out,
        "aggregate": aggregate,
        "crisp_value": crisp_value,
        "rows": rows,
    }


def setup_small_axis(ax):
    ax.set_ylim(-0.05, 1.12)
    ax.set_yticks([0, 1])
    ax.grid(True, linewidth=0.4, alpha=0.35)
    ax.tick_params(labelsize=7)


def draw_input_axis(ax, input_name, mf_name, input_value, alpha, show_title=False):
    in_def = INPUT_MF[input_name]
    x = np.linspace(in_def["range"][0], in_def["range"][1], 700)
    y = curve(x, in_def["sets"][mf_name])

    ax.plot(x, y, linewidth=1.4)
    ax.axvline(input_value, linewidth=1.1, linestyle="-")
    ax.axhline(alpha, linewidth=1.0, linestyle="--")
    ax.fill_between(x, 0, np.minimum(alpha, y), alpha=0.25)

    ax.set_xlim(in_def["range"])
    setup_small_axis(ax)

    if show_title:
        ax.set_title(
            f"{in_def['label']}\n{in_def['value_label']}",
            fontsize=10,
            fontweight="bold",
        )

    ax.text(
        0.02,
        0.82,
        mf_name,
        transform=ax.transAxes,
        fontsize=7,
        fontweight="bold",
    )


def draw_output_axis(ax, output_name, output_set, alpha, show_title=False):
    out_def = OUTPUT_MF[output_name]
    x = np.linspace(out_def["range"][0], out_def["range"][1], 700)
    y = curve(x, out_def["sets"][output_set])
    clipped = np.minimum(alpha, y)

    ax.plot(x, y, linewidth=1.2)
    ax.axhline(alpha, linewidth=1.0, linestyle="--")
    ax.fill_between(x, 0, clipped, alpha=0.35)

    ax.set_xlim(out_def["range"])
    setup_small_axis(ax)

    if show_title:
        ax.set_title(out_def["label"], fontsize=10, fontweight="bold")

    ax.text(
        0.02,
        0.82,
        output_set,
        transform=ax.transAxes,
        fontsize=7,
        fontweight="bold",
    )


def draw_aggregate_axis(ax, output_name, output_result):
    out_def = OUTPUT_MF[output_name]
    x = output_result["x_out"]
    agg = output_result["aggregate"]
    crisp = output_result["crisp_value"]

    ax.plot(x, agg, linewidth=1.6)
    ax.fill_between(x, 0, agg, alpha=0.35)
    ax.axvline(crisp, linewidth=1.4, linestyle="-")

    ax.set_xlim(out_def["range"])
    setup_small_axis(ax)

    ax.set_title(
        f"AGGREGASI DAN DEFUZZIFIKASI\n{out_def['label']} = {crisp:.3f}",
        fontsize=10,
        fontweight="bold",
    )


def save_active_rule_table():
    os.makedirs(TABLE_DIR, exist_ok=True)

    output_path = os.path.join(
        TABLE_DIR,
        f"tabel_rule_inference_{CASE_NAME}.csv",
    )

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "rule",
                "lateral",
                "proximity",
                "urgency",
                "mu_lateral",
                "mu_proximity",
                "mu_urgency",
                "firing_strength",
                "risk_output",
                "speed_output",
                "turn_output",
            ]
        )

        for rule in RULES:
            strength = calculate_rule_strength(rule)
            writer.writerow(
                [
                    rule["no"],
                    rule["lateral"],
                    rule["proximity"],
                    rule["urgency"],
                    round(strength["mu_lateral"], 4),
                    round(strength["mu_proximity"], 4),
                    round(strength["mu_urgency"], 4),
                    round(strength["alpha"], 4),
                    rule["risk"],
                    rule["speed"],
                    rule["turn"],
                ]
            )

    return output_path


def plot_rule_inference(output_name):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    output_result = calculate_output(output_name)
    rows = output_result["rows"]

    n_rules = len(RULES)
    n_rows = n_rules + 1
    n_cols = 4

    fig, axes = plt.subplots(
        n_rows,
        n_cols,
        figsize=(12, 18),
        constrained_layout=False,
    )

    fig.suptitle(
        f"Rule Inference Mamdani - {CASE_NAME.replace('_', ' ').title()} - {OUTPUT_MF[output_name]['label']}",
        fontsize=16,
        fontweight="bold",
        y=0.995,
    )

    for idx, row in enumerate(rows):
        rule = row["rule"]
        strength = row["strength"]
        alpha = strength["alpha"]

        draw_input_axis(
            axes[idx, 0],
            "lateral",
            rule["lateral"],
            INPUT_VALUE["lateral"],
            alpha,
            show_title=(idx == 0),
        )
        draw_input_axis(
            axes[idx, 1],
            "proximity",
            rule["proximity"],
            INPUT_VALUE["proximity"],
            alpha,
            show_title=(idx == 0),
        )
        draw_input_axis(
            axes[idx, 2],
            "urgency",
            rule["urgency"],
            INPUT_VALUE["urgency"],
            alpha,
            show_title=(idx == 0),
        )
        draw_output_axis(
            axes[idx, 3],
            output_name,
            rule[output_name],
            alpha,
            show_title=(idx == 0),
        )

        axes[idx, 0].set_ylabel(
            f"Rule {rule['no']}\nα={alpha:.2f}",
            fontsize=8,
            rotation=0,
            labelpad=28,
            va="center",
        )

    for col in range(3):
        axes[-1, col].axis("off")

    draw_aggregate_axis(axes[-1, 3], output_name, output_result)

    fig.text(
        0.5,
        0.012,
        "Input crisp: L = 0.00, P = 0.57, U = 0.70. Garis vertikal menunjukkan input crisp. Garis putus-putus menunjukkan firing strength rule.",
        ha="center",
        fontsize=9,
    )

    plt.tight_layout(rect=[0.03, 0.03, 1.0, 0.975])

    output_path = os.path.join(
        OUTPUT_DIR,
        f"G07_rule_inference_{output_name}_{CASE_NAME}.png",
    )

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    return output_path, output_result["crisp_value"]


def main():
    print("Membuat dokumentasi rule inference Mamdani...")

    table_path = save_active_rule_table()

    created_files = []
    for output_name in ["risk", "speed", "turn"]:
        image_path, crisp_value = plot_rule_inference(output_name)
        created_files.append((output_name, image_path, crisp_value))

    print("\nTabel rule inference:")
    print(f"- {table_path}")

    print("\nGambar rule inference:")
    for output_name, image_path, crisp_value in created_files:
        print(f"- {output_name}: {image_path} | crisp = {crisp_value:.3f}")

    print("\nSelesai.")


if __name__ == "__main__":
    main()