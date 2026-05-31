# Tabel Hasil Simulasi Fuzzy Collision Avoidance

## Tabel 1. Ringkasan Output Fuzzy Controller

|   No | Skenario                |   Jumlah Data |   Risk Minimum |   Risk Maksimum |   Risk Rata-rata |   Speed Rata-rata | Distribusi Command                                                              | Distribusi Risk Class                 |
|-----:|:------------------------|--------------:|---------------:|----------------:|-----------------:|------------------:|:--------------------------------------------------------------------------------|:--------------------------------------|
|    1 | Crossing kiri ke kanan  |           101 |          0.147 |           0.45  |            0.295 |             0.579 | {'HOLD_COURSE': 53, 'TURN_RIGHT_SLOW': 33, 'SLOW_DOWN': 15}                     | {'LOW': 53, 'MEDIUM': 48}             |
|    2 | Crossing kanan ke kiri  |           101 |          0.147 |           0.45  |            0.295 |             0.579 | {'HOLD_COURSE': 53, 'TURN_RIGHT_SLOW': 31, 'TURN_LEFT_SLOW': 9, 'SLOW_DOWN': 8} | {'LOW': 53, 'MEDIUM': 48}             |
|    3 | Obstacle frontal statis |           101 |          0.137 |           0.847 |            0.452 |             0.427 | {'TURN_RIGHT_SLOW': 41, 'HOLD_COURSE': 31, 'STOP': 29}                          | {'MEDIUM': 41, 'LOW': 31, 'HIGH': 29} |
|    4 | Tanpa obstacle          |           101 |          0.137 |           0.137 |            0.137 |             0.8   | {'HOLD_COURSE': 101}                                                            | {'LOW': 101}                          |
|    5 | Obstacle samping aman   |           101 |          0.153 |           0.161 |            0.156 |             0.774 | {'HOLD_COURSE': 101}                                                            | {'LOW': 101}                          |

## Tabel 2. Ringkasan Simulasi Lintasan USV

|   No | Skenario                |   Posisi Akhir X (m) |   Posisi Akhir Y (m) |   Deviasi Lateral Maks. (m) |   Kecepatan Rata-rata (m/s) |   Kecepatan Minimum (m/s) | Jarak Minimum Simulatif (m)   |   Jumlah Pergantian Command |
|-----:|:------------------------|---------------------:|---------------------:|----------------------------:|----------------------------:|--------------------------:|:------------------------------|----------------------------:|
|    1 | Crossing kiri ke kanan  |                1.501 |               11.855 |                       2.234 |                       0.637 |                     0.385 | 0.411                         |                           4 |
|    2 | Crossing kanan ke kiri  |                1.137 |               11.936 |                       1.665 |                       0.637 |                     0.385 | 2.250                         |                           5 |
|    3 | Obstacle frontal statis |                2.166 |                7.532 |                       2.166 |                       0.422 |                     0     | 2.445                         |                           2 |
|    4 | Tanpa obstacle          |                0     |               17.783 |                       0     |                       0.88  |                     0.88  | -                             |                           0 |
|    5 | Obstacle samping aman   |                0     |               17.206 |                       0     |                       0.852 |                     0.846 | 5.000                         |                           0 |

## Tabel 3. Validasi Skenario Simulasi

|   No | Skenario                |   Risk Maksimum | Command Count                                                                   | Jarak Minimum Simulatif (m)   | Status Validasi Simulasi                                    | Catatan Analisis                                                                                        |
|-----:|:------------------------|----------------:|:--------------------------------------------------------------------------------|:------------------------------|:------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------|
|    1 | Crossing kiri ke kanan  |           0.45  | {'HOLD_COURSE': 53, 'TURN_RIGHT_SLOW': 33, 'SLOW_DOWN': 15}                     | 0.411                         | Valid simulatif - crossing terdeteksi sebagai risiko MEDIUM | Skenario crossing paling kritis; respons fuzzy menurunkan kecepatan dan menjaga risk pada kelas MEDIUM. |
|    2 | Crossing kanan ke kiri  |           0.45  | {'HOLD_COURSE': 53, 'TURN_RIGHT_SLOW': 31, 'TURN_LEFT_SLOW': 9, 'SLOW_DOWN': 8} | 2.250                         | Valid simulatif - crossing terdeteksi sebagai risiko MEDIUM | Obstacle crossing tetap berada pada kelas MEDIUM dan tidak mencapai kondisi STOP.                       |
|    3 | Obstacle frontal statis |           0.847 | {'TURN_RIGHT_SLOW': 41, 'HOLD_COURSE': 31, 'STOP': 29}                          | 2.445                         | Valid - sistem melakukan STOP pada obstacle frontal         | Obstacle frontal menghasilkan kondisi HIGH dan command STOP, sesuai respons konservatif.                |
|    4 | Tanpa obstacle          |           0.137 | {'HOLD_COURSE': 101}                                                            | -                             | Valid - sistem mempertahankan HOLD_COURSE                   | Tidak ada obstacle; sistem mempertahankan lintasan tanpa pergantian command.                            |
|    5 | Obstacle samping aman   |           0.161 | {'HOLD_COURSE': 101}                                                            | 5.000                         | Valid - obstacle samping tidak memicu avoidance             | Obstacle berada di sisi luar corridor sehingga sistem tetap HOLD_COURSE.                                |

Catatan: jarak minimum pada tabel merupakan jarak simulatif berdasarkan model kinematik sederhana, bukan hasil validasi keselamatan fisik final pada platform USV nyata.
