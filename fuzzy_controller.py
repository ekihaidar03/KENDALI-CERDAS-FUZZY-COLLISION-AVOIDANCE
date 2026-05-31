import numpy as np


def clamp(x, batas_bawah, batas_atas):
    return max(batas_bawah, min(batas_atas, x))


def trimf(x, a, b, c):
    scalar_input = np.isscalar(x)
    x = np.array([x], dtype=float) if scalar_input else np.asarray(x, dtype=float)

    y = np.zeros_like(x)

    naik = (a < x) & (x <= b)
    turun = (b < x) & (x < c)

    if b != a:
        y[naik] = (x[naik] - a) / (b - a)

    if c != b:
        y[turun] = (c - x[turun]) / (c - b)

    y[x == b] = 1.0
    y = np.clip(y, 0.0, 1.0)

    if scalar_input:
        return float(y[0])

    return y


def trapmf(x, a, b, c, d):
    scalar_input = np.isscalar(x)
    x = np.array([x], dtype=float) if scalar_input else np.asarray(x, dtype=float)

    y = np.zeros_like(x)

    if a == b:
        y[x <= b] = 1.0
    else:
        naik = (a < x) & (x < b)
        y[naik] = (x[naik] - a) / (b - a)

    datar = (b <= x) & (x <= c)
    y[datar] = 1.0

    if c == d:
        y[x >= c] = 1.0
    else:
        turun = (c < x) & (x < d)
        y[turun] = (d - x[turun]) / (d - c)

    y = np.clip(y, 0.0, 1.0)

    if scalar_input:
        return float(y[0])

    return y


class FuzzyCollisionAvoidance:
    def __init__(self):
        self.speed_x = np.linspace(0.0, 1.0, 501)
        self.turn_x = np.linspace(-1.0, 1.0, 501)
        self.risk_x = np.linspace(0.0, 1.0, 501)

    def fuzz_lateral(self, lateral):
        lateral = clamp(lateral, -1.0, 1.0)

        return {
            "kiri": trapmf(lateral, -1.0, -1.0, -0.60, -0.15),
            "tengah": trimf(lateral, -0.35, 0.0, 0.35),
            "kanan": trapmf(lateral, 0.15, 0.60, 1.0, 1.0),
        }

    def fuzz_proximity(self, proximity):
        proximity = clamp(proximity, 0.0, 1.0)

        return {
            "jauh": trapmf(proximity, 0.00, 0.00, 0.25, 0.45),
            "sedang": trimf(proximity, 0.30, 0.55, 0.80),
            "dekat": trapmf(proximity, 0.65, 0.82, 1.00, 1.00),
        }

    def fuzz_urgency(self, urgency):
        urgency = clamp(urgency, 0.0, 1.0)

        return {
            "rendah": trapmf(urgency, 0.00, 0.00, 0.25, 0.45),
            "sedang": trimf(urgency, 0.30, 0.55, 0.80),
            "tinggi": trapmf(urgency, 0.75, 0.90, 1.00, 1.00),
        }

    def mf_speed(self, label):
        x = self.speed_x

        if label == "stop":
            return trapmf(x, 0.00, 0.00, 0.05, 0.18)

        if label == "slow":
            return trimf(x, 0.12, 0.35, 0.58)

        if label == "normal":
            return trapmf(x, 0.50, 0.72, 1.00, 1.00)

        raise ValueError("label speed tidak dikenal")

    def mf_turn(self, label):
        x = self.turn_x

        if label == "left":
            return trapmf(x, -1.00, -1.00, -0.75, -0.22)

        if label == "straight":
            return trimf(x, -0.30, 0.00, 0.30)

        if label == "right":
            return trapmf(x, 0.22, 0.75, 1.00, 1.00)

        raise ValueError("label turn tidak dikenal")

    def mf_risk(self, label):
        x = self.risk_x

        if label == "low":
            return trapmf(x, 0.00, 0.00, 0.18, 0.35)

        if label == "medium":
            return trimf(x, 0.25, 0.45, 0.65)

        if label == "high":
            return trapmf(x, 0.62, 0.78, 1.00, 1.00)

        raise ValueError("label risk tidak dikenal")

    def centroid(self, x, mu):
        total = np.sum(mu)

        if total <= 1e-12:
            return 0.0

        return float(np.sum(x * mu) / total)

    def hitung(self, lateral, proximity, urgency):
        lat = self.fuzz_lateral(lateral)
        prox = self.fuzz_proximity(proximity)
        urg = self.fuzz_urgency(urgency)

        speed_out = np.zeros_like(self.speed_x)
        turn_out = np.zeros_like(self.turn_x)
        risk_out = np.zeros_like(self.risk_x)

        def aturan(alpha, speed_label, turn_label, risk_label):
            nonlocal speed_out, turn_out, risk_out

            if alpha <= 0.0:
                return

            speed_out = np.maximum(
                speed_out,
                np.minimum(alpha, self.mf_speed(speed_label)),
            )

            turn_out = np.maximum(
                turn_out,
                np.minimum(alpha, self.mf_turn(turn_label)),
            )

            risk_out = np.maximum(
                risk_out,
                np.minimum(alpha, self.mf_risk(risk_label)),
            )

        # Obstacle jauh atau belum mengancam.
        aturan(min(prox["jauh"], urg["rendah"]), "normal", "straight", "low")
        aturan(min(prox["jauh"], urg["sedang"]), "normal", "straight", "low")
        aturan(min(prox["jauh"], urg["tinggi"]), "slow", "straight", "medium")

        # Obstacle berada di depan / dekat corridor.
        aturan(min(lat["tengah"], prox["sedang"], urg["rendah"]), "slow", "straight", "medium")
        aturan(min(lat["tengah"], prox["sedang"], urg["sedang"]), "slow", "right", "medium")
        aturan(min(lat["tengah"], prox["sedang"], urg["tinggi"]), "slow", "right", "medium")

        aturan(min(lat["tengah"], prox["dekat"], urg["rendah"]), "slow", "right", "medium")
        aturan(min(lat["tengah"], prox["dekat"], urg["sedang"]), "stop", "right", "high")
        aturan(min(lat["tengah"], prox["dekat"], urg["tinggi"]), "stop", "right", "high")

        # Obstacle dari sisi kiri.
        # Untuk crossing kiri dengan risiko sedang, respons dibuat lebih konservatif:
        # melambat dulu, bukan langsung belok kanan terlalu lama.
        aturan(min(lat["kiri"], prox["sedang"], urg["rendah"]), "normal", "straight", "low")
        aturan(min(lat["kiri"], prox["sedang"], urg["sedang"]), "slow", "straight", "medium")
        aturan(min(lat["kiri"], prox["sedang"], urg["tinggi"]), "slow", "straight", "medium")

        aturan(min(lat["kiri"], prox["dekat"], urg["rendah"]), "slow", "straight", "medium")
        aturan(min(lat["kiri"], prox["dekat"], urg["sedang"]), "slow", "straight", "medium")
        aturan(min(lat["kiri"], prox["dekat"], urg["tinggi"]), "stop", "right", "high")

        # Obstacle dari sisi kanan.
        # Jika obstacle kanan mulai berisiko, sistem boleh memberi bias ke kiri.
        aturan(min(lat["kanan"], prox["sedang"], urg["rendah"]), "normal", "straight", "low")
        aturan(min(lat["kanan"], prox["sedang"], urg["sedang"]), "slow", "left", "medium")
        aturan(min(lat["kanan"], prox["sedang"], urg["tinggi"]), "slow", "left", "medium")

        aturan(min(lat["kanan"], prox["dekat"], urg["rendah"]), "slow", "left", "medium")
        aturan(min(lat["kanan"], prox["dekat"], urg["sedang"]), "slow", "left", "medium")
        aturan(min(lat["kanan"], prox["dekat"], urg["tinggi"]), "stop", "left", "high")

        speed = self.centroid(self.speed_x, speed_out)
        turn = self.centroid(self.turn_x, turn_out)
        risk = self.centroid(self.risk_x, risk_out)

        risk_class = self.kelas_risiko(risk)
        command = self.pilih_command(risk_class, turn)

        return {
            "speed": speed,
            "turn": turn,
            "risk": risk,
            "risk_class": risk_class,
            "command": command,
        }

    def kelas_risiko(self, risk):
        if risk < 0.30:
            return "LOW"

        if risk < 0.60:
            return "MEDIUM"

        return "HIGH"

    def pilih_command(self, risk_class, turn):
        if risk_class == "LOW":
            return "HOLD_COURSE"

        if risk_class == "MEDIUM":
            if turn > 0.35:
                return "TURN_RIGHT_SLOW"

            if turn < -0.35:
                return "TURN_LEFT_SLOW"

            return "SLOW_DOWN"

        return "STOP"


def ubah_fitur_visual_ke_input_fuzzy(x, bot, area, vttc, dlog, corridor):
    x = clamp(x, 0.0, 1.0)
    bot = clamp(bot, 0.0, 1.0)
    area = clamp(area, 0.0, 1.0)

    lateral = 2.0 * (x - 0.5)

    if corridor:
        lateral *= 0.55

    area_norm = clamp(area / 0.45, 0.0, 1.0)

    proximity = (0.65 * bot) + (0.35 * area_norm)
    proximity = clamp(proximity, 0.0, 1.0)

    if vttc is None or vttc <= 0:
        vttc_norm = 0.0

    elif vttc <= 1.5:
        vttc_norm = 1.0

    elif vttc >= 6.0:
        vttc_norm = 0.0

    else:
        vttc_norm = (6.0 - vttc) / 4.5

    dlog_norm = clamp(dlog / 0.18, 0.0, 1.0)

    urgency = (0.70 * vttc_norm) + (0.30 * dlog_norm)

    if corridor:
        urgency += 0.10

    urgency = clamp(urgency, 0.0, 1.0)

    return lateral, proximity, urgency


if __name__ == "__main__":
    fuzzy = FuzzyCollisionAvoidance()

    data_uji = [
        ("Obstacle jauh", 0.50, 0.30, 0.04, 8.0, 0.01, False),
        ("Obstacle depan sedang", 0.50, 0.70, 0.15, 3.0, 0.08, True),
        ("Obstacle depan dekat", 0.50, 0.92, 0.35, 1.2, 0.15, True),
        ("Obstacle kiri crossing", 0.25, 0.70, 0.18, 3.0, 0.08, True),
        ("Obstacle kanan crossing", 0.75, 0.70, 0.18, 3.0, 0.08, True),
    ]

    for nama, x, bot, area, vttc, dlog, corridor in data_uji:
        lateral, proximity, urgency = ubah_fitur_visual_ke_input_fuzzy(
            x=x,
            bot=bot,
            area=area,
            vttc=vttc,
            dlog=dlog,
            corridor=corridor,
        )

        hasil = fuzzy.hitung(lateral, proximity, urgency)

        print("\n" + nama)
        print(
            "input fuzzy  : lateral={:.2f}, proximity={:.2f}, urgency={:.2f}".format(
                lateral,
                proximity,
                urgency,
            )
        )
        print(
            "output fuzzy : speed={:.3f}, turn={:.3f}, risk={:.3f}".format(
                hasil["speed"],
                hasil["turn"],
                hasil["risk"],
            )
        )
        print("kelas/command:", hasil["risk_class"], "-", hasil["command"])