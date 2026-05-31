import os
import ast

import pandas as pd


REPORT_DIR = "results/report_tables"

COMMAND_COLUMNS = [
    "HOLD_COURSE",
    "SLOW_DOWN",
    "TURN_LEFT_SLOW",
    "TURN_RIGHT_SLOW",
    "STOP",
]

RISK_COLUMNS = [
    "LOW",
    "MEDIUM",
    "HIGH",
]


def buat_folder():
    os.makedirs(REPORT_DIR, exist_ok=True)


def parse_dict(teks):
    if pd.isna(teks):
        return {}

    if isinstance(teks, dict):
        return teks

    try:
        hasil = ast.literal_eval(str(teks))
        if isinstance(hasil, dict):
            return hasil
    except (ValueError, SyntaxError):
        pass

    return {}


def nama_skenario_rapih(nama):
    mapping = {
        "frontal_static_obstacle": "Obstacle frontal statis",
        "crossing_left_to_right": "Crossing kiri ke kanan",
        "crossing_right_to_left": "Crossing kanan ke kiri",
        "side_safe_obstacle": "Obstacle samping aman",
        "no_obstacle": "Tanpa obstacle",
    }

    return mapping.get(nama, nama)


def angka_laporan(nilai, digit=3):
    if pd.isna(nilai):
        return "-"

    teks = f"{float(nilai):.{digit}f}"

    # Format ini lebih nyaman untuk laporan Indonesia dan Excel regional Indonesia.
    return teks.replace(".", ",")


def ambil_count(data_dict, key):
    nilai = data_dict.get(key, 0)

    try:
        return int(nilai)
    except (TypeError, ValueError):
        return 0


def status_validasi(row):
    nama = row["scenario"]
    command_count = parse_dict(row.get("command_count", "{}"))

    risk_max = float(row.get("risk_max", 0.0))
    min_distance = row.get("min_distance_to_obstacle_m", None)

    if nama == "no_obstacle":
        if ambil_count(command_count, "HOLD_COURSE") > 0:
            return "Valid - sistem mempertahankan HOLD_COURSE"
        return "Perlu evaluasi - command berubah saat tidak ada obstacle"

    if nama == "side_safe_obstacle":
        if risk_max < 0.30 and ambil_count(command_count, "HOLD_COURSE") > 0:
            return "Valid - obstacle samping tidak memicu avoidance"
        return "Perlu evaluasi - obstacle samping memicu avoidance"

    if nama == "frontal_static_obstacle":
        if ambil_count(command_count, "STOP") > 0:
            return "Valid - sistem melakukan STOP pada obstacle frontal"
        return "Perlu evaluasi - obstacle frontal belum menghasilkan STOP"

    if nama in ["crossing_left_to_right", "crossing_right_to_left"]:
        if pd.notna(min_distance) and float(min_distance) > 0.30 and risk_max < 0.60:
            return "Valid simulatif - crossing terdeteksi sebagai risiko MEDIUM"
        return "Perlu evaluasi - jarak simulatif crossing terlalu kecil"

    return "Belum diklasifikasikan"


def catatan_analisis(row):
    nama = row["scenario"]

    if nama == "crossing_left_to_right":
        return (
            "Skenario crossing paling kritis; fuzzy controller menurunkan kecepatan "
            "dan menjaga risk pada kelas MEDIUM."
        )

    if nama == "crossing_right_to_left":
        return (
            "Obstacle crossing tetap berada pada kelas MEDIUM dan tidak mencapai "
            "kondisi STOP."
        )

    if nama == "frontal_static_obstacle":
        return (
            "Obstacle frontal menghasilkan risk HIGH dan command STOP, sesuai "
            "respons konservatif collision avoidance."
        )

    if nama == "side_safe_obstacle":
        return (
            "Obstacle berada di sisi luar corridor sehingga sistem tetap "
            "HOLD_COURSE."
        )

    if nama == "no_obstacle":
        return (
            "Tidak ada obstacle; sistem mempertahankan lintasan tanpa pergantian "
            "command."
        )

    return "-"


def simpan_csv_excel(df, nama_file):
    path = os.path.join(REPORT_DIR, nama_file)

    # sep=';' dipakai agar Excel regional Indonesia membuka kolom dengan rapi.
    df.to_csv(path, index=False, sep=";", encoding="utf-8-sig")

    return path


def buat_tabel_ringkasan_fuzzy():
    path = "results/simulation_summary.csv"

    if not os.path.exists(path):
        raise FileNotFoundError(
            "File results/simulation_summary.csv belum ada. "
            "Jalankan dulu: python scenario_generator.py"
        )

    df = pd.read_csv(path)

    rows = []

    for idx, row in df.iterrows():
        command_count = parse_dict(row.get("command_count", "{}"))
        risk_count = parse_dict(row.get("risk_class_count", "{}"))

        data = {
            "No": idx + 1,
            "Skenario": nama_skenario_rapih(row["scenario"]),
            "Jumlah data": int(row["jumlah_data"]),
            "Risk minimum": angka_laporan(row["risk_min"]),
            "Risk maksimum": angka_laporan(row["risk_max"]),
            "Risk rata-rata": angka_laporan(row["risk_mean"]),
            "Speed rata-rata": angka_laporan(row["speed_mean"]),
        }

        for command in COMMAND_COLUMNS:
            data[f"Jumlah {command}"] = ambil_count(command_count, command)

        for risk in RISK_COLUMNS:
            data[f"Jumlah {risk}"] = ambil_count(risk_count, risk)

        rows.append(data)

    tabel = pd.DataFrame(rows)

    simpan_csv_excel(tabel, "tabel_1_ringkasan_fuzzy_rapih.csv")

    return tabel


def buat_tabel_ringkasan_lintasan():
    path = "results/usv_trajectory_summary.csv"

    if not os.path.exists(path):
        raise FileNotFoundError(
            "File results/usv_trajectory_summary.csv belum ada. "
            "Jalankan dulu: python usv_simulator.py"
        )

    df = pd.read_csv(path)

    rows = []

    for idx, row in df.iterrows():
        rows.append(
            {
                "No": idx + 1,
                "Skenario": nama_skenario_rapih(row["scenario"]),
                "Posisi akhir X (m)": angka_laporan(row["final_x_m"]),
                "Posisi akhir Y (m)": angka_laporan(row["final_y_m"]),
                "Deviasi lateral maksimum (m)": angka_laporan(row["max_abs_cross_track_m"]),
                "Kecepatan rata-rata (m/s)": angka_laporan(row["mean_speed_mps"]),
                "Kecepatan minimum (m/s)": angka_laporan(row["min_speed_mps"]),
                "Jarak minimum simulatif (m)": angka_laporan(row["min_distance_to_obstacle_m"]),
                "Jumlah pergantian command": int(row["command_switch_count"]),
            }
        )

    tabel = pd.DataFrame(rows)

    simpan_csv_excel(tabel, "tabel_2_ringkasan_lintasan_rapih.csv")

    return tabel


def buat_tabel_validasi_skenario():
    path_fuzzy = "results/simulation_summary.csv"
    path_lintasan = "results/usv_trajectory_summary.csv"

    if not os.path.exists(path_fuzzy):
        raise FileNotFoundError(
            "File results/simulation_summary.csv belum ada. "
            "Jalankan dulu: python scenario_generator.py"
        )

    if not os.path.exists(path_lintasan):
        raise FileNotFoundError(
            "File results/usv_trajectory_summary.csv belum ada. "
            "Jalankan dulu: python usv_simulator.py"
        )

    fuzzy = pd.read_csv(path_fuzzy)
    lintasan = pd.read_csv(path_lintasan)

    df = fuzzy.merge(lintasan, on="scenario", how="left")

    rows = []

    for idx, row in df.iterrows():
        command_count = parse_dict(row.get("command_count", "{}"))
        risk_count = parse_dict(row.get("risk_class_count", "{}"))

        rows.append(
            {
                "No": idx + 1,
                "Skenario": nama_skenario_rapih(row["scenario"]),
                "Risk maksimum": angka_laporan(row["risk_max"]),
                "Jumlah LOW": ambil_count(risk_count, "LOW"),
                "Jumlah MEDIUM": ambil_count(risk_count, "MEDIUM"),
                "Jumlah HIGH": ambil_count(risk_count, "HIGH"),
                "HOLD_COURSE": ambil_count(command_count, "HOLD_COURSE"),
                "SLOW_DOWN": ambil_count(command_count, "SLOW_DOWN"),
                "TURN_LEFT_SLOW": ambil_count(command_count, "TURN_LEFT_SLOW"),
                "TURN_RIGHT_SLOW": ambil_count(command_count, "TURN_RIGHT_SLOW"),
                "STOP": ambil_count(command_count, "STOP"),
                "Jarak minimum simulatif (m)": angka_laporan(
                    row.get("min_distance_to_obstacle_m", None)
                ),
                "Status validasi simulasi": status_validasi(row),
                "Catatan analisis": catatan_analisis(row),
            }
        )

    tabel = pd.DataFrame(rows)

    simpan_csv_excel(tabel, "tabel_3_validasi_skenario_rapih.csv")

    return tabel


def dataframe_to_markdown(df):
    kolom = list(df.columns)

    lines = []
    lines.append("| " + " | ".join(kolom) + " |")
    lines.append("| " + " | ".join(["---"] * len(kolom)) + " |")

    for _, row in df.iterrows():
        isi = []
        for kol in kolom:
            nilai = str(row[kol]).replace("\n", " ").replace("|", "/")
            isi.append(nilai)
        lines.append("| " + " | ".join(isi) + " |")

    return "\n".join(lines)


def simpan_markdown(tabel1, tabel2, tabel3):
    path = os.path.join(REPORT_DIR, "tabel_laporan_rapih.md")

    with open(path, "w", encoding="utf-8") as f:
        f.write("# Tabel Hasil Simulasi Fuzzy Collision Avoidance\n\n")

        f.write("## Tabel 1. Ringkasan Output Fuzzy Controller\n\n")
        f.write(dataframe_to_markdown(tabel1))
        f.write("\n\n")

        f.write("## Tabel 2. Ringkasan Simulasi Lintasan USV\n\n")
        f.write(dataframe_to_markdown(tabel2))
        f.write("\n\n")

        f.write("## Tabel 3. Validasi Skenario Simulasi\n\n")
        f.write(dataframe_to_markdown(tabel3))
        f.write("\n\n")

        f.write(
            "Catatan: jarak minimum pada tabel merupakan jarak simulatif berdasarkan "
            "model kinematik sederhana. Nilai tersebut belum dapat dianggap sebagai "
            "validasi keselamatan fisik final pada platform USV nyata.\n"
        )


def simpan_ringkasan_txt(tabel3):
    path = os.path.join(REPORT_DIR, "ringkasan_laporan_rapih.txt")

    with open(path, "w", encoding="utf-8") as f:
        f.write("RINGKASAN HASIL SIMULASI FUZZY COLLISION AVOIDANCE\n")
        f.write("=" * 62)
        f.write("\n\n")

        for _, row in tabel3.iterrows():
            f.write(f"{row['No']}. {row['Skenario']}\n")
            f.write(f"   Risk maksimum                : {row['Risk maksimum']}\n")
            f.write(f"   Jarak minimum simulatif      : {row['Jarak minimum simulatif (m)']} m\n")
            f.write(f"   Status                       : {row['Status validasi simulasi']}\n")
            f.write(f"   Catatan                      : {row['Catatan analisis']}\n")
            f.write("\n")

        f.write(
            "Catatan engineering: hasil ini digunakan sebagai validasi awal berbasis "
            "simulasi. Validasi keselamatan fisik final tetap memerlukan uji langsung "
            "pada USV SEANO.\n"
        )


def main():
    buat_folder()

    tabel1 = buat_tabel_ringkasan_fuzzy()
    tabel2 = buat_tabel_ringkasan_lintasan()
    tabel3 = buat_tabel_validasi_skenario()

    simpan_markdown(tabel1, tabel2, tabel3)
    simpan_ringkasan_txt(tabel3)

    print("\nTabel laporan versi rapi selesai dibuat.")
    print(f"Folder output: {REPORT_DIR}")
    print("- tabel_1_ringkasan_fuzzy_rapih.csv")
    print("- tabel_2_ringkasan_lintasan_rapih.csv")
    print("- tabel_3_validasi_skenario_rapih.csv")
    print("- tabel_laporan_rapih.md")
    print("- ringkasan_laporan_rapih.txt")

    print("\nPreview tabel validasi:")
    print(tabel3.to_string(index=False))


if __name__ == "__main__":
    main()