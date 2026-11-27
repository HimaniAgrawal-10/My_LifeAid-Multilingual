
# LifeAid – Multilingual Emergency Assistance

LifeAid is a web-based emergency assistance system designed to help users access first-aid guidance, emergency contacts, blood donor information, and nearby hospital details.

## Features

- **Multilingual interface:** Users can select their preferred language during login.
- **Emergency first-aid guides:** Provides guidance for emergencies such as heart attacks, burns, snake bites, bleeding, and choking.
- **Nearby hospital finder:** Uses the user's location to search for nearby hospitals and display them on a map.
- **Blood donor finder:** Allows users to register as donors and search for available donors.
- **Hospital information:** Users can add and search hospital details.
- **Emergency contacts:** Provides access to emergency contact information.

## Technology Stack

- Python
- Flask
- SQLite
- HTML, CSS, JavaScript
- Bootstrap
- Leaflet and OpenStreetMap for map features

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/HimaniAgrawal-10/My_LifeAid-Multilingual.git
cd My_LifeAid-Multilingual
```

### 2. Open the application folder

If `app.py` is inside a subfolder, navigate to that folder before running the application.

### 3. Install dependencies

Install the required Python packages. If the project includes a `requirements.txt` file, run:

```bash
python -m pip install -r requirements.txt
```

If it does not, install the packages required by the project, including Flask:

```bash
python -m pip install flask
```

### 4. Run the application

```bash
python app.py
```

Open the local address shown in the terminal, usually:

```text
http://127.0.0.1:5000
```

## Using the Nearby Hospital Finder

1. Open the Nearby Hospitals feature.
2. Allow location access in your browser.
3. Select a search radius.
4. View the hospitals returned by the map data source and the application's saved hospital records.

Hospital listings depend on available map data and may not include every hospital. For emergencies, contact local emergency services and verify hospital details directly.

## Project Structure

```text
LifeAid/
├── app.py
├── database.db
├── templates/
├── static/
└── README.md
```

*The exact files and folders may vary depending on your project version.*

## Disclaimer

LifeAid is an educational project and is not a substitute for professional medical advice or emergency services. In an emergency, contact local emergency services immediately and follow qualified medical guidance.

## Author

**Himani Agrawal**  
GitHub: [HimaniAgrawal-10](https://github.com/HimaniAgrawal-10)
