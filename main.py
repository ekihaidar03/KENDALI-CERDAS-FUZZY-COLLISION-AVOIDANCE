import os
import sys
import subprocess
from datetime import datetime


URUTAN_PROGRAM = [
    {
        "file": "fuzzy_controller.py",
        "keterangan": "Cek awal fuzzy controller",
        "wajib_output": [],
    },
    {
        "file": "scenario_generator.py",
        "keterangan": "Membuat data skenario dan log simulasi fuzzy",
        "wajib_output": [
            "results/simulation_log.csv",
            "results/simulation_summary.csv",
        ],
    },
    {
        "file": "baseline_crisp.py",
        "keterangan": "Membuat pembanding baseline crisp terhadap fuzzy controller",
        "wajib_output": [
            "results/baseline_crisp_log.csv",
            "results/baseline_crisp_summary.csv",
        ],
    },
    {
        "file": "usv_simulator.py",
        "keterangan": "Membuat simulasi lintasan sederhana USV",
        "wajib_output": [
            "results/usv_trajectory_log.csv",
            "results/usv_trajectory_summary.csv",
        ],
    },
    {
        "file": "plot_results.py",
        "keterangan": "Membuat grafik dasar hasil simulasi",
        "wajib_output": [
            "results/figures",
        ],
    },
    {
        "file": "plot_results_report.py",
        "keterangan": "Membuat grafik versi laporan",
        "wajib_output": [
            "results/figures_report",
        ],
    },
    {
        "file": "report_tables.py",
        "keterangan": "Membuat tabel CSV dan ringkasan laporan",
        "wajib_output": [
            "results/report_tables/tabel_1_ringkasan_fuzzy_rapih.csv",
            "results/report_tables/tabel_2_ringkasan_lintasan_rapih.csv",
            "results/report_tables/tabel_3_validasi_skenario_rapih.csv",
            "results/report_tables/tabel_laporan_rapih.md",
            "results/report_tables/ringkasan_laporan_rapih.txt",
        ],
    },
    {
        "file": "excel_report_generator.py",
        "keterangan": "Membuat workbook Excel laporan",
        "wajib_output": [
            "results/report_tables/laporan_simulasi_fuzzy_seano.xlsx",
        ],
    },
]


def garis():
    print("=" * 72)


def cek_file_program():
    file_hilang = []

    for item in URUTAN_PROGRAM:
        if not os.path.exists(item["file"]):
            file_hilang.append(item["file"])

    if file_hilang:
        print("\nAda file program yang belum ditemukan:")
        for nama in file_hilang:
            print(f"- {nama}")

        print("\nLengkapi file tersebut dulu sebelum menjalankan main.py.")
        return False

    return True


def cek_output(item):
    output_hilang = []

    for path in item["wajib_output"]:
        if not os.path.exists(path):
            output_hilang.append(path)

    return output_hilang


def jalankan_program(item):
    nama_file = item["file"]
    keterangan = item["keterangan"]

    garis()
    print(f"Menjalankan: {nama_file}")
    print(f"Keterangan : {keterangan}")
    garis()

    command = [sys.executable, nama_file]

    proses = subprocess.run(
        command,
        text=True,
        capture_output=True,
    )

    if proses.stdout:
        print(proses.stdout)

    if proses.stderr:
        print("\nPesan error/warning:")
        print(proses.stderr)

    if proses.returncode != 0:
        print(f"\nGAGAL: {nama_file} berhenti dengan return code {proses.returncode}")
        return False

    output_hilang = cek_output(item)

    if output_hilang:
        print(f"\nPERINGATAN: {nama_file} selesai, tetapi output berikut belum ditemukan:")
        for path in output_hilang:
            print(f"- {path}")
        return False

    print(f"\nOK: {nama_file} selesai.")
    return True


def tulis_run_summary(status_semua):
    os.makedirs("results", exist_ok=True)

    path = "results/run_summary.txt"

    with open(path, "w", encoding="utf-8") as f:
        f.write("RINGKASAN EKSEKUSI PIPELINE FUZZY COLLISION AVOIDANCE\n")
        f.write("=" * 68)
        f.write("\n\n")
        f.write(f"Waktu eksekusi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Python       : {sys.executable}\n")
        f.write("\n")

        for item in status_semua:
            status = "BERHASIL" if item["berhasil"] else "GAGAL"
            f.write(f"- {item['file']} : {status}\n")

        f.write("\nOutput utama yang diharapkan:\n")
        f.write("- results/simulation_log.csv\n")
        f.write("- results/simulation_summary.csv\n")
        f.write("- results/baseline_crisp_log.csv\n")
        f.write("- results/baseline_crisp_summary.csv\n")
        f.write("- results/usv_trajectory_log.csv\n")
        f.write("- results/usv_trajectory_summary.csv\n")
        f.write("- results/figures/\n")
        f.write("- results/figures_report/\n")
        f.write("- results/report_tables/tabel_3_validasi_skenario_rapih.csv\n")
        f.write("- results/report_tables/laporan_simulasi_fuzzy_seano.xlsx\n")

        f.write("\nCatatan:\n")
        f.write(
            "File Excel laporan harus ditutup terlebih dahulu sebelum pipeline dijalankan ulang, "
            "karena Python tidak bisa menimpa file .xlsx yang masih terbuka di Excel.\n"
        )
        f.write(
            "File baseline_crisp.py digunakan sebagai pembanding rule threshold biasa "
            "terhadap fuzzy controller. Baseline ini bukan metode utama.\n"
        )

    return path


def main():
    print("\nPIPELINE SIMULASI FUZZY COLLISION AVOIDANCE USV SEANO")
    print("Pastikan file Excel output sedang tidak terbuka sebelum menjalankan pipeline.\n")

    if not cek_file_program():
        return

    status_semua = []

    for item in URUTAN_PROGRAM:
        berhasil = jalankan_program(item)

        status_semua.append(
            {
                "file": item["file"],
                "berhasil": berhasil,
            }
        )

        if not berhasil:
            print("\nPipeline dihentikan karena ada program yang gagal.")
            path_summary = tulis_run_summary(status_semua)
            print(f"Ringkasan disimpan di: {path_summary}")
            return

    garis()
    print("SEMUA PROGRAM BERHASIL DIJALANKAN.")
    garis()

    path_summary = tulis_run_summary(status_semua)

    print("\nOutput utama:")
    print("- results/simulation_log.csv")
    print("- results/simulation_summary.csv")
    print("- results/baseline_crisp_log.csv")
    print("- results/baseline_crisp_summary.csv")
    print("- results/usv_trajectory_log.csv")
    print("- results/usv_trajectory_summary.csv")
    print("- results/figures/")
    print("- results/figures_report/")
    print("- results/report_tables/tabel_3_validasi_skenario_rapih.csv")
    print("- results/report_tables/laporan_simulasi_fuzzy_seano.xlsx")
    print(f"- {path_summary}")

    print("\nSelesai.")


if __name__ == "__main__":
    main()