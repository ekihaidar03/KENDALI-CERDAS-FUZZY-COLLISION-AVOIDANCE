# Tabel Hasil Simulasi Fuzzy Collision Avoidance

## Tabel 1. Ringkasan Output Fuzzy Controller

| No | Skenario | Jumlah data | Risk minimum | Risk maksimum | Risk rata-rata | Speed rata-rata | Jumlah HOLD_COURSE | Jumlah SLOW_DOWN | Jumlah TURN_LEFT_SLOW | Jumlah TURN_RIGHT_SLOW | Jumlah STOP | Jumlah LOW | Jumlah MEDIUM | Jumlah HIGH |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Crossing kiri ke kanan | 101 | 0,147 | 0,450 | 0,295 | 0,579 | 53 | 15 | 0 | 33 | 0 | 53 | 48 | 0 |
| 2 | Crossing kanan ke kiri | 101 | 0,147 | 0,450 | 0,295 | 0,579 | 53 | 8 | 9 | 31 | 0 | 53 | 48 | 0 |
| 3 | Obstacle frontal statis | 101 | 0,137 | 0,847 | 0,452 | 0,427 | 31 | 0 | 0 | 41 | 29 | 31 | 41 | 29 |
| 4 | Tanpa obstacle | 101 | 0,137 | 0,137 | 0,137 | 0,800 | 101 | 0 | 0 | 0 | 0 | 101 | 0 | 0 |
| 5 | Obstacle samping aman | 101 | 0,153 | 0,161 | 0,156 | 0,774 | 101 | 0 | 0 | 0 | 0 | 101 | 0 | 0 |

## Tabel 2. Ringkasan Simulasi Lintasan USV

| No | Skenario | Posisi akhir X (m) | Posisi akhir Y (m) | Deviasi lateral maksimum (m) | Kecepatan rata-rata (m/s) | Kecepatan minimum (m/s) | Jarak minimum simulatif (m) | Jumlah pergantian command |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Crossing kiri ke kanan | 1,501 | 11,855 | 2,234 | 0,637 | 0,385 | 0,411 | 4 |
| 2 | Crossing kanan ke kiri | 1,137 | 11,936 | 1,665 | 0,637 | 0,385 | 2,250 | 5 |
| 3 | Obstacle frontal statis | 2,166 | 7,532 | 2,166 | 0,422 | 0,000 | 2,445 | 2 |
| 4 | Tanpa obstacle | 0,000 | 17,783 | 0,000 | 0,880 | 0,880 | - | 0 |
| 5 | Obstacle samping aman | 0,000 | 17,206 | 0,000 | 0,852 | 0,846 | 5,000 | 0 |

## Tabel 3. Validasi Skenario Simulasi

| No | Skenario | Risk maksimum | Jumlah LOW | Jumlah MEDIUM | Jumlah HIGH | HOLD_COURSE | SLOW_DOWN | TURN_LEFT_SLOW | TURN_RIGHT_SLOW | STOP | Jarak minimum simulatif (m) | Status validasi simulasi | Catatan analisis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Crossing kiri ke kanan | 0,450 | 53 | 48 | 0 | 53 | 15 | 0 | 33 | 0 | 0,411 | Valid simulatif - crossing terdeteksi sebagai risiko MEDIUM | Skenario crossing paling kritis; fuzzy controller menurunkan kecepatan dan menjaga risk pada kelas MEDIUM. |
| 2 | Crossing kanan ke kiri | 0,450 | 53 | 48 | 0 | 53 | 8 | 9 | 31 | 0 | 2,250 | Valid simulatif - crossing terdeteksi sebagai risiko MEDIUM | Obstacle crossing tetap berada pada kelas MEDIUM dan tidak mencapai kondisi STOP. |
| 3 | Obstacle frontal statis | 0,847 | 31 | 41 | 29 | 31 | 0 | 0 | 41 | 29 | 2,445 | Valid - sistem melakukan STOP pada obstacle frontal | Obstacle frontal menghasilkan risk HIGH dan command STOP, sesuai respons konservatif collision avoidance. |
| 4 | Tanpa obstacle | 0,137 | 101 | 0 | 0 | 101 | 0 | 0 | 0 | 0 | - | Valid - sistem mempertahankan HOLD_COURSE | Tidak ada obstacle; sistem mempertahankan lintasan tanpa pergantian command. |
| 5 | Obstacle samping aman | 0,161 | 101 | 0 | 0 | 101 | 0 | 0 | 0 | 0 | 5,000 | Valid - obstacle samping tidak memicu avoidance | Obstacle berada di sisi luar corridor sehingga sistem tetap HOLD_COURSE. |

Catatan: jarak minimum pada tabel merupakan jarak simulatif berdasarkan model kinematik sederhana. Nilai tersebut belum dapat dianggap sebagai validasi keselamatan fisik final pada platform USV nyata.
