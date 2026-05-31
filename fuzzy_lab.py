import os
import csv
import math
from dataclasses import dataclass
from datetime import datetime

import numpy as np
import matplotlib.pyplot as plt


RESULT_DIR = "results"
LAB_DIR = os.path.join(RESULT_DIR, "fuzzy_lab")
RUN_DIR = os.path.join(RESULT_DIR, "lab_runs")


def clip(value, lower, upper):
    return max(lower, min(upper, value))


def trimf(x, a, b, c):
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x, dtype=float)

    idx = (a < x) & (x <= b)
    y[idx] = (x[idx] - a) / (b - a)

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
    denominator = np.sum(mu)
    if denominator <= 1e-12:
        return float(np.mean(x))
    return float(np.sum(x * mu) / denominator)


@dataclass(frozen=True)
class MembershipFunction:
    name: str
    mf_type: str
    parameters: tuple

    def compute(self, x):
        if self.mf_type == "trimf":
            return trimf(x, *self.parameters)
        if self.mf_type == "trapmf":
            return trapmf(x, *self.parameters)
        raise ValueError(f"Tipe membership function tidak dikenal: {self.mf_type}")

    def degree(self, value):
        return float(self.compute(np.array([value], dtype=float))[0])


@dataclass(frozen=True)
class FuzzyVariable:
    name: str
    label: str
    domain: tuple
    membership_functions: tuple

    def universe(self, points=2001):
        return np.linspace(self.domain[0], self.domain[1], points)

    def fuzzify(self, value):
        value = clip(value, self.domain[0], self.domain[1])
        return {mf.name: mf.degree(value) for mf in self.membership_functions}

    def get_mf(self, name):
        for mf in self.membership_functions:
            if mf.name == name:
                return mf
        raise KeyError(f"Membership function {name} tidak ada pada variabel {self.name}")


@dataclass(frozen=True)
class FuzzyRule:
    number: int
    lateral: str
    proximity: str
    urgency: str
    risk: str
    speed: str
    turn: str


INPUT_VARIABLES = {
    "lateral": FuzzyVariable(
        name="lateral",
        label="Lateral Position",
        domain=(-1.0, 1.0),
        membership_functions=(
            MembershipFunction("LEFT", "trapmf", (-1.00, -1.00, -0.60, -0.15)),
            MembershipFunction("CENTER", "trimf", (-0.35, 0.00, 0.35)),
            MembershipFunction("RIGHT", "trapmf", (0.15, 0.60, 1.00, 1.00)),
        ),
    ),
    "proximity": FuzzyVariable(
        name="proximity",
        label="Visual Proximity",
        domain=(0.0, 1.0),
        membership_functions=(
            MembershipFunction("FAR", "trapmf", (0.00, 0.00, 0.25, 0.45)),
            MembershipFunction("MEDIUM", "trimf", (0.30, 0.55, 0.80)),
            MembershipFunction("NEAR", "trapmf", (0.65, 0.82, 1.00, 1.00)),
        ),
    ),
    "urgency": FuzzyVariable(
        name="urgency",
        label="Approach Urgency",
        domain=(0.0, 1.0),
        membership_functions=(
            MembershipFunction("LOW", "trapmf", (0.00, 0.00, 0.25, 0.45)),
            MembershipFunction("MEDIUM", "trimf", (0.30, 0.55, 0.80)),
            MembershipFunction("HIGH", "trapmf", (0.75, 0.90, 1.00, 1.00)),
        ),
    ),
}


OUTPUT_VARIABLES = {
    "risk": FuzzyVariable(
        name="risk",
        label="Risk Score",
        domain=(0.0, 1.0),
        membership_functions=(
            MembershipFunction("LOW", "trapmf", (0.00, 0.00, 0.18, 0.35)),
            MembershipFunction("MEDIUM", "trimf", (0.25, 0.45, 0.65)),
            MembershipFunction("HIGH", "trapmf", (0.62, 0.78, 1.00, 1.00)),
        ),
    ),
    "speed": FuzzyVariable(
        name="speed",
        label="Speed Factor",
        domain=(0.0, 1.0),
        membership_functions=(
            MembershipFunction("STOP", "trapmf", (0.00, 0.00, 0.05, 0.18)),
            MembershipFunction("SLOW", "trimf", (0.12, 0.35, 0.58)),
            MembershipFunction("NORMAL", "trapmf", (0.50, 0.72, 1.00, 1.00)),
        ),
    ),
    "turn": FuzzyVariable(
        name="turn",
        label="Turn Bias",
        domain=(-1.0, 1.0),
        membership_functions=(
            MembershipFunction("LEFT", "trapmf", (-1.00, -1.00, -0.75, -0.22)),
            MembershipFunction("STRAIGHT", "trimf", (-0.30, 0.00, 0.30)),
            MembershipFunction("RIGHT", "trapmf", (0.22, 0.75, 1.00, 1.00)),
        ),
    ),
}


RULES = (
    FuzzyRule(1, "LEFT", "FAR", "LOW", "LOW", "NORMAL", "STRAIGHT"),
    FuzzyRule(2, "LEFT", "MEDIUM", "LOW", "LOW", "NORMAL", "STRAIGHT"),
    FuzzyRule(3, "LEFT", "NEAR", "LOW", "MEDIUM", "SLOW", "RIGHT"),
    FuzzyRule(4, "LEFT", "FAR", "MEDIUM", "LOW", "NORMAL", "STRAIGHT"),
    FuzzyRule(5, "LEFT", "MEDIUM", "MEDIUM", "MEDIUM", "SLOW", "RIGHT"),
    FuzzyRule(6, "LEFT", "NEAR", "MEDIUM", "HIGH", "STOP", "RIGHT"),
    FuzzyRule(7, "LEFT", "FAR", "HIGH", "MEDIUM", "SLOW", "RIGHT"),
    FuzzyRule(8, "LEFT", "MEDIUM", "HIGH", "HIGH", "SLOW", "RIGHT"),
    FuzzyRule(9, "LEFT", "NEAR", "HIGH", "HIGH", "STOP", "RIGHT"),
    FuzzyRule(10, "CENTER", "FAR", "LOW", "LOW", "NORMAL", "STRAIGHT"),
    FuzzyRule(11, "CENTER", "MEDIUM", "LOW", "LOW", "NORMAL", "STRAIGHT"),
    FuzzyRule(12, "CENTER", "NEAR", "LOW", "MEDIUM", "SLOW", "STRAIGHT"),
    FuzzyRule(13, "CENTER", "FAR", "MEDIUM", "LOW", "NORMAL", "STRAIGHT"),
    FuzzyRule(14, "CENTER", "MEDIUM", "MEDIUM", "MEDIUM", "SLOW", "RIGHT"),
    FuzzyRule(15, "CENTER", "NEAR", "MEDIUM", "HIGH", "STOP", "RIGHT"),
    FuzzyRule(16, "CENTER", "FAR", "HIGH", "MEDIUM", "SLOW", "RIGHT"),
    FuzzyRule(17, "CENTER", "MEDIUM", "HIGH", "HIGH", "SLOW", "RIGHT"),
    FuzzyRule(18, "CENTER", "NEAR", "HIGH", "HIGH", "STOP", "RIGHT"),
    FuzzyRule(19, "RIGHT", "FAR", "LOW", "LOW", "NORMAL", "STRAIGHT"),
    FuzzyRule(20, "RIGHT", "MEDIUM", "LOW", "LOW", "NORMAL", "STRAIGHT"),
    FuzzyRule(21, "RIGHT", "NEAR", "LOW", "MEDIUM", "SLOW", "LEFT"),
    FuzzyRule(22, "RIGHT", "FAR", "MEDIUM", "LOW", "NORMAL", "STRAIGHT"),
    FuzzyRule(23, "RIGHT", "MEDIUM", "MEDIUM", "MEDIUM", "SLOW", "LEFT"),
    FuzzyRule(24, "RIGHT", "NEAR", "MEDIUM", "HIGH", "STOP", "LEFT"),
    FuzzyRule(25, "RIGHT", "FAR", "HIGH", "MEDIUM", "SLOW", "LEFT"),
    FuzzyRule(26, "RIGHT", "MEDIUM", "HIGH", "HIGH", "SLOW", "LEFT"),
    FuzzyRule(27, "RIGHT", "NEAR", "HIGH", "HIGH", "STOP", "LEFT"),
)


def ensure_directories():
    os.makedirs(RESULT_DIR, exist_ok=True)
    os.makedirs(LAB_DIR, exist_ok=True)
    os.makedirs(RUN_DIR, exist_ok=True)


def normalize_from_vision(
    x_center,
    bbox_bottom,
    bbox_area_ratio,
    visual_ttc,
    dlog_area,
    in_corridor,
    apply_lateral_correction=True,
):
    x_center = clip(float(x_center), 0.0, 1.0)
    bbox_bottom = clip(float(bbox_bottom), 0.0, 1.0)
    bbox_area_ratio = max(0.0, float(bbox_area_ratio))
    visual_ttc = max(0.0, float(visual_ttc))
    dlog_area = float(dlog_area)
    in_corridor = bool(in_corridor)

    lateral_raw = 2.0 * (x_center - 0.5)

    if apply_lateral_correction and in_corridor:
        lateral = 0.55 * lateral_raw
    else:
        lateral = lateral_raw

    lateral = clip(lateral, -1.0, 1.0)

    area_norm = clip(bbox_area_ratio / 0.45, 0.0, 1.0)
    proximity = clip(0.65 * bbox_bottom + 0.35 * area_norm, 0.0, 1.0)

    if visual_ttc <= 1.5:
        ttc_norm = 1.0
    elif visual_ttc >= 6.0:
        ttc_norm = 0.0
    else:
        ttc_norm = (6.0 - visual_ttc) / 4.5

    dlog_norm = clip(dlog_area / 0.18, 0.0, 1.0)
    corridor_bonus = 0.10 if in_corridor else 0.0
    urgency = clip(0.70 * ttc_norm + 0.30 * dlog_norm + corridor_bonus, 0.0, 1.0)

    return {
        "x_center": x_center,
        "bbox_bottom": bbox_bottom,
        "bbox_area_ratio": bbox_area_ratio,
        "visual_ttc": visual_ttc,
        "dlog_area": dlog_area,
        "in_corridor": in_corridor,
        "lateral_raw": lateral_raw,
        "lateral": lateral,
        "area_norm": area_norm,
        "proximity": proximity,
        "ttc_norm": ttc_norm,
        "dlog_norm": dlog_norm,
        "corridor_bonus": corridor_bonus,
        "urgency": urgency,
    }


def classify_risk(risk_score):
    if risk_score < 0.30:
        return "LOW"
    if risk_score < 0.60:
        return "MEDIUM"
    return "HIGH"


def decide_command(risk_score, speed_factor, turn_bias):
    risk_class = classify_risk(risk_score)

    if risk_class == "HIGH":
        return "STOP"

    if risk_class == "MEDIUM":
        if turn_bias >= 0.20:
            return "TURN_RIGHT_SLOW"
        if turn_bias <= -0.20:
            return "TURN_LEFT_SLOW"
        if speed_factor < 0.60:
            return "SLOW_DOWN"
        return "HOLD_COURSE"

    return "HOLD_COURSE"


def evaluate_fuzzy(lateral, proximity, urgency, universe_points=2001):
    lateral = clip(float(lateral), -1.0, 1.0)
    proximity = clip(float(proximity), 0.0, 1.0)
    urgency = clip(float(urgency), 0.0, 1.0)

    crisp_inputs = {
        "lateral": lateral,
        "proximity": proximity,
        "urgency": urgency,
    }

    input_degrees = {
        "lateral": INPUT_VARIABLES["lateral"].fuzzify(lateral),
        "proximity": INPUT_VARIABLES["proximity"].fuzzify(proximity),
        "urgency": INPUT_VARIABLES["urgency"].fuzzify(urgency),
    }

    output_universe = {
        name: variable.universe(points=universe_points)
        for name, variable in OUTPUT_VARIABLES.items()
    }

    aggregated = {
        "risk": np.zeros_like(output_universe["risk"]),
        "speed": np.zeros_like(output_universe["speed"]),
        "turn": np.zeros_like(output_universe["turn"]),
    }

    active_rules = []

    for rule in RULES:
        mu_lateral = input_degrees["lateral"][rule.lateral]
        mu_proximity = input_degrees["proximity"][rule.proximity]
        mu_urgency = input_degrees["urgency"][rule.urgency]

        alpha = min(mu_lateral, mu_proximity, mu_urgency)

        if alpha <= 1e-12:
            continue

        risk_mf = OUTPUT_VARIABLES["risk"].get_mf(rule.risk)
        speed_mf = OUTPUT_VARIABLES["speed"].get_mf(rule.speed)
        turn_mf = OUTPUT_VARIABLES["turn"].get_mf(rule.turn)

        risk_clip = np.minimum(alpha, risk_mf.compute(output_universe["risk"]))
        speed_clip = np.minimum(alpha, speed_mf.compute(output_universe["speed"]))
        turn_clip = np.minimum(alpha, turn_mf.compute(output_universe["turn"]))

        aggregated["risk"] = np.maximum(aggregated["risk"], risk_clip)
        aggregated["speed"] = np.maximum(aggregated["speed"], speed_clip)
        aggregated["turn"] = np.maximum(aggregated["turn"], turn_clip)

        active_rules.append(
            {
                "rule": rule.number,
                "lateral_set": rule.lateral,
                "proximity_set": rule.proximity,
                "urgency_set": rule.urgency,
                "risk_set": rule.risk,
                "speed_set": rule.speed,
                "turn_set": rule.turn,
                "mu_lateral": mu_lateral,
                "mu_proximity": mu_proximity,
                "mu_urgency": mu_urgency,
                "alpha": alpha,
            }
        )

    risk_score = centroid(output_universe["risk"], aggregated["risk"])
    speed_factor = centroid(output_universe["speed"], aggregated["speed"])
    turn_bias = centroid(output_universe["turn"], aggregated["turn"])

    risk_class = classify_risk(risk_score)
    command = decide_command(risk_score, speed_factor, turn_bias)

    output_degrees = {
        "risk": OUTPUT_VARIABLES["risk"].fuzzify(risk_score),
        "speed": OUTPUT_VARIABLES["speed"].fuzzify(speed_factor),
        "turn": OUTPUT_VARIABLES["turn"].fuzzify(turn_bias),
    }

    return {
        "crisp_inputs": crisp_inputs,
        "input_degrees": input_degrees,
        "active_rules": active_rules,
        "output_universe": output_universe,
        "aggregated": aggregated,
        "outputs": {
            "risk": risk_score,
            "speed": speed_factor,
            "turn": turn_bias,
            "risk_class": risk_class,
            "command": command,
        },
        "output_degrees": output_degrees,
    }


def print_separator():
    print("=" * 72)


def print_result(result):
    inputs = result["crisp_inputs"]
    outputs = result["outputs"]

    print_separator()
    print("HASIL MAMDANI FUZZY LOGIC CONTROLLER")
    print_separator()
    print(f"Lateral Position : {inputs['lateral']:.3f}")
    print(f"Visual Proximity : {inputs['proximity']:.3f}")
    print(f"Approach Urgency : {inputs['urgency']:.3f}")
    print("")
    print(f"Risk Score       : {outputs['risk']:.3f}")
    print(f"Speed Factor     : {outputs['speed']:.3f}")
    print(f"Turn Bias        : {outputs['turn']:.3f}")
    print(f"Risk Class       : {outputs['risk_class']}")
    print(f"Command          : {outputs['command']}")
    print_separator()

    print("")
    print("Fuzzifikasi input:")
    for var_name, degrees in result["input_degrees"].items():
        label = INPUT_VARIABLES[var_name].label
        print(f"{label}:")
        for mf_name, degree in degrees.items():
            print(f"  {mf_name:<10} = {degree:.3f}")

    print("")
    print("Rule aktif:")
    if not result["active_rules"]:
        print("  Tidak ada rule aktif.")
    else:
        header = (
            f"{'Rule':>4}  {'Lateral':<8} {'Prox':<8} {'Urgency':<8} "
            f"{'Risk':<8} {'Speed':<8} {'Turn':<8} {'alpha':>7}"
        )
        print(header)
        print("-" * len(header))
        for row in result["active_rules"]:
            print(
                f"{row['rule']:>4}  "
                f"{row['lateral_set']:<8} "
                f"{row['proximity_set']:<8} "
                f"{row['urgency_set']:<8} "
                f"{row['risk_set']:<8} "
                f"{row['speed_set']:<8} "
                f"{row['turn_set']:<8} "
                f"{row['alpha']:>7.3f}"
            )


def timestamp_name():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_result_package(result, source_data=None, tag="fuzzy_lab"):
    ensure_directories()

    folder = os.path.join(RUN_DIR, f"{timestamp_name()}_{tag}")
    os.makedirs(folder, exist_ok=True)

    input_path = os.path.join(folder, "input_summary.csv")
    rule_path = os.path.join(folder, "active_rules.csv")
    output_path = os.path.join(folder, "output_summary.csv")
    text_path = os.path.join(folder, "result_summary.txt")
    graph_path = os.path.join(folder, "output_aggregation.png")

    with open(input_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["parameter", "value"])
        if source_data:
            for key, value in source_data.items():
                writer.writerow([key, value])
        for key, value in result["crisp_inputs"].items():
            writer.writerow([key, value])

    with open(rule_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "rule",
            "lateral_set",
            "proximity_set",
            "urgency_set",
            "risk_set",
            "speed_set",
            "turn_set",
            "mu_lateral",
            "mu_proximity",
            "mu_urgency",
            "alpha",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in result["active_rules"]:
            writer.writerow(row)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["output", "value"])
        for key, value in result["outputs"].items():
            writer.writerow([key, value])

    with open(text_path, "w", encoding="utf-8") as f:
        f.write("MAMDANI FUZZY LOGIC CONTROLLER - USV SEANO\n")
        f.write("=" * 60 + "\n\n")

        if source_data:
            f.write("Data vision mentah:\n")
            for key, value in source_data.items():
                f.write(f"{key}: {value}\n")
            f.write("\n")

        f.write("Input fuzzy:\n")
        f.write(f"Lateral Position: {result['crisp_inputs']['lateral']:.3f}\n")
        f.write(f"Visual Proximity: {result['crisp_inputs']['proximity']:.3f}\n")
        f.write(f"Approach Urgency: {result['crisp_inputs']['urgency']:.3f}\n\n")

        f.write("Output crisp:\n")
        f.write(f"Risk Score: {result['outputs']['risk']:.3f}\n")
        f.write(f"Speed Factor: {result['outputs']['speed']:.3f}\n")
        f.write(f"Turn Bias: {result['outputs']['turn']:.3f}\n")
        f.write(f"Risk Class: {result['outputs']['risk_class']}\n")
        f.write(f"Command: {result['outputs']['command']}\n\n")

        f.write("Rule aktif:\n")
        for row in result["active_rules"]:
            f.write(
                f"Rule {row['rule']}: "
                f"IF LATERAL is {row['lateral_set']} "
                f"AND PROXIMITY is {row['proximity_set']} "
                f"AND URGENCY is {row['urgency_set']} "
                f"THEN RISK is {row['risk_set']}, "
                f"SPEED is {row['speed_set']}, "
                f"TURN is {row['turn_set']} "
                f"alpha = {row['alpha']:.3f}\n"
            )

    plot_output_aggregation(result, graph_path)

    return {
        "folder": folder,
        "input_summary": input_path,
        "active_rules": rule_path,
        "output_summary": output_path,
        "result_summary": text_path,
        "output_graph": graph_path,
    }


def plot_membership_functions(output_folder=LAB_DIR):
    ensure_directories()
    os.makedirs(output_folder, exist_ok=True)

    saved_files = []

    all_variables = {}
    all_variables.update(INPUT_VARIABLES)
    all_variables.update(OUTPUT_VARIABLES)

    for variable in all_variables.values():
        x = variable.universe(points=2001)

        plt.figure(figsize=(9, 4.8))
        for mf in variable.membership_functions:
            plt.plot(x, mf.compute(x), linewidth=2.0, label=mf.name)

        plt.title(f"Membership Function - {variable.label}", fontsize=14, fontweight="bold")
        plt.xlabel(variable.label)
        plt.ylabel("Derajat keanggotaan")
        plt.ylim(-0.05, 1.10)
        plt.grid(True, alpha=0.35)
        plt.legend(loc="best")
        plt.tight_layout()

        safe_name = variable.name.replace(" ", "_").lower()
        path = os.path.join(output_folder, f"membership_{safe_name}.png")
        plt.savefig(path, dpi=300, bbox_inches="tight")
        plt.close()

        saved_files.append(path)

    return saved_files


def plot_output_aggregation(result, output_path=None):
    ensure_directories()
    if output_path is None:
        output_path = os.path.join(LAB_DIR, f"output_aggregation_{timestamp_name()}.png")

    fig, axes = plt.subplots(3, 1, figsize=(10.5, 12.5))

    plot_order = [
        ("risk", "Risk Score"),
        ("speed", "Speed Factor"),
        ("turn", "Turn Bias"),
    ]

    for ax, (output_name, title) in zip(axes, plot_order):
        variable = OUTPUT_VARIABLES[output_name]
        x = result["output_universe"][output_name]

        for mf in variable.membership_functions:
            ax.plot(x, mf.compute(x), linewidth=1.7, label=mf.name)

        ax.fill_between(x, 0.0, result["aggregated"][output_name], alpha=0.35, label="agregasi")
        crisp_value = result["outputs"][output_name]
        ax.axvline(crisp_value, linestyle="--", linewidth=1.8, label=f"centroid = {crisp_value:.3f}")

        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.set_xlabel(variable.label)
        ax.set_ylabel("Derajat keanggotaan")
        ax.set_ylim(-0.05, 1.10)
        ax.grid(True, alpha=0.35)
        ax.legend(loc="best")

    fig.suptitle("Clipping, Agregasi, dan Defuzzifikasi Mamdani", fontsize=15, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    return output_path


def plot_surface_viewer(
    output_name,
    x_input,
    y_input,
    fixed_inputs,
    mesh_points=41,
    output_folder=LAB_DIR,
):
    ensure_directories()
    os.makedirs(output_folder, exist_ok=True)

    if output_name not in OUTPUT_VARIABLES:
        raise ValueError("output_name harus salah satu dari: risk, speed, turn")

    if x_input not in INPUT_VARIABLES or y_input not in INPUT_VARIABLES:
        raise ValueError("x_input dan y_input harus salah satu dari: lateral, proximity, urgency")

    if x_input == y_input:
        raise ValueError("x_input dan y_input tidak boleh sama")

    x_var = INPUT_VARIABLES[x_input]
    y_var = INPUT_VARIABLES[y_input]
    z_var = OUTPUT_VARIABLES[output_name]

    x = np.linspace(x_var.domain[0], x_var.domain[1], mesh_points)
    y = np.linspace(y_var.domain[0], y_var.domain[1], mesh_points)
    x_grid, y_grid = np.meshgrid(x, y)
    z_grid = np.zeros_like(x_grid)

    for i in range(y_grid.shape[0]):
        for j in range(x_grid.shape[1]):
            inputs = {
                "lateral": fixed_inputs.get("lateral", 0.0),
                "proximity": fixed_inputs.get("proximity", 0.57),
                "urgency": fixed_inputs.get("urgency", 0.70),
            }

            inputs[x_input] = float(x_grid[i, j])
            inputs[y_input] = float(y_grid[i, j])

            result = evaluate_fuzzy(
                lateral=inputs["lateral"],
                proximity=inputs["proximity"],
                urgency=inputs["urgency"],
                universe_points=801,
            )
            z_grid[i, j] = result["outputs"][output_name]

    fig = plt.figure(figsize=(10, 8.5))
    ax = fig.add_subplot(111, projection="3d")

    surface = ax.plot_surface(
        x_grid,
        y_grid,
        z_grid,
        cmap="viridis",
        edgecolor="k",
        linewidth=0.25,
        antialiased=True,
        alpha=0.95,
    )

    ax.set_title(f"Surface Viewer {z_var.label}", fontsize=16, fontweight="bold", pad=18)
    ax.set_xlabel(x_var.label, labelpad=12)
    ax.set_ylabel(y_var.label, labelpad=12)
    ax.set_zlabel(z_var.label, labelpad=12)
    ax.set_zlim(z_var.domain[0], z_var.domain[1])

    fixed_text = []
    for key in ("lateral", "proximity", "urgency"):
        if key not in (x_input, y_input):
            fixed_text.append(f"{INPUT_VARIABLES[key].label} = {fixed_inputs.get(key, 0.0):.2f}")

    if fixed_text:
        fig.text(0.50, 0.03, ", ".join(fixed_text), ha="center", fontsize=11)

    fig.colorbar(surface, shrink=0.65, aspect=14, label=z_var.label)
    ax.view_init(elev=28, azim=-135)
    plt.tight_layout()

    file_name = f"surface_{output_name}_{x_input}_{y_input}_{timestamp_name()}.png"
    path = os.path.join(output_folder, file_name)
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()

    return path


def input_float(prompt, default=None, lower=None, upper=None):
    while True:
        if default is None:
            raw = input(f"{prompt}: ").strip()
        else:
            raw = input(f"{prompt} [{default}]: ").strip()

        if raw == "" and default is not None:
            value = float(default)
        else:
            raw = raw.replace(",", ".")
            try:
                value = float(raw)
            except ValueError:
                print("Input harus berupa angka.")
                continue

        if lower is not None and value < lower:
            print(f"Nilai minimal adalah {lower}.")
            continue

        if upper is not None and value > upper:
            print(f"Nilai maksimal adalah {upper}.")
            continue

        return value


def input_yes_no(prompt, default=True):
    default_text = "Y" if default else "N"

    while True:
        raw = input(f"{prompt} [Y/N, default {default_text}]: ").strip().lower()

        if raw == "":
            return default

        if raw in ("y", "yes", "iya", "1", "true"):
            return True

        if raw in ("n", "no", "tidak", "0", "false"):
            return False

        print("Jawab dengan Y atau N.")


def menu_vision_input():
    print_separator()
    print("INPUT DATA VISION MENTAH")
    print_separator()

    x_center = input_float("x_center, posisi pusat bounding box 0 sampai 1", 0.50, 0.0, 1.0)
    bbox_bottom = input_float("bbox_bottom, posisi bawah bounding box 0 sampai 1", 0.80, 0.0, 1.0)
    bbox_area_ratio = input_float("bbox_area_ratio", 0.23, 0.0, None)
    visual_ttc = input_float("visual_ttc dalam detik", 2.80, 0.0, None)
    dlog_area = input_float("dlog_area", 0.11, None, None)
    in_corridor = input_yes_no("Obstacle berada pada corridor lintasan", True)
    apply_lateral_correction = input_yes_no("Terapkan koreksi lateral corridor Lc = 0.55L", True)

    source = normalize_from_vision(
        x_center=x_center,
        bbox_bottom=bbox_bottom,
        bbox_area_ratio=bbox_area_ratio,
        visual_ttc=visual_ttc,
        dlog_area=dlog_area,
        in_corridor=in_corridor,
        apply_lateral_correction=apply_lateral_correction,
    )

    result = evaluate_fuzzy(
        lateral=source["lateral"],
        proximity=source["proximity"],
        urgency=source["urgency"],
    )

    print_result(result)

    save = input_yes_no("Simpan hasil ke folder results/lab_runs", True)
    if save:
        files = save_result_package(result, source_data=source, tag="vision")
        print("")
        print("File tersimpan:")
        for path in files.values():
            print(f"- {path}")


def menu_fuzzy_input():
    print_separator()
    print("INPUT FUZZY LANGSUNG")
    print_separator()

    lateral = input_float("Lateral Position, -1 sampai 1", 0.00, -1.0, 1.0)
    proximity = input_float("Visual Proximity, 0 sampai 1", 0.70, 0.0, 1.0)
    urgency = input_float("Approach Urgency, 0 sampai 1", 0.78, 0.0, 1.0)

    result = evaluate_fuzzy(lateral=lateral, proximity=proximity, urgency=urgency)
    print_result(result)

    save = input_yes_no("Simpan hasil ke folder results/lab_runs", True)
    if save:
        files = save_result_package(result, source_data=None, tag="fuzzy_input")
        print("")
        print("File tersimpan:")
        for path in files.values():
            print(f"- {path}")


def menu_membership():
    print_separator()
    print("MEMBUAT GRAFIK MEMBERSHIP FUNCTION")
    print_separator()

    saved = plot_membership_functions()
    print("Grafik membership function selesai dibuat:")
    for path in saved:
        print(f"- {path}")


def menu_surface():
    print_separator()
    print("SURFACE VIEWER")
    print_separator()

    print("Output yang tersedia: risk, speed, turn")
    output_name = input("Pilih output [risk]: ").strip().lower() or "risk"

    print("Input yang tersedia: lateral, proximity, urgency")
    x_input = input("Sumbu X [proximity]: ").strip().lower() or "proximity"
    y_input = input("Sumbu Y [urgency]: ").strip().lower() or "urgency"

    fixed = {
        "lateral": 0.00,
        "proximity": 0.57,
        "urgency": 0.70,
    }

    for key in fixed:
        if key not in (x_input, y_input):
            fixed[key] = input_float(
                f"Nilai tetap {INPUT_VARIABLES[key].label}",
                fixed[key],
                INPUT_VARIABLES[key].domain[0],
                INPUT_VARIABLES[key].domain[1],
            )

    mesh_points = int(input_float("Jumlah mesh point", 41, 11, 101))

    try:
        path = plot_surface_viewer(
            output_name=output_name,
            x_input=x_input,
            y_input=y_input,
            fixed_inputs=fixed,
            mesh_points=mesh_points,
        )
        print(f"Surface viewer selesai dibuat: {path}")
    except Exception as exc:
        print(f"Gagal membuat surface viewer: {exc}")


def menu_demo_case():
    print_separator()
    print("DEMO KASUS OBSTACLE DEPAN TRANSISI")
    print_separator()

    source = normalize_from_vision(
        x_center=0.50,
        bbox_bottom=0.80,
        bbox_area_ratio=0.23,
        visual_ttc=2.80,
        dlog_area=0.11,
        in_corridor=True,
        apply_lateral_correction=True,
    )

    result = evaluate_fuzzy(
        lateral=source["lateral"],
        proximity=source["proximity"],
        urgency=source["urgency"],
    )

    print_result(result)
    files = save_result_package(result, source_data=source, tag="demo_obstacle_depan_transisi")

    print("")
    print("File demo tersimpan:")
    for path in files.values():
        print(f"- {path}")


def menu_rule_base():
    print_separator()
    print("RULE BASE 27 ATURAN")
    print_separator()

    header = (
        f"{'No':>2}  {'Lateral':<8} {'Proximity':<9} {'Urgency':<8} "
        f"{'Risk':<7} {'Speed':<7} {'Turn':<8}"
    )
    print(header)
    print("-" * len(header))

    for rule in RULES:
        print(
            f"{rule.number:>2}  "
            f"{rule.lateral:<8} "
            f"{rule.proximity:<9} "
            f"{rule.urgency:<8} "
            f"{rule.risk:<7} "
            f"{rule.speed:<7} "
            f"{rule.turn:<8}"
        )


def main():
    ensure_directories()

    while True:
        print("")
        print_separator()
        print("MAMDANI FUZZY LAB - COLLISION AVOIDANCE USV SEANO")
        print_separator()
        print("1. Hitung dari data vision mentah")
        print("2. Hitung dari input fuzzy langsung")
        print("3. Buat grafik membership function")
        print("4. Buat surface viewer")
        print("5. Jalankan demo obstacle depan transisi")
        print("6. Tampilkan rule base 27 aturan")
        print("0. Keluar")
        print_separator()

        choice = input("Pilih menu: ").strip()

        if choice == "1":
            menu_vision_input()
        elif choice == "2":
            menu_fuzzy_input()
        elif choice == "3":
            menu_membership()
        elif choice == "4":
            menu_surface()
        elif choice == "5":
            menu_demo_case()
        elif choice == "6":
            menu_rule_base()
        elif choice == "0":
            print("Selesai.")
            break
        else:
            print("Pilihan tidak valid.")


if __name__ == "__main__":
    main()