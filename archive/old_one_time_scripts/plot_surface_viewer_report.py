import os
import numpy as np
import matplotlib.pyplot as plt


OUTPUT_DIR = "results/figures_report"


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


def mf_curve(x, mf_def):
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
        "label": "Risk Score",
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
        "label": "Speed Factor",
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
        "label": "Turn Bias",
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

    for lateral in ["LEFT", "CENTER", "RIGHT"]:
        for urgency in ["LOW", "MEDIUM", "HIGH"]:
            for proximity in ["FAR", "MEDIUM", "NEAR"]:
                risk, speed, turn = RULE_TABLE[lateral][urgency][proximity]

                rules.append(
                    {
                        "lateral": lateral,
                        "proximity": proximity,
                        "urgency": urgency,
                        "risk": risk,
                        "speed": speed,
                        "turn": turn,
                    }
                )

    return rules


RULES = build_rules()


def calculate_fuzzy_output(lateral_value, proximity_value, urgency_value, output_name):
    output_def = OUTPUT_MF[output_name]
    x_out = np.linspace(output_def["range"][0], output_def["range"][1], 1000)
    aggregate = np.zeros_like(x_out)

    for rule in RULES:
        mu_lateral = eval_mf(
            lateral_value,
            INPUT_MF["lateral"]["sets"][rule["lateral"]],
        )

        mu_proximity = eval_mf(
            proximity_value,
            INPUT_MF["proximity"]["sets"][rule["proximity"]],
        )

        mu_urgency = eval_mf(
            urgency_value,
            INPUT_MF["urgency"]["sets"][rule["urgency"]],
        )

        alpha = min(mu_lateral, mu_proximity, mu_urgency)

        output_set = rule[output_name]
        output_curve = mf_curve(x_out, output_def["sets"][output_set])
        clipped_output = np.minimum(alpha, output_curve)

        aggregate = np.maximum(aggregate, clipped_output)

    return centroid(x_out, aggregate)


def make_surface_xy(
    x_name,
    y_name,
    fixed_inputs,
    output_name,
    mesh_points=31,
):
    x_min, x_max = INPUT_MF[x_name]["range"]
    y_min, y_max = INPUT_MF[y_name]["range"]

    x_vals = np.linspace(x_min, x_max, mesh_points)
    y_vals = np.linspace(y_min, y_max, mesh_points)

    X, Y = np.meshgrid(x_vals, y_vals)
    Z = np.zeros_like(X, dtype=float)

    for i in range(Y.shape[0]):
        for j in range(X.shape[1]):
            inputs = {
                "lateral": fixed_inputs.get("lateral", 0.0),
                "proximity": fixed_inputs.get("proximity", 0.57),
                "urgency": fixed_inputs.get("urgency", 0.70),
            }

            inputs[x_name] = X[i, j]
            inputs[y_name] = Y[i, j]

            Z[i, j] = calculate_fuzzy_output(
                lateral_value=inputs["lateral"],
                proximity_value=inputs["proximity"],
                urgency_value=inputs["urgency"],
                output_name=output_name,
            )

    return X, Y, Z


def axis_label(name):
    labels = {
        "lateral": "Lateral Position",
        "proximity": "Visual Proximity",
        "urgency": "Approach Urgency",
    }
    return labels[name]


def fixed_text(fixed_inputs, x_name, y_name):
    parts = []

    for key in ["lateral", "proximity", "urgency"]:
        if key not in [x_name, y_name]:
            parts.append(f"{axis_label(key)} = {fixed_inputs.get(key, 0.0):.2f}")

    return ", ".join(parts)


def plot_surface(
    file_name,
    title,
    x_name,
    y_name,
    fixed_inputs,
    output_name,
    view_elev=28,
    view_azim=-135,
):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    X, Y, Z = make_surface_xy(
        x_name=x_name,
        y_name=y_name,
        fixed_inputs=fixed_inputs,
        output_name=output_name,
        mesh_points=31,
    )

    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_subplot(111, projection="3d")

    surface = ax.plot_surface(
        X,
        Y,
        Z,
        cmap="viridis",
        edgecolor="black",
        linewidth=0.35,
        antialiased=True,
        alpha=0.95,
    )

    ax.set_title(title, fontsize=16, fontweight="bold", pad=18)
    ax.set_xlabel(axis_label(x_name), fontsize=11, labelpad=10)
    ax.set_ylabel(axis_label(y_name), fontsize=11, labelpad=10)
    ax.set_zlabel(OUTPUT_MF[output_name]["label"], fontsize=11, labelpad=10)

    ax.view_init(elev=view_elev, azim=view_azim)

    x_min, x_max = INPUT_MF[x_name]["range"]
    y_min, y_max = INPUT_MF[y_name]["range"]
    z_min, z_max = OUTPUT_MF[output_name]["range"]

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_zlim(z_min, z_max)

    ax.grid(True)

    fig.colorbar(
        surface,
        ax=ax,
        shrink=0.65,
        pad=0.10,
        label=OUTPUT_MF[output_name]["label"],
    )

    fig.text(
        0.5,
        0.03,
        fixed_text(fixed_inputs, x_name, y_name),
        ha="center",
        fontsize=10,
    )

    output_path = os.path.join(OUTPUT_DIR, file_name)
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    return output_path


def main():
    print("Membuat surface viewer 3D Mamdani Fuzzy Controller...")

    generated_files = []

    generated_files.append(
        plot_surface(
            file_name="G08_surface_risk_proximity_urgency_center.png",
            title="Surface Viewer Risk Score",
            x_name="proximity",
            y_name="urgency",
            fixed_inputs={
                "lateral": 0.00,
                "proximity": 0.57,
                "urgency": 0.70,
            },
            output_name="risk",
        )
    )

    generated_files.append(
        plot_surface(
            file_name="G09_surface_speed_proximity_urgency_center.png",
            title="Surface Viewer Speed Factor",
            x_name="proximity",
            y_name="urgency",
            fixed_inputs={
                "lateral": 0.00,
                "proximity": 0.57,
                "urgency": 0.70,
            },
            output_name="speed",
        )
    )

    generated_files.append(
        plot_surface(
            file_name="G10_surface_turn_lateral_proximity_medium_urgency.png",
            title="Surface Viewer Turn Bias",
            x_name="lateral",
            y_name="proximity",
            fixed_inputs={
                "lateral": 0.00,
                "proximity": 0.57,
                "urgency": 0.70,
            },
            output_name="turn",
            view_elev=28,
            view_azim=-130,
        )
    )

    generated_files.append(
        plot_surface(
            file_name="G11_surface_risk_lateral_proximity_medium_urgency.png",
            title="Surface Viewer Risk Score terhadap Lateral dan Proximity",
            x_name="lateral",
            y_name="proximity",
            fixed_inputs={
                "lateral": 0.00,
                "proximity": 0.57,
                "urgency": 0.70,
            },
            output_name="risk",
            view_elev=28,
            view_azim=-130,
        )
    )

    print("\nSurface viewer berhasil dibuat:")
    for path in generated_files:
        print(f"- {path}")


if __name__ == "__main__":
    main()