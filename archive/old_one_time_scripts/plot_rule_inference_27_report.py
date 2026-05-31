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


def mf_curve(x, mf_def):
    if mf_def["type"] == "trimf":
        return trimf(x, *mf_def["params"])

    if mf_def["type"] == "trapmf":
        return trapmf(x, *mf_def["params"])

    raise ValueError(f"Tipe membership function tidak dikenal: {mf_def['type']}")


def eval_mf(value, mf_def):
    x = np.array([value], dtype=float)
    return float(mf_curve(x, mf_def)[0])


def centroid(x, mu):
    area = np.sum(mu)

    if area <= 1e-12:
        return float(np.mean(x))

    return float(np.sum(x * mu) / area)


INPUT_MF = {
    "lateral": {
        "title": "LATERAL",
        "value_text": "L = 0.00",
        "range": (-1.0, 1.0),
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
        "title": "PROXIMITY",
        "value_text": "P = 0.57",
        "range": (0.0, 1.0),
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
        "title": "URGENCY",
        "value_text": "U = 0.70",
        "range": (0.0, 1.0),
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
        "title": "RISK SCORE",
        "range": (0.0, 1.0),
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
        "title": "SPEED FACTOR",
        "range": (0.0, 1.0),
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
        "title": "TURN BIAS",
        "range": (-1.0, 1.0),
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


RULE_TABLE = {
    "LEFT": {
        "LOW": {
            "FAR": ("LOW", "NORMAL", "STRAIGHT"),
            "MEDIUM": ("LOW", "NORMAL", "STRAIGHT"),
            "NEAR": ("MEDIUM", "SLOW", "RIGHT"),
        },
        "MEDIUM": {
            "FAR": ("LOW", "NORMAL", "STRAIGHT"),
            "MEDIUM": ("MEDIUM", "SLOW", "RIGHT"),
            "NEAR": ("HIGH", "STOP", "RIGHT"),
        },
        "HIGH": {
            "FAR": ("MEDIUM", "SLOW", "RIGHT"),
            "MEDIUM": ("HIGH", "SLOW", "RIGHT"),
            "NEAR": ("HIGH", "STOP", "RIGHT"),
        },
    },
    "CENTER": {
        "LOW": {
            "FAR": ("LOW", "NORMAL", "STRAIGHT"),
            "MEDIUM": ("LOW", "NORMAL", "STRAIGHT"),
            "NEAR": ("MEDIUM", "SLOW", "STRAIGHT"),
        },
        "MEDIUM": {
            "FAR": ("LOW", "NORMAL", "STRAIGHT"),
            "MEDIUM": ("MEDIUM", "SLOW", "RIGHT"),
            "NEAR": ("HIGH", "STOP", "RIGHT"),
        },
        "HIGH": {
            "FAR": ("MEDIUM", "SLOW", "RIGHT"),
            "MEDIUM": ("HIGH", "SLOW", "RIGHT"),
            "NEAR": ("HIGH", "STOP", "RIGHT"),
        },
    },
    "RIGHT": {
        "LOW": {
            "FAR": ("LOW", "NORMAL", "STRAIGHT"),
            "MEDIUM": ("LOW", "NORMAL", "STRAIGHT"),
            "NEAR": ("MEDIUM", "SLOW", "LEFT"),
        },
        "MEDIUM": {
            "FAR": ("LOW", "NORMAL", "STRAIGHT"),
            "MEDIUM": ("MEDIUM", "SLOW", "LEFT"),
            "NEAR": ("HIGH", "STOP", "LEFT"),
        },
        "HIGH": {
            "FAR": ("MEDIUM", "SLOW", "LEFT"),
            "MEDIUM": ("HIGH", "SLOW", "LEFT"),
            "NEAR": ("HIGH", "STOP", "LEFT"),
        },
    },
}


def build_rules():
    rules = []
    rule_no = 1

    for lateral in ["LEFT", "CENTER", "RIGHT"]:
        for urgency in ["LOW", "MEDIUM", "HIGH"]:
            for proximity in ["FAR", "MEDIUM", "NEAR"]:
                risk, speed, turn = RULE_TABLE[lateral][urgency][proximity]

                rules.append(
                    {
                        "no": rule_no,
                        "lateral": lateral,
                        "proximity": proximity,
                        "urgency": urgency,
                        "risk": risk,
                        "speed": speed,
                        "turn": turn,
                    }
                )

                rule_no += 1

    return rules


RULES = build_rules()


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
    output_def = OUTPUT_MF[output_name]
    x_out = np.linspace(output_def["range"][0], output_def["range"][1], 1500)
    aggregate = np.zeros_like(x_out)

    row_data = []

    for rule in RULES:
        strength = calculate_rule_strength(rule)
        alpha = strength["alpha"]

        output_set = rule[output_name]
        base_curve = mf_curve(x_out, output_def["sets"][output_set])
        clipped_curve = np.minimum(alpha, base_curve)

        aggregate = np.maximum(aggregate, clipped_curve)

        row_data.append(
            {
                "rule": rule,
                "strength": strength,
                "x_out": x_out,
                "base_curve": base_curve,
                "clipped_curve": clipped_curve,
            }
        )

    crisp = centroid(x_out, aggregate)

    return {
        "x_out": x_out,
        "aggregate": aggregate,
        "crisp": crisp,
        "row_data": row_data,
    }


def setup_axis(ax):
    ax.set_ylim(-0.05, 1.10)
    ax.set_yticks([0, 1])
    ax.grid(True, linewidth=0.35, alpha=0.35)
    ax.tick_params(axis="both", labelsize=6)


def draw_input_cell(ax, input_name, mf_name, input_value, alpha, show_title=False):
    input_def = INPUT_MF[input_name]
    x = np.linspace(input_def["range"][0], input_def["range"][1], 900)
    y = mf_curve(x, input_def["sets"][mf_name])
    clipped = np.minimum(alpha, y)

    ax.plot(x, y, linewidth=1.2)
    ax.axvline(input_value, linewidth=1.0)
    ax.axhline(alpha, linewidth=0.9, linestyle="--")
    ax.fill_between(x, 0, clipped, alpha=0.25)

    ax.set_xlim(input_def["range"])
    setup_axis(ax)

    if show_title:
        ax.set_title(
            f"{input_def['title']}\n{input_def['value_text']}",
            fontsize=9,
            fontweight="bold",
        )

    ax.text(
        0.03,
        0.78,
        mf_name,
        transform=ax.transAxes,
        fontsize=6.5,
        fontweight="bold",
    )


def draw_output_cell(ax, output_name, output_set, alpha, show_title=False):
    output_def = OUTPUT_MF[output_name]
    x = np.linspace(output_def["range"][0], output_def["range"][1], 900)
    y = mf_curve(x, output_def["sets"][output_set])
    clipped = np.minimum(alpha, y)

    ax.plot(x, y, linewidth=1.2)
    ax.axhline(alpha, linewidth=0.9, linestyle="--")
    ax.fill_between(x, 0, clipped, alpha=0.35)

    ax.set_xlim(output_def["range"])
    setup_axis(ax)

    if show_title:
        ax.set_title(
            output_def["title"],
            fontsize=9,
            fontweight="bold",
        )

    ax.text(
        0.03,
        0.78,
        output_set,
        transform=ax.transAxes,
        fontsize=6.5,
        fontweight="bold",
    )


def draw_aggregate_cell(ax, output_name, output_result):
    output_def = OUTPUT_MF[output_name]
    x = output_result["x_out"]
    aggregate = output_result["aggregate"]
    crisp = output_result["crisp"]

    ax.plot(x, aggregate, linewidth=1.4)
    ax.fill_between(x, 0, aggregate, alpha=0.35)
    ax.axvline(crisp, linewidth=1.2)

    ax.set_xlim(output_def["range"])
    setup_axis(ax)

    ax.set_title(
        f"AGGREGASI\n{output_def['title']} = {crisp:.3f}",
        fontsize=8,
        fontweight="bold",
    )


def plot_rule_viewer(output_name):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    output_result = calculate_output(output_name)
    row_data = output_result["row_data"]

    n_rules = len(RULES)
    n_rows = n_rules + 1
    n_cols = 4

    fig, axes = plt.subplots(
        n_rows,
        n_cols,
        figsize=(12, 35),
        constrained_layout=False,
    )

    fig.suptitle(
        f"Rule Inference Mamdani 27 Rule - {OUTPUT_MF[output_name]['title']}",
        fontsize=16,
        fontweight="bold",
        y=0.998,
    )

    for idx, row in enumerate(row_data):
        rule = row["rule"]
        strength = row["strength"]
        alpha = strength["alpha"]

        draw_input_cell(
            axes[idx, 0],
            "lateral",
            rule["lateral"],
            INPUT_VALUE["lateral"],
            alpha,
            show_title=(idx == 0),
        )

        draw_input_cell(
            axes[idx, 1],
            "proximity",
            rule["proximity"],
            INPUT_VALUE["proximity"],
            alpha,
            show_title=(idx == 0),
        )

        draw_input_cell(
            axes[idx, 2],
            "urgency",
            rule["urgency"],
            INPUT_VALUE["urgency"],
            alpha,
            show_title=(idx == 0),
        )

        draw_output_cell(
            axes[idx, 3],
            output_name,
            rule[output_name],
            alpha,
            show_title=(idx == 0),
        )

        axes[idx, 0].set_ylabel(
            f"{rule['no']}\nα={alpha:.2f}",
            fontsize=7,
            rotation=0,
            labelpad=22,
            va="center",
        )

    for col in range(3):
        axes[-1, col].axis("off")

    draw_aggregate_cell(axes[-1, 3], output_name, output_result)

    fig.text(
        0.5,
        0.010,
        "Input crisp: L = 0.00, P = 0.57, U = 0.70. Garis vertikal menunjukkan input crisp. Garis putus-putus menunjukkan firing strength.",
        ha="center",
        fontsize=9,
    )

    plt.tight_layout(rect=[0.035, 0.025, 1.0, 0.988])

    output_path = os.path.join(
        OUTPUT_DIR,
        f"G07_rule_inference_27_{output_name}_{CASE_NAME}.png",
    )

    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    return output_path, output_result["crisp"]


def save_rule_table():
    os.makedirs(TABLE_DIR, exist_ok=True)

    output_path = os.path.join(
        TABLE_DIR,
        f"tabel_rule_base_27_{CASE_NAME}.csv",
    )

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(
            [
                "No",
                "Lateral Position",
                "Visual Proximity",
                "Approach Urgency",
                "Risk Score",
                "Speed Factor",
                "Turn Bias",
                "mu_lateral",
                "mu_proximity",
                "mu_urgency",
                "firing_strength",
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
                    rule["risk"],
                    rule["speed"],
                    rule["turn"],
                    round(strength["mu_lateral"], 4),
                    round(strength["mu_proximity"], 4),
                    round(strength["mu_urgency"], 4),
                    round(strength["alpha"], 4),
                ]
            )

    return output_path


def main():
    print("Membuat grafik rule inference dari 27 rule...")

    table_path = save_rule_table()

    output_files = []

    for output_name in ["risk", "speed", "turn"]:
        image_path, crisp_value = plot_rule_viewer(output_name)
        output_files.append((output_name, image_path, crisp_value))

    print("\nTabel rule base 27 rule:")
    print(f"- {table_path}")

    print("\nGrafik rule inference:")
    for output_name, image_path, crisp_value in output_files:
        print(f"- {output_name}: {image_path} | crisp = {crisp_value:.3f}")

    print("\nSelesai.")


if __name__ == "__main__":
    main()