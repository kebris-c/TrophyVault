# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    trophy_vault.py                                    :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: kebris-c <kebris-c@student.42madrid.c      +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2025/05/16 18:01:49 by kebris-c          #+#    #+#              #
#    Updated: 2025/05/16 18:32:03 by kebris-c         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

#!/usr/bin/env python3

import os
import sys
import json
import sqlite3
import requests
import threading
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QComboBox, QLineEdit, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QMessageBox, QDialog, QFormLayout,
                            QTabWidget, QFileDialog, QTextEdit, QStackedWidget, QSplashScreen,
                            QCheckBox, QGroupBox, QRadioButton, QScrollArea, QFrame, QSizePolicy,
                            QListWidget, QListWidgetItem, QGridLayout, QProgressBar)
from PyQt5.QtGui import QIcon, QPixmap, QColor, QFont, QPalette, QBrush, QPainter, QCursor
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QRect, QEvent, QThread, pyqtSignal

# Constantes
APP_NAME = "Trophy Vault"
APP_VERSION = "2.0.0"
DB_NAME = "trophy_vault.db"
TROPHY_TYPES = ["Bronce", "Plata", "Oro", "Platino", "Oculto", "Especial"]
TROPHY_COLORS = {
    "Bronce": "#CD7F32",
    "Plata": "#C0C0C0",
    "Oro": "#FFD700",
    "Platino": "#E5E4E2",
    "Oculto": "#444444",
    "Especial": "#7F00FF"
}
DEFAULT_PROFILE_PIC = "resources/profile/sololeveling.png"
BACKGROUND_IMG = "resources/background/background.png"
APP_ICON = "resources/app_icon/trophy_icon.ico"
TROPHY_ICONS_DIR = "resources/trophy_icons"

# Lista predefinida de juegos populares de PS5
POPULAR_PS5_GAMES = [
    "Elden Ring", "Marvel's Spider-Man 2", "God of War Ragnarök", "Hogwarts Legacy",
    "Baldur's Gate 3", "Horizon Forbidden West", "Final Fantasy VII Rebirth",
    "Demon's Souls", "Gran Turismo 7", "Returnal", "Ratchet & Clank: Rift Apart",
    "Cyberpunk 2077", "The Last of Us Part I", "Ghost of Tsushima Director's Cut",
    "Resident Evil 4", "Astro's Playroom", "Death Stranding Director's Cut",
    "Deathloop", "FIFA 23", "Call of Duty: Modern Warfare III", "Mortal Kombat 1",
    "Star Wars Jedi: Survivor", "Helldivers 2", "Dragon Ball Z: Kakarot",
    "Fortnite", "Monster Hunter Rise", "Alan Wake 2", "Lies of P", "Expedition 33",
    "Stellar Blade", "Lords of the Fallen", "Like a Dragon: Infinite Wealth",
    "Final Fantasy XVI", "Armored Core VI", "Silent Hill 2"
]

# Trofeos especiales para "Frikazo Estelar"
SPECIAL_TROPHIES = [
    ("Consiguió sobrevivir a una relación jugando 12 horas al día al Monster Hunter: Wild", 
     "Especial", 
     "Cuando el amor y la caza de monstruos chocan, siempre ganará la obsesión por los logros."),
    ("Sorprendentemente para un otaku gamer, tiene novia desde hace más de 10 años", 
     "Platino", 
     "Un logro que desafía todas las estadísticas y estereotipos conocidos."),
    ("Ha reventado más de un objeto por la rabia mientras jugaba", 
     "Bronce", 
     "Mandos, auriculares y otros periféricos sacrificados en nombre de la frustración."),
    ("Ha gastado sus ahorros en videojuegos", 
     "Plata", 
     "Quien necesita comida cuando puedes tener la última expansión."),
    ("Logró platinar más juegos que amigos tiene", 
     "Oro", 
     "La vida social es temporal, los trofeos de platino son eternos."),
    ("Ha logrado ser una referencia para los gamers de su generación", 
     "Platino", 
     "Sus consejos y recomendaciones son seguidos religiosamente."),
    ("Lograr pasar más de un día seguido sin insultar a Ubisoft", 
     "Oro", 
     "Un ejercicio de autocontrol sin precedentes."),
    ("Platinó incluso a sus amistades", 
     "Especial", 
     "Ha conseguido que todos sus amigos sean gamers completos."),
    ("Bordeando la vejez y la adolescencia", 
     "Especial", 
     "30+ años pero con la energía y entusiasmo de un quinceañero cuando se trata de videojuegos."),
    ("Estar informado hasta de los eventos de videojuegos no oficiales", 
     "Plata", 
     "Si hay un rumor sobre un juego, él ya lo sabe."),
    ("No oler mal, siempre", 
     "Platino", 
     "Sorprendentemente, mantiene la higiene personal incluso en las maratones de juego más intensas."),
    ("Record de bebidas energéticas mientras jugaba", 
     "Oro", 
     "Su sangre es 70% cafeína y taurina después de ciertas sesiones."),
    ("Lograr una alimentación de infarto, literalmente", 
     "Bronce", 
     "Pizza, snacks y comida rápida: los pilares de una dieta gamer.")
]

class StyleManager:
    """Gestor de estilos para la aplicación"""
    
    @staticmethod
    def get_main_style():
        return """
            QMainWindow, QDialog {
                background-color: #1E1E2E;
                color: #CDD6F4;
            }
            QWidget {
                color: #CDD6F4;
                font-family: 'Segoe UI', Arial;
            }
            QLabel {
                color: #CDD6F4;
            }
            QPushButton {
                background-color: #313244;
                color: #CDD6F4;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #45475A;
            }
            QPushButton:pressed {
                background-color: #585B70;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #313244;
                border: 1px solid #45475A;
                border-radius: 4px;
                padding: 4px;
                color: #CDD6F4;
            }
            QTableWidget {
                background-color: #313244;
                alternate-background-color: #2A2A3E;
                border: 1px solid #45475A;
                gridline-color: #45475A;
                color: #CDD6F4;
            }
            QTableWidget::item:selected {
                background-color: #74C7EC;
                color: #1E1E2E;
            }
            QHeaderView::section {
                background-color: #1E1E2E;
                border: 1px solid #45475A;
                padding: 4px;
                color: #CDD6F4;
            }
            QTabWidget::pane {
                border: 1px solid #45475A;
                background-color: #1E1E2E;
            }
            QTabBar::tab {
                background-color: #313244;
                color: #CDD6F4;
                border-bottom-color: #45475A;
                padding: 8px 12px;
            }
            QTabBar::tab:selected {
                background-color: #45475A;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
            QProgressBar {
                border: 1px solid #45475A;
                border-radius: 5px;
                text-align: center;
                color: #CDD6F4;
            }
            QProgressBar::chunk {
                background-color: #74C7EC;
                width: 10px;
                margin: 0.5px;
            }
        """
    
    @staticmethod
    def get_trophy_style(trophy_type):
        base_style = """
            QTableWidgetItem {
                padding: 4px;
                border-radius: 3px;
            }
        """
        color = TROPHY_COLORS.get(trophy_type, "#FFFFFF")
        return base_style + f"background-color: {color}40;"  # 40 = 25% opacity


class DatabaseManager:
    """Gestor de la base de datos"""
    
    def __init__(self):
        # Crear directorio de datos si no existe
        os.makedirs("data", exist_ok=True)
        
        # Conectar a la base de datos SQLite
        self.conn = sqlite3.connect(os.path.join("data", DB_NAME))
        self.cursor = self.conn.cursor()
        
        # Crear tablas si no existen
        self._create_tables()
        
    def _create_tables(self):
        """Crear las tablas de la base de datos"""
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                platform TEXT NOT NULL,
                image_path TEXT,
                completion_percentage REAL DEFAULT 0,
                last_played DATE,
                total_trophies INTEGER DEFAULT 0,
                earned_trophies INTEGER DEFAULT 0
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trophies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                type TEXT NOT NULL,
                custom BOOLEAN DEFAULT 0,
                date_earned TIMESTAMP,
                earned BOOLEAN DEFAULT 0,
                image_path TEXT,
                FOREIGN KEY (game_id) REFERENCES games (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS profile (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                psn_id TEXT,
                profile_image TEXT,
                total_bronze INTEGER DEFAULT 0,
                total_silver INTEGER DEFAULT 0,
                total_gold INTEGER DEFAULT 0,
                total_platinum INTEGER DEFAULT 0,
                total_hidden INTEGER DEFAULT 0,
                total_special INTEGER DEFAULT 0,
                first_run BOOLEAN DEFAULT 1
            )
        ''')
        
        self.conn.commit()
    
    def create_default_profile(self, username="Dani", psn_id=""):
        """Crear perfil por defecto si no existe"""
        self.cursor.execute('SELECT * FROM profile WHERE id = 1')
        if not self.cursor.fetchone():
            self.cursor.execute('''
                INSERT INTO profile (id, username, psn_id, profile_image, first_run)
                VALUES (1, ?, ?, ?, 1)
            ''', (username, psn_id, DEFAULT_PROFILE_PIC))
            self.conn.commit()
            return True
        return False
    
    def is_first_run(self):
        """Comprobar si es la primera ejecución"""
        self.cursor.execute('SELECT first_run FROM profile WHERE id = 1')
        result = self.cursor.fetchone()
        return result and result[0] == 1
    
    def set_first_run_completed(self):
        """Marcar primera ejecución como completada"""
        self.cursor.execute('UPDATE profile SET first_run = 0 WHERE id = 1')
        self.conn.commit()
    
    def get_profile(self):
        """Obtener datos del perfil"""
        self.cursor.execute('SELECT * FROM profile WHERE id = 1')
        return self.cursor.fetchone()
    
    def update_profile(self, username, psn_id, profile_image):
        """Actualizar perfil"""
        self.cursor.execute('''
            UPDATE profile 
            SET username = ?, psn_id = ?, profile_image = ?
            WHERE id = 1
        ''', (username, psn_id, profile_image))
        self.conn.commit()
    
    def add_game(self, name, platform, image_path=None):
        """Añadir un nuevo juego"""
        self.cursor.execute('''
            INSERT INTO games (name, platform, image_path, last_played)
            VALUES (?, ?, ?, ?)
        ''', (name, platform, image_path, datetime.now().isoformat()))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def get_games(self):
        """Obtener todos los juegos"""
        self.cursor.execute('''
            SELECT g.id, g.name, g.platform, g.completion_percentage, g.last_played,
                   COUNT(t.id) as trophy_count, SUM(CASE WHEN t.earned = 1 THEN 1 ELSE 0 END) as earned_count,
                   g.image_path
            FROM games g
            LEFT JOIN trophies t ON g.id = t.game_id
            GROUP BY g.id
            ORDER BY g.name
        ''')
        return self.cursor.fetchall()
    
    def get_game_by_name(self, name):
        """Obtener juego por nombre"""
        self.cursor.execute('SELECT id FROM games WHERE name = ?', (name,))
        game = self.cursor.fetchone()
        return game[0] if game else None
    
    def delete_game(self, game_id):
        """Eliminar un juego y sus trofeos"""
        self.cursor.execute('DELETE FROM trophies WHERE game_id = ?', (game_id,))
        self.cursor.execute('DELETE FROM games WHERE id = ?', (game_id,))
        self.conn.commit()
    
    def add_trophy(self, game_id, name, trophy_type, description, custom=False, earned=False, date_earned=None, image_path=None):
        """Añadir un nuevo trofeo"""
        if earned and not date_earned:
            date_earned = datetime.now().isoformat()
            
        self.cursor.execute('''
            INSERT INTO trophies (game_id, name, description, type, custom, earned, date_earned, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (game_id, name, description, trophy_type, custom, earned, date_earned, image_path))
        
        last_id = self.cursor.lastrowid
        
        # Actualizar contadores de trofeos si está conseguido
        if earned:
            self._update_trophy_counters(trophy_type, 1)
            
        # Actualizar progreso del juego
        self._update_game_progress(game_id)
        
        self.conn.commit()
        return last_id
    
    def get_trophies(self, game_id=None, trophy_type=None, search=None, only_earned=False):
        """Obtener trofeos con filtros opcionales"""
        query = '''
            SELECT t.id, t.name, g.name, t.type, t.date_earned, t.description, t.earned, t.image_path, t.game_id
            FROM trophies t
            JOIN games g ON t.game_id = g.id
            WHERE 1=1
        '''
        params = []
        
        if game_id:
            query += " AND t.game_id = ?"
            params.append(game_id)
            
        if trophy_type:
            query += " AND t.type = ?"
            params.append(trophy_type)
            
        if search:
            query += " AND (t.name LIKE ? OR t.description LIKE ?)"
            search_param = f"%{search}%"
            params.append(search_param)
            params.append(search_param)
        
        if only_earned:
            query += " AND t.earned = 1"
            
        query += " ORDER BY t.date_earned DESC, t.name ASC"
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def get_trophy_path(self, trophy_type):
        """Obtener ruta del icono del trofeo por tipo"""
        trophy_file = trophy_type.lower() + ".png"
        return os.path.join(TROPHY_ICONS_DIR, trophy_file)
    
    def earn_trophy(self, trophy_id):
        """Marcar un trofeo como conseguido"""
        # Obtener tipo de trofeo
        self.cursor.execute('SELECT type, earned, game_id FROM trophies WHERE id = ?', (trophy_id,))
        trophy_data = self.cursor.fetchone()
        
        # Si ya está conseguido, no hacer nada
        if trophy_data[1]:
            return False
        
        # Marcar como conseguido
        self.cursor.execute('''
            UPDATE trophies 
            SET earned = 1, date_earned = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), trophy_id))
        
        # Actualizar contadores
        self._update_trophy_counters(trophy_data[0], 1)
        
        # Actualizar progreso del juego
        self._update_game_progress(trophy_data[2])
        
        self.conn.commit()
        return True
    
    def unearn_trophy(self, trophy_id):
        """Desmarcar un trofeo como conseguido"""
        # Obtener tipo de trofeo
        self.cursor.execute('SELECT type, earned, game_id FROM trophies WHERE id = ?', (trophy_id,))
        trophy_data = self.cursor.fetchone()
        
        # Si no está conseguido, no hacer nada
        if not trophy_data[1]:
            return False
        
        # Marcar como no conseguido
        self.cursor.execute('''
            UPDATE trophies 
            SET earned = 0, date_earned = NULL
            WHERE id = ?
        ''', (trophy_id,))
        
        # Actualizar contadores
        self._update_trophy_counters(trophy_data[0], -1)
        
        # Actualizar progreso del juego
        self._update_game_progress(trophy_data[2])
        
        self.conn.commit()
        return True
    
    def _update_trophy_counters(self, trophy_type, increment):
        """Actualizar contadores de trofeos en el perfil"""
        column = None
        if trophy_type == "Bronce":
            column = "total_bronze"
        elif trophy_type == "Plata":
            column = "total_silver"
        elif trophy_type == "Oro":
            column = "total_gold"
        elif trophy_type == "Platino":
            column = "total_platinum"
        elif trophy_type == "Oculto":
            column = "total_hidden"
        elif trophy_type == "Especial":
            column = "total_special"
        
        if column:
            if increment > 0:
                self.cursor.execute(f'UPDATE profile SET {column} = {column} + ? WHERE id = 1', (increment,))
            else:
                self.cursor.execute(f'UPDATE profile SET {column} = {column} - ? WHERE id = 1', (abs(increment),))
    
    def _update_game_progress(self, game_id):
        """Actualizar porcentaje de progreso de un juego"""
        # Contar trofeos totales y conseguidos
        self.cursor.execute('''
            SELECT COUNT(*) as total, SUM(CASE WHEN earned = 1 THEN 1 ELSE 0 END) as earned
            FROM trophies
            WHERE game_id = ?
        ''', (game_id,))
        
        counts = self.cursor.fetchone()
        total = counts[0] or 0
        earned = counts[1] or 0
        
        if total > 0:
            progress = (earned / total) * 100
        else:
            progress = 0
        
        # Actualizar juego
        self.cursor.execute('''
            UPDATE games
            SET completion_percentage = ?, 
                total_trophies = ?,
                earned_trophies = ?,
                last_played = ?
            WHERE id = ?
        ''', (progress, total, earned, datetime.now().isoformat(), game_id))
    
    def get_stats(self):
        """Obtener estadísticas generales"""
        stats = {}
        
        # Total de juegos
        self.cursor.execute('SELECT COUNT(*) FROM games')
        stats['total_games'] = self.cursor.fetchone()[0]
        
        # Juegos completados (100%)
        self.cursor.execute('SELECT COUNT(*) FROM games WHERE completion_percentage = 100')
        stats['completed_games'] = self.cursor.fetchone()[0]
        
        # Total de trofeos
        self.cursor.execute('SELECT COUNT(*) FROM trophies')
        stats['total_trophies'] = self.cursor.fetchone()[0]
        
        # Trofeos conseguidos
        self.cursor.execute('SELECT COUNT(*) FROM trophies WHERE earned = 1')
        stats['earned_trophies'] = self.cursor.fetchone()[0]
        
        # Porcentaje global
        if stats['total_trophies'] > 0:
            stats['global_percentage'] = (stats['earned_trophies'] / stats['total_trophies']) * 100
        else:
            stats['global_percentage'] = 0
        
        # Top juegos por trofeos
        self.cursor.execute('''
            SELECT g.name, g.completion_percentage, 
                   (SELECT COUNT(*) FROM trophies WHERE game_id = g.id) as total,
                   (SELECT COUNT(*) FROM trophies WHERE game_id = g.id AND earned = 1) as earned
            FROM games g
            ORDER BY g.completion_percentage DESC, earned DESC
            LIMIT 10
        ''')
        stats['top_games'] = self.cursor.fetchall()
        
        # Trofeos por tipo
        profile = self.get_profile()
        stats['trophy_counts'] = {
            'Platino': profile[7],
            'Oro': profile[6],
            'Plata': profile[5],
            'Bronce': profile[4],
            'Oculto': profile[8],
            'Especial': profile[9]
        }
        
        # Últimos trofeos conseguidos
        self.cursor.execute('''
            SELECT t.name, g.name, t.type, t.date_earned
            FROM trophies t
            JOIN games g ON t.game_id = g.id
            WHERE t.earned = 1
            ORDER BY t.date_earned DESC
            LIMIT 5
        ''')
        stats['recent_trophies'] = self.cursor.fetchall()
        
        return stats
    
    def get_special_trophies(self):
        """Obtener trofeos especiales (custom)"""
        self.cursor.execute('''
            SELECT t.id, t.name, t.type, t.description, t.earned, t.date_earned
            FROM trophies t
            WHERE t.custom = 1
            ORDER BY t.type, t.name
        ''')
        return self.cursor.fetchall()
    
    def close(self):
        """Cerrar conexión con la base de datos"""
        if self.conn:
            self.conn.close()


class IntroWizard(QDialog):
    """Asistente de configuración inicial"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.selected_games = []
        self.selected_trophies = {}
        
        self.setWindowTitle(f"Bienvenido a {APP_NAME}")
        self.setMinimumSize(800, 600)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        
        # Aplicar estilo
        self.setStyleSheet(StyleManager.get_main_style())
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Stacked widget para las páginas del asistente
        self.wizard_pages = QStackedWidget()
        
        # Crear páginas
        self.create_welcome_page()
        self.create_profile_page()
        self.create_games_selection_page()
        self.create_trophies_page()
        self.create_final_page()
        
        main_layout.addWidget(self.wizard_pages)
        
        # Botones de navegación
        nav_buttons = QWidget()
        nav_layout = QHBoxLayout(nav_buttons)
        
        self.back_btn = QPushButton("Atrás")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        
        self.next_btn = QPushButton("Siguiente")
        self.next_btn.clicked.connect(self.go_next)
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addStretch()
        nav_layout.addWidget(self.next_btn)
        
        main_layout.addWidget(nav_buttons)
    
    def create_welcome_page(self):
        """Crear página de bienvenida"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Logo
        logo_label = QLabel()
        pixmap = QPixmap(APP_ICON)
        logo_label.setPixmap(pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Título
        title = QLabel(f"¡Bienvenido a {APP_NAME}!")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        
        # Descripción
        desc = QLabel(
            "Este asistente te ayudará a configurar tu perfil y añadir tus juegos y trofeos favoritos.\n\n"
            "En unos simples pasos tendrás todo listo para comenzar a llevar un registro de tus logros gaming."
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        
        layout.addStretch()
        layout.addWidget(logo_label)
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(desc)
        layout.addStretch()
        
        self.wizard_pages.addWidget(page)
    
    def create_profile_page(self):
        """Crear página de configuración de perfil"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        # Título
        title = QLabel("Configura tu Perfil")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        
        # Formulario
        form = QWidget()
        form_layout = QFormLayout(form)
        
        profile = self.db_manager.get_profile()
        
        self.username_edit = QLineEdit(profile[1])
        self.psn_id_edit = QLineEdit(profile[2] or "")
        self.psn_id_edit.setPlaceholderText("Tu ID de PlayStation Network")
        
        form_layout.addRow("Nombre:", self.username_edit)
        form_layout.addRow("PSN ID:", self.psn_id_edit)
        
        # Imagen de perfil
        img_widget = QWidget()
        img_layout = QHBoxLayout(img_widget)
        
        self.profile_img_preview = QLabel()
        pixmap = QPixmap(profile[3] or DEFAULT_PROFILE_PIC)
        self.profile_img_preview.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        self.profile_img_path = QLineEdit(profile[3] or DEFAULT_PROFILE_PIC)
        self.profile_img_path.setReadOnly(True)
        
        browse_btn = QPushButton("Cambiar")
        browse_btn.clicked.connect(self.browse_profile_img)
        
        img_layout.addWidget(self.profile_img_preview)
        img_layout.addSpacing(10)
        img_layout.addWidget(self.profile_img_path)
        img_layout.addWidget(browse_btn)

        form_layout.addRow("Imagen de perfil:", img_widget)

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(form)
        layout.addStretch()

        self.wizard_pages.addWidget(page)

    def create_games_selection_page(self):
        """Crear página de selección de juegos"""
        page = QWidget()
        layout = QVBoxLayout(page)

        # Título
        title = QLabel("Selecciona tus Juegos")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))

        desc = QLabel("Elige los juegos que ya has jugado o que quieres tener en tu colección.")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)

        # Lista de juegos
        self.game_list = QListWidget()
        self.game_list.setSelectionMode(QListWidget.MultiSelection)

        # Añadir juegos a la lista
        for game in POPULAR_PS5_GAMES:
            item = QListWidgetItem(game)
            self.game_list.addItem(item)

        # Botón para añadir juego personalizado
        custom_game_widget = QWidget()
        custom_layout = QHBoxLayout(custom_game_widget)

        self.custom_game_edit = QLineEdit()
        self.custom_game_edit.setPlaceholderText("Añadir juego personalizado")

        add_game_btn = QPushButton("Añadir")
        add_game_btn.clicked.connect(self.add_custom_game)

        custom_layout.addWidget(self.custom_game_edit)
        custom_layout.addWidget(add_game_btn)

        layout.addWidget(title)
        layout.addWidget(desc)
        layout.addSpacing(10)
        layout.addWidget(self.game_list)
        layout.addWidget(custom_game_widget)

        self.wizard_pages.addWidget(page)

    def create_trophies_page(self):
        """Crear página de selección de trofeos por juego"""
        page = QWidget()
        layout = QVBoxLayout(page)

        # Título
        self.trophy_page_title = QLabel("Selecciona tus Trofeos")
        self.trophy_page_title.setAlignment(Qt.AlignCenter)
        self.trophy_page_title.setFont(QFont("Segoe UI", 16, QFont.Bold))

        self.trophy_page_desc = QLabel("Marca los trofeos que ya has conseguido para este juego.")
        self.trophy_page_desc.setWordWrap(True)
        self.trophy_page_desc.setAlignment(Qt.AlignCenter)

        # Lista de trofeos (se rellenará dinámicamente)
        self.trophy_list = QListWidget()

        layout.addWidget(self.trophy_page_title)
        layout.addWidget(self.trophy_page_desc)
        layout.addSpacing(10)
        layout.addWidget(self.trophy_list)

        self.wizard_pages.addWidget(page)

    def create_final_page(self):
        """Crear página final"""
        page = QWidget()
        layout = QVBoxLayout(page)

        # Icono de completado
        check_label = QLabel("✅")
        check_label.setAlignment(Qt.AlignCenter)
        check_label.setFont(QFont("Segoe UI", 48))

        # Título
        title = QLabel("¡Todo Listo!")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))

        # Descripción
        desc = QLabel(
            "Tu configuración inicial ha sido completada con éxito.\n\n"
            "Ahora puedes comenzar a usar Trophy Vault para gestionar "
            "tu colección de trofeos y ver tus estadísticas."
        )
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)

        layout.addStretch()
        layout.addWidget(check_label)
        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(desc)
        layout.addStretch()

        self.wizard_pages.addWidget(page)

    def browse_profile_img(self):
        """Abrir diálogo para seleccionar imagen de perfil"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Imágenes (*.png *.jpg *.jpeg)")
        file_dialog.setViewMode(QFileDialog.Detail)

        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            self.profile_img_path.setText(selected_file)

            pixmap = QPixmap(selected_file)
            self.profile_img_preview.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def add_custom_game(self):
        """Añadir juego personalizado a la lista"""
        game_name = self.custom_game_edit.text().strip()
        if game_name:
            # Comprobar si ya existe
            items = self.game_list.findItems(game_name, Qt.MatchExactly)
            if not items:
                item = QListWidgetItem(game_name)
                self.game_list.addItem(item)
                item.setSelected(True)
                self.custom_game_edit.clear()

    def go_next(self):
        """Avanzar a la siguiente página"""
        current_page = self.wizard_pages.currentIndex()

        # Validaciones específicas por página
        if current_page == 0:  # Página de bienvenida
            # No se necesita validación
            pass
        elif current_page == 1:  # Página de perfil
            # Validar nombre de usuario
            if not self.username_edit.text().strip():
                QMessageBox.warning(self, "Datos incompletos", "Por favor, introduce un nombre.")
                return
        elif current_page == 2:  # Página de selección de juegos
            # Obtener juegos seleccionados
            self.selected_games = []
            for i in range(self.game_list.count()):
                item = self.game_list.item(i)
                if item.isSelected():
                    self.selected_games.append(item.text())

            if not self.selected_games:
                QMessageBox.warning(self, "Sin selección", "Por favor, selecciona al menos un juego.")
                return

            # Preparar la primera página de trofeos
            self.current_game_index = 0
            self.prepare_trophy_page()
        elif current_page == 3:  # Página de trofeos
            # Guardar trofeos seleccionados del juego actual
            game_name = self.selected_games[self.current_game_index]
            self.selected_trophies[game_name] = []

            for i in range(self.trophy_list.count()):
                item = self.trophy_list.item(i)
                checkbox = self.trophy_list.itemWidget(item)
                if checkbox and checkbox.isChecked():
                    trophy_data = item.data(Qt.UserRole)
                    self.selected_trophies[game_name].append(trophy_data)

            # Avanzar al siguiente juego o a la página final
            self.current_game_index += 1
            if self.current_game_index < len(self.selected_games):
                self.prepare_trophy_page()
                return  # No avanzar a la siguiente página del wizard
            else:
                # Guardar todos los datos recopilados
                self.save_wizard_data()
        elif current_page == 4:  # Página final
            # Finalizar el asistente
            self.accept()

        # Avanzar a la siguiente página
        next_page = current_page + 1
        if next_page < self.wizard_pages.count():
            self.wizard_pages.setCurrentIndex(next_page)
            self.back_btn.setEnabled(next_page > 0)

            # Cambiar el texto del botón en la última página
            if next_page == self.wizard_pages.count() - 1:
                self.next_btn.setText("Finalizar")

    def go_back(self):
        """Retroceder a la página anterior"""
        current_page = self.wizard_pages.currentIndex()

        # Caso especial para la página de trofeos
        if current_page == 3:
            # Si estamos en un juego posterior al primero, volver al juego anterior
            if self.current_game_index > 0:
                self.current_game_index -= 1
                self.prepare_trophy_page()
                return

        # Retroceder a la página anterior del wizard
        prev_page = current_page - 1
        if prev_page >= 0:
            self.wizard_pages.setCurrentIndex(prev_page)
            self.back_btn.setEnabled(prev_page > 0)
            self.next_btn.setText("Siguiente")

    def prepare_trophy_page(self):
        """Preparar página de trofeos para el juego actual"""
        game_name = self.selected_games[self.current_game_index]

        # Actualizar título y descripción
        self.trophy_page_title.setText(f"Trofeos de {game_name}")
        self.trophy_page_desc.setText(f"Marca los trofeos que ya has conseguido para {game_name} ({self.current_game_index + 1}/{len(self.selected_games)}).")

        # Limpiar lista de trofeos
        self.trophy_list.clear()

        # Aquí añadiríamos trofeos reales si los tuviéramos
        # Por ahora, añadimos algunos genéricos
        trophy_types = ["Platino", "Oro", "Oro", "Plata", "Plata", "Plata", "Bronce", "Bronce", "Bronce", "Bronce", "Oculto"]

        for i, trophy_type in enumerate(trophy_types):
            # Crear ítem y widget personalizado
            item = QListWidgetItem()

            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(5, 2, 5, 2)

            # Icono del trofeo
            icon_label = QLabel()
            trophy_path = os.path.join(TROPHY_ICONS_DIR, trophy_type.lower() + ".png")
            if os.path.exists(trophy_path):
                pixmap = QPixmap(trophy_path)
                icon_label.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))

            # Checkbox y texto
            checkbox = QCheckBox(f"Trofeo {i+1} ({trophy_type})")

            # Guardar datos del trofeo
            trophy_data = {
                "name": f"Trofeo {i+1}",
                "type": trophy_type,
                "description": f"Descripción del trofeo {i+1}"
            }
            item.setData(Qt.UserRole, trophy_data)

            layout.addWidget(icon_label)
            layout.addWidget(checkbox)
            layout.addStretch()

            item.setSizeHint(widget.sizeHint())
            self.trophy_list.addItem(item)
            self.trophy_list.setItemWidget(item, widget)

    def save_wizard_data(self):
        """Guardar todos los datos recopilados en el asistente"""
        # Actualizar perfil
        self.db_manager.update_profile(
            self.username_edit.text().strip(),
            self.psn_id_edit.text().strip(),
            self.profile_img_path.text()
        )

        # Crear juegos y trofeos
        for game_name in self.selected_games:
            # Añadir juego
            game_id = self.db_manager.add_game(
                name=game_name,
                platform="PlayStation 5"
            )

            # Añadir trofeos del juego
            if game_name in self.selected_trophies:
                for trophy_data in self.selected_trophies[game_name]:
                    self.db_manager.add_trophy(
                        game_id=game_id,
                        name=trophy_data["name"],
                        trophy_type=trophy_data["type"],
                        description=trophy_data["description"],
                        earned=True  # Los seleccionados ya los ha conseguido
                    )

        # Añadir trofeos especiales de "Frikazo Estelar"
        frikazo_id = self.db_manager.get_game_by_name("Frikazo Estelar")
        if not frikazo_id:
            frikazo_id = self.db_manager.add_game(
                name="Frikazo Estelar",
                platform="Vida Real"
            )

        # Añadir trofeos especiales
        for trophy_data in SPECIAL_TROPHIES:
            self.db_manager.add_trophy(
                game_id=frikazo_id,
                name=trophy_data[0],
                trophy_type=trophy_data[1],
                description=trophy_data[2],
                custom=True,
                earned=True  # Los trofeos especiales ya están conseguidos
            )

        # Marcar primera ejecución como completada
        self.db_manager.set_first_run_completed()


class TrophyDialog(QDialog):
    """Diálogo para añadir o editar un trofeo"""

    def __init__(self, db_manager, game_id=None, trophy_id=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.game_id = game_id
        self.trophy_id = trophy_id

        self.setWindowTitle("Trofeo")
        self.setMinimumWidth(500)

        # Aplicar estilo
        self.setStyleSheet(StyleManager.get_main_style())

        # Layout principal
        layout = QVBoxLayout(self)

        # Elementos del formulario
        form = QFormLayout()

        # Nombre del trofeo
        self.name_edit = QLineEdit()
        form.addRow("Nombre:", self.name_edit)

        # Descripción
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        form.addRow("Descripción:", self.description_edit)

        # Tipo de trofeo
        self.type_combo = QComboBox()
        for trophy_type in TROPHY_TYPES:
            self.type_combo.addItem(trophy_type)
        form.addRow("Tipo:", self.type_combo)

        # Conseguido
        self.earned_check = QCheckBox("Trofeo conseguido")
        form.addRow("Estado:", self.earned_check)

        # Fecha (solo visible si está conseguido)
        date_widget = QWidget()
        date_layout = QHBoxLayout(date_widget)
        date_layout.setContentsMargins(0, 0, 0, 0)

        self.date_edit = QLineEdit()
        self.date_edit.setPlaceholderText("YYYY-MM-DD HH:MM:SS")
        self.date_edit.setEnabled(False)

        self.now_btn = QPushButton("Ahora")
        self.now_btn.clicked.connect(self.set_date_now)
        self.now_btn.setEnabled(False)

        date_layout.addWidget(self.date_edit)
        date_layout.addWidget(self.now_btn)

        form.addRow("Fecha:", date_widget)

        # Escuchar cambios en el checkbox
        self.earned_check.stateChanged.connect(self.toggle_date)

        # Juego (en caso de que no se haya especificado)
        if not self.game_id:
            self.game_combo = QComboBox()

            # Obtener lista de juegos
            games = self.db_manager.get_games()
            for game in games:
                self.game_combo.addItem(game[1], game[0])

            form.addRow("Juego:", self.game_combo)

        layout.addLayout(form)

        # Botones
        buttons = QHBoxLayout()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)

        self.save_btn = QPushButton("Guardar")
        self.save_btn.clicked.connect(self.save_trophy)

        buttons.addWidget(cancel_btn)
        buttons.addWidget(self.save_btn)

        layout.addLayout(buttons)

        # Si estamos editando, cargar datos
        if self.trophy_id:
            self.load_trophy_data()

    def load_trophy_data(self):
        """Cargar datos del trofeo a editar"""
        # TODO: Implementar carga de datos
        pass

    def toggle_date(self, state):
        """Activar/desactivar campos de fecha"""
        enabled = state == Qt.Checked
        self.date_edit.setEnabled(enabled)
        self.now_btn.setEnabled(enabled)

        if enabled:
            self.set_date_now()

    def set_date_now(self):
        """Establecer fecha actual"""
        now = datetime.now().isoformat(sep=' ', timespec='seconds')
        self.date_edit.setText(now)

    def save_trophy(self):
        """Guardar trofeo"""
        # Validar datos
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "El nombre del trofeo es obligatorio.")
            return

        # Recopilar datos
        description = self.description_edit.toPlainText().strip()
        trophy_type = self.type_combo.currentText()
        earned = self.earned_check.isChecked()

        # Fecha
        date_earned = None
        if earned:
            try:
                date_text = self.date_edit.text().strip()
                if date_text:
                    date_earned = date_text
            except ValueError:
                QMessageBox.warning(self, "Error", "Formato de fecha incorrecto.")
                return

        # ID del juego
        game_id = self.game_id
        if not game_id and hasattr(self, 'game_combo'):
            game_id = self.game_combo.currentData()

        # Guardar en la base de datos
        if self.trophy_id:
            # TODO: Actualizar trofeo existente
            pass
        else:
            # Crear nuevo trofeo
            try:
                self.db_manager.add_trophy(
                    game_id=game_id,
                    name=name,
                    trophy_type=trophy_type,
                    description=description,
                    earned=earned,
                    date_earned=date_earned,
                    custom=True
                )
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el trofeo: {str(e)}")


class GameDialog(QDialog):
    """Diálogo para añadir o editar un juego"""

    def __init__(self, db_manager, game_id=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.game_id = game_id

        self.setWindowTitle("Juego")
        self.setMinimumWidth(500)

        # Aplicar estilo
        self.setStyleSheet(StyleManager.get_main_style())

        # Layout principal
        layout = QVBoxLayout(self)

        # Elementos del formulario
        form = QFormLayout()

        # Nombre del juego
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nombre del juego")
        form.addRow("Nombre:", self.name_edit)

        # Plataforma
        self.platform_combo = QComboBox()
        platforms = ["PlayStation 5", "PlayStation 4", "PlayStation 3", "Xbox Series X|S", "Xbox One", "Nintendo Switch", "PC", "Otra"]
        for platform in platforms:
            self.platform_combo.addItem(platform)
        form.addRow("Plataforma:", self.platform_combo)

        # Imagen del juego
        img_widget = QWidget()
        img_layout = QHBoxLayout(img_widget)
        img_layout.setContentsMargins(0, 0, 0, 0)

        self.image_path_edit = QLineEdit()
        self.image_path_edit.setReadOnly(True)

        browse_btn = QPushButton("Examinar")
        browse_btn.clicked.connect(self.browse_image)

        img_layout.addWidget(self.image_path_edit)
        img_layout.addWidget(browse_btn)

        form.addRow("Imagen:", img_widget)

        layout.addLayout(form)

        # Botones
        buttons = QHBoxLayout()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save_game)

        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)

        layout.addLayout(buttons)

        # Si estamos editando, cargar datos
        if self.game_id:
            self.load_game_data()

    def load_game_data(self):
        """Cargar datos del juego a editar"""
        # TODO: Implementar carga de datos
        pass

    def browse_image(self):
        """Abrir diálogo para seleccionar imagen del juego"""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Imágenes (*.png *.jpg *.jpeg)")
        file_dialog.setViewMode(QFileDialog.Detail)

        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            self.image_path_edit.setText(selected_file)

    def save_game(self):
        """Guardar juego"""
        # Validar datos
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "El nombre del juego es obligatorio.")
            return

        # Recopilar datos
        platform = self.platform_combo.currentText()
        image_path = self.image_path_edit.text().strip() or None

        # Guardar en la base de datos
        if self.game_id:
            # TODO: Actualizar juego existente
            pass
        else:
            # Crear nuevo juego
            try:
                self.db_manager.add_game(
                    name=name,
                    platform=platform,
                    image_path=image_path
                )
                self.accept()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el juego: {str(e)}")


class TrophyVaultApp(QMainWindow):
    """Aplicación principal"""

    def __init__(self):
        super().__init__()

        # Inicializar base de datos
        self.db_manager = DatabaseManager()

        # Crear perfil por defecto si no existe
        self.db_manager.create_default_profile()

        # Configurar interfaz
        self.setup_ui()

        # Mostrar asistente de primera ejecución si es necesario
        if self.db_manager.is_first_run():
            self.show_intro_wizard()

    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(1000, 700)

        # Icono de la aplicación
        self.setWindowIcon(QIcon(APP_ICON))

        # Aplicar estilo
        self.setStyleSheet(StyleManager.get_main_style())

        # Fondo
        if os.path.exists(BACKGROUND_IMG):
            palette = QPalette()
            pixmap = QPixmap(BACKGROUND_IMG)
            palette.setBrush(QPalette.Window, QBrush(pixmap.scaled(
                self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)))
            self.setPalette(palette)

            # Permitir redimensionar y mantener el fondo
            self.setAutoFillBackground(True)

        # Widget central
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Header (info de perfil)
        header = self.create_header()

        # Contenido principal (pestañas)
        content = self.create_content()

        main_layout.addWidget(header)
        main_layout.addWidget(content)

        self.setCentralWidget(central_widget)

    def create_header(self):
        """Crear cabecera con información de perfil"""
        header = QWidget()
        header_layout = QHBoxLayout(header)

        # Obtener datos del perfil
        profile = self.db_manager.get_profile()

        # Imagen de perfil
        profile_pic = QLabel()
        pixmap = QPixmap(profile[3] or DEFAULT_PROFILE_PIC)
        profile_pic.setPixmap(pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # Información del perfil
        profile_info = QWidget()
        info_layout = QVBoxLayout(profile_info)
        info_layout.setContentsMargins(0, 0, 0, 0)

        username_label = QLabel(profile[1])
        username_label.setFont(QFont("Segoe UI", 14, QFont.Bold))

        psn_id_label = QLabel(f"PSN ID: {profile[2] if profile[2] else 'No especificado'}")

        info_layout.addWidget(username_label)
        info_layout.addWidget(psn_id_label)

        # Contador de trofeos
        trophy_counts = QWidget()
        trophy_layout = QHBoxLayout(trophy_counts)
        trophy_layout.setContentsMargins(0, 0, 0, 0)

        # Contar trofeos por tipo
        for i, trophy_type in enumerate(["Platino", "Oro", "Plata", "Bronce", "Oculto", "Especial"]):
            count_widget = QWidget()
            count_layout = QVBoxLayout(count_widget)
            count_layout.setContentsMargins(0, 0, 0, 0)

            # Icono
            icon_label = QLabel()
            trophy_path = os.path.join(TROPHY_ICONS_DIR, trophy_type.lower() + ".png")
            if os.path.exists(trophy_path):
                pixmap = QPixmap(trophy_path)
                icon_label.setPixmap(pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                icon_label.setAlignment(Qt.AlignCenter)

            # Contador
            count = profile[4 + i] if profile[4 + i] is not None else 0
            count_label = QLabel(str(count))
            count_label.setAlignment(Qt.AlignCenter)

            count_layout.addWidget(icon_label)
            count_layout.addWidget(count_label)

            trophy_layout.addWidget(count_widget)

        # Botón de editar perfil
        edit_profile_btn = QPushButton("Editar Perfil")
        edit_profile_btn.clicked.connect(self.edit_profile)

        header_layout.addWidget(profile_pic)
        header_layout.addWidget(profile_info)
        header_layout.addStretch()
        header_layout.addWidget(trophy_counts)
        header_layout.addWidget(edit_profile_btn)

        return header

    def create_content(self):
        """Crear contenido principal con pestañas"""
        tabs = QTabWidget()

        # Pestaña de inicio/dashboard
        dashboard_tab = self.create_dashboard_tab()
        tabs.addTab(dashboard_tab, "Inicio")

        # Pestaña de juegos
        games_tab = self.create_games_tab()
        tabs.addTab(games_tab, "Juegos")

        # Pestaña de trofeos
        trophies_tab = self.create_trophies_tab()
        tabs.addTab(trophies_tab, "Trofeos")

        # Pestaña de trofeos especiales
        special_tab = self.create_special_tab()
        tabs.addTab(special_tab, "Trofeos Especiales")

        return tabs

    def create_dashboard_tab(self):
        """Crear pestaña de inicio/dashboard"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Obtener estadísticas
        stats = self.db_manager.get_stats()

        # Sección de estadísticas generales
        stats_group = QGroupBox("
