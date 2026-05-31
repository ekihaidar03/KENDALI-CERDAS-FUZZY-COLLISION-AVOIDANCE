# Simulasi Mamdani Fuzzy Logic Controller untuk Collision Avoidance USV SEANO

Repository ini berisi rancangan dan simulasi Mamdani Fuzzy Logic Controller untuk sistem collision avoidance berbasis kamera pada USV SEANO. Program dibuat sebagai bagian dari tugas Kendali Cerdas dengan tema Tugas Akhir:

**Implementasi Sistem Collision Avoidance dengan Pendekatan Artificial Intelligence untuk Meningkatkan Keselamatan Navigasi pada USV SEANO**

Sistem ini dirancang sebagai alat simulasi dan analisis fuzzy berbasis Python. Program dapat digunakan untuk menghitung respons collision avoidance dari data visual obstacle, menampilkan proses fuzzifikasi, menjalankan rule base Mamdani, melakukan defuzzifikasi centroid, serta menghasilkan grafik dan tabel hasil simulasi.

## 1. Tujuan Program

Program ini dibuat untuk menggantikan kebutuhan dasar MATLAB Fuzzy Logic Toolbox dalam konteks tugas Kendali Cerdas. Fokus utama program adalah simulasi Mamdani Fuzzy Logic Controller untuk mendukung pengambilan keputusan collision avoidance pada USV berbasis kamera.

Fungsi utama program meliputi:

1. Mengolah data visual obstacle menjadi input fuzzy.
2. Menghitung derajat keanggotaan input.
3. Menjalankan rule base Mamdani sebanyak 27 aturan.
4. Menghasilkan output fuzzy berupa risk score, speed factor, dan turn bias.
5. Melakukan defuzzifikasi dengan metode centroid.
6. Menentukan risk class dan command akhir.
7. Menghasilkan grafik membership function, surface viewer, grafik clipping, tabel CSV, dan workbook Excel laporan.

## 2. Metode yang Digunakan

Metode soft computing yang digunakan adalah **Mamdani Fuzzy Logic Controller**. Metode ini dipilih karena mampu merepresentasikan keputusan berbasis aturan linguistik, sehingga cocok untuk sistem collision avoidance yang memiliki kondisi tidak pasti akibat penggunaan kamera sebagai sensor utama.

Tahapan inferensi fuzzy yang digunakan adalah:

1. Normalisasi input visual.
2. Fuzzifikasi.
3. Evaluasi rule menggunakan operator minimum.
4. Implikasi Mamdani menggunakan clipping.
5. Agregasi output menggunakan operator maksimum.
6. Defuzzifikasi menggunakan centroid.
7. Penentuan risk class dan command navigasi.

## 3. Variabel Input dan Output

### 3.1 Input Fuzzy

Sistem menggunakan tiga input fuzzy.

| No | Input | Range | Keterangan |
|---:|---|---:|---|
| 1 | Lateral Position | -1 sampai 1 | Posisi lateral obstacle terhadap tengah citra |
| 2 | Visual Proximity | 0 sampai 1 | Indikasi kedekatan obstacle berdasarkan bounding box |
| 3 | Approach Urgency | 0 sampai 1 | Indikasi tingkat kedaruratan obstacle mendekati USV |

### 3.2 Output Fuzzy

Sistem menghasilkan tiga output fuzzy.

| No | Output | Range | Keterangan |
|---:|---|---:|---|
| 1 | Risk Score | 0 sampai 1 | Nilai risiko collision avoidance |
| 2 | Speed Factor | 0 sampai 1 | Faktor pengurangan kecepatan |
| 3 | Turn Bias | -1 sampai 1 | Arah kecenderungan belok |

### 3.3 Command Akhir

Command akhir ditentukan berdasarkan hasil risk score, speed factor, dan turn bias.

| Command | Keterangan |
|---|---|
| HOLD_COURSE | USV mempertahankan lintasan |
| SLOW_DOWN | USV mengurangi kecepatan |
| TURN_LEFT_SLOW | USV berbelok pelan ke kiri |
| TURN_RIGHT_SLOW | USV berbelok pelan ke kanan |
| STOP | USV berhenti karena kondisi risiko tinggi |

## 4. Persamaan Normalisasi Input

Data visual dari kamera tidak langsung dimasukkan ke sistem fuzzy. Data terlebih dahulu diubah menjadi tiga input crisp fuzzy.

### 4.1 Lateral Position

## 4. Persamaan Normalisasi Input

Data visual dari kamera tidak langsung dimasukkan ke sistem fuzzy. Data terlebih dahulu diubah menjadi tiga input crisp fuzzy, yaitu **Lateral Position**, **Visual Proximity**, dan **Approach Urgency**.

### 4.1 Lateral Position

Lateral position digunakan untuk menyatakan posisi obstacle terhadap titik tengah citra kamera.

$$
L = 2(x_c - 0.5)
$$

dengan:

- \(L\) adalah lateral position.
- \(x_c\) adalah posisi pusat bounding box pada sumbu horizontal citra.
- Nilai \(x_c\) berada pada rentang 0 sampai 1.

Jika obstacle berada pada corridor lintasan, program dapat menerapkan koreksi lateral:

$$
L_c = 0.55L
$$

Koreksi ini digunakan agar obstacle yang berada di dalam corridor lintasan lebih diperlakukan sebagai obstacle depan, bukan terlalu cepat dianggap sebagai obstacle samping.

### 4.2 Visual Proximity

Visual proximity digunakan untuk memperkirakan tingkat kedekatan obstacle berdasarkan posisi bawah bounding box dan rasio area bounding box.

Rasio area bounding box dinormalisasi dengan persamaan:

$$
A_n = \mathrm{clip}\left(\frac{A}{0.45}, 0, 1\right)
$$

Visual proximity dihitung sebagai:

$$
P = \mathrm{clip}\left(0.65B + 0.35A_n, 0, 1\right)
$$

dengan:

- \(P\) adalah visual proximity.
- \(B\) adalah posisi bawah bounding box.
- \(A\) adalah rasio area bounding box.
- \(A_n\) adalah rasio area yang telah dinormalisasi.

### 4.3 Approach Urgency

Approach urgency digunakan untuk memperkirakan tingkat kedaruratan obstacle berdasarkan visual time-to-collision, perubahan ukuran area bounding box, dan status obstacle terhadap corridor lintasan.

Komponen perubahan area bounding box dinormalisasi sebagai:

$$
D_n = \mathrm{clip}\left(\frac{d\log(A)}{0.18}, 0, 1\right)
$$

Approach urgency dihitung sebagai:

$$
U = \mathrm{clip}\left(0.70T_n + 0.30D_n + C, 0, 1\right)
$$

dengan:

- \(U\) adalah approach urgency.
- \(T_{vTTC}\) adalah visual time-to-collision.
- \(d\log(A)\) adalah perubahan logaritmik area bounding box.
- \(C\) adalah corridor bonus. Nilainya 0.10 jika obstacle berada pada corridor lintasan dan 0 jika tidak.

## 5. Fungsi Keanggotaan

Sistem menggunakan kombinasi fungsi keanggotaan segitiga dan trapesium. Fungsi segitiga digunakan untuk himpunan tengah, sedangkan fungsi trapesium digunakan untuk himpunan ujung atau shoulder.

### 5.1 Fungsi Segitiga

Fungsi keanggotaan segitiga dinyatakan sebagai:

$$
\mu(x;a,b,c)=
\begin{cases}
0, & x \leq a \text{ atau } x \geq c \\
\dfrac{x-a}{b-a}, & a < x \leq b \\
\dfrac{c-x}{c-b}, & b < x < c
\end{cases}
$$

### 5.2 Fungsi Trapesium

Fungsi keanggotaan trapesium dinyatakan sebagai:

$$
\mu(x;a,b,c,d)=
\begin{cases}
0, & x \leq a \text{ atau } x \geq d \\
\dfrac{x-a}{b-a}, & a < x < b \\
1, & b \leq x \leq c \\
\dfrac{d-x}{d-c}, & c < x < d
\end{cases}
$$

Pada rancangan ini, bentuk trapesium juga digunakan sebagai shoulder function. Contohnya adalah himpunan paling kiri dan paling kanan, seperti LEFT, RIGHT, FAR, NEAR, LOW, HIGH, STOP, dan NORMAL.

## 6. Rule Base dan Inferensi Mamdani

Rule base terdiri dari 27 aturan karena sistem memiliki tiga input fuzzy dan masing-masing input memiliki tiga himpunan linguistik.

$$
3 \times 3 \times 3 = 27
$$

Bentuk umum rule Mamdani yang digunakan adalah:

$$
\text{IF } L \text{ is } A_1 \text{ AND } P \text{ is } A_2 \text{ AND } U \text{ is } A_3
$$

$$
\text{THEN Risk is } B_1,\ \text{Speed is } B_2,\ \text{Turn is } B_3
$$

Operator AND pada bagian antecedent dihitung menggunakan operator minimum.

$$
\alpha_i =
\min\left(
\mu_{A_1}(L),
\mu_{A_2}(P),
\mu_{A_3}(U)
\right)
$$

dengan \(\alpha_i\) adalah firing strength rule ke-\(i\).

Implikasi Mamdani dilakukan dengan metode clipping.

$$
\mu'_{B_i}(y) =
\min\left(
\alpha_i,\mu_{B_i}(y)
\right)
$$

Jika terdapat beberapa rule yang menghasilkan output fuzzy yang sama, maka output tersebut digabungkan menggunakan operator maksimum.

$$
\mu_B(y) =
\max\left(
\mu'_{B_1}(y),
\mu'_{B_2}(y),
...,
\mu'_{B_n}(y)
\right)
$$

Defuzzifikasi dilakukan menggunakan metode centroid.

$$
y^* =
\frac{\sum_{k=1}^{N} y_k \mu(y_k)}
{\sum_{k=1}^{N} \mu(y_k)}
$$

Nilai crisp hasil defuzzifikasi kemudian digunakan untuk menentukan risk score, speed factor, turn bias, risk class, dan command akhir.
## 7. Struktur Repository

```text
collision_avoidance_mamdani_fuzzy/
    fuzzy_controller.py
    fuzzy_lab.py
    scenario_generator.py
    usv_simulator.py
    baseline_crisp.py
    plot_results.py
    plot_results_report.py
    report_tables.py
    excel_report_generator.py
    main.py
    requirements.txt
    README.md
    .gitignore

    results/
        figures/
        figures_report/
        fuzzy_lab/
        lab_runs/
        report_tables/
        simulation_data/

    archive/
        old_one_time_scripts/
````

Keterangan file utama:

| File                      | Fungsi                                                         |
| ------------------------- | -------------------------------------------------------------- |
| fuzzy_controller.py       | Model utama Mamdani Fuzzy Logic Controller                     |
| fuzzy_lab.py              | Alat simulasi interaktif seperti Fuzzy Logic Toolbox sederhana |
| scenario_generator.py     | Membuat data skenario obstacle sintetik                        |
| usv_simulator.py          | Simulasi lintasan USV sederhana                                |
| baseline_crisp.py         | Pembanding terhadap metode crisp threshold                     |
| plot_results_report.py    | Membuat grafik hasil simulasi untuk laporan                    |
| report_tables.py          | Membuat tabel CSV dan ringkasan laporan                        |
| excel_report_generator.py | Membuat workbook Excel laporan                                 |
| main.py                   | Menjalankan pipeline utama                                     |
| requirements.txt          | Daftar library Python yang dibutuhkan                          |

## 8. Instalasi

Program dibuat menggunakan Python 3.10. Library yang digunakan dapat dipasang melalui terminal.

```powershell
python -m pip install -r requirements.txt
```

Jika belum menggunakan virtual environment, disarankan membuat environment terlebih dahulu.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## 9. Cara Menjalankan Program Utama

Untuk menjalankan seluruh pipeline simulasi:

```powershell
python main.py
```

Program akan menghasilkan data simulasi, grafik, tabel laporan, dan workbook Excel.

Output utama berada pada folder:

```text
results/
```

## 10. Cara Menggunakan Fuzzy Lab

`fuzzy_lab.py` adalah alat simulasi interaktif yang dibuat sebagai pengganti MATLAB Fuzzy Logic Toolbox versi ringan.

Jalankan:

```powershell
python fuzzy_lab.py
```

Menu yang tersedia:

```text
1. Hitung dari data vision mentah
2. Hitung dari input fuzzy langsung
3. Buat grafik membership function
4. Buat surface viewer
5. Jalankan demo obstacle depan transisi
6. Tampilkan rule base 27 aturan
0. Keluar
```

### 10.1 Demo Obstacle Depan Transisi

Pilih menu:

```text
5
```

Contoh hasil:

```text
Lateral Position : 0.000
Visual Proximity : 0.699
Approach Urgency : 0.781

Risk Score       : 0.717
Speed Factor     : 0.278
Turn Bias        : 0.637
Risk Class       : HIGH
Command          : STOP
```

Hasil tersebut menunjukkan bahwa obstacle berada pada kondisi risiko tinggi sehingga command akhir yang diberikan adalah STOP.

### 10.2 Input Data Vision Mentah

Pilih menu:

```text
1
```

Masukkan parameter berikut:

| Parameter       | Keterangan                                            |
| --------------- | ----------------------------------------------------- |
| x_center        | Posisi pusat bounding box pada sumbu horizontal citra |
| bbox_bottom     | Posisi bawah bounding box                             |
| bbox_area_ratio | Rasio area bounding box                               |
| visual_ttc      | Visual time-to-collision                              |
| dlog_area       | Perubahan logaritmik area bounding box                |
| in_corridor     | Status obstacle terhadap corridor lintasan            |

Program akan menghitung input fuzzy, rule aktif, output crisp, risk class, dan command akhir.

### 10.3 Input Fuzzy Langsung

Pilih menu:

```text
2
```

Masukkan nilai:

```text
Lateral Position
Visual Proximity
Approach Urgency
```

Mode ini digunakan jika pengguna ingin menguji langsung nilai input fuzzy tanpa memasukkan data visual mentah.

### 10.4 Membuat Membership Function

Pilih menu:

```text
3
```

Output akan tersimpan pada:

```text
results/fuzzy_lab/
```

### 10.5 Membuat Surface Viewer

Pilih menu:

```text
4
```

Contoh konfigurasi surface viewer utama:

```text
Output: risk
Sumbu X: proximity
Sumbu Y: urgency
Lateral Position tetap: 0.00
Mesh point: 41
```

Surface viewer digunakan untuk melihat hubungan dua input fuzzy terhadap satu output fuzzy. Karena sistem memiliki tiga input, satu input harus dibuat tetap.

## 11. Output Program

Program menghasilkan beberapa jenis output.

| Folder                  | Isi                                           |
| ----------------------- | --------------------------------------------- |
| results/figures         | Grafik simulasi awal                          |
| results/figures_report  | Grafik final untuk laporan                    |
| results/fuzzy_lab       | Grafik hasil Fuzzy Lab                        |
| results/lab_runs        | Hasil perhitungan per kasus dari Fuzzy Lab    |
| results/report_tables   | Tabel CSV, ringkasan TXT, dan workbook Excel  |
| results/simulation_data | Folder untuk menyimpan data simulasi tambahan |

Contoh file output:

```text
simulation_log.csv
simulation_summary.csv
usv_trajectory_log.csv
usv_trajectory_summary.csv
laporan_simulasi_fuzzy_seano.xlsx
output_aggregation.png
active_rules.csv
result_summary.txt
```

## 12. Contoh Analisis Kasus

Pada kasus obstacle depan transisi, data visual yang digunakan adalah:

| Parameter       |  Nilai |
| --------------- | -----: |
| x_center        |   0.50 |
| bbox_bottom     |   0.80 |
| bbox_area_ratio |   0.23 |
| visual_ttc      | 2.80 s |
| dlog_area       |   0.11 |
| in_corridor     |   True |

Hasil normalisasi:

| Input Fuzzy      | Nilai |
| ---------------- | ----: |
| Lateral Position | 0.000 |
| Visual Proximity | 0.699 |
| Approach Urgency | 0.781 |

Hasil defuzzifikasi:

| Output       | Nilai |
| ------------ | ----: |
| Risk Score   | 0.717 |
| Speed Factor | 0.278 |
| Turn Bias    | 0.637 |

Karena nilai risk score lebih besar dari 0,60, maka sistem mengklasifikasikan kondisi sebagai HIGH.
