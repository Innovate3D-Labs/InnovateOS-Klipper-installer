# Contributing to InnovateOS Klipper Installer

## 👋 Willkommen

Danke für dein Interesse an InnovateOS! Wir freuen uns über jede Unterstützung.

## 🤝 Wie du beitragen kannst

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Committe deine Änderungen (`git commit -m 'Add some AmazingFeature'`)
4. Push den Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

## 📝 Pull Request Prozess

1. Aktualisiere die README.md mit Details zu deinen Änderungen
2. Füge Tests für neue Funktionen hinzu
3. Stelle sicher, dass alle Tests erfolgreich sind
4. Folge dem Code-Style des Projekts

## 🔍 Code Review

- Jeder Pull Request wird von mindestens einem Maintainer geprüft
- Feedback wird innerhalb von 48 Stunden gegeben
- Änderungen können angefordert werden

## 📋 Issue Guidelines

### Bugs melden

1. Überprüfe ob der Bug bereits gemeldet wurde
2. Nutze die Issue-Template
3. Beschreibe:
   - Erwartetes Verhalten
   - Aktuelles Verhalten
   - Schritte zum Reproduzieren
   - System-Informationen

### Feature Requests

1. Beschreibe das Feature
2. Erkläre den Nutzen
3. Schlage mögliche Implementierungen vor

## 🏗️ Entwicklungsumgebung

1. Clone das Repository:
```bash
git clone https://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer.git
```

2. Installiere die Abhängigkeiten:
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

3. Starte die Entwicklungsserver:
```bash
# Backend
cd backend
python -m uvicorn main:app --reload

# Frontend
cd frontend
npm run serve
```

## 🧪 Tests

```bash
# Backend Tests
cd backend
pytest

# Frontend Tests
cd frontend
npm run test:unit
```

## 📚 Dokumentation

- Aktualisiere die Dokumentation für neue Features
- Füge JSDoc/Docstrings für neue Funktionen hinzu
- Halte die API-Dokumentation aktuell

## 🔒 Security

- Melde Sicherheitslücken direkt an security@innovate3d-labs.com
- Folge verantwortungsvoller Offenlegung
- Verschlüssele sensitive Informationen

## 📜 Code of Conduct

Dieses Projekt folgt dem [Contributor Covenant](https://www.contributor-covenant.org/version/2/0/code_of_conduct/). 

## 📝 Lizenz

Mit deinem Beitrag stimmst du zu, dass dein Code unter der MIT-Lizenz veröffentlicht wird.
