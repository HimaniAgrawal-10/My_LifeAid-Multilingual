# LifeAid – Multilingual Emergency Healthcare Platform

LifeAid is a multilingual emergency healthcare platform designed to help users access first-aid guidance, find blood donors, search for hospitals, and access emergency contacts during emergencies.

Users can select their preferred language and navigate the website in a language that is easier for them to understand.

## 🚀 Features

- **Multilingual Website:** Select a preferred language to translate website content.
- **First-Aid Guidance:** Access guidance for heart attacks, burns, snake bites, bleeding, and choking.
- **Blood Donor Finder:** Search for blood donors by blood group and city.
- **Nearby Blood Donor Finder:** Use browser GPS to find donors who have explicitly consented to share their approximate location and contact details.
- **Nearby Hospital Finder:** Find mapped hospitals and clinics around the current location using OpenStreetMap, plus saved LifeAid directory entries.
- **Distance Calculation:** Sort nearby records by approximate distance in kilometres.
- **Hospital Search:** Find hospitals using available location and contact information.
- **Emergency Contacts:** Access emergency contact information.
- **User Authentication:** Register and log in to the platform.
- **Responsive Interface:** Navigate the website through a Bootstrap-based interface.

## 🌐 Supported Languages

LifeAid supports language selection for:

- English
- Hindi
- Urdu
- Gujarati
- Marathi
- Punjabi
- Bengali
- Tamil
- Telugu

*Online translation requires an internet connection. Translation availability and accuracy may vary.*

## 🛠️ Technologies Used

- Python
- Flask
- SQLite
- HTML5
- CSS3
- JavaScript
- Bootstrap
- Google Translate integration

## 💻 Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/HimaniAgrawal-10/LifeAid-Multilingual-Prj.git
```

### 2. Open the project folder

```bash
cd LifeAid-Multilingual-Prj
```

### 3. Install Flask

Make sure Python is installed on your computer.

```bash
python -m pip install flask
```

If the project includes a `requirements.txt` file, you can install its listed dependencies using:

```bash
python -m pip install -r requirements.txt
```

### 4. Run the application

```bash
python app.py
```

### 5. Open LifeAid in your browser

Visit:

http://127.0.0.1:5000/login

Register or log in, select your preferred language, and explore the available features.

## 📁 Project Structure

```text
LIFE_AID--main/
├── app.py
├── database.db
├── requirements.txt
├── templates/
├── static/
└── README.md
```

*The exact files and folders may vary depending on the current project version.*

## 🔮 Future Improvements

- Improve translation coverage and accuracy across all pages.
- Add verified emergency service information.
- Improve mobile accessibility.
- Deploy the application to a public hosting platform.
- Strengthen authentication and data protection.

## ⚠️ Disclaimer

LifeAid is an educational project and is not a substitute for professional medical advice or emergency services. First-aid information and translations should be verified by qualified professionals before real-world use.

## 👩‍💻 Author

**Himani Agrawal**

GitHub: [HimaniAgrawal-10](https://github.com/HimaniAgrawal-10)

Project Repository: [LifeAid-Multilingual-Prj](https://github.com/HimaniAgrawal-10/LifeAid-Multilingual-Prj)


## 📍 Location-based finder setup

- Open the app using `http://127.0.0.1:5000` or deploy it over HTTPS. Browser geolocation requires a secure context (localhost is allowed for local testing).
- Hospital directory entries added through LifeAid must have their coordinates captured at the facility. Add the services offered, such as Emergency, ICU, Blood Bank or Ambulance.
- Donors can optionally capture and share their approximate coordinates. They appear in nearby searches only after ticking the location-sharing consent checkbox. Existing donor rows remain in the database but will not appear in GPS searches until the donor updates/registers with consent and coordinates.
- Nearby public hospital/clinic listings are fetched from OpenStreetMap's Overpass service. Data may be incomplete or outdated; call facilities to verify services and availability.
- Leaflet map tiles and OpenStreetMap search require an internet connection.
- The database is upgraded automatically on startup by adding nullable location columns; existing records are preserved. Back up `database.db` before deployment.

### New routes

- `/nearby-hospitals` – interactive nearby hospital map.
- `/nearby-donors` – nearby donor map with blood-group and radius filters.
- `/api/saved-hospitals` – returns saved LifeAid hospitals within a requested radius.
- `/api/nearby-donors` – returns consenting donor records within a requested radius.
