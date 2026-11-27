from flask import Flask, render_template, request, redirect, jsonify, session
import sqlite3
import math
import os
import json
import urllib.parse
import urllib.request
import urllib.error

app = Flask(__name__)
app.secret_key = os.environ.get("LIFEAID_SECRET_KEY", "lifeaid-local-development-key")

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

def get_db():
    """Open a SQLite connection that returns rows by column name."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_location_columns():
    """Safely add location fields without deleting existing project data."""
    conn = sqlite3.connect(DATABASE)
    for table, column, definition in [
        ("donors", "latitude", "REAL"),
        ("donors", "longitude", "REAL"),
        ("donors", "location_share", "INTEGER NOT NULL DEFAULT 0"),
        ("hospitals", "latitude", "REAL"),
        ("hospitals", "longitude", "REAL"),
        ("hospitals", "services", "TEXT"),
    ]:
        existing = [row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()]
        if column not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
    conn.commit()
    conn.close()

def valid_coordinate(value, minimum, maximum):
    try:
        number = float(value)
        return number if minimum <= number <= maximum else None
    except (TypeError, ValueError):
        return None

def distance_km(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS points using the Haversine formula."""
    earth_radius = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * earth_radius * math.asin(math.sqrt(a))


def fetch_osm_hospitals(latitude, longitude, radius_m):
    """Fetch mapped hospitals from OpenStreetMap Overpass, trying fallback servers."""
    query = (
        f'[out:json][timeout:25];('
        f'nwr["amenity"="hospital"](around:{radius_m},{latitude},{longitude});'
        f'nwr["healthcare"="hospital"](around:{radius_m},{latitude},{longitude});'
        f');out center tags;'
    )
    encoded = urllib.parse.urlencode({"data": query})
    endpoints = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass.nchc.org.tw/api/interpreter",
    ]
    last_error = None
    for endpoint in endpoints:
        for method in ("POST", "GET"):
            try:
                headers = {"User-Agent": "LifeAidStudentProject/1.0 (nearby hospital search)"}
                if method == "POST":
                    req = urllib.request.Request(
                        endpoint, data=encoded.encode("utf-8"),
                        headers={**headers, "Content-Type": "application/x-www-form-urlencoded"},
                        method="POST"
                    )
                else:
                    req = urllib.request.Request(endpoint + "?" + encoded, headers=headers)
                with urllib.request.urlopen(req, timeout=35) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                facilities = []
                for element in payload.get("elements", []):
                    tags = element.get("tags", {})
                    center = element.get("center", element)
                    lat, lon = center.get("lat"), center.get("lon")
                    if lat is None or lon is None:
                        continue
                    distance = distance_km(latitude, longitude, float(lat), float(lon))
                    if distance * 1000 > radius_m:
                        continue
                    address = ", ".join(filter(None, [
                        tags.get("addr:housenumber"), tags.get("addr:street"),
                        tags.get("addr:suburb") or tags.get("addr:neighbourhood"),
                        tags.get("addr:city") or tags.get("addr:district")
                    ])) or tags.get("addr:full", "")
                    facilities.append({
                        "name": tags.get("name") or tags.get("name:en") or "Hospital (name not listed)",
                        "latitude": float(lat), "longitude": float(lon),
                        "address": address,
                        "phone": tags.get("phone") or tags.get("contact:phone", ""),
                        "services": tags.get("healthcare:speciality") or "Hospital",
                        "distance_km": round(distance, 2),
                        "source": "OpenStreetMap"
                    })
                facilities.sort(key=lambda item: item["distance_km"])
                return facilities, None
            except Exception as exc:
                last_error = f"{endpoint} ({method}): {exc}"
    return [], last_error or "Map data service unavailable"


init_location_columns()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        print(request.form)

        name = request.form.get("name")
        email = request.form["email"]
        password = request.form["password"]
        city = request.form["city"]
        language = request.form["language"] 

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO users
            (name, email, password, city, language)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, email, password, city, language)
        )

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        print("LOGIN FORM:", request.form)
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:
            session["user_id"] = user[0]
            session["user_language"] = user[5] or "English"
            return render_template("dashboard.html", username=user[1])
        else:
           return render_template(
        "login.html",
        error="Invalid Email or Password"
    )

    return render_template("login.html")


# ---------------------------
# Emergency Guidance
# ---------------------------
@app.route("/dashboard")
def dashboard():
    return render_template(
        "dashboard.html",
        username="Guest"
    )

@app.route("/heart-attack")
def heart_attack():
    # Use the language selected by the currently logged-in user.
    language = session.get("user_language")
    user_id = session.get("user_id")

    # Backward-compatible fallback for existing local data when no session exists.
    if not language:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT language FROM users WHERE id=?", (user_id or 1,))
        result = cursor.fetchone()
        conn.close()
        language = result[0] if result and result[0] else "English"

    return render_template("heart_attack.html", language=language)


@app.route("/burns")
def burns():
    return render_template("burns.html")


@app.route("/snake-bite")
def snake_bite():
    return render_template("snake_bite.html")


@app.route("/bleeding")
def bleeding():
    return render_template("bleeding.html")


@app.route("/choking")
def choking():
    return render_template("choking.html")


# ---------------------------
# Blood Donor Module
# ---------------------------

@app.route("/donor-register", methods=["GET", "POST"])
def donor_register():
    if request.method == "POST":
        name = request.form["name"].strip()
        blood_group = request.form["blood_group"].strip()
        city = request.form.get("city", "").strip()
        phone = request.form["phone"].strip()
        latitude = valid_coordinate(request.form.get("latitude"), -90, 90)
        longitude = valid_coordinate(request.form.get("longitude"), -180, 180)
        share_location = 1 if request.form.get("location_share") == "yes" else 0
        if not name or not phone:
            return render_template("donor_register.html", error="Please enter your name and phone number.")
        if share_location and (latitude is None or longitude is None):
            return render_template("donor_register.html", error="Please capture your location or uncheck location sharing.")
        conn = get_db()
        conn.execute(
            "INSERT INTO donors (name, blood_group, city, phone, latitude, longitude, location_share) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, blood_group, city, phone, latitude if share_location else None, longitude if share_location else None, share_location)
        )
        conn.commit()
        conn.close()
        return render_template("donor_register.html", success="Donor registered successfully. Your location is shared only because you gave consent.")
    return render_template("donor_register.html")

@app.route("/search-donor", methods=["GET", "POST"])
def search_donor():

    if request.method == "POST":

        blood_group = request.form["blood_group"]
        city = request.form["city"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM donors
            WHERE LOWER(blood_group)=LOWER(?)
            AND LOWER(city)=LOWER(?)
            """,
            (blood_group, city)
        )

        donors = cursor.fetchall()

        conn.close()

        return render_template(
            "donor_results.html",
            donors=donors
        )

    return render_template("search_donor.html")


@app.route("/nearby-donors")
def nearby_donors_page():
    return render_template("nearby_donors.html")

@app.route("/api/nearby-donors")
def api_nearby_donors():
    latitude = valid_coordinate(request.args.get("lat"), -90, 90)
    longitude = valid_coordinate(request.args.get("lon"), -180, 180)
    blood_group = request.args.get("blood_group", "").strip()
    try:
        radius = min(max(float(request.args.get("radius", 25)), 1), 100)
    except ValueError:
        radius = 25
    if latitude is None or longitude is None:
        return jsonify({"error": "Valid current latitude and longitude are required."}), 400
    conn = get_db()
    if blood_group:
        rows = conn.execute("SELECT id, name, blood_group, city, phone, latitude, longitude FROM donors WHERE location_share=1 AND latitude IS NOT NULL AND longitude IS NOT NULL AND LOWER(blood_group)=LOWER(?)", (blood_group,)).fetchall()
    else:
        rows = conn.execute("SELECT id, name, blood_group, city, phone, latitude, longitude FROM donors WHERE location_share=1 AND latitude IS NOT NULL AND longitude IS NOT NULL").fetchall()
    conn.close()
    results = []
    for row in rows:
        distance = distance_km(latitude, longitude, row["latitude"], row["longitude"])
        if distance <= radius:
            results.append({"id": row["id"], "name": row["name"], "blood_group": row["blood_group"], "city": row["city"], "phone": row["phone"], "latitude": row["latitude"], "longitude": row["longitude"], "distance_km": round(distance, 2)})
    results.sort(key=lambda item: item["distance_km"])
    return jsonify({"donors": results, "count": len(results)})

@app.route("/nearby-hospitals")
def nearby_hospitals_page():
    return render_template("nearby_hospitals.html")

@app.route("/api/nearby-hospitals")
def api_nearby_hospitals():
    latitude = valid_coordinate(request.args.get("lat"), -90, 90)
    longitude = valid_coordinate(request.args.get("lon"), -180, 180)
    try:
        radius = min(max(float(request.args.get("radius", 10)), 1), 50)
    except (TypeError, ValueError):
        radius = 10
    if latitude is None or longitude is None:
        return jsonify({"error": "Valid current latitude and longitude are required."}), 400
    hospitals, error = fetch_osm_hospitals(latitude, longitude, int(radius * 1000))
    conn = get_db()
    rows = conn.execute("SELECT id, hospital_name, city, address, phone, services, latitude, longitude FROM hospitals WHERE latitude IS NOT NULL AND longitude IS NOT NULL").fetchall()
    conn.close()
    for row in rows:
        distance = distance_km(latitude, longitude, row["latitude"], row["longitude"])
        if distance <= radius:
            hospitals.append({"name": row["hospital_name"], "latitude": row["latitude"], "longitude": row["longitude"],
                "address": row["address"] or row["city"], "phone": row["phone"], "services": row["services"] or "Not specified",
                "distance_km": round(distance, 2), "source": "LifeAid directory"})
    unique = {}
    for hospital in hospitals:
        key = (hospital["name"].strip().lower(), round(float(hospital["latitude"]), 5), round(float(hospital["longitude"]), 5))
        if key not in unique:
            unique[key] = hospital
    results = sorted(unique.values(), key=lambda item: item["distance_km"])
    return jsonify({"hospitals": results, "count": len(results), "map_data_available": error is None,
                    "warning": ("Map data service unavailable; showing saved LifeAid records only. Details: " + str(error)) if error else
                    "Map listings may be incomplete. Call to verify services and availability."})

@app.route("/api/saved-hospitals")
def api_saved_hospitals():
    latitude = valid_coordinate(request.args.get("lat"), -90, 90)
    longitude = valid_coordinate(request.args.get("lon"), -180, 180)
    try:
        radius = min(max(float(request.args.get("radius", 25)), 1), 100)
    except ValueError:
        radius = 25
    if latitude is None or longitude is None:
        return jsonify({"error": "Valid current latitude and longitude are required."}), 400
    conn = get_db()
    rows = conn.execute("SELECT id, hospital_name, city, address, phone, services, latitude, longitude FROM hospitals WHERE latitude IS NOT NULL AND longitude IS NOT NULL").fetchall()
    conn.close()
    results = []
    for row in rows:
        distance = distance_km(latitude, longitude, row["latitude"], row["longitude"])
        if distance <= radius:
            results.append({"id": row["id"], "name": row["hospital_name"], "city": row["city"], "address": row["address"], "phone": row["phone"], "services": row["services"] or "Not specified", "latitude": row["latitude"], "longitude": row["longitude"], "distance_km": round(distance, 2), "source": "LifeAid directory"})
    results.sort(key=lambda item: item["distance_km"])
    return jsonify({"hospitals": results, "count": len(results)})

# ---------------------------
# Hospital Module
# ---------------------------

@app.route("/add-hospital", methods=["GET", "POST"])
def add_hospital():
    if request.method == "POST":
        hospital_name = request.form["hospital_name"].strip()
        city = request.form.get("city", "").strip()
        address = request.form["address"].strip()
        phone = request.form["phone"].strip()
        services = request.form.get("services", "").strip()
        latitude = valid_coordinate(request.form.get("latitude"), -90, 90)
        longitude = valid_coordinate(request.form.get("longitude"), -180, 180)
        if latitude is None or longitude is None:
            return render_template("add_hospital.html", error="Please capture the hospital's location before saving.")
        conn = get_db()
        conn.execute(
            "INSERT INTO hospitals (hospital_name, city, address, phone, services, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (hospital_name, city, address, phone, services, latitude, longitude)
        )
        conn.commit()
        conn.close()
        return render_template("add_hospital.html", success="Hospital saved with its map location.")
    return render_template("add_hospital.html")

@app.route("/search-hospital", methods=["GET", "POST"])
def search_hospital():

    if request.method == "POST":

        city = request.form["city"]

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM hospitals
            WHERE LOWER(city)=LOWER(?)
            """,
            (city,)
        )

        hospitals = cursor.fetchall()

        conn.close()

        return render_template(
            "hospital_results.html",
            hospitals=hospitals
        )

    return render_template("search_hospital.html")


# ---------------------------
# Emergency Contacts
# ---------------------------

@app.route("/emergency-contacts")
def emergency_contacts():
    return render_template("emergency_contacts.html")


# ---------------------------
# Run App
# ---------------------------
@app.route("/save-language", methods=["POST"])
def save_language():

    language = request.form["language"]

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET language=? WHERE id=1",
        (language,)
    )

    conn.commit()
    conn.close()

    return render_template("dashboard.html")
if __name__ == "__main__":
    app.run(debug=True)
