# Jagdzeiten Brandenburg

Private Seite für Freunde (nicht in Suchmaschinen): https://cocoscodes.github.io/jagdzeiten-brandenburg/

Alle Jagd- und Schonzeiten in Brandenburg auf einer Zeitachse, mit Countdown, Sonnenzeiten und Hochsitz-Ansicht.

- Daten stehen im Block `DATA` / `META` in `src/src.html`.
- Bauen: `python3 src/build.py src/src.html .` (braucht `pip install qrcode pillow`).
- Monatliche Prüfung gegen § 5 BbgJagdDV und JagdzeitV; geänderte Zeilen bekommen `changed: "YYYY-MM-DD"` und einen Eintrag in `META.changes`.

Keine Rechtsberatung, maßgeblich ist der amtliche Text.
