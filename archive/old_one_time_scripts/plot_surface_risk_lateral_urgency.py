from plot_surface_viewer_report import plot_surface


def main():
    output_path = plot_surface(
        file_name="G12_surface_risk_lateral_urgency_medium_proximity.png",
        title="Surface Viewer Risk Score terhadap Lateral Position dan Approach Urgency",
        x_name="lateral",
        y_name="urgency",
        fixed_inputs={
            "lateral": 0.00,
            "proximity": 0.57,
            "urgency": 0.70,
        },
        output_name="risk",
        view_elev=28,
        view_azim=-130,
    )

    print("Surface viewer berhasil dibuat:")
    print(f"- {output_path}")


if __name__ == "__main__":
    main()