# Simulasi Mamdani Fuzzy Logic Controller untuk Collision Avoidance USV SEANO

Project ini berisi rancangan dan simulasi **Mamdani Fuzzy Logic Controller** untuk sistem **collision avoidance berbasis kamera** pada USV SEANO. Program ini dibuat sebagai bagian dari tugas Kendali Cerdas dengan tema Tugas Akhir:

**Implementasi Sistem Collision Avoidance dengan Pendekatan Artificial Intelligence untuk Meningkatkan Keselamatan Navigasi pada USV SEANO**

Metode yang digunakan adalah **Fuzzy Logic Controller tipe Mamdani**. Sistem menerima parameter visual obstacle seperti posisi lateral, kedekatan visual, dan urgensi pendekatan. Parameter tersebut diproses melalui fuzzifikasi, rule base, inferensi Mamdani, dan defuzzifikasi centroid untuk menghasilkan keputusan manuver berupa `HOLD_COURSE`, `SLOW_DOWN`, `TURN_LEFT_SLOW`, `TURN_RIGHT_SLOW`, atau `STOP`.

---

## 1. Tujuan Project

Tujuan project ini adalah membuat simulasi awal sistem collision avoidance berbasis fuzzy untuk mengevaluasi hubungan antara parameter visual kamera dan keputusan kendali USV.

Secara khusus, project ini digunakan untuk:

1. Merancang Fuzzy Logic Controller berbasis parameter visual.
2. Membuat skenario obstacle sintetik yang menyerupai kondisi navigasi USV.
3. Membandingkan hasil fuzzy dengan baseline crisp rule.
4. Menyimulasikan lintasan sederhana USV berdasarkan output fuzzy.
5. Menghasilkan grafik, CSV, dan workbook Excel yang siap digunakan untuk laporan teknik.

---

## 2. Batasan Engineering

Project ini adalah **validasi awal berbasis simulasi kinematik**, bukan validasi keselamatan fisik final.

Nilai jarak minimum, lintasan, dan command pada simulasi dihitung dari model sederhana di Python. Oleh karena itu, hasil ini belum boleh diklaim sebagai bukti keselamatan fisik final pada USV nyata.

Validasi fisik final tetap memerlukan pengujian langsung pada USV SEANO dengan log runtime, video pengujian, observasi operator, dan data kondisi aktual di lapangan.

---

## 3. Struktur Program

```text
collision_avoidance_mamdani_fuzzy/
├── fuzzy_controller.py
├── scenario_generator.py
├── baseline_crisp.py
├── usv_simulator.py
├── plot_results.py
├── plot_results_report.py
├── report_tables.py
├── excel_report_generator.py
├── main.py
├── requirements.txt
├── README.md
└── results/
```

Penjelasan file:

| File                        | Fungsi                                                 |
| --------------------------- | ------------------------------------------------------ |
| `fuzzy_controller.py`       | Implementasi Mamdani Fuzzy Logic Controller.           |
| `scenario_generator.py`     | Membuat data skenario obstacle dan log simulasi fuzzy. |
| `baseline_crisp.py`         | Membuat pembanding berbasis rule threshold/crisp.      |
| `usv_simulator.py`          | Membuat simulasi lintasan sederhana USV.               |
| `plot_results.py`           | Membuat grafik dasar hasil simulasi.                   |
| `plot_results_report.py`    | Membuat grafik versi laporan dengan format lebih rapi. |
| `report_tables.py`          | Membuat tabel CSV dan ringkasan laporan.               |
| `excel_report_generator.py` | Membuat workbook Excel laporan.                        |
| `main.py`                   | Menjalankan seluruh pipeline secara otomatis.          |

---

## 4. Input Fuzzy Controller

Fuzzy controller menggunakan tiga input utama:

### 4.1 Posisi Lateral Obstacle

Input ini menunjukkan posisi obstacle terhadap frame kamera.

| Nilai | Makna                                |
| ----- | ------------------------------------ |
| -1    | Obstacle berada di kiri frame        |
| 0     | Obstacle berada di tengah / corridor |
| +1    | Obstacle berada di kanan frame       |

Membership function:

* `kiri`
* `tengah`
* `kanan`

### 4.2 Kedekatan Visual

Input ini menunjukkan indikasi kedekatan obstacle secara visual berdasarkan posisi bawah bounding box dan area bounding box.

Membership function:

* `jauh`
* `sedang`
* `dekat`

Catatan: nilai ini bukan jarak meter absolut. Kamera monocular tidak mengukur jarak fisik secara langsung.

### 4.3 Urgensi Pendekatan

Input ini menunjukkan seberapa cepat obstacle terlihat mendekat berdasarkan visual TTC dan pertumbuhan ukuran bounding box.

Membership function:

* `rendah`
* `sedang`
* `tinggi`

---

## 5. Output Fuzzy Controller

Fuzzy controller menghasilkan tiga bentuk output utama:

| Output  | Makna                                  |
| ------- | -------------------------------------- |
| `speed` | Faktor kecepatan USV, 0 sampai 1       |
| `turn`  | Bias belok, -1 kiri, 0 lurus, +1 kanan |
| `risk`  | Skor risiko kontinu, 0 sampai 1        |

Output kemudian diklasifikasikan menjadi:

| Risk class |            Rentang | Command                   |
| ---------- | -----------------: | ------------------------- |
| LOW        |        risk < 0,30 | `HOLD_COURSE`             |
| MEDIUM     | 0,30 ≤ risk < 0,60 | `SLOW_DOWN` / `TURN_SLOW` |
| HIGH       |        risk ≥ 0,60 | `STOP`                    |

---

## 6. Skenario Simulasi

Project ini menggunakan lima skenario utama:

| Skenario                  | Tujuan                                              |
| ------------------------- | --------------------------------------------------- |
| `no_obstacle`             | Menguji kondisi tanpa obstacle.                     |
| `side_safe_obstacle`      | Menguji obstacle samping yang tidak masuk corridor. |
| `frontal_static_obstacle` | Menguji obstacle frontal yang berisiko tinggi.      |
| `crossing_left_to_right`  | Menguji obstacle crossing dari kiri ke kanan.       |
| `crossing_right_to_left`  | Menguji obstacle crossing dari kanan ke kiri.       |

---

## 7. Cara Instalasi

Disarankan menjalankan project ini di virtual environment.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Jika aktivasi virtual environment diblokir PowerShell, jalankan:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

---

## 8. Cara Menjalankan Program

Untuk menjalankan seluruh pipeline:

```powershell
python main.py
```

Sebelum menjalankan ulang pipeline, pastikan file Excel berikut sedang tidak terbuka:

```text
results/report_tables/laporan_simulasi_fuzzy_seano.xlsx
```

Jika file Excel masih terbuka, Python tidak dapat menimpa file tersebut.

---

## 9. Output Program

Setelah `main.py` berhasil dijalankan, output utama berada pada folder `results/`.

### 9.1 Output Data

| File                                 | Isi                                     |
| ------------------------------------ | --------------------------------------- |
| `results/simulation_log.csv`         | Log lengkap hasil fuzzy controller.     |
| `results/simulation_summary.csv`     | Ringkasan hasil fuzzy per skenario.     |
| `results/baseline_crisp_log.csv`     | Log pembanding baseline crisp.          |
| `results/baseline_crisp_summary.csv` | Ringkasan perbandingan fuzzy dan crisp. |
| `results/usv_trajectory_log.csv`     | Log simulasi lintasan USV.              |
| `results/usv_trajectory_summary.csv` | Ringkasan simulasi lintasan USV.        |
| `results/run_summary.txt`            | Ringkasan eksekusi pipeline.            |

### 9.2 Output Grafik

Grafik dasar:

```text
results/figures/
```

Grafik versi laporan:

```text
results/figures_report/
```

Grafik yang direkomendasikan untuk laporan:

| File                                         | Fungsi                                    |
| -------------------------------------------- | ----------------------------------------- |
| `G02_membership_visual_proximity.png`        | Fungsi keanggotaan kedekatan visual.      |
| `G03_membership_approach_urgency.png`        | Fungsi keanggotaan urgensi pendekatan.    |
| `G10_risk_frontal_static_obstacle.png`       | Risk score pada obstacle frontal.         |
| `G30_command_frontal_static_obstacle.png`    | Command decision pada obstacle frontal.   |
| `G40_trajectory_frontal_static_obstacle.png` | Lintasan USV pada obstacle frontal.       |
| `G40_trajectory_crossing_left_to_right.png`  | Lintasan USV pada crossing kiri ke kanan. |
| `G60_surface_risk_center_obstacle.png`       | Surface risk fuzzy untuk obstacle tengah. |

### 9.3 Output Tabel Laporan

```text
results/report_tables/
```

File penting:

| File                                   | Fungsi                               |
| -------------------------------------- | ------------------------------------ |
| `tabel_1_ringkasan_fuzzy_rapih.csv`    | Tabel ringkasan fuzzy.               |
| `tabel_2_ringkasan_lintasan_rapih.csv` | Tabel ringkasan lintasan.            |
| `tabel_3_validasi_skenario_rapih.csv`  | Tabel validasi skenario.             |
| `tabel_laporan_rapih.md`               | Tabel laporan dalam format Markdown. |
| `ringkasan_laporan_rapih.txt`          | Ringkasan naratif hasil simulasi.    |
| `laporan_simulasi_fuzzy_seano.xlsx`    | Workbook Excel laporan.              |

---

## 10. Hasil Utama Simulasi

Hasil simulasi menunjukkan bahwa fuzzy controller dapat membedakan kondisi aman, crossing, dan obstacle frontal.

Ringkasan interpretasi:

1. Pada skenario tanpa obstacle, sistem mempertahankan `HOLD_COURSE`.
2. Pada obstacle samping aman, sistem tetap `HOLD_COURSE` karena obstacle tidak masuk corridor.
3. Pada obstacle frontal statis, sistem meningkatkan risk hingga kelas `HIGH` dan menghasilkan command `STOP`.
4. Pada skenario crossing, sistem menghasilkan respons kelas `MEDIUM` tanpa langsung masuk `STOP`.
5. Skenario crossing kiri ke kanan menjadi kondisi paling kritis dalam simulasi, sehingga perlu diberi perhatian pada pengembangan atau validasi berikutnya.

---

## 11. Baseline Crisp

Project ini menyertakan `baseline_crisp.py` sebagai pembanding.

Baseline crisp menggunakan rule threshold sederhana untuk menghasilkan risk class dan command. Pembanding ini digunakan untuk menunjukkan perbedaan antara pendekatan crisp dan fuzzy.

Fuzzy controller tetap menjadi metode utama, sedangkan baseline crisp hanya digunakan sebagai referensi pembanding.

---

## 12. Catatan untuk Laporan

Kalimat yang aman digunakan dalam laporan:

> Simulasi ini digunakan sebagai validasi awal terhadap rancangan Mamdani Fuzzy Logic Controller sebelum implementasi pada sistem fisik. Hasil simulasi menunjukkan bahwa sistem mampu membedakan kondisi aman, crossing, dan frontal obstacle melalui perubahan risk class dan command. Namun, karena model yang digunakan masih berupa model kinematik sederhana, hasil ini belum dapat dianggap sebagai validasi keselamatan fisik final.

Kalimat yang tidak disarankan:

> Sistem ini telah terbukti aman secara fisik berdasarkan simulasi.

Kalimat tersebut terlalu kuat dan tidak tepat karena belum ada pengujian fisik langsung pada USV nyata.

---

## 13. Catatan Git

File yang sebaiknya tidak ikut di-push:

```text
.venv/
__pycache__/
*.pyc
~$*.xlsx
```

Folder `results/` boleh di-push jika hasil simulasi perlu disertakan sebagai bukti. Jika repository ingin lebih ringan, simpan hanya grafik dan tabel final yang diperlukan.

---

## 14. Status Project

Status saat ini:

* Fuzzy controller selesai.
* Scenario generator selesai.
* Baseline crisp selesai.
* Simulasi lintasan selesai.
* Grafik laporan selesai.
* Tabel laporan selesai.
* Workbook Excel laporan selesai.
* Pipeline otomatis `main.py` selesai.

Project siap digunakan sebagai dasar laporan teknik Kendali Cerdas.
