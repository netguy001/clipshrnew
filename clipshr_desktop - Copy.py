import sys
import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import yt_dlp
import io
import urllib.request
from urllib.parse import urlparse

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QCheckBox,
    QProgressBar,
    QMessageBox,
    QGroupBox,
    QGridLayout,
    QTabWidget,
    QDialog,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QRadioButton,
    QButtonGroup,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QSizePolicy,
    QSplitter,
)
from PyQt5.QtCore import (
    Qt,
    QThread,
    pyqtSignal,
    QSize,
    QDir,
    QUrl,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
)
from PyQt5.QtGui import (
    QFont,
    QIcon,
    QPixmap,
    QColor,
    QPalette,
    QDesktopServices,
    QPainter,
)


# --- Configuration Files ---
CONFIG_FILE = "config.json"
HISTORY_FILE = "history.json"

# --- Professional Color Palettes (Improved & Extended) ---
PALETTES = {
    "light": {
        "name": "Light Mode (Default)",
        "BG_MAIN": "#F5F7FA",
        "BG_CARD": "#FFFFFF",
        "TEXT_PRIMARY": "#2C3E50",
        "TEXT_SECONDARY": "#7F8C8D",
        "ACCENT_BLUE": "#3498DB",
        "ACCENT_GREEN": "#27AE60",
        "ACCENT_RED": "#E74C3C",
        "ACCENT_ORANGE": "#E67E22",
        "BORDER": "#E1E8ED",
    },
    "dark": {
        "name": "Dark Mode (Professional)",
        "BG_MAIN": "#1E2430",
        "BG_CARD": "#2C3440",
        "TEXT_PRIMARY": "#E8EAED",
        "TEXT_SECONDARY": "#9AA0A6",
        "ACCENT_BLUE": "#5DADE2",
        "ACCENT_GREEN": "#2ECC71",
        "ACCENT_RED": "#EC7063",
        "ACCENT_ORANGE": "#F39C12",
        "BORDER": "#404854",
    },
    "ocean": {
        "name": "Ocean Blue",
        "BG_MAIN": "#0A1929",
        "BG_CARD": "#132F4C",
        "TEXT_PRIMARY": "#B2BAC2",
        "TEXT_SECONDARY": "#6B7A90",
        "ACCENT_BLUE": "#66B2FF",
        "ACCENT_GREEN": "#5BE49B",
        "ACCENT_RED": "#FF6B6B",
        "ACCENT_ORANGE": "#FFA94D",
        "BORDER": "#1E3A5F",
    },
    "forest": {
        "name": "Forest Green",
        "BG_MAIN": "#F1F8F4",
        "BG_CARD": "#FFFFFF",
        "TEXT_PRIMARY": "#1B4332",
        "TEXT_SECONDARY": "#52796F",
        "ACCENT_BLUE": "#2D6A4F",
        "ACCENT_GREEN": "#40916C",
        "ACCENT_RED": "#D32F2F",
        "ACCENT_ORANGE": "#F4A261",
        "BORDER": "#D8F3DC",
    },
    "midnight": {
        "name": "Midnight Purple",
        "BG_MAIN": "#1A1625",
        "BG_CARD": "#2D2438",
        "TEXT_PRIMARY": "#E0DEF2",
        "TEXT_SECONDARY": "#9D97B5",
        "ACCENT_BLUE": "#9D4EDD",
        "ACCENT_GREEN": "#06FFA5",
        "ACCENT_RED": "#FF006E",
        "ACCENT_ORANGE": "#FFBE0B",
        "BORDER": "#3E3551",
    },
}


def generate_qss(palette_key):
    """Generates professional QSS stylesheet based on selected palette."""
    if palette_key not in PALETTES:
        palette_key = "light"
    p = PALETTES[palette_key]

    # Calculate hover/press colors
    accent_qcolor = QColor(p["ACCENT_BLUE"])
    accent_hover = accent_qcolor.lighter(115).name()
    accent_press = accent_qcolor.darker(115).name()

    # Determine if dark theme
    is_dark = QColor(p["BG_MAIN"]).lightness() < 128
    selection_bg = (
        QColor(p["ACCENT_BLUE"]).lighter(150).name()
        if not is_dark
        else QColor(p["ACCENT_BLUE"]).darker(150).name()
    )

    qss = f"""
        /* ===== GENERAL STYLES ===== */
        QMainWindow, QWidget {{
            background-color: {p['BG_MAIN']};
            color: {p['TEXT_PRIMARY']};
            font-family: "Segoe UI", "Roboto", "Inter", sans-serif;
            font-size: 10pt;
        }}
        
        QLabel {{ 
            color: {p['TEXT_PRIMARY']};
            background: transparent;
        }}

        /* ===== TABS ===== */
        QTabWidget::pane {{ 
            border: none;
            background-color: {p['BG_MAIN']};
            border-radius: 8px;
        }}
        QTabBar::tab {{
            background: {p['BG_CARD']}; 
            border: 1px solid {p['BORDER']};
            border-bottom: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 12px 24px;
            margin-right: 4px;
            font-weight: 500;
            color: {p['TEXT_SECONDARY']};
        }}
        QTabBar::tab:selected {{
            background: {p['BG_MAIN']};
            color: {p['ACCENT_BLUE']};
            font-weight: 600;
            border-bottom: 3px solid {p['ACCENT_BLUE']};
        }}
        QTabBar::tab:hover {{
            background: {QColor(p['BG_CARD']).lighter(105).name()};
        }}

        /* ===== BUTTONS ===== */
        QPushButton {{
            background-color: {p['ACCENT_BLUE']};
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            font-weight: 600;
            min-height: 38px;
            font-size: 10pt;
        }}
        QPushButton:hover {{
            background-color: {accent_hover};
        }}
        QPushButton:pressed {{
            background-color: {accent_press};
        }}
        QPushButton:disabled {{
            background-color: {p['TEXT_SECONDARY']};
            color: {p['BG_CARD']};
        }}
        
        QPushButton#SecondaryButton {{
            background-color: {p['BG_CARD']};
            color: {p['TEXT_PRIMARY']};
            border: 2px solid {p['BORDER']};
        }}
        QPushButton#SecondaryButton:hover {{
            background-color: {QColor(p['BG_CARD']).lighter(105).name()};
            border-color: {p['ACCENT_BLUE']};
        }}
        
        QPushButton#DangerButton {{
            background-color: {p['ACCENT_RED']};
        }}
        QPushButton#DangerButton:hover {{
            background-color: {QColor(p['ACCENT_RED']).darker(115).name()};
        }}

        /* ===== INPUT FIELDS ===== */
        QLineEdit {{
            border: 2px solid {p['BORDER']};
            padding: 12px 16px;
            border-radius: 8px;
            background-color: {p['BG_CARD']};
            color: {p['TEXT_PRIMARY']};
            min-height: 40px;
            font-size: 10pt;
        }}
        QLineEdit:focus {{
            border-color: {p['ACCENT_BLUE']};
        }}

        /* ===== GROUP BOXES (CARDS) ===== */
        QGroupBox {{
            background-color: {p['BG_CARD']};
            border: 1px solid {p['BORDER']};
            border-radius: 12px;
            margin-top: 20px; 
            padding: 20px 15px 15px 15px;
            font-weight: 600;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 5px 10px;
            color: {p['ACCENT_BLUE']};
            font-weight: bold;
            font-size: 11pt;
            background-color: {p['BG_CARD']};
            border-radius: 4px;
        }}

        /* ===== PROGRESS BAR ===== */
        QProgressBar {{
            border: none;
            border-radius: 8px;
            text-align: center;
            color: {p['TEXT_PRIMARY']};
            background-color: {p['BORDER']};
            height: 28px;
            font-weight: 600;
        }}
        QProgressBar::chunk {{
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {p['ACCENT_GREEN']}, stop:1 {p['ACCENT_BLUE']});
            border-radius: 8px;
        }}

        /* ===== TABLE WIDGET ===== */
        QTableWidget {{
            background-color: {p['BG_CARD']};
            border: 1px solid {p['BORDER']};
            border-radius: 8px;
            gridline-color: {p['BORDER']};
            selection-background-color: {selection_bg};
        }}
        QHeaderView::section {{
            background-color: {p['BG_CARD']};
            color: {p['ACCENT_BLUE']};
            padding: 10px;
            border: none;
            border-bottom: 2px solid {p['BORDER']};
            font-weight: bold;
            font-size: 10pt;
        }}
        
        /* ===== LIST WIDGET ===== */
        QListWidget {{
            border: 1px solid {p['BORDER']};
            border-radius: 8px;
            background-color: {p['BG_CARD']};
            padding: 8px;
            outline: none;
        }}
        QListWidget::item {{
            margin-bottom: 6px;
            padding: 12px;
            background-color: {p['BG_MAIN']}; 
            border: 1px solid {p['BORDER']};
            border-radius: 8px;
            font-size: 10pt;
        }}
        QListWidget::item:hover {{
            background-color: {QColor(p['BG_MAIN']).lighter(105).name()};
            border-color: {p['ACCENT_BLUE']};
        }}
        QListWidget::item:selected {{
            background-color: {selection_bg};
            border: 2px solid {p['ACCENT_BLUE']};
            color: {p['TEXT_PRIMARY']};
        }}
        
        /* ===== CHECKBOX ===== */
        QCheckBox {{
            color: {p['TEXT_PRIMARY']};
            spacing: 8px;
        }}
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
            border: 2px solid {p['BORDER']};
            background-color: {p['BG_CARD']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {p['ACCENT_BLUE']};
            border-color: {p['ACCENT_BLUE']};
        }}
        
        /* ===== RADIO BUTTON ===== */
        QRadioButton {{
            color: {p['TEXT_PRIMARY']};
            spacing: 8px;
            padding: 6px;
        }}
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 2px solid {p['BORDER']};
            background-color: {p['BG_CARD']};
        }}
        QRadioButton::indicator:checked {{
            background-color: {p['ACCENT_BLUE']};
            border-color: {p['ACCENT_BLUE']};
        }}
        
        /* ===== SCROLL AREA ===== */
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        QScrollBar:vertical {{
            background: {p['BG_MAIN']};
            width: 12px;
            border-radius: 6px;
        }}
        QScrollBar::handle:vertical {{
            background: {p['BORDER']};
            border-radius: 6px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {p['ACCENT_BLUE']};
        }}
    """
    return qss


# --- Utility Functions ---


def load_config():
    """Loads configuration with all default values."""
    default_config = {
        "media_folder": "media",
        "default_compress": True,
        "theme": "light",
        "window_width": 1400,
        "window_height": 900,
    }

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                if config["theme"] not in PALETTES:
                    config["theme"] = "light"
                return config
        except json.JSONDecodeError:
            print("Error reading config.json. Using defaults.")
            return default_config
    return default_config


def save_config(config):
    """Saves the current configuration."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)


def get_media_folder():
    """Returns the absolute path to the media folder."""
    config = load_config()
    return os.path.abspath(config["media_folder"])


def load_db():
    """Loads the download history database."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Error reading history.json. Starting fresh.")
            return []
    return []


def save_db(data):
    """Saves the download history database."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def format_bytes(size_bytes):
    """Converts bytes to human-readable format."""
    if size_bytes is None:
        return "N/A"
    if size_bytes == 0:
        return "0 B"

    size_name = ("B", "KB", "MB", "GB", "TB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {size_name[i]}"


def is_image_url(url):
    """Checks if URL is a direct image file."""
    if not url:
        return False
    path = urlparse(url).path
    if not path:
        return False
    ext = Path(path).suffix.lower()
    return ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".svg"]


# --- Enhanced Loading Overlay with Animation ---


class LoadingOverlay(QWidget):
    """Professional loading overlay with animated spinner."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # Semi-transparent dark background
        self.setStyleSheet(
            """
            LoadingOverlay {
                background-color: rgba(0, 0, 0, 150);
                border-radius: 12px;
            }
        """
        )

        # Layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Spinning loader label
        self.spinner_label = QLabel()
        self.spinner_label.setFixedSize(80, 80)
        self.spinner_label.setStyleSheet("background: transparent;")
        layout.addWidget(self.spinner_label, alignment=Qt.AlignCenter)

        # Message label
        self.message_label = QLabel("Loading...")
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet(
            """
            color: white; 
            font-size: 16pt; 
            font-weight: 600;
            background: transparent;
            padding: 10px;
        """
        )
        layout.addWidget(self.message_label)

        # Spinner animation
        self.rotation_angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate_spinner)

        self.hide()

    def rotate_spinner(self):
        """Rotates the spinner animation."""
        self.rotation_angle = (self.rotation_angle + 10) % 360
        self.update_spinner()

    def update_spinner(self):
        """Draws the rotating spinner."""
        pixmap = QPixmap(80, 80)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw spinning arcs
        pen = painter.pen()
        pen.setWidth(6)
        pen.setCapStyle(Qt.RoundCap)
        pen.setColor(QColor("#3498DB"))
        painter.setPen(pen)

        painter.translate(40, 40)
        painter.rotate(self.rotation_angle)

        # Draw three arcs for spinner effect
        for i in range(3):
            painter.rotate(120)
            painter.drawArc(-30, -30, 60, 60, 0, 120 * 16)

        painter.end()
        self.spinner_label.setPixmap(pixmap)

    def showEvent(self, event):
        """Centers overlay and starts animation."""
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.timer.start(30)  # 30ms refresh rate for smooth animation
        self.update_spinner()
        super().showEvent(event)

    def hideEvent(self, event):
        """Stops animation when hidden."""
        self.timer.stop()
        super().hideEvent(event)

    def set_message(self, message):
        """Updates the loading message."""
        self.message_label.setText(message)


# --- Worker Thread: Fetch Metadata ---


class YtdlpWorker(QThread):
    """Thread to fetch video/audio metadata using yt-dlp."""

    metadata_fetched = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "extract_flat": False,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                self.metadata_fetched.emit(info)

        except Exception as e:
            error_msg = str(e)
            if "Unsupported URL" in error_msg or "No video" in error_msg:
                self.error_occurred.emit(
                    "This URL is not supported. Please try a video/audio link from YouTube, "
                    "Vimeo, or other supported platforms."
                )
            else:
                self.error_occurred.emit(f"Failed to fetch metadata: {error_msg}")


# --- Worker Thread: Download Image ---


class ImageDownloadWorker(QThread):
    """Thread to download direct image links."""

    image_data_fetched = pyqtSignal(bytes, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            req = urllib.request.Request(
                self.url, headers={"User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(req, timeout=15) as response:
                if response.getcode() != 200:
                    raise Exception(f"HTTP Error: {response.getcode()}")

                content_type = response.info().get_content_type()
                if not content_type.startswith("image/"):
                    raise Exception(
                        f"URL did not return an image (got: {content_type})"
                    )

                image_data = response.read()
                parsed_url = urlparse(self.url)
                filename = Path(parsed_url.path).name or "downloaded_image.jpg"

                self.image_data_fetched.emit(image_data, filename)

        except Exception as e:
            self.error_occurred.emit(f"Image download failed: {str(e)}")


# --- Worker Thread: Download Media/Image ---


class DownloadWorker(QThread):
    """Thread to handle actual downloads (media or image)."""

    progress_signal = pyqtSignal(float, str)
    finished_signal = pyqtSignal(str, str, str, str)
    error_signal = pyqtSignal(str)

    def __init__(
        self,
        url,
        format_id,
        start_time,
        end_time,
        filepath,
        filename_template,
        is_image=False,
    ):
        super().__init__()
        self.url = url
        self.format_id = format_id
        self.start_time = start_time
        self.end_time = end_time
        self.filepath = filepath
        self.filename_template = filename_template
        self.is_image = is_image

    def hook(self, d):
        """Progress hook for yt-dlp downloads."""
        if d["status"] == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 1)
            percent = (downloaded / total) * 100 if total else 0

            speed = d.get("speed", 0)
            eta = d.get("eta", 0)

            status_text = f"Speed: {format_bytes(speed)}/s"
            if eta:
                status_text += f" | ETA: {eta}s"

            self.progress_signal.emit(percent, status_text)

    def download_image(self):
        """Handles direct image file download."""
        try:
            req = urllib.request.Request(
                self.url, headers={"User-Agent": "Mozilla/5.0"}
            )

            with urllib.request.urlopen(req, timeout=15) as response:
                if response.getcode() != 200:
                    raise Exception(f"HTTP Error: {response.getcode()}")

                total_size = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                image_data = b""

                # Download with progress
                chunk_size = 8192
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    image_data += chunk
                    downloaded += len(chunk)

                    if total_size:
                        percent = (downloaded / total_size) * 100
                        self.progress_signal.emit(
                            percent, f"Downloaded: {format_bytes(downloaded)}"
                        )

                final_filepath = os.path.join(self.filepath, self.filename_template)

                with open(final_filepath, "wb") as f:
                    f.write(image_data)

                final_size = os.path.getsize(final_filepath)
                self.finished_signal.emit(
                    final_filepath,
                    self.filename_template,
                    format_bytes(final_size),
                    "image",
                )

        except Exception as e:
            self.error_signal.emit(f"Image download failed: {str(e)}")

    def run(self):
        """Main download execution."""
        if self.is_image:
            self.download_image()
            return

        # Media download via yt-dlp
        try:
            output_template = os.path.join(self.filepath, self.filename_template)

            # Build yt-dlp options
            ydl_opts = {
                "format": self.format_id,
                "outtmpl": {"default": output_template},
                "progress_hooks": [self.hook],
                "noplaylist": True,
                "merge_output_format": "mp4",
            }

            # Add trimming via external args if needed (FIXED METHOD)
            external_args = []
            if self.start_time:
                external_args.extend(["-ss", self.start_time])
            if self.end_time:
                external_args.extend(["-to", self.end_time])

            if external_args:
                # Check FFmpeg availability
                try:
                    subprocess.run(
                        ["ffmpeg", "-version"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True,
                    )
                except (FileNotFoundError, subprocess.CalledProcessError):
                    self.error_signal.emit(
                        "FFmpeg not found! Trimming and merging require FFmpeg. "
                        "Please install FFmpeg and add it to your system PATH."
                    )
                    return

                ydl_opts["postprocessor_args"] = {"ffmpeg": external_args}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)

                final_filename = ydl.prepare_filename(info)
                final_filename = os.path.basename(final_filename)
                final_filepath = os.path.join(self.filepath, final_filename)

                final_size = os.path.getsize(final_filepath)

                self.finished_signal.emit(
                    final_filepath,
                    final_filename,
                    format_bytes(final_size),
                    self.format_id,
                )

        except Exception as e:
            self.error_signal.emit(f"Download failed: {str(e)}")


# --- Main Application Class ---


class ClipShrApp(QMainWindow):
    """Main application window for ClipShr."""

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.media_folder = get_media_folder()
        self.metadata = None
        self.selected_format = None
        self.is_image_mode = False

        # Worker threads
        self.ytdlp_thread = None
        self.download_thread = None
        self.image_fetch_thread = None

        # Window setup
        self.setGeometry(
            100, 100, self.config["window_width"], self.config["window_height"]
        )
        self.setWindowTitle("ClipShr - Professional Media Downloader")
        self.setMinimumSize(1200, 800)

        # Progress bar (will be used in downloader tab)
        self.progress_bar = QProgressBar()

        # Setup UI
        self.setup_ui()
        self.apply_theme(self.config["theme"])

        # Ensure media folder exists
        Path(self.media_folder).mkdir(exist_ok=True)

    def apply_theme(self, theme_name):
        """Applies the selected theme to the entire application."""
        if theme_name not in PALETTES:
            theme_name = "light"

        qss = generate_qss(theme_name)
        palette_data = PALETTES[theme_name]

        # Create Qt Palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(palette_data["BG_MAIN"]))
        palette.setColor(QPalette.WindowText, QColor(palette_data["TEXT_PRIMARY"]))
        palette.setColor(QPalette.Base, QColor(palette_data["BG_CARD"]))
        palette.setColor(QPalette.Text, QColor(palette_data["TEXT_PRIMARY"]))
        palette.setColor(QPalette.Button, QColor(palette_data["ACCENT_BLUE"]))
        palette.setColor(QPalette.ButtonText, QColor("white"))
        palette.setColor(QPalette.Highlight, QColor(palette_data["ACCENT_BLUE"]))
        palette.setColor(QPalette.HighlightedText, QColor("white"))

        QApplication.setPalette(palette)
        self.setStyleSheet(qss)

        self.config["theme"] = theme_name
        save_config(self.config)

    def setup_ui(self):
        """Initializes the main window layout and tabs."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Tab Widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create Tabs
        self.downloader_tab = self.create_downloader_tab()
        self.tab_widget.addTab(self.downloader_tab, "📥 Downloader")

        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(self.history_tab, "📜 History")

        self.settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")

        main_layout.addWidget(self.tab_widget)

        # Loading Overlay (on top of everything)
        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.hide()

        # Connect tab change event
        self.tab_widget.currentChanged.connect(self.on_tab_change)

        # Load history on startup
        self.load_history()

    # ===== DOWNLOADER TAB =====

    def create_downloader_tab(self):
        """Creates the main downloader interface."""
        downloader_widget = QWidget()
        main_vbox = QVBoxLayout(downloader_widget)
        main_vbox.setSpacing(20)
        main_vbox.setContentsMargins(25, 25, 25, 25)

        # ===== A. URL INPUT SECTION =====
        url_group = QGroupBox("🔗 Enter Media Link")
        url_layout = QHBoxLayout(url_group)
        url_layout.setSpacing(15)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "Paste YouTube, Vimeo, or direct media/image URL here..."
        )
        self.url_input.returnPressed.connect(self.determine_fetch_type)
        self.url_input.textChanged.connect(self.clear_ui_on_text_change)

        self.fetch_button = QPushButton("🔍 Fetch Details")
        self.fetch_button.setMinimumWidth(150)
        self.fetch_button.clicked.connect(self.determine_fetch_type)

        url_layout.addWidget(self.url_input, 4)
        url_layout.addWidget(self.fetch_button, 1)
        main_vbox.addWidget(url_group)

        # ===== B. CONTENT AREA (PREVIEW + FORMATS) =====
        content_splitter = QSplitter(Qt.Horizontal)
        content_splitter.setChildrenCollapsible(False)

        # B1. PREVIEW & METADATA PANEL (LEFT)
        preview_container = self.create_preview_panel()
        content_splitter.addWidget(preview_container)

        # B2. FORMATS & ACTIONS PANEL (RIGHT)
        formats_container = self.create_formats_panel()
        content_splitter.addWidget(formats_container)

        # Set initial sizes (40% preview, 60% formats)
        content_splitter.setStretchFactor(0, 40)
        content_splitter.setStretchFactor(1, 60)

        main_vbox.addWidget(content_splitter, 1)

        return downloader_widget

    def create_preview_panel(self):
        """Creates the preview and metadata panel."""
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setSpacing(15)
        vbox.setContentsMargins(0, 0, 10, 0)

        # === THUMBNAIL PREVIEW ===
        preview_group = QGroupBox("🖼️ Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setMinimumSize(400, 225)
        self.thumbnail_label.setMaximumHeight(300)
        self.thumbnail_label.setScaledContents(False)
        self.thumbnail_label.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #CCCCCC;
                border-radius: 8px;
                padding: 20px;
                color: #999999;
                font-size: 11pt;
            }
        """
        )
        self.thumbnail_label.setText(
            "📋 Paste a link above and click 'Fetch Details' to preview"
        )
        self.thumbnail_label.setWordWrap(True)

        preview_layout.addWidget(self.thumbnail_label)
        vbox.addWidget(preview_group)

        # === METADATA DETAILS ===
        self.metadata_group = QGroupBox("ℹ️ Media Information")
        meta_grid = QGridLayout(self.metadata_group)
        meta_grid.setSpacing(12)
        meta_grid.setColumnStretch(1, 1)

        # Create metadata labels
        labels = ["Title:", "Source:", "Date:", "Type:", "URL:"]
        self.meta_labels = {}

        for i, label_text in enumerate(labels):
            key = label_text.rstrip(":")

            label = QLabel(label_text)
            label.setStyleSheet("font-weight: 600; color: #666666;")
            meta_grid.addWidget(label, i, 0, Qt.AlignTop)

            value = QLabel("N/A")
            value.setWordWrap(True)
            value.setTextInteractionFlags(Qt.TextSelectableByMouse)
            value.setStyleSheet("font-weight: 500;")
            meta_grid.addWidget(value, i, 1)

            self.meta_labels[key] = value

        vbox.addWidget(self.metadata_group)

        # === TRIMMING SECTION ===
        self.trim_group = QGroupBox("✂️ Trim Media (Optional)")
        trim_vbox = QVBoxLayout(self.trim_group)
        trim_vbox.setSpacing(10)

        # Manual time input
        manual_group = QGroupBox("Manual Time Input")
        manual_grid = QGridLayout(manual_group)
        manual_grid.setSpacing(10)

        manual_grid.addWidget(QLabel("Start Time (HH:MM:SS):"), 0, 0)
        self.start_time_input = QLineEdit("00:00:00")
        self.start_time_input.setPlaceholderText("e.g., 00:00:10")
        manual_grid.addWidget(self.start_time_input, 0, 1)

        manual_grid.addWidget(QLabel("End Time (HH:MM:SS):"), 1, 0)
        self.end_time_input = QLineEdit()
        self.end_time_input.setPlaceholderText("Leave blank for full duration")
        manual_grid.addWidget(self.end_time_input, 1, 1)

        trim_vbox.addWidget(manual_group)

        # Info note
        note_label = QLabel(
            "💡 Note: Trimming requires FFmpeg to be installed on your system."
        )
        note_label.setStyleSheet("color: #888888; font-size: 9pt; font-style: italic;")
        note_label.setWordWrap(True)
        trim_vbox.addWidget(note_label)

        vbox.addWidget(self.trim_group)
        self.trim_group.hide()  # Hidden by default

        vbox.addStretch(1)
        return container

    def create_formats_panel(self):
        """Creates the formats selection and download panel."""
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.setSpacing(15)
        vbox.setContentsMargins(10, 0, 0, 0)

        formats_group = QGroupBox("📦 Available Formats & Download")
        formats_layout = QVBoxLayout(formats_group)
        formats_layout.setSpacing(15)

        # Format Lists Splitter
        format_splitter = QSplitter(Qt.Vertical)
        format_splitter.setChildrenCollapsible(False)

        # VIDEO FORMATS
        self.video_format_group = QGroupBox("🎬 Video Formats (with Audio)")
        video_vbox = QVBoxLayout(self.video_format_group)
        video_vbox.setSpacing(8)

        video_info = QLabel("Quality | Format | Size")
        video_info.setStyleSheet("font-weight: 600; color: #888888; font-size: 9pt;")
        video_vbox.addWidget(video_info)

        self.video_list_widget = QListWidget()
        self.video_list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.video_list_widget.itemSelectionChanged.connect(
            self.on_video_format_selected
        )
        video_vbox.addWidget(self.video_list_widget)

        format_splitter.addWidget(self.video_format_group)

        # AUDIO FORMATS
        self.audio_format_group = QGroupBox("🎵 Audio Only Formats")
        audio_vbox = QVBoxLayout(self.audio_format_group)
        audio_vbox.setSpacing(8)

        audio_info = QLabel("Quality | Format | Size")
        audio_info.setStyleSheet("font-weight: 600; color: #888888; font-size: 9pt;")
        audio_vbox.addWidget(audio_info)

        self.audio_list_widget = QListWidget()
        self.audio_list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.audio_list_widget.itemSelectionChanged.connect(
            self.on_audio_format_selected
        )
        audio_vbox.addWidget(self.audio_list_widget)

        format_splitter.addWidget(self.audio_format_group)

        # Set stretch factors
        format_splitter.setStretchFactor(0, 60)
        format_splitter.setStretchFactor(1, 40)

        formats_layout.addWidget(format_splitter)

        # === PROGRESS BAR ===
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        formats_layout.addWidget(self.progress_bar)

        # === STATUS LABEL ===
        self.status_label = QLabel("✅ Ready to fetch a link")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(
            """
            padding: 10px;
            font-weight: 600;
            font-size: 10pt;
            border-radius: 6px;
        """
        )
        formats_layout.addWidget(self.status_label)

        # === DOWNLOAD BUTTON ===
        self.download_button = QPushButton("⬇️ Download Selected Format")
        self.download_button.setMinimumHeight(50)
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setEnabled(False)
        formats_layout.addWidget(self.download_button)

        vbox.addWidget(formats_group)
        return container

    # ===== DOWNLOADER LOGIC - FETCHING & PROCESSING =====

    def determine_fetch_type(self):
        """Determines if URL is an image or media link and fetches accordingly."""
        url = self.url_input.text().strip()

        if not url:
            self.update_status("❌ Please enter a URL", error=True)
            return

        # Check if it's a direct image URL
        if is_image_url(url):
            self.is_image_mode = True
            self.fetch_image_details(url)
        else:
            self.is_image_mode = False
            self.fetch_metadata(url)

    def fetch_image_details(self, url):
        """Fetches and processes direct image URLs."""
        self.update_status("🔄 Fetching image details...")
        self.fetch_button.setEnabled(False)
        self.download_button.setEnabled(False)

        self.loading_overlay.set_message("🖼️ Downloading image preview...")
        self.loading_overlay.show()

        self.image_fetch_thread = ImageDownloadWorker(url)
        self.image_fetch_thread.image_data_fetched.connect(self.process_image_details)
        self.image_fetch_thread.error_occurred.connect(self.handle_fetch_error)
        self.image_fetch_thread.start()

    def process_image_details(self, image_data, filename):
        """Processes downloaded image and displays preview."""
        self.loading_overlay.hide()
        self.fetch_button.setEnabled(True)

        # Store metadata
        self.metadata = {
            "is_image": True,
            "url": self.url_input.text().strip(),
            "title": filename,
            "filename": filename,
            "filesize": len(image_data),
        }

        self.update_status("✅ Image ready! Select format to download.")

        # Display thumbnail
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)

        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.thumbnail_label.width(),
                self.thumbnail_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.thumbnail_label.setPixmap(scaled_pixmap)
            self.thumbnail_label.setText("")
        else:
            self.thumbnail_label.setText("⚠️ Could not load image preview")

        # Update metadata display
        self.meta_labels["Title"].setText(filename)
        self.meta_labels["Source"].setText(urlparse(self.url_input.text()).netloc)
        self.meta_labels["Date"].setText(datetime.now().strftime("%Y-%m-%d"))
        self.meta_labels["Type"].setText(
            f"Image ({Path(filename).suffix.upper().lstrip('.')})"
        )
        self.meta_labels["URL"].setText(self.metadata["url"])

        # Update format lists for image
        self.video_list_widget.clear()
        self.audio_list_widget.clear()
        self.video_format_group.setTitle("🖼️ Image Format")
        self.audio_format_group.setTitle("ℹ️ Info")

        # Create image format entry
        image_format = {
            "format_id": "image_original",
            "display_quality": f"Original {Path(filename).suffix.upper().lstrip('.')} Format",
            "ext": Path(filename).suffix.upper().lstrip("."),
            "size": format_bytes(len(image_data)),
            "raw_format": {
                "vcodec": "image",
                "acodec": "none",
            },
        }

        self._populate_format_list(self.video_list_widget, [image_format])

        # Info in audio section
        info_item = QListWidgetItem("💡 Direct image download - no conversion needed")
        info_item.setFlags(Qt.NoItemFlags)  # Make it non-selectable
        self.audio_list_widget.addItem(info_item)

        self.trim_group.hide()
        self.download_button.setEnabled(False)

    def fetch_metadata(self, url):
        """Fetches video/audio metadata using yt-dlp."""
        self.update_status("🔄 Fetching media details...")
        self.fetch_button.setEnabled(False)
        self.download_button.setEnabled(False)

        self.loading_overlay.set_message("🎬 Extracting media information...")
        self.loading_overlay.show()

        self.ytdlp_thread = YtdlpWorker(url)
        self.ytdlp_thread.metadata_fetched.connect(self.process_metadata)
        self.ytdlp_thread.error_occurred.connect(self.handle_fetch_error)
        self.ytdlp_thread.start()

    def handle_fetch_error(self, error_message):
        """Handles errors during metadata fetching."""
        self.loading_overlay.hide()
        self.update_status(f"❌ {error_message}", error=True)
        self.fetch_button.setEnabled(True)
        self.download_button.setEnabled(False)

        QMessageBox.warning(self, "Fetch Error", error_message)

    def process_metadata(self, info):
        """Processes metadata from yt-dlp and displays it."""
        self.loading_overlay.hide()
        self.metadata = info
        self.fetch_button.setEnabled(True)

        self.update_status("✅ Media details loaded! Select a format to download.")

        # Display preview and formats
        self.display_preview(info)
        self.display_formats(info.get("formats", []))
        self.trim_group.show()

    def display_preview(self, info):
        """Displays thumbnail and metadata information."""
        # Update metadata labels
        title = info.get("title", "Unknown Title")
        uploader = (
            info.get("uploader")
            or info.get("channel")
            or info.get("extractor", "Unknown")
        )
        duration = info.get("duration")
        ext = info.get("ext", "unknown").upper()

        self.meta_labels["Title"].setText(title)
        self.meta_labels["Source"].setText(uploader)
        self.meta_labels["Type"].setText(f"Media ({ext})")
        self.meta_labels["URL"].setText(info.get("webpage_url", self.url_input.text()))

        # Format upload date
        upload_date = info.get("upload_date")
        if upload_date and len(upload_date) == 8:
            try:
                formatted_date = datetime.strptime(upload_date, "%Y%m%d").strftime(
                    "%Y-%m-%d"
                )
                self.meta_labels["Date"].setText(formatted_date)
            except:
                self.meta_labels["Date"].setText("Unknown")
        else:
            self.meta_labels["Date"].setText("Unknown")

        # Handle duration for trimming
        if duration:
            duration_str = str(timedelta(seconds=int(duration))).split(".")[0]
            self.meta_labels["Type"].setText(
                f"Media ({ext}) - Duration: {duration_str}"
            )
            self.end_time_input.setPlaceholderText(f"Max: {duration_str}")

        # Display thumbnail
        thumbnail_url = info.get("thumbnail")
        if thumbnail_url:
            try:
                req = urllib.request.Request(
                    thumbnail_url, headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    image_data = response.read()

                pixmap = QPixmap()
                pixmap.loadFromData(image_data)

                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.thumbnail_label.width(),
                        self.thumbnail_label.height(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation,
                    )
                    self.thumbnail_label.setPixmap(scaled_pixmap)
                    self.thumbnail_label.setText("")
                else:
                    self.thumbnail_label.setText("🖼️ Thumbnail not available")
            except Exception as e:
                self.thumbnail_label.setText(
                    f"⚠️ Could not load thumbnail\n({str(e)[:50]})"
                )
        else:
            self.thumbnail_label.setText("🖼️ No thumbnail available")

    def display_formats(self, formats):
        """Displays available formats grouped by video and audio."""
        self.video_list_widget.clear()
        self.audio_list_widget.clear()

        video_formats = []
        audio_formats = []

        # Add BEST QUALITY option (auto-merged video+audio)
        best_video_size = 0
        best_audio_size = 0

        for f in formats:
            size = f.get("filesize") or f.get("filesize_approx") or 0

            if f.get("vcodec") != "none" and size > best_video_size:
                best_video_size = size

            if (
                f.get("acodec") != "none"
                and f.get("vcodec") == "none"
                and size > best_audio_size
            ):
                best_audio_size = size

        # Create BEST QUALITY format entry
        if best_video_size > 0:
            estimated_size = best_video_size + best_audio_size
            video_formats.append(
                {
                    "format_id": "bestvideo+bestaudio/best",
                    "display_quality": "🏆 BEST QUALITY (Full Video + Audio)",
                    "ext": "MP4 (Merged)",
                    "size": (
                        format_bytes(estimated_size)
                        if estimated_size > 0
                        else "~Size Unknown"
                    ),
                    "raw_format": {
                        "vcodec": "best",
                        "acodec": "best",
                        "height": 999999,  # For sorting priority
                    },
                    "is_best": True,
                }
            )

        # Process all formats
        for f in formats:
            filesize = f.get("filesize") or f.get("filesize_approx")

            # Skip formats without size info
            if not filesize:
                continue

            format_data = {
                "format_id": f["format_id"],
                "ext": f.get("ext", "unknown").upper(),
                "size": format_bytes(filesize),
                "raw_format": f,
            }

            height = f.get("height", 0)
            fps = f.get("fps", 30)
            vcodec = f.get("vcodec", "none")
            acodec = f.get("acodec", "none")

            # VIDEO + AUDIO (Combined)
            if vcodec != "none" and acodec != "none":
                quality_text = f"{height}p" if height else "Unknown"
                if fps and fps > 30:
                    quality_text += f" {fps}fps"

                format_data["display_quality"] = f"📹 {quality_text} (Video + Audio)"
                video_formats.append(format_data)

            # VIDEO ONLY (No audio - usually not needed since we have BEST)
            elif vcodec != "none" and acodec == "none":
                # Skip video-only formats to avoid confusion, since BEST handles merging
                continue

            # AUDIO ONLY
            elif vcodec == "none" and acodec != "none":
                abr = f.get("abr", 0)
                quality_text = f"{int(abr)}kbps" if abr else "Unknown Quality"

                format_data["display_quality"] = f"🎵 Audio Only - {quality_text}"
                audio_formats.append(format_data)

        # Sort formats
        video_formats.sort(key=lambda x: x["raw_format"].get("height", 0), reverse=True)

        audio_formats.sort(key=lambda x: x["raw_format"].get("abr", 0), reverse=True)

        # Populate lists
        self._populate_format_list(self.video_list_widget, video_formats)
        self._populate_format_list(self.audio_list_widget, audio_formats)

        # Show message if no formats found
        if not video_formats:
            item = QListWidgetItem("⚠️ No video formats available")
            item.setFlags(Qt.NoItemFlags)
            self.video_list_widget.addItem(item)

        if not audio_formats:
            item = QListWidgetItem("⚠️ No audio formats available")
            item.setFlags(Qt.NoItemFlags)
            self.audio_list_widget.addItem(item)

    def _populate_format_list(self, list_widget, formats):
        """Helper to populate format lists with styled items."""
        list_widget.clear()

        if not formats:
            return

        palette = PALETTES[self.config["theme"]]

        for f in formats:
            # Create custom widget for list item
            item_widget = QWidget()
            item_layout = QGridLayout(item_widget)
            item_layout.setContentsMargins(10, 5, 10, 5)
            item_layout.setHorizontalSpacing(15)

            # Determine color based on format type
            if f.get("is_best"):
                color = palette["ACCENT_RED"]
                weight = "bold"
            elif "Video + Audio" in f["display_quality"]:
                color = palette["ACCENT_BLUE"]
                weight = "600"
            else:
                color = palette["TEXT_PRIMARY"]
                weight = "500"

            # Quality label
            quality_label = QLabel(f["display_quality"])
            quality_label.setStyleSheet(
                f"""
                font-weight: {weight};
                font-size: 10pt;
                color: {color};
                background: transparent;
            """
            )
            item_layout.addWidget(quality_label, 0, 0, Qt.AlignLeft)

            # Format label
            format_label = QLabel(f"| {f['ext']}")
            format_label.setStyleSheet(
                """
                font-size: 9pt;
                color: #888888;
                background: transparent;
            """
            )
            item_layout.addWidget(format_label, 0, 1, Qt.AlignRight)

            # Size label
            size_label = QLabel(f["size"])
            size_label.setStyleSheet(
                f"""
                font-weight: bold;
                font-size: 10pt;
                color: {palette['ACCENT_GREEN']};
                background: transparent;
            """
            )
            item_layout.addWidget(size_label, 0, 2, Qt.AlignRight)

            # Set column stretches
            item_layout.setColumnStretch(0, 5)
            item_layout.setColumnStretch(1, 1)
            item_layout.setColumnStretch(2, 2)

            # Create list item
            list_item = QListWidgetItem(list_widget)
            list_item.setSizeHint(QSize(list_widget.width() - 20, 50))
            list_item.setData(Qt.UserRole, f)

            list_widget.setItemWidget(list_item, item_widget)

    def on_video_format_selected(self):
        """Handles video format selection."""
        self.audio_list_widget.clearSelection()
        selected_items = self.video_list_widget.selectedItems()
        self._handle_format_selection(selected_items)

    def on_audio_format_selected(self):
        """Handles audio format selection."""
        self.video_list_widget.clearSelection()
        selected_items = self.audio_list_widget.selectedItems()
        self._handle_format_selection(selected_items)

    def _handle_format_selection(self, selected_items):
        """Stores selected format and enables download button."""
        if selected_items:
            self.selected_format = selected_items[0].data(Qt.UserRole)

            if self.selected_format:
                self.download_button.setEnabled(True)
                quality = self.selected_format.get("display_quality", "N/A")
                self.update_status(f"✅ Selected: {quality} - Ready to download!")
        else:
            self.selected_format = None
            self.download_button.setEnabled(False)
            self.update_status("ℹ️ Select a format to continue")

    def clear_ui_on_text_change(self, text):
        """Resets UI when URL input changes."""
        self.metadata = None
        self.selected_format = None
        self.is_image_mode = False
        self.download_button.setEnabled(False)
        self.progress_bar.setValue(0)

        self.update_status("✅ Ready to fetch a link")

        # Clear preview
        self.thumbnail_label.setPixmap(QPixmap())
        self.thumbnail_label.setText(
            "📋 Paste a link above and click 'Fetch Details' to preview"
        )

        # Clear metadata
        for label in self.meta_labels.values():
            label.setText("N/A")

        # Clear format lists
        self.video_list_widget.clear()
        self.audio_list_widget.clear()
        self.video_format_group.setTitle("🎬 Video Formats (with Audio)")
        self.audio_format_group.setTitle("🎵 Audio Only Formats")

        # Reset time inputs
        self.start_time_input.setText("00:00:00")
        self.end_time_input.clear()
        self.trim_group.hide()

    def update_status(self, message, error=False):
        """Updates the status label with appropriate styling."""
        self.status_label.setText(message)

        palette = PALETTES[self.config["theme"]]

        if error:
            bg_color = palette["ACCENT_RED"]
            text_color = "white"
        elif "✅" in message or "Ready" in message:
            bg_color = palette["BG_CARD"]
            text_color = palette["ACCENT_GREEN"]
        else:
            bg_color = palette["BG_CARD"]
            text_color = palette["TEXT_PRIMARY"]

        self.status_label.setStyleSheet(
            f"""
            background-color: {bg_color};
            color: {text_color};
            padding: 12px;
            font-weight: 600;
            font-size: 10pt;
            border-radius: 6px;
            border: 1px solid {palette['BORDER']};
        """
        )

    # ===== DOWNLOAD EXECUTION =====

    def start_download(self):
        """Initiates the download process."""
        if not self.metadata or not self.selected_format:
            self.update_status(
                "❌ Please fetch media and select a format first", error=True
            )
            return

        url = self.url_input.text().strip()
        format_id = self.selected_format["format_id"]

        # Get trim times
        start_time = self.start_time_input.text().strip()
        end_time = self.end_time_input.text().strip()

        # Reset trim times if default
        if start_time == "00:00:00":
            start_time = None
        if not end_time:
            end_time = None

        # Validate trim times if provided
        if start_time or end_time:
            try:
                if start_time:
                    datetime.strptime(start_time, "%H:%M:%S")
                if end_time:
                    datetime.strptime(end_time, "%H:%M:%S")
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Invalid Time Format",
                    "Please use HH:MM:SS format for trim times (e.g., 00:01:30)",
                )
                return

        self.update_status("⬇️ Starting download...")
        self.download_button.setEnabled(False)
        self.fetch_button.setEnabled(False)
        self.progress_bar.setValue(0)

        # Prepare filename template
        if self.is_image_mode:
            filename_template = self.metadata["filename"]
        else:
            filename_template = "%(title)s.%(ext)s"

        # Create download worker
        self.download_thread = DownloadWorker(
            url=url,
            format_id=format_id,
            start_time=start_time,
            end_time=end_time,
            filepath=self.media_folder,
            filename_template=filename_template,
            is_image=self.is_image_mode,
        )

        # Connect signals
        self.download_thread.progress_signal.connect(self.update_download_progress)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.error_signal.connect(self.handle_download_error)

        # Start download
        self.download_thread.start()

    def update_download_progress(self, percent, status_text):
        """Updates progress bar during download."""
        self.progress_bar.setValue(int(percent))
        self.update_status(f"⬇️ Downloading... {int(percent)}% | {status_text}")

    def download_finished(self, filepath, filename, size_str, format_id):
        """Handles successful download completion."""
        self.progress_bar.setValue(100)
        self.update_status(f"✅ Download Complete! Size: {size_str}")

        # Save to history
        db = load_db()
        history_item = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "original_url": self.url_input.text().strip(),
            "title": self.metadata.get("title", filename),
            "format": self.selected_format.get("display_quality", format_id),
            "filename": filename,
            "size": size_str,
            "is_image": self.is_image_mode,
        }
        db.append(history_item)
        save_db(db)

        # Re-enable buttons
        self.download_button.setEnabled(True)
        self.fetch_button.setEnabled(True)

        # Show success message with options
        msg = QMessageBox(self)
        msg.setWindowTitle("Download Complete")
        msg.setText(f"✅ Successfully downloaded!")
        msg.setInformativeText(
            f"File: {filename}\n" f"Size: {size_str}\n" f"Location: {self.media_folder}"
        )
        msg.setIcon(QMessageBox.Information)

        open_btn = msg.addButton("📂 Open File", QMessageBox.ActionRole)
        folder_btn = msg.addButton("📁 Open Folder", QMessageBox.ActionRole)
        msg.addButton("OK", QMessageBox.AcceptRole)

        msg.exec_()

        # Handle button clicks
        if msg.clickedButton() == open_btn:
            QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
        elif msg.clickedButton() == folder_btn:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self.media_folder))

    def handle_download_error(self, error_message):
        """Handles download errors."""
        self.progress_bar.setValue(0)
        self.update_status(f"❌ Download Failed: {error_message}", error=True)

        self.download_button.setEnabled(True)
        self.fetch_button.setEnabled(True)

        QMessageBox.critical(
            self,
            "Download Error",
            f"Failed to download media:\n\n{error_message}\n\n"
            "Common issues:\n"
            "• FFmpeg not installed (required for BEST QUALITY and trimming)\n"
            "• Network connection lost\n"
            "• Invalid URL or removed video",
        )

    # ===== HISTORY TAB =====

    def create_history_tab(self):
        """Creates the download history tab."""
        history_widget = QWidget()
        vbox = QVBoxLayout(history_widget)
        vbox.setContentsMargins(25, 25, 25, 25)
        vbox.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("📜 Download History")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch(1)

        # Refresh button
        self.refresh_history_btn = QPushButton("🔄 Refresh")
        self.refresh_history_btn.setObjectName("SecondaryButton")
        self.refresh_history_btn.setMinimumWidth(120)
        self.refresh_history_btn.clicked.connect(self.load_history)
        header_layout.addWidget(self.refresh_history_btn)

        # Clear history button
        self.clear_history_button = QPushButton("🗑️ Clear All History")
        self.clear_history_button.setObjectName("DangerButton")
        self.clear_history_button.setMinimumWidth(150)
        self.clear_history_button.clicked.connect(self.clear_history_prompt)
        header_layout.addWidget(self.clear_history_button)

        vbox.addLayout(header_layout)

        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels(
            [
                "📅 Date",
                "📝 Title",
                "🎬 Type",
                "📦 Format",
                "💾 Size",
                "✅ Status",
                "⚙️ Actions",
            ]
        )

        # Configure table
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Title stretches
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setShowGrid(False)

        vbox.addWidget(self.history_table)

        # Stats footer
        self.history_stats_label = QLabel()
        self.history_stats_label.setStyleSheet(
            """
            padding: 10px;
            font-size: 10pt;
            color: #666666;
        """
        )
        vbox.addWidget(self.history_stats_label)

        return history_widget

    def load_history(self):
        """Loads and displays download history."""
        db = load_db()
        self.history_table.setRowCount(len(db))

        total_size = 0

        for row, item in enumerate(reversed(db)):  # Newest first
            # Date
            date_text = item.get("timestamp", "N/A").split(" ")[0]
            date_item = QTableWidgetItem(date_text)
            self.history_table.setItem(row, 0, date_item)

            # Title
            title = item.get("title", "Unknown")
            if len(title) > 50:
                title = title[:47] + "..."
            title_item = QTableWidgetItem(title)
            title_item.setToolTip(item.get("title", "Unknown"))
            self.history_table.setItem(row, 1, title_item)

            # Type
            type_text = "🖼️ Image" if item.get("is_image") else "🎬 Media"
            type_item = QTableWidgetItem(type_text)
            self.history_table.setItem(row, 2, type_item)

            # Format
            format_text = item.get("format", "N/A")
            if len(format_text) > 30:
                format_text = format_text[:27] + "..."
            format_item = QTableWidgetItem(format_text)
            format_item.setToolTip(item.get("format", "N/A"))
            self.history_table.setItem(row, 3, format_item)

            # Size
            size_item = QTableWidgetItem(item.get("size", "N/A"))
            self.history_table.setItem(row, 4, size_item)

            # Calculate total size for stats
            size_str = item.get("size", "0 B")
            try:
                # Parse size string like "43.69 MB"
                parts = size_str.split()
                if len(parts) == 2:
                    value = float(parts[0])
                    unit = parts[1]
                    multipliers = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}
                    total_size += value * multipliers.get(unit, 0)
            except:
                pass

            # Status
            status_item = QTableWidgetItem("✅ Completed")
            palette = PALETTES[self.config["theme"]]
            status_item.setForeground(QColor(palette["ACCENT_GREEN"]))
            self.history_table.setItem(row, 5, status_item)

            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 5, 5, 5)
            action_layout.setSpacing(5)

            # Open file button
            open_btn = QPushButton("📂 Open")
            open_btn.setMinimumWidth(70)
            open_btn.clicked.connect(
                lambda checked, r=row: self.open_downloaded_file(r)
            )
            action_layout.addWidget(open_btn)

            # Delete record button
            delete_btn = QPushButton("🗑️")
            delete_btn.setObjectName("DangerButton")
            delete_btn.setMaximumWidth(40)
            delete_btn.setToolTip("Delete this record")
            delete_btn.clicked.connect(
                lambda checked, r=row: self.delete_history_item(r)
            )
            action_layout.addWidget(delete_btn)

            self.history_table.setCellWidget(row, 6, action_widget)
            self.history_table.setRowHeight(row, 50)

        # Update stats
        total_downloads = len(db)
        total_size_str = format_bytes(total_size)
        self.history_stats_label.setText(
            f"📊 Total Downloads: {total_downloads} | 💾 Total Size: {total_size_str}"
        )

    def open_downloaded_file(self, row_index):
        """Opens the downloaded file from history."""
        db = load_db()
        db_index = len(db) - 1 - row_index

        if db_index < 0 or db_index >= len(db):
            return

        item = db[db_index]
        filename = item.get("filename")

        if not filename:
            QMessageBox.warning(self, "Error", "Filename not found in history.")
            return

        filepath = os.path.join(self.media_folder, filename)

        if not os.path.exists(filepath):
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("File Not Found")
            msg.setText("The file no longer exists at the expected location.")
            msg.setInformativeText(
                f"Expected: {filepath}\n\nIt may have been moved or deleted."
            )
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            return

        # Open file with default application
        QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))

    def delete_history_item(self, row_index):
        """Deletes a single history record."""
        db = load_db()
        db_index = len(db) - 1 - row_index

        if db_index < 0 or db_index >= len(db):
            return

        item = db[db_index]
        title = item.get("title", "this item")

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Delete history record for:\n\n'{title}'?\n\n"
            "⚠️ This will NOT delete the actual file, only the record.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            db.pop(db_index)
            save_db(db)
            self.load_history()

    def clear_history_prompt(self):
        """Prompts user before clearing all history and files."""
        db = load_db()

        if not db:
            QMessageBox.information(self, "No History", "History is already empty.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("⚠️ Clear All History & Files")
        dialog.setMinimumWidth(500)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)

        # Warning message
        warning_label = QLabel(
            "⚠️ <b>WARNING: This action cannot be undone!</b><br><br>"
            "This will permanently delete:<br>"
            "• All download history records<br>"
            "• All downloaded files in the media folder<br><br>"
            f"Total items: {len(db)}"
        )
        warning_label.setWordWrap(True)
        warning_label.setStyleSheet(
            "padding: 15px; background-color: #FFF3CD; border-radius: 6px;"
        )
        layout.addWidget(warning_label)

        # Confirmation input
        confirm_label = QLabel("Type <b>DELETE ALL</b> to confirm:")
        layout.addWidget(confirm_label)

        confirm_input = QLineEdit()
        confirm_input.setPlaceholderText("DELETE ALL")
        layout.addWidget(confirm_input)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)

        confirm_btn = QPushButton("⚠️ Delete Everything")
        confirm_btn.setObjectName("DangerButton")
        confirm_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(confirm_btn)

        layout.addLayout(button_layout)

        # Execute dialog
        if dialog.exec_() == QDialog.Accepted:
            if confirm_input.text() == "DELETE ALL":
                deleted_count = 0
                failed_files = []

                for item in db:
                    filename = item.get("filename", "")
                    filepath = os.path.join(self.media_folder, filename)

                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                            deleted_count += 1
                        except Exception as e:
                            failed_files.append(f"{filename}: {str(e)}")

                # Clear history database
                save_db([])
                self.load_history()

                # Show result
                result_msg = f"✅ History cleared successfully!\n\n"
                result_msg += f"Files deleted: {deleted_count}\n"

                if failed_files:
                    result_msg += f"\n⚠️ Failed to delete {len(failed_files)} file(s):\n"
                    result_msg += "\n".join(failed_files[:5])
                    if len(failed_files) > 5:
                        result_msg += f"\n... and {len(failed_files) - 5} more"

                QMessageBox.information(self, "History Cleared", result_msg)
            else:
                QMessageBox.warning(
                    self,
                    "Confirmation Failed",
                    "Text did not match 'DELETE ALL'. Action cancelled.",
                )

    # ===== SETTINGS TAB =====

    def create_settings_tab(self):
        """Creates the settings and preferences tab."""
        settings_widget = QWidget()
        main_layout = QVBoxLayout(settings_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # Header
        header_label = QLabel("⚙️ Application Settings")
        header_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        main_layout.addWidget(header_label)

        # Scroll area for settings
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(20)

        # ===== THEME SETTINGS =====
        theme_group = QGroupBox("🎨 Appearance & Theme")
        theme_layout = QVBoxLayout(theme_group)
        theme_layout.setSpacing(12)

        theme_info = QLabel("Choose your preferred color theme:")
        theme_info.setStyleSheet("color: #666666; margin-bottom: 10px;")
        theme_layout.addWidget(theme_info)

        self.theme_radio_group = QButtonGroup(self)

        for theme_key, theme_data in PALETTES.items():
            radio_widget = QWidget()
            radio_layout = QHBoxLayout(radio_widget)
            radio_layout.setContentsMargins(10, 8, 10, 8)
            radio_layout.setSpacing(15)

            # Radio button
            radio = QRadioButton(theme_data["name"])
            radio.setProperty("theme_key", theme_key)

            if theme_key == self.config["theme"]:
                radio.setChecked(True)

            self.theme_radio_group.addButton(radio)
            radio_layout.addWidget(radio)

            # Color preview swatches
            swatch_layout = QHBoxLayout()
            swatch_layout.setSpacing(4)

            colors = [
                theme_data["ACCENT_BLUE"],
                theme_data["ACCENT_GREEN"],
                theme_data["ACCENT_RED"],
                theme_data["ACCENT_ORANGE"],
            ]

            for color in colors:
                swatch = QLabel()
                swatch.setFixedSize(24, 24)
                swatch.setStyleSheet(
                    f"""
                    background-color: {color};
                    border-radius: 4px;
                    border: 1px solid rgba(0,0,0,0.1);
                """
                )
                swatch_layout.addWidget(swatch)

            radio_layout.addStretch(1)
            radio_layout.addLayout(swatch_layout)

            # Style the radio container
            radio_widget.setStyleSheet(
                f"""
                QWidget {{
                    background-color: {theme_data['BG_CARD']};
                    border: 2px solid {theme_data['BORDER']};
                    border-radius: 8px;
                }}
                QWidget:hover {{
                    border-color: {theme_data['ACCENT_BLUE']};
                }}
            """
            )

            theme_layout.addWidget(radio_widget)

        self.theme_radio_group.buttonClicked.connect(self.change_theme_from_radio)
        scroll_layout.addWidget(theme_group)

        # ===== DOWNLOAD FOLDER SETTINGS =====
        folder_group = QGroupBox("📁 Download Location")
        folder_layout = QVBoxLayout(folder_group)
        folder_layout.setSpacing(12)

        folder_info = QLabel("All downloaded media will be saved to this folder:")
        folder_info.setStyleSheet("color: #666666;")
        folder_layout.addWidget(folder_info)

        folder_row = QHBoxLayout()
        folder_row.setSpacing(10)

        self.folder_path_label = QLineEdit(self.config["media_folder"])
        self.folder_path_label.setReadOnly(True)
        folder_row.addWidget(self.folder_path_label, 3)

        self.change_folder_button = QPushButton("📂 Change Folder")
        self.change_folder_button.setObjectName("SecondaryButton")
        self.change_folder_button.setMinimumWidth(140)
        self.change_folder_button.clicked.connect(self.change_download_folder)
        folder_row.addWidget(self.change_folder_button)

        self.open_folder_button = QPushButton("🔗 Open Folder")
        self.open_folder_button.setMinimumWidth(120)
        self.open_folder_button.clicked.connect(self.open_media_folder)
        folder_row.addWidget(self.open_folder_button)

        folder_layout.addLayout(folder_row)
        scroll_layout.addWidget(folder_group)

        # ===== DOWNLOAD PREFERENCES =====
        prefs_group = QGroupBox("🔧 Download Preferences")
        prefs_layout = QVBoxLayout(prefs_group)
        prefs_layout.setSpacing(15)

        # Metadata embedding checkbox
        self.compress_checkbox = QCheckBox(
            "Embed metadata and optimize files (Recommended)"
        )
        self.compress_checkbox.setChecked(self.config.get("default_compress", True))
        self.compress_checkbox.stateChanged.connect(self.save_download_preferences)

        compress_info = QLabel(
            "   ℹ️ Embeds title, artist, and thumbnail into downloaded media files"
        )
        compress_info.setStyleSheet(
            "color: #666666; font-size: 9pt; margin-left: 20px;"
        )

        prefs_layout.addWidget(self.compress_checkbox)
        prefs_layout.addWidget(compress_info)

        scroll_layout.addWidget(prefs_group)

        # ===== SYSTEM INFO =====
        info_group = QGroupBox("💻 System Information")
        info_layout = QVBoxLayout(info_group)
        info_layout.setSpacing(10)

        # Check FFmpeg availability
        ffmpeg_available = self.check_ffmpeg()
        ffmpeg_status = "✅ Installed" if ffmpeg_available else "❌ Not Found"
        ffmpeg_color = "#27AE60" if ffmpeg_available else "#E74C3C"

        info_items = [
            ("FFmpeg Status:", ffmpeg_status, ffmpeg_color),
            ("Media Folder:", self.media_folder, None),
            ("App Version:", "v2.0.0 - Professional Edition", None),
        ]

        for label_text, value_text, color in info_items:
            item_layout = QHBoxLayout()

            label = QLabel(label_text)
            label.setStyleSheet("font-weight: 600; min-width: 150px;")
            item_layout.addWidget(label)

            value = QLabel(value_text)
            if color:
                value.setStyleSheet(f"color: {color}; font-weight: 600;")
            else:
                value.setStyleSheet("color: #666666;")
            value.setWordWrap(True)
            item_layout.addWidget(value, 1)

            info_layout.addLayout(item_layout)

        if not ffmpeg_available:
            ffmpeg_help = QLabel(
                "⚠️ FFmpeg is required for BEST QUALITY downloads and trimming. "
                "<a href='https://ffmpeg.org/download.html' style='color: #3498DB;'>Download FFmpeg</a>"
            )
            ffmpeg_help.setOpenExternalLinks(True)
            ffmpeg_help.setWordWrap(True)
            ffmpeg_help.setStyleSheet(
                "padding: 10px; background-color: #FFF3CD; border-radius: 6px;"
            )
            info_layout.addWidget(ffmpeg_help)

        scroll_layout.addWidget(info_group)

        # ===== ABOUT SECTION =====
        about_group = QGroupBox("ℹ️ About ClipShr")
        about_layout = QVBoxLayout(about_group)

        about_text = QLabel(
            "<p style='line-height: 1.6;'>"
            "<b>ClipShr</b> is a professional media downloader that supports "
            "YouTube, Vimeo, and 1000+ websites.<br><br>"
            "<b>Features:</b><br>"
            "• High-quality video and audio downloads<br>"
            "• Multiple format options<br>"
            "• Media trimming and clipping<br>"
            "• Download history tracking<br>"
            "• Beautiful themes<br><br>"
            "Built with PyQt5 and yt-dlp<br>"
            "© 2025 ClipShr - All Rights Reserved"
            "</p>"
        )
        about_text.setWordWrap(True)
        about_text.setStyleSheet("color: #666666; padding: 10px;")
        about_layout.addWidget(about_text)

        scroll_layout.addWidget(about_group)

        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        return settings_widget

    def change_theme_from_radio(self, radio_button):
        """Changes theme based on radio button selection."""
        theme_key = radio_button.property("theme_key")
        if theme_key:
            self.apply_theme(theme_key)

            # Visual feedback
            self.statusBar().showMessage(
                f"✅ Theme changed to: {PALETTES[theme_key]['name']}", 3000
            )

    def change_download_folder(self):
        """Opens dialog to select a new download folder."""
        current_folder = self.config.get("media_folder", "media")

        new_folder = QFileDialog.getExistingDirectory(
            self,
            "Select Download Folder",
            current_folder,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )

        if new_folder:
            self.config["media_folder"] = new_folder
            save_config(self.config)
            self.media_folder = new_folder
            self.folder_path_label.setText(new_folder)

            # Ensure folder exists
            Path(new_folder).mkdir(exist_ok=True)

            QMessageBox.information(
                self,
                "Folder Changed",
                f"✅ Download folder successfully changed to:\n\n{new_folder}",
            )

    def open_media_folder(self):
        """Opens the media folder in file explorer."""
        if not os.path.exists(self.media_folder):
            Path(self.media_folder).mkdir(exist_ok=True)

        QDesktopServices.openUrl(QUrl.fromLocalFile(self.media_folder))

    def save_download_preferences(self):
        """Saves download preference changes."""
        self.config["default_compress"] = self.compress_checkbox.isChecked()
        save_config(self.config)

    def check_ffmpeg(self):
        """Checks if FFmpeg is installed and available."""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True,
            )
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False

    def on_tab_change(self, index):
        """Handles tab changes (refresh history when switching to History tab)."""
        if self.tab_widget.tabText(index) == "📜 History":
            self.load_history()

    def resizeEvent(self, event):
        """Handles window resize to reposition loading overlay."""
        super().resizeEvent(event)
        if self.loading_overlay.isVisible():
            self.loading_overlay.setGeometry(self.rect())

    def closeEvent(self, event):
        """Handles application close - saves window size."""
        self.config["window_width"] = self.width()
        self.config["window_height"] = self.height()
        save_config(self.config)
        event.accept()


# ===== APPLICATION ENTRY POINT =====


def main():
    """Main application entry point."""
    # Load config and ensure media folder exists
    config = load_config()
    Path(get_media_folder()).mkdir(exist_ok=True)

    # Create application
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Set application metadata
    app.setApplicationName("ClipShr")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("ClipShr")

    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Create and show main window
    window = ClipShrApp()
    window.show()

    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
