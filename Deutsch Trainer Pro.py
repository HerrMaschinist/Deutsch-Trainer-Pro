"""
Deutsch Trainer Pro - Version basierend auf Mathe Trainer Pro, angepasst für Deutschübungen.

Features:
- Klassenstufenspezifische Übungsaufgaben in Deutsch (Klasse 1 bis 4)
- Übungsbereiche: Grammatik, Rechtschreibung, Textverständnis (nach Lehrplan Baden-Württemberg)
- Adaptives Level- und XP-System mit Achievements (Levelaufstieg bei genügend XP)
- Detaillierte Statistiken & Fortschrittsanzeige am Ende jeder Runde
- Logging aller Aktionen (für Debugging und Nachverfolgung)
- Flexible Speicherung der Nutzerdaten (profiles.json im Benutzerverzeichnis unter DeutschTrainerProData)
- Robuste Eingabevalidierung und Fehlermeldungen für Texteingaben
- Erweiterte GUI mit Menüoptionen (Thema ändern, Schriftgröße, Fortschritt zurücksetzen)
"""
import sys
import random
import json
import time
import os
import logging
from enum import Enum
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QStackedWidget, QMessageBox, QComboBox, 
    QProgressBar, QHBoxLayout, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QAction

# Logging-Konfiguration
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

class Difficulty(Enum):
    EINFACH = "Einfach"
    MITTEL = "Mittel"
    SCHWER = "Schwer"

def get_data_dir():
    """
    Ermittelt den Pfad zum Datenordner im Benutzerverzeichnis.
    Hier werden externe Dateien wie profiles.json gespeichert.
    """
    data_dir = os.path.join(os.path.expanduser("~"), "DeutschTrainerProData")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

def resource_path(filename):
    """
    Gibt den absoluten Pfad zu einer Ressourcendatei relativ zum Datenordner zurück.
    """
    return os.path.join(get_data_dir(), filename)

def get_tip_of_the_day():
    """
    Liefert einen zufälligen Tipp (Deutsch lernen).
    """
    tips = [
        "Übung macht den Meister – auch beim Deutschlernen!",
        "Lies regelmäßig Bücher, um dein Sprachgefühl zu verbessern.",
        "Denke an die Großschreibung der Nomen in jedem Satz.",
        "Überprüfe nach dem Schreiben die Rechtschreibung deiner Wörter.",
        "Nimm dir Zeit und lies die Aufgabe sorgfältig durch."
    ]
    return random.choice(tips)

class DeutschTrainerPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deutsch Trainer Pro")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #222; color: white; font-size: 16px;")
        
        # Initiale Variablen für den Trainingszustand
        self.current_solution = None
        self.score = 0
        self.total_problems = 10
        self.current_problem_number = 0
        self.timer_duration = 30000  # 30 Sekunden pro Aufgabe
        self.start_time = None
        self.total_time = 0
        self.correct_answers = 0
        self.wrong_answers = 0

        # Nutzerprofile laden (Punktestand, Level, XP, Achievements)
        self.user_profiles = self.load_profiles()
        self.current_user = None

        # Timer initialisieren
        self.timer = QTimer()
        self.timer.timeout.connect(self.time_out)
    
        # GUI-Elemente aufbauen
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)
        
        # Menü erstellen
        self.create_menus()
        # Seiten erstellen
        self.selection_page = self.create_selection_page()
        self.problem_page = self.create_problem_page()
        self.result_page = self.create_result_page()
        self.stacked_widget.addWidget(self.selection_page)
        self.stacked_widget.addWidget(self.problem_page)
        self.stacked_widget.addWidget(self.result_page)
        
        logging.info("Deutsch Trainer Pro gestartet")
        self.show()
    
    def create_menus(self):
        menubar = self.menuBar()
        settings_menu = menubar.addMenu('Einstellungen')
        
        theme_action = QAction('Thema ändern', self)
        theme_action.triggered.connect(self.change_theme)
        settings_menu.addAction(theme_action)
        
        font_action = QAction('Schriftgröße anpassen', self)
        font_action.triggered.connect(self.change_font_size)
        settings_menu.addAction(font_action)
        
        reset_action = QAction('Fortschritt zurücksetzen', self)
        reset_action.triggered.connect(self.reset_progress)
        settings_menu.addAction(reset_action)
    
    def change_theme(self):
        QMessageBox.information(self, "Thema ändern", "Die Funktion 'Thema ändern' ist noch nicht implementiert.")
    
    def change_font_size(self):
        QMessageBox.information(self, "Schriftgröße anpassen", "Die Funktion 'Schriftgröße anpassen' ist noch nicht implementiert.")
    
    def reset_progress(self):
        reply = QMessageBox.question(
            self, 'Fortschritt zurücksetzen',
            'Bist du sicher, dass du deinen Fortschritt zurücksetzen möchtest?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Setzt den Fortschritt des aktuellen Benutzers zurück
            self.user_profiles[self.current_user] = {
                "score": 0,
                "level": 1,
                "xp": 0,
                "achievements": []
            }
            self.save_profiles()
            QMessageBox.information(self, "Zurückgesetzt", "Dein Fortschritt wurde zurückgesetzt.")
            logging.info("Fortschritt für Benutzer %s zurückgesetzt", self.current_user)
    
    def create_selection_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        
        title = QLabel("Deutsch Trainer Pro")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 32px; font-weight: 700; color: #2c3e50;")
        layout.addWidget(title)

        # Eingabefeld für Name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Dein Name...")
        self.name_input.setStyleSheet("font-size: 18px;")
        self.name_input.setToolTip("Gib deinen Namen ein")
        layout.addWidget(self.name_input)
        
        # Auswahl der Klassenstufe (1-4)
        self.class_selection = QComboBox()
        self.class_selection.addItems(["Klasse 1", "Klasse 2", "Klasse 3", "Klasse 4"])
        self.class_selection.setStyleSheet("font-size: 18px;")
        self.class_selection.setToolTip("Wähle deine Klassenstufe aus")
        layout.addWidget(self.class_selection)

        # Auswahl des Schwierigkeitsgrads (Einfach/Mittel/Schwer)
        self.difficulty_selection = QComboBox()
        self.difficulty_selection.addItems(["Einfach", "Mittel", "Schwer"])
        self.difficulty_selection.setStyleSheet("font-size: 18px;")
        self.difficulty_selection.setToolTip("Wähle den Schwierigkeitsgrad")
        layout.addWidget(self.difficulty_selection)

        # Option für Timer deaktivieren
        self.timer_checkbox = QCheckBox("Timer deaktivieren")
        self.timer_checkbox.setStyleSheet("font-size: 18px;")
        self.timer_checkbox.setToolTip("Aktiviere oder deaktiviere den Timer pro Aufgabe")
        layout.addWidget(self.timer_checkbox)
        
        # Eingabefeld für Anzahl der Aufgaben
        self.num_problems_input = QLineEdit()
        self.num_problems_input.setPlaceholderText("Anzahl der Aufgaben (Standard: 10)")
        self.num_problems_input.setStyleSheet("font-size: 18px;")
        self.num_problems_input.setToolTip("Gib die Anzahl der Aufgaben pro Sitzung ein")
        layout.addWidget(self.num_problems_input)

        # Start-Button
        start_btn = QPushButton("Jetzt starten!")
        start_btn.setStyleSheet("background-color: #008080; color: white; padding: 10px; border-radius: 10px;")
        start_btn.clicked.connect(self.start_trainer)
        layout.addWidget(start_btn)
        
        return widget
    
    def create_problem_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        # Label für die Aufgabenstellung
        self.problem_label = QLabel("Aufgabe: ?")
        self.problem_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.problem_label.setStyleSheet("font-size: 32px; font-weight: 700; color: #2c3e50;")
        layout.addWidget(self.problem_label)

        # Eingabefeld für die Antwort
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Antwort eingeben...")
        self.answer_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.answer_input.setStyleSheet("font-size: 24px;")
        self.answer_input.setToolTip("Gib deine Antwort hier ein")
        # Wenn Enter gedrückt wird, Antwort prüfen
        self.answer_input.returnPressed.connect(self.check_answer)
        layout.addWidget(self.answer_input)

        # Button zum Prüfen der Antwort
        check_btn = QPushButton("Antwort prüfen")
        check_btn.setStyleSheet("background-color: #008080; color: white; padding: 10px; border-radius: 10px;")
        check_btn.clicked.connect(self.check_answer)
        layout.addWidget(check_btn)
        
        # Fortschrittsbalken für Aufgabenfortschritt
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.total_problems)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Label für Punktestand und Level
        self.highscore_label = QLabel("Punkte: 0 | Level: 1")
        self.highscore_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.highscore_label.setStyleSheet("font-size: 20px; color: yellow;")
        layout.addWidget(self.highscore_label)
        
        # Button zurück zum Hauptmenü
        self.back_button = QPushButton("Zurück zum Hauptmenü")
        self.back_button.setStyleSheet("background-color: #d35400; color: white; padding: 10px; border-radius: 10px;")
        self.back_button.clicked.connect(self.go_to_main_menu)
        layout.addWidget(self.back_button)
        
        widget.setLayout(layout)
        return widget
    
    def create_result_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)

        self.result_label = QLabel("Ergebnisse")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet("font-size: 32px; font-weight: 700; color: #2c3e50;")
        layout.addWidget(self.result_label)

        # Statistiken (Punkte, richtige/falsche Antworten, Zeit, Tipp des Tages)
        self.statistics_label = QLabel("")
        self.statistics_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.statistics_label.setStyleSheet("font-size: 24px; color: white;")
        layout.addWidget(self.statistics_label)

        # Achievements-Anzeige
        self.achievement_label = QLabel("")
        self.achievement_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.achievement_label.setStyleSheet("font-size: 20px; color: lightgreen;")
        layout.addWidget(self.achievement_label)

        # Button zum Neustart
        self.restart_button = QPushButton("Erneut spielen")
        self.restart_button.setStyleSheet("background-color: #27ae60; color: white; padding: 10px; border-radius: 10px;")
        self.restart_button.clicked.connect(self.restart_game)
        layout.addWidget(self.restart_button)
        
        # Button zurück zum Hauptmenü (von Ergebnis-Seite aus)
        self.back_to_menu_button = QPushButton("Zum Hauptmenü")
        self.back_to_menu_button.setStyleSheet("background-color: #d35400; color: white; padding: 10px; border-radius: 10px;")
        self.back_to_menu_button.clicked.connect(self.go_to_main_menu)
        layout.addWidget(self.back_to_menu_button)

        widget.setLayout(layout)
        return widget

    def start_trainer(self):
        """
        Startet das Training mit den ausgewählten Einstellungen.
        Initialisiert das Benutzerprofil und die Aufgabengenerierung.
        """
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Fehler", "Bitte gib einen Namen ein.")
            return
        # Benutzerprofil auswählen oder neu anlegen
        self.current_user = name
        if name not in self.user_profiles:
            # Neues Profil erstellen
            self.user_profiles[name] = {
                "score": 0,
                "level": 1,
                "xp": 0,
                "achievements": []
            }
            logging.info("Neues Profil für '%s' erstellt", name)
        else:
            # Sicherstellen, dass alle benötigten Felder existieren
            self.user_profiles[name].setdefault("score", 0)
            self.user_profiles[name].setdefault("level", 1)
            self.user_profiles[name].setdefault("xp", 0)
            self.user_profiles[name].setdefault("achievements", [])
        self.save_profiles()
        
        # Auswahl der Klassenstufe und des Schwierigkeitsgrads speichern
        self.selected_class = self.class_selection.currentText()
        self.selected_difficulty = self.difficulty_selection.currentText()
        
        # Anzahl der Aufgaben festlegen (Standard 10 falls Eingabe leer/ungültig)
        num_problems_text = self.num_problems_input.text().strip()
        if num_problems_text.isdigit():
            self.total_problems = int(num_problems_text)
        else:
            self.total_problems = 10
        
        # Zurücksetzen der Punkte und Zähler für neue Spielsitzung
        self.score = 0
        self.correct_answers = 0
        self.wrong_answers = 0
        self.total_time = 0
        self.current_problem_number = 0
        # Fortschrittsbalken anpassen
        self.progress_bar.setMaximum(self.total_problems)
        self.progress_bar.setValue(0)
        # Level im UI anzeigen (bleibt gleich zu Beginn)
        level = self.user_profiles[self.current_user]['level']
        self.highscore_label.setText(f"Punkte: 0 | Level: {level}")
        # Zum Aufgaben-Screen wechseln
        self.stacked_widget.setCurrentIndex(1)
        logging.info("Training gestartet für Benutzer '%s' (Klasse: %s, Schwierigkeitsgrad: %s)",
                     self.current_user, self.selected_class, self.selected_difficulty)
        # Erste Aufgabe generieren
        self.generate_problem()
    
    def time_out(self):
        """
        Wird aufgerufen, wenn der Timer für eine Aufgabe abläuft.
        Markiert die Aufgabe als falsch und lädt die nächste.
        """
        QMessageBox.warning(self, "Zeit abgelaufen", "Die Zeit ist um! Die nächste Aufgabe wird geladen.")
        self.wrong_answers += 1
        self.current_problem_number += 1
        self.progress_bar.setValue(self.current_problem_number)
        logging.info("Aufgabe %d: Zeit abgelaufen", self.current_problem_number)
        
        if self.current_problem_number >= self.total_problems:
            # Keine Aufgaben mehr übrig, Spiel beenden
            self.end_game()
        else:
            # Nächste Aufgabe generieren
            self.generate_problem()
    
    def generate_problem(self):
        """Wählt basierend auf der Klassenstufe die passende Aufgabenmethode aus und startet ggf. den Timer."""
        klasse = self.selected_class
        logging.debug("Generiere Aufgabe für %s", klasse)
        # Aufgabengenerierung je nach gewählter Klasse
        if klasse == "Klasse 1":
            self.generate_problem_klasse1()
        elif klasse == "Klasse 2":
            self.generate_problem_klasse2()
        elif klasse == "Klasse 3":
            self.generate_problem_klasse3()
        elif klasse == "Klasse 4":
            self.generate_problem_klasse4()
        else:
            QMessageBox.warning(self, "Fehler", "Unbekannte Klassenstufe.")
            logging.error("Unbekannte Klassenstufe: %s", klasse)
            self.go_to_main_menu()
            return

        # Vorbereitungen für die beantwortung der Aufgabe
        self.answer_input.clear()
        if not self.timer_checkbox.isChecked():
            # Timer starten, falls nicht deaktiviert
            self.timer.start(self.timer_duration)
        else:
            self.timer.stop()
        self.start_time = time.time()
    
    # ---------------- Klasse 1 (Deutsch) - Erweiterte Aufgaben ---------------
    def generate_problem_klasse1(self):
        aufgabentyp = random.choice(["Grammatik", "Rechtschreibung", "Textverständnis"])
        
        # Flexiblere Lösungsmöglichkeiten
        aufgaben = {
            "Grammatik": [
                ("Unterstreiche das Nomen: [Hund, läuft, schnell]", ("Hund", "hund")),
                ("Welches Wort ist ein Verb? [Apfel, springt, rot]", ("springt", "Springt")),
                ("Ergänze den Artikel: __ Baum", ("der", "Der", "ein", "Ein"))
            ],
            "Rechtschreibung": [
                ("Welches Wort reimt sich auf 'Haus'? [Maus, Baum, Topf]", ("Maus", "maus")),
                ("Zähle die Buchstaben in 'Schule':", "6"),
                ("Setze den fehlenden Vokal ein: B__ll", ("a", "A"))
            ],
            "Textverständnis": [
                ("Max hat 3 Äpfel und gibt 2 ab. Wie viele hat er noch?", ("1", "eins")),
                ("Die Sonne scheint. Was ziehst du an? [Mantel, T-Shirt]", ("T-Shirt", "Tshirt", "tshirt")),
                ("Welche Farbe hat Gras?", ("grün", "Grün"))
            ]
        }
        
        question, solutions = random.choice(aufgaben[aufgabentyp])
        self.problem_label.setText(question)
        self.current_solution = solutions

    # ---------------- Klasse 2 (Deutsch) - Erweiterte Aufgaben ---------------
    def generate_problem_klasse2(self):
        aufgaben = {
            "Grammatik": [
                ("Bilde den Imperativ: 'du gehst'", ("Geh!", "geh")),
                ("Welches Wort ist im Genitiv? [Vaters Auto, rote Blume]", ("Vaters", "vaters")),
                ("Setze ein Adjektiv ein: Der ___ Vogel singt.", ("schöne", "bunte", "kleine"))
            ],
            "Rechtschreibung": [
                ("Welche Anlauttabelle passt? '__onne' [S, Z, Sch]", ("S", "s")),
                ("Korrektur: 'er geht in die schule'", ("Er geht in die Schule.", "Schule")),
                ("Trenne das Wort: 'Sommerferien'", ("Som-mer-fe-ri-en", "Sommer-ferien"))
            ],
            "Textverständnis": [
                ("Paul hat 5€. Ein Eis kostet 2€. Wie viel bleibt?", ("3€", "3")),
                ("Wie heißt die Hauptfigur in 'Rotkäppchen'?", ("Rotkäppchen", "rotkäppchen")),
                ("Welche Jahreszeit kommt nach Frühling?", ("Sommer", "sommer"))
            ]
        }
        
        aufgabentyp = random.choice(["Grammatik", "Rechtschreibung", "Textverständnis"])
        question, solutions = random.choice(aufgaben[aufgabentyp])
        self.problem_label.setText(question)
        self.current_solution = solutions

    # ---------------- Klasse 3 (Deutsch) - Erweiterte Aufgaben ---------------
    def generate_problem_klasse3(self):
        aufgaben = {
            "Grammatik": [
                ("Nenne das Verb im Satz: 'Der Vogel fliegt hoch.'", "fliegt"),
                ("Nenne das Adjektiv im Satz: 'Der Himmel ist blau.'", "blau"),
                ("In welcher Zeit steht der Satz: 'Ich bin geschwommen.'?", "Perfekt"),
                ("Bilde das Präteritum von 'laufen'.", "lief"),
                ("Welches Wort ist ein Nomen? 'Baum, rennt, schön'", "Baum")
            ],
            "Rechtschreibung": [
                ("Finde 3 Fehler: 'Diße Katze liegt auf dem teppich'", ("Diße, teppich", "diese, Teppich")),
                ("Bilde eine Zusammensetzung aus 'Fahr' und 'Rad'", ("Fahrrad", "fahrrad")),
                ("Schreibe das Wort richtig: 'Schmetterlng'", "Schmetterling"),
                ("Setze ß oder ss ein: 'Fu__ball'", "Fußball")
            ],
            "Textverständnis": [
                ("Warum tragen wir im Winter dicke Kleidung?", ("weil es kalt ist", "Kälte", "warm bleiben")),
                ("Tom geht zur Schule. Unterwegs trifft er Anna.\nWen trifft Tom?", "Anna"),
                ("Der Bär ist hungrig. Er findet Honig.\nWas findet der Bär?", "Honig")
            ]
        }
        
        aufgabentyp = random.choice(["Grammatik", "Rechtschreibung", "Textverständnis"])
        question, solutions = random.choice(aufgaben[aufgabentyp])
        self.problem_label.setText(question)
        self.current_solution = solutions

    # ---------------- Klasse 4 (Deutsch) - Erweiterte Aufgaben ---------------
    def generate_problem_klasse4(self):
        aufgaben = {
            "Grammatik": [
                ("Bilde den Konjunktiv II: 'ich gehe'", ("ich ginge", "ich würde gehen")),
                ("Nenne das Stilmittel: 'Das Haus schlief'", ("Personifikation", "Metapher")),
                ("Nenne das Subjekt im Satz: 'Der alte Mann geht spazieren.'", "Der alte Mann"),
                ("Nenne das Akkusativobjekt im Satz: 'Der Hund fängt den Ball.'", "den Ball")
            ],
            "Rechtschreibung": [
                ("Schreibe den Satz korrekt: 'gestern waren Wir im zoo'", "Gestern waren wir im Zoo."),
                ("Welches Wort ist richtig geschrieben: 'wahrscheinlich' oder 'wahr scheinlich'?", "wahrscheinlich"),
                ("Wie schreibt man 'Fluss' im Plural?", "Flüsse"),
                ("Setze das Komma richtig: 'Ich mag Hunde Katzen und Vögel.'", "Ich mag Hunde, Katzen und Vögel.")
            ],
            "Textverständnis": [
                ("Interpretiere: 'Die Uhr tickt laut.' Was könnte das bedeuten?", ("Eile", "Stress", "Zeitdruck")),
                ("Die Sonne scheint hell. Tina trägt eine Sonnenbrille.\nWas trägt Tina?", "eine Sonnenbrille"),
                ("Laura hat Durst. Sie trinkt ein Glas Wasser.\nWarum trinkt Laura Wasser?", ("Weil sie Durst hat.", "Sie hat Durst."))
            ]
        }
        
        aufgabentyp = random.choice(["Grammatik", "Rechtschreibung", "Textverständnis"])
        question, solutions = random.choice(aufgaben[aufgabentyp])
        self.problem_label.setText(question)
        self.current_solution = solutions

    def get_user_answer(self):
        """
        Liest die Antwort aus dem Eingabefeld aus und führt grundlegende Validierung durch.
        Bei Textaufgaben wird der eingegebene Text unverändert zurückgegeben.
        """
        text = self.answer_input.text().strip()
        if text == "":
            raise ValueError("Bitte gib eine Antwort ein.")
        # Bei Deutschübungen behandeln wir alle Antworten als Text (Strings)
        return text

    def validate_answer(self, user_answer):
        """
        Prüft, ob die gegebene Antwort mit der Lösung übereinstimmt.
        Für Textantworten muss die Zeichenfolge exakt mit der erwarteten übereinstimmen (Groß-/Kleinschreibung beachten).
        Bei mehreren zulässigen Antworten wird geprüft, ob eine davon getroffen wurde.
        """
        # Normalisierung der Eingabe
        user_answer = user_answer.strip().lower().replace(" ", "").replace(".", "").replace(",", "")
        
        if isinstance(self.current_solution, (tuple, list)):
            solutions = [str(sol).lower().strip().replace(" ", "") for sol in self.current_solution]
            return user_answer in solutions
        
        solution = str(self.current_solution).lower().strip().replace(" ", "")
        return user_answer == solution

    def check_answer(self):
        """
        Wertet die gegebene Antwort aus, aktualisiert Statistik und Level/XP und lädt die nächste Aufgabe.
        """
        try:
            end_time = time.time()
            time_taken = end_time - self.start_time
            self.total_time += time_taken

            user_answer = self.get_user_answer()
            if self.validate_answer(user_answer):
                # Antwort korrekt
                self.score += 10
                self.correct_answers += 1
                # XP gutschreiben und Level ggf. erhöhen
                self.user_profiles[self.current_user]['xp'] += 10
                QMessageBox.information(self, "Richtig!", "Super, die Antwort ist korrekt!")
                logging.info("Aufgabe %d richtig gelöst", self.current_problem_number + 1)
            else:
                # Antwort falsch
                self.wrong_answers += 1
                # Korrekte Lösung darstellen (bei mehreren akzeptablen Lösungen nur die erste anzeigen)
                if isinstance(self.current_solution, (tuple, list)):
                    correct_solution_display = self.current_solution[0]
                else:
                    correct_solution_display = self.current_solution
                QMessageBox.warning(self, "Falsch!", f"Leider falsch, die richtige Antwort war {correct_solution_display}.")
                logging.info("Aufgabe %d falsch gelöst", self.current_problem_number + 1)
            # Level ggf. aktualisieren (und Achievement hinzufügen)
            self.update_level()
            # Nächste Aufgabe vorbereiten
            self.current_problem_number += 1
            self.progress_bar.setValue(self.current_problem_number)
            level = self.user_profiles[self.current_user]['level']
            # Punktestand und Level anzeigen
            self.highscore_label.setText(f"Punkte: {self.score} | Level: {level}")
            if self.current_problem_number >= self.total_problems:
                # Alle Aufgaben geschafft -> Endergebnis anzeigen
                self.end_game()
            else:
                # Weitere Aufgaben verfügbar -> nächste generieren
                self.generate_problem()
        except ValueError as e:
            # Eingabevalidierungs-Fehler (z.B. leere Eingabe)
            QMessageBox.warning(self, "Fehler", str(e))
            logging.error("Fehler bei der Eingabe: %s", e)

    def update_level(self):
        """
        Aktualisiert das Level basierend auf den gesammelten XP.
        Jedes neue Level erfordert XP = aktuelles Level * 100.
        Schaltet ein Achievement frei, wenn ein neues Level erreicht wurde.
        """
        xp = self.user_profiles[self.current_user]['xp']
        level = self.user_profiles[self.current_user]['level']
        required_xp = level * 100
        if xp >= required_xp:
            # Levelaufstieg
            self.user_profiles[self.current_user]['level'] += 1
            new_level = self.user_profiles[self.current_user]['level']
            achievement_msg = f"Level {new_level} erreicht!"
            # Achievement nur hinzufügen, wenn noch nicht vorhanden
            if achievement_msg not in self.user_profiles[self.current_user]['achievements']:
                self.user_profiles[self.current_user]['achievements'].append(achievement_msg)
            QMessageBox.information(self, "Level up!", f"Gratulation! Du bist jetzt Level {new_level}!\n{achievement_msg}")
            logging.info("Benutzer '%s' hat %s", self.current_user, achievement_msg)
            self.save_profiles()

    def end_game(self):
        """
        Beendet das aktuelle Spiel und zeigt die Ergebnisse sowie einen Tipp des Tages an.
        """
        # Timer stoppen, falls noch aktiv
        self.timer.stop()
        avg_time = self.total_time / max(self.correct_answers + self.wrong_answers, 1)
        tip = get_tip_of_the_day()
        # Statistiken zusammenstellen
        self.statistics_label.setText(
            f"Du hast {self.score} Punkte erzielt!\n"
            f"Korrekte Antworten: {self.correct_answers}\n"
            f"Falsche Antworten: {self.wrong_answers}\n"
            f"Durchschnittliche Zeit pro Aufgabe: {avg_time:.2f} Sekunden\n\n"
            f"Tipp des Tages: {tip}"
        )
        # Erreichte Achievements anzeigen (falls vorhanden)
        achievements = self.user_profiles[self.current_user].get("achievements", [])
        if achievements:
            self.achievement_label.setText("Erreichte Achievements: " + ", ".join(achievements))
        else:
            self.achievement_label.setText("")
        # Profil speichern (Punkte/XP)
        self.save_profiles()
        # Ergebnis-Seite anzeigen
        self.stacked_widget.setCurrentIndex(2)
        logging.info("Training beendet für %s", self.current_user)

    def restart_game(self):
        """
        Startet eine neue Runde mit den gleichen Einstellungen (Klasse, Schwierigkeit, Anzahl Aufgaben).
        """
        # Zähler und Score zurücksetzen
        self.score = 0
        self.correct_answers = 0
        self.wrong_answers = 0
        self.total_time = 0
        self.current_problem_number = 0
        self.progress_bar.setValue(0)
        level = self.user_profiles[self.current_user]['level']
        self.highscore_label.setText(f"Punkte: 0 | Level: {level}")
        # Zurück zur Aufgaben-Seite und neue Aufgabe generieren
        self.stacked_widget.setCurrentIndex(1)
        self.generate_problem()
        logging.info("Training neu gestartet für %s", self.current_user)

    def go_to_main_menu(self):
        """
        Kehrt zurück zur Hauptmenü-Seite (Auswahlseite).
        """
        self.stacked_widget.setCurrentIndex(0)
        self.timer.stop()
        logging.info("Zurück zum Hauptmenü")

    def save_profiles(self):
        """
        Speichert die Nutzerprofile (Score, Level, XP, Achievements) in einer JSON-Datei.
        """
        profiles_path = resource_path("profiles.json")
        try:
            with open(profiles_path, "w") as f:
                json.dump(self.user_profiles, f)
        except Exception as e:
            logging.error("Fehler beim Speichern der Profile: %s", e)

    def load_profiles(self):
        """
        Lädt die Nutzerprofile aus der JSON-Datei. Falls keine Datei existiert, wird ein leeres Dictionary zurückgegeben.
        """
        profiles_path = resource_path("profiles.json")
        try:
            with open(profiles_path, "r") as f:
                profiles = json.load(f)
                return profiles
        except FileNotFoundError:
            return {}
        except Exception as e:
            logging.error("Fehler beim Laden der Profile: %s", e)
            return {}

# Hauptprogrammstart
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DeutschTrainerPro()
    sys.exit(app.exec())