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
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QDir, QUrl
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette, QDesktopServices


# --- Configuration and Utility Functions ---

CONFIG_FILE = "config.json"
HISTORY_FILE = "history.json"

# Define professional, eye-relaxing color palettes (Added two new themes)
PALETTES = {
    "light": {
        "name": "Light Mode (Default)",
        "BG_MAIN": "#F8FAFB",
        "BG_CARD": "#FFFFFF",
        "TEXT_PRIMARY": "#333333",
        "ACCENT_BLUE": "#4A90E2",
        "ACCENT_GREEN": "#2ECC71",
        "ACCENT_RED": "#E74C3C",
        "SWATCH_COLOR": "#4A90E2",  # Used in Settings for swatch
    },
    "dark": {
        "name": "Dark Mode (Slate)",
        "BG_MAIN": "#2C3E50",
        "BG_CARD": "#34495E",
        "TEXT_PRIMARY": "#EAEAEA",
        "ACCENT_BLUE": "#5DADE2",
        "ACCENT_GREEN": "#27AE60",
        "ACCENT_RED": "#E74C3C",
        "SWATCH_COLOR": "#5DADE2",  # Used in Settings for swatch
    },
    "calm_green": {
        "name": "Calm Green",
        "BG_MAIN": "#F2F7F2",
        "BG_CARD": "#FFFFFF",
        "TEXT_PRIMARY": "#474D47",
        "ACCENT_BLUE": "#4CAF50",
        "ACCENT_GREEN": "#66BB6A",
        "ACCENT_RED": "#D32F2F",
        "SWATCH_COLOR": "#4CAF50",  # Used in Settings for swatch
    },
    "deep_ocean": {  # NEW THEME
        "name": "Deep Ocean",
        "BG_MAIN": "#1B2A41",
        "BG_CARD": "#273D58",
        "TEXT_PRIMARY": "#CFD8DC",
        "ACCENT_BLUE": "#00BCD4",
        "ACCENT_GREEN": "#00E676",
        "ACCENT_RED": "#FF5252",
        "SWATCH_COLOR": "#00BCD4",  # Used in Settings for swatch
    },
    "corporate": {  # NEW THEME
        "name": "Corporate Grey",
        "BG_MAIN": "#EFEFEF",
        "BG_CARD": "#FFFFFF",
        "TEXT_PRIMARY": "#444444",
        "ACCENT_BLUE": "#9C27B0",
        "ACCENT_GREEN": "#8BC34A",
        "ACCENT_RED": "#F44336",
        "SWATCH_COLOR": "#9C27B0",  # Used in Settings for swatch
    },
}


def generate_qss(palette_key):
    """Generates the QSS string based on the selected palette."""
    if palette_key not in PALETTES:
        palette_key = "light"
    palette = PALETTES[palette_key]

    accent_qcolor = QColor(palette["ACCENT_BLUE"])
    accent_hover = accent_qcolor.lighter(115).name()
    accent_press = accent_qcolor.darker(115).name()

    is_dark = QColor(palette["BG_MAIN"]).lightness() < 128
    selection_bg = (
        QColor(palette["ACCENT_BLUE"]).lighter(150).name()
        if not is_dark
        else QColor(palette["ACCENT_BLUE"]).darker(150).name()
    )

    qss = f"""
        /* General Styles - {palette['name']} */
        QMainWindow, QWidget {{
            background-color: {palette['BG_MAIN']};
            color: {palette['TEXT_PRIMARY']};
            font-family: "Segoe UI", "Inter", sans-serif;
            font-size: 11pt;
        }}
        
        QLabel {{ color: {palette['TEXT_PRIMARY']}; }}

        /* Tabs */
        QTabWidget::pane {{ 
            border-top: 2px solid #DDDDDD; 
            background-color: {palette['BG_CARD']};
        }}
        QTabBar::tab {{
            background: {QColor(palette['BG_MAIN']).lighter(110).name() if not is_dark else QColor(palette['BG_MAIN']).lighter(120).name()}; 
            border: 1px solid #DDDDDD;
            border-bottom-color: #DDDDDD; 
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            padding: 10px 20px;
            min-width: 150px;
            font-weight: 500;
        }}
        QTabBar::tab:selected {{
            background: {palette['BG_CARD']};
            border-color: #DDDDDD;
            border-bottom-color: {palette['BG_CARD']};
            color: {palette['ACCENT_BLUE']};
            font-weight: 600;
        }}

        /* Buttons (General) */
        QPushButton {{
            background-color: {palette['ACCENT_BLUE']};
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 6px;
            font-weight: 600;
            min-height: 35px;
        }}
        QPushButton:hover {{
            background-color: {accent_hover};
        }}
        QPushButton:pressed {{
            background-color: {accent_press};
        }}
        
        /* Secondary Buttons */
        QPushButton#SecondaryButton {{
            background-color: {QColor(palette['BG_MAIN']).lighter(110).name() if not is_dark else QColor(palette['BG_CARD']).lighter(110).name()};
            color: {palette['TEXT_PRIMARY']};
            border: 1px solid #CCCCCC;
            font-weight: 500;
        }}
        QPushButton#SecondaryButton:hover {{
            background-color: {QColor(palette['BG_MAIN']).darker(105).name() if not is_dark else QColor(palette['BG_CARD']).lighter(120).name()};
        }}
        
        /* Danger Button (Clear History) */
        QPushButton#DangerButton {{
            background-color: {palette['ACCENT_RED']};
        }}
        QPushButton#DangerButton:hover {{
            background-color: {QColor(palette['ACCENT_RED']).darker(120).name()};
        }}

        /* Line Edits & ComboBoxes */
        QLineEdit, QComboBox, QSpinBox {{
            border: 1px solid #CCCCCC;
            padding: 10px;
            border-radius: 6px;
            background-color: {palette['BG_CARD']};
            color: {palette['TEXT_PRIMARY']};
            min-height: 35px;
        }}

        /* Group Boxes (Cards) */
        QGroupBox {{
            background-color: {palette['BG_CARD']};
            border: 1px solid #E0E0E0;
            border-radius: 10px;
            margin-top: 15px; 
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 5px;
            color: {palette['ACCENT_BLUE']};
            font-weight: bold;
            font-size: 12pt;
        }}

        /* Progress Bar */
        QProgressBar {{
            border: 1px solid #CCCCCC;
            border-radius: 5px;
            text-align: center;
            color: {palette['TEXT_PRIMARY']};
            background-color: {QColor(palette['BG_MAIN']).lighter(110).name() if not is_dark else QColor(palette['BG_CARD']).lighter(110).name()};
        }}
        QProgressBar::chunk {{
            background-color: {palette['ACCENT_GREEN']};
            border-radius: 5px;
        }}

        /* Table Widget (History) */
        QTableWidget {{
            background-color: {palette['BG_CARD']};
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            gridline-color: #F0F0F0;
            selection-background-color: {selection_bg};
        }}
        QHeaderView::section {{
            background-color: {QColor(palette['BG_CARD']).lighter(105).name() if not is_dark else QColor(palette['BG_CARD']).darker(105).name()};
            color: {palette['ACCENT_BLUE']};
            padding: 8px;
            border-bottom: 2px solid #DDDDDD;
            font-weight: bold;
        }}
        
        /* Format List Items */
        QListWidget {{
            border: 1px solid #DDDDDD;
            border-radius: 6px;
            background-color: {palette['BG_CARD']};
            padding: 5px;
        }}
        QListWidget::item {{
            margin-bottom: 4px;
            padding: 10px;
            border: 1px solid {QColor(palette['BG_CARD']).lighter(105).name() if not is_dark else QColor(palette['BG_CARD']).darker(105).name()};
            border-radius: 6px;
            background-color: {QColor(palette['BG_MAIN']).lighter(110).name() if not is_dark else QColor(palette['BG_CARD']).lighter(105).name()};
            font-size: 10pt;
        }}
        QListWidget::item:selected {{
            background-color: {selection_bg};
            border: 2px solid {palette['ACCENT_BLUE']};
            color: {palette['TEXT_PRIMARY']};
        }}
        
        /* QSplitter */
        QSplitter::handle {{
            background-color: {palette['BG_MAIN']};
            height: 10px;
            margin: 0 2px;
        }}
        
        /* Preview area labels */
        QLabel#MetaDataLabel {{
            font-weight: 500;
            color: {QColor(palette['TEXT_PRIMARY']).darker(130).name() if not is_dark else QColor(palette['TEXT_PRIMARY']).lighter(130).name()};
            font-size: 10pt;
        }}
        QLabel#MetaDataValue {{
            font-weight: 600;
            color: {palette['TEXT_PRIMARY']};
            font-size: 10pt;
        }}
    """
    return qss


def generate_palette_qpalette(theme_name):
    """Generates a QPalette based on the selected theme."""
    if theme_name not in PALETTES:
        theme_name = "light"
    palette_data = PALETTES[theme_name]

    qp = QPalette()
    qp.setColor(QPalette.Window, QColor(palette_data["BG_MAIN"]))
    qp.setColor(QPalette.WindowText, QColor(palette_data["TEXT_PRIMARY"]))
    qp.setColor(QPalette.Base, QColor(palette_data["BG_CARD"]))
    qp.setColor(QPalette.Text, QColor(palette_data["TEXT_PRIMARY"]))
    qp.setColor(QPalette.Button, QColor(palette_data["ACCENT_BLUE"]))
    qp.setColor(
        QPalette.ButtonText,
        QColor("white" if theme_name in ["dark", "deep_ocean"] else "black"),
    )
    # Highlight/Selection colors
    qp.setColor(QPalette.Highlight, QColor(palette_data["ACCENT_BLUE"]))
    qp.setColor(QPalette.HighlightedText, QColor("white"))

    return qp


def load_config():
    """Loads configuration, ensuring all keys exist."""
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
            print("Error reading config.json. Using default.")
            return default_config
    else:
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
    """Converts bytes to a human-readable string (KB, MB, GB)."""
    if size_bytes is None:
        return "N/A"

    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024
        i += 1
    return f"{size_bytes:,.2f} {size_name[i]}"


def is_image_url(url):
    """Checks if a URL path suggests a direct image file."""
    if not url:
        return False
    path = urlparse(url).path
    if not path:
        return False
    ext = Path(path).suffix.lower()
    return ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"]


# --- Custom Loading Widget ---
class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(
            f"background-color: {QColor(PALETTES['dark']['ACCENT_BLUE']).name()}80; border-radius: 10px;"
        )
        self.layout = QVBoxLayout(self)
        self.label = QLabel("Fetching details. Please wait...")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 16pt; background: none;")
        self.layout.addWidget(self.label)
        self.hide()

    def showEvent(self, event):
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().showEvent(event)

    def set_message(self, message):
        self.label.setText(message)


# --- Worker Threads ---


class YtdlpWorker(QThread):
    """Thread to fetch video metadata using yt-dlp."""

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
                "force_generic_extractor": True,
                "dump_single_json": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                self.metadata_fetched.emit(info)
        except Exception as e:
            if "Unsupported URL" in str(e):
                self.metadata_fetched.emit({"is_unsupported": True})
            else:
                self.error_occurred.emit(f"Error fetching media metadata: {e}")


class ImageDownloadWorker(QThread):
    """Thread to download and process direct image links."""

    image_data_fetched = pyqtSignal(bytes, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            with urllib.request.urlopen(self.url, timeout=10) as response:
                if response.getcode() != 200:
                    raise Exception(f"HTTP Error: {response.getcode()}")

                content_type = response.info().get_content_type()

                if not content_type.startswith("image/"):
                    raise Exception(
                        f"URL did not return an image content type: {content_type}"
                    )

                image_data = response.read()

                parsed_url = urlparse(self.url)
                filename = Path(parsed_url.path).name or "image.jpg"

                self.image_data_fetched.emit(image_data, filename)

        except Exception as e:
            self.error_occurred.emit(f"Error downloading image: {e}")


class DownloadWorker(QThread):
    """Thread to handle the actual download process (media or image)."""

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
        if d["status"] == "downloading":
            downloaded_bytes = d.get("downloaded_bytes", 0)
            total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate", 1)
            percent = (downloaded_bytes / total_bytes) * 100 if total_bytes else 0
            speed = d.get("speed", "N/A")
            status_text = (
                f"Speed: {format_bytes(speed)}/s | ETA: {d.get('eta', 'N/A')}s"
            )
            self.progress_signal.emit(percent, status_text)
        elif d["status"] == "finished":
            # Post-processing can start here, no progress updates until it finishes
            if d.get("post_process"):
                self.progress_signal.emit(100.0, "Post-processing/Trimming...")
            pass

    def download_image(self):
        """Handles direct image file download."""
        try:
            with urllib.request.urlopen(self.url, timeout=10) as response:
                if response.getcode() != 200:
                    raise Exception(f"HTTP Error: {response.getcode()}")

                image_data = response.read()
                final_filename = self.filename_template
                final_filepath = os.path.join(self.filepath, final_filename)

                with open(final_filepath, "wb") as f:
                    f.write(image_data)

                final_size = os.path.getsize(final_filepath)

                self.finished_signal.emit(
                    final_filepath, final_filename, format_bytes(final_size), "image"
                )

        except Exception as e:
            self.error_signal.emit(f"Image download failed: {e}")

    def run(self):
        if self.is_image:
            self.download_image()
            return

        # Standard media download (yt-dlp)
        try:
            output_template = os.path.join(self.filepath, self.filename_template)

            # --- TRIMMING/CLIPPING SETUP ---
            start_time = self.start_time
            end_time = self.end_time
            download_sections = None

            # Check for FFmpeg dependency only when trimming or selecting merged format ('best')
            needs_ffmpeg = (start_time or end_time) or (
                self.format_id == "bestvideo*+bestaudio/best"
            )

            if needs_ffmpeg:
                try:
                    # Check for ffmpeg command availability
                    subprocess.run(
                        ["ffmpeg", "-version"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        check=True,  # Will raise an exception if ffmpeg is not found
                    )
                except (FileNotFoundError, subprocess.CalledProcessError):
                    self.error_signal.emit(
                        "FFmpeg not found. Trimming or downloading best quality formats requires FFmpeg to be installed and in your PATH."
                    )
                    return

            # If trimming is required, use yt-dlp's native download_sections option (Fixes PostProcessor error)
            if start_time or end_time:
                start_section = start_time or "00:00:00"
                end_section = end_time or "inf"
                download_sections = [f"*{start_section}-{end_section}"]

            ydl_opts = {
                "format": self.format_id,
                "outtmpl": {"default": output_template},
                "progress_hooks": [self.hook],
                "noplaylist": True,
                "download_sections": download_sections,  # The fix for trimming
                "postprocessors": [],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)

                # Correctly derive the final filename after yt-dlp processing
                final_filename = ydl.prepare_filename(info).replace(
                    self.filepath + os.sep, ""
                )
                final_filepath = os.path.join(self.filepath, final_filename)

                final_size = os.path.getsize(final_filepath)

                self.finished_signal.emit(
                    final_filepath,
                    final_filename,
                    format_bytes(final_size),
                    self.format_id,
                )

        except Exception as e:
            self.error_signal.emit(f"Download failed: {e}")


# --- Application UI Class ---


class ClipShrApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.media_folder = get_media_folder()
        self.metadata = None
        self.selected_format = None
        self.is_image_mode = False

        self.ytdlp_thread = None
        self.download_thread = None
        self.image_fetch_thread = None

        self.setGeometry(
            100, 100, self.config["window_width"], self.config["window_height"]
        )
        self.setWindowTitle("ClipShr - Professional Media Downloader")
        self.setWindowIcon(QIcon("icon.png"))

        self.progress_bar = QProgressBar()

        self.setup_ui()
        self.apply_theme(self.config["theme"])

        Path(self.media_folder).mkdir(exist_ok=True)

    def apply_theme(self, theme_name):
        """Applies the selected QSS theme and palette."""
        qss = generate_qss(theme_name)
        qp = generate_palette_qpalette(theme_name)

        QApplication.setPalette(qp)
        self.setStyleSheet(qss)
        self.config["theme"] = theme_name
        save_config(self.config)

    def setup_ui(self):
        """Initializes the main window layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.downloader_tab = self.create_downloader_tab()
        self.tab_widget.addTab(
            self.downloader_tab, QIcon.fromTheme("system-downloads"), "Downloader"
        )

        self.history_tab = self.create_history_tab()
        self.tab_widget.addTab(
            self.history_tab, QIcon.fromTheme("document-history"), "History"
        )

        self.settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(
            self.settings_tab, QIcon.fromTheme("preferences-system"), "Settings"
        )

        main_layout.addWidget(self.tab_widget)

        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.hide()

        self.tab_widget.currentChanged.connect(self.on_tab_change)
        self.load_history()

    # --- Downloader Tab UI ---

    def create_downloader_tab(self):
        downloader_widget = QWidget()
        main_vbox = QVBoxLayout(downloader_widget)
        main_vbox.setSpacing(15)
        main_vbox.setContentsMargins(20, 20, 20, 20)

        # A. URL Input Bar
        url_hbox = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "Paste media (video/audio) or direct image link here..."
        )
        self.url_input.returnPressed.connect(self.determine_fetch_type)
        self.url_input.textChanged.connect(self.clear_ui_on_text_change)

        self.fetch_button = QPushButton("Fetch Details")
        self.fetch_button.clicked.connect(self.determine_fetch_type)

        url_hbox.addWidget(self.url_input)
        url_hbox.addWidget(self.fetch_button)
        main_vbox.addLayout(url_hbox)

        # B. Content Area (Preview and Formats/Actions)
        content_hbox = QHBoxLayout()
        content_hbox.setSpacing(20)

        # B1. Preview & Metadata Panel (Left - 40% width)
        preview_meta_container = QWidget()
        self.preview_vbox = QVBoxLayout(preview_meta_container)
        self.preview_vbox.setSpacing(15)

        # The Preview Widget (Image/Video Placeholder)
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setMinimumSize(450, 253)
        self.thumbnail_label.setMaximumHeight(350)
        self.thumbnail_label.setText(
            "Paste a link and click 'Fetch' to see the preview."
        )
        self.thumbnail_label.setWordWrap(True)
        self.thumbnail_label.setStyleSheet(
            "font-size: 10pt; color: #666666; border: 1px dashed #CCCCCC; border-radius: 8px;"
        )
        self.preview_vbox.addWidget(self.thumbnail_label)

        # Metadata Layout (Below Preview - using a GroupBox for clarity)
        self.metadata_group = QGroupBox("Media Details")
        meta_grid = QGridLayout(self.metadata_group)
        meta_grid.setSpacing(8)

        # Row 0: Title
        meta_grid.addWidget(QLabel("Title:"), 0, 0, Qt.AlignTop)
        self.title_label = QLabel("N/A")
        self.title_label.setObjectName("MetaDataValue")
        self.title_label.setWordWrap(True)
        meta_grid.addWidget(self.title_label, 0, 1, Qt.AlignTop)

        # Row 1: Source (Source/Uploader/Date)
        meta_grid.addWidget(QLabel("Source:"), 1, 0)
        self.source_label = QLabel("N/A")
        self.source_label.setObjectName("MetaDataValue")
        meta_grid.addWidget(self.source_label, 1, 1)

        meta_grid.addWidget(QLabel("Date:"), 2, 0)
        self.date_label = QLabel("N/A")
        self.date_label.setObjectName("MetaDataValue")
        meta_grid.addWidget(self.date_label, 2, 1)

        meta_grid.addWidget(QLabel("File Type:"), 3, 0)
        self.type_label = QLabel("N/A")
        self.type_label.setObjectName("MetaDataValue")
        meta_grid.addWidget(self.type_label, 3, 1)

        meta_grid.addWidget(QLabel("URL:"), 4, 0)
        self.url_label = QLabel("N/A")
        self.url_label.setObjectName("MetaDataValue")
        self.url_label.setWordWrap(True)
        meta_grid.addWidget(self.url_label, 4, 1)

        meta_grid.setColumnStretch(1, 1)
        self.preview_vbox.addWidget(self.metadata_group)

        # Clipping/Trimming Section (Below metadata)
        self.trim_group = QGroupBox("Media Clipping (Optional)")
        self.trim_group.setObjectName("TrimGroup")
        trim_vbox = QVBoxLayout(self.trim_group)

        # Option 1: Manual Input
        manual_trim_group = QGroupBox("1. Manual Time Input")
        manual_trim_grid = QGridLayout(manual_trim_group)
        manual_trim_grid.setSpacing(10)

        manual_trim_grid.addWidget(QLabel("Start Time (HH:MM:SS):"), 0, 0)
        self.start_time_input = QLineEdit("00:00:00")
        self.start_time_input.setPlaceholderText("e.g., 00:00:10")
        manual_trim_grid.addWidget(self.start_time_input, 0, 1)

        manual_trim_grid.addWidget(QLabel("End Time (HH:MM:SS):"), 1, 0)
        self.end_time_input = QLineEdit()
        self.end_time_input.setPlaceholderText("Leave blank for end of media")
        manual_trim_grid.addWidget(self.end_time_input, 1, 1)
        trim_vbox.addWidget(manual_trim_group)

        # Option 2: Interactive Timeline (Placeholder)
        interactive_group = QGroupBox("2. Interactive Timeline (Future Feature)")
        interactive_vbox = QVBoxLayout(interactive_group)
        interactive_vbox.addWidget(
            QLabel(
                "Interactive drag-and-drop timeline selection is not yet implemented in this version."
            )
        )

        timeline_placeholder = QLabel(" [ Visual Timeline / Waveform Placeholder ] ")
        timeline_placeholder.setAlignment(Qt.AlignCenter)
        timeline_placeholder.setStyleSheet(
            "background-color: #EEEEEE; border: 1px solid #DDDDDD; padding: 10px; font-style: italic;"
        )
        interactive_vbox.addWidget(timeline_placeholder)

        trim_vbox.addWidget(interactive_group)

        self.preview_vbox.addWidget(self.trim_group)
        self.preview_vbox.addStretch(1)

        content_hbox.addWidget(preview_meta_container, 40)

        # B2. Formats and Actions Panel (Right - 60% width)
        actions_group = QGroupBox("Available Formats & Download Options")
        actions_vbox = QVBoxLayout(actions_group)
        actions_vbox.setSpacing(10)

        # Format Lists (Split into two)
        format_splitter = QSplitter(Qt.Vertical)

        # Video Formats
        self.video_format_group = QGroupBox("Video Formats")
        video_vbox = QVBoxLayout(self.video_format_group)
        video_vbox.addWidget(QLabel("Quality | Format | Size"))
        self.video_list_widget = QListWidget()
        self.video_list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.video_list_widget.itemSelectionChanged.connect(
            self.on_video_format_selected
        )
        video_vbox.addWidget(self.video_list_widget)
        format_splitter.addWidget(self.video_format_group)

        # Audio Formats
        self.audio_format_group = QGroupBox("Audio Formats")
        audio_vbox = QVBoxLayout(self.audio_format_group)
        audio_vbox.addWidget(QLabel("Quality | Format | Size"))
        self.audio_list_widget = QListWidget()
        self.audio_list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.audio_list_widget.itemSelectionChanged.connect(
            self.on_audio_format_selected
        )
        audio_vbox.addWidget(self.audio_list_widget)
        format_splitter.addWidget(self.audio_format_group)

        format_splitter.setStretchFactor(0, 2)
        format_splitter.setStretchFactor(1, 1)

        actions_vbox.addWidget(format_splitter)

        # Progress and Download
        actions_vbox.addWidget(self.progress_bar)

        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)

        self.status_label = QLabel("Status: Ready to fetch link.")
        actions_vbox.addWidget(self.status_label)

        self.download_button = QPushButton("Download Selected Format")
        self.download_button.clicked.connect(self.start_download)
        self.download_button.setEnabled(False)
        actions_vbox.addWidget(self.download_button)

        content_hbox.addWidget(actions_group, 60)
        main_vbox.addLayout(content_hbox)

        return downloader_widget

    # --- Downloader Logic ---

    def determine_fetch_type(self):
        """Checks if the URL is a direct image link or a media link."""
        url = self.url_input.text().strip()
        if not url:
            self.status_label.setText("Error: Please enter a URL.")
            return

        # Clear any previous selection before fetching new details
        self.selected_format = None
        self.download_button.setEnabled(False)

        if is_image_url(url):
            self.is_image_mode = True
            self.fetch_image_details(url)
        else:
            self.is_image_mode = False
            self.fetch_metadata(url)

    def fetch_image_details(self, url):
        """Starts the thread to fetch image details."""
        self.status_label.setText("Status: Fetching image details...")
        self.fetch_button.setEnabled(False)
        self.download_button.setEnabled(False)

        self.loading_overlay.set_message("Downloading and preparing image preview...")
        self.loading_overlay.show()

        self.image_fetch_thread = ImageDownloadWorker(url)
        self.image_fetch_thread.image_data_fetched.connect(self.process_image_details)
        self.image_fetch_thread.error_occurred.connect(self.handle_fetch_error)
        self.image_fetch_thread.start()

    def process_image_details(self, image_data, filename):
        """Processes and displays image details."""
        self.loading_overlay.hide()
        self.fetch_button.setEnabled(True)

        self.metadata = {
            "is_image": True,
            "url": self.url_input.text().strip(),
            "title": filename,
            "filename": filename,
            "filesize": len(image_data),
        }

        self.status_label.setText("Status: Image details fetched. Ready to download.")

        # Display image preview
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        scaled_pixmap = pixmap.scaled(
            self.thumbnail_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.thumbnail_label.setPixmap(scaled_pixmap)
        self.thumbnail_label.setText("")

        # Display text metadata
        self.title_label.setText(filename)
        self.source_label.setText(urlparse(self.url_input.text()).netloc)
        self.date_label.setText(datetime.now().strftime("%Y-%m-%d"))
        self.type_label.setText(Path(filename).suffix.upper().lstrip("."))
        self.url_label.setText(self.metadata["url"])

        # Update format lists for image mode
        self.video_list_widget.clear()
        self.audio_list_widget.clear()
        self.video_format_group.setTitle("Image Formats")
        self.audio_format_group.setTitle("Download Options")

        item = QListWidgetItem(self.video_list_widget)

        theme = self.config["theme"]
        # INCREASED FONT SIZE for clarity
        html_content = (
            f'<div style="display: flex; justify-content: space-between; width: 100%;">'
            f'  <span style="font-weight: bold; font-size: 14pt; color: {PALETTES[theme]["ACCENT_GREEN"]};">Original Format</span>'
            f'  <span style="font-size: 12pt; color: #666666;">| {Path(filename).suffix.upper().lstrip(".")}</span>'
            f'  <span style="font-weight: bold; font-size: 14pt;">{format_bytes(len(image_data))}</span>'
            f"</div>"
        )
        content_label = QLabel(html_content)
        item.setSizeHint(QSize(self.video_list_widget.width(), 55))
        self.video_list_widget.setItemWidget(item, content_label)

        image_format = {
            "format_id": "image_original",
            "size": format_bytes(len(image_data)),
        }
        item.setData(Qt.UserRole, image_format)

        self.audio_list_widget.addItem(
            "No other formats available for direct image download."
        )

        # Automatically select the single image format
        self.video_list_widget.setCurrentItem(item)
        self.selected_format = image_format
        self.download_button.setEnabled(True)

        self.trim_group.hide()

    def fetch_metadata(self, url):
        """Starts the thread to fetch video/audio metadata."""
        self.status_label.setText("Status: Fetching video/audio details...")
        self.fetch_button.setEnabled(False)
        self.download_button.setEnabled(False)

        self.loading_overlay.set_message("Fetching details. Please wait...")
        self.loading_overlay.show()

        self.ytdlp_thread = YtdlpWorker(url)
        self.ytdlp_thread.metadata_fetched.connect(self.process_metadata)
        self.ytdlp_thread.error_occurred.connect(self.handle_fetch_error)
        self.ytdlp_thread.start()

    def handle_fetch_error(self, error_message):
        """Handles errors during the metadata fetch process."""
        self.loading_overlay.hide()
        self.status_label.setText(f"Error: {error_message}")
        self.fetch_button.setEnabled(True)
        self.download_button.setEnabled(False)

    def process_metadata(self, info):
        """Processes the metadata received from yt-dlp."""
        self.loading_overlay.hide()

        if info.get("is_unsupported"):
            self.status_label.setText(
                "Error: URL not supported by media extractor. Try using it as a direct image link."
            )
            self.fetch_button.setEnabled(True)
            self.clear_metadata_display()
            return

        self.metadata = info
        self.fetch_button.setEnabled(True)
        self.status_label.setText(
            "Status: Details fetched successfully. Select a format."
        )

        self.display_preview(info)
        self.display_formats(info.get("formats", []))
        self.trim_group.show()

    def clear_ui_on_text_change(self, text):
        """Resets UI elements when the URL input changes."""
        self.metadata = None
        self.selected_format = None
        self.is_image_mode = False
        self.download_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Status: Ready to fetch link.")

        self.thumbnail_label.setText(
            "Paste a link and click 'Fetch' to see the preview."
        )
        self.thumbnail_label.setPixmap(QPixmap())

        self.clear_metadata_display()

        self.video_list_widget.clear()
        self.audio_list_widget.clear()
        self.video_format_group.setTitle("Video Formats")
        self.audio_format_group.setTitle("Audio Formats")
        self.trim_group.hide()

    def clear_metadata_display(self):
        """Clears all metadata labels."""
        self.title_label.setText("N/A")
        self.source_label.setText("N/A")
        self.date_label.setText("N/A")
        self.type_label.setText("N/A")
        self.url_label.setText("N/A")
        self.start_time_input.setText("00:00:00")
        self.end_time_input.clear()

    def display_preview(self, info):
        """Displays the media thumbnail and key information."""

        # 1. Display Text Metadata
        title = info.get("title", "N/A")
        duration_s = info.get("duration")

        self.title_label.setText(title)
        self.source_label.setText(
            info.get("uploader") or info.get("extractor") or "N/A"
        )
        self.url_label.setText(info.get("webpage_url", "N/A"))

        upload_date = info.get("upload_date")
        if upload_date and len(upload_date) == 8:
            formatted_date = datetime.strptime(upload_date, "%Y%m%d").strftime(
                "%Y-%m-%d"
            )
            self.date_label.setText(formatted_date)
        else:
            self.date_label.setText("N/A")

        if duration_s is not None and isinstance(duration_s, (int, float)):
            duration_text = str(timedelta(seconds=duration_s)).split(".")[0]
            self.type_label.setText(f"Media ({duration_text})")
            self.end_time_input.setText(duration_text)
        else:
            self.type_label.setText(f"Media")
            self.end_time_input.clear()

        # 2. Display Thumbnail Image
        thumbnail_url = info.get("thumbnail")
        if thumbnail_url:
            try:
                with urllib.request.urlopen(thumbnail_url, timeout=5) as u:
                    raw_data = u.read()

                pixmap = QPixmap()
                pixmap.loadFromData(raw_data)

                max_size = self.thumbnail_label.maximumHeight()
                scaled_pixmap = pixmap.scaled(
                    max_size * 16 // 9,
                    max_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
                self.thumbnail_label.setPixmap(scaled_pixmap)
                self.thumbnail_label.setText("")
            except Exception:
                self.thumbnail_label.setText("Could not load thumbnail.")
        else:
            self.thumbnail_label.setText("No thumbnail available.")

    def display_formats(self, formats):
        """Displays available formats, grouped into Video and Audio."""
        self.video_list_widget.clear()
        self.audio_list_widget.clear()

        video_formats = []
        audio_formats = []

        # Add a special "Best Quality (Video+Audio)" entry first
        best_format = {
            "format_id": "bestvideo*+bestaudio/best",
            "display_quality": "BEST QUALITY (Requires FFmpeg for merge)",
            "ext": "mp4/mkv/webm",
            "size": "Estimated (Best)",
            "raw_format": {"height": 9999, "abr": 9999},  # Highest sorting priority
        }
        video_formats.append(best_format)

        for f in formats:
            # Skip if no known size information
            if f.get("filesize") is None and f.get("filesize_approx") is None:
                continue

            size = f.get("filesize") or f.get("filesize_approx")
            size_str = format_bytes(size)

            # Skip the specific 'best' formats already covered by the manual entry
            if f.get("format_id") in ["bestvideo", "bestaudio", "bestvideo+bestaudio"]:
                continue

            format_data = {
                "format_id": f["format_id"],
                "ext": f.get("ext", "unk"),
                "size": size_str,
                "raw_format": f,
            }

            # Grouping Logic:
            if f.get("vcodec") != "none" and f.get("acodec") != "none":
                # Combined Video+Audio
                format_data["display_quality"] = f"{f.get('height')}p ({f.get('ext')})"
                video_formats.append(format_data)
            elif f.get("vcodec") != "none" and f.get("acodec") == "none":
                # Video Only (often requires merging, but good for specific workflows)
                format_data["display_quality"] = f"Video Only - {f.get('height')}p"
                video_formats.append(format_data)
            elif f.get("vcodec") == "none" and f.get("acodec") != "none":
                # Audio Only
                format_data["display_quality"] = (
                    f"Audio Only - {f.get('abr', 'N/A')}k ({f.get('ext')})"
                )
                audio_formats.append(format_data)

        # Sort video formats by height descending
        video_formats.sort(key=lambda x: x["raw_format"].get("height", 0), reverse=True)
        # Sort audio formats by bitrate descending
        audio_formats.sort(key=lambda x: x["raw_format"].get("abr", 0), reverse=True)

        # Populate List Widgets
        self._populate_format_list(self.video_list_widget, video_formats)
        self._populate_format_list(self.audio_list_widget, audio_formats)

        if not video_formats and not audio_formats:
            self.video_list_widget.addItem(
                "No downloadable formats with size information found."
            )
            self.download_button.setEnabled(False)

    def _populate_format_list(self, list_widget, formats):
        """Helper to create and populate list items with structured content. (UI Fix applied here)"""
        list_widget.clear()
        theme = self.config["theme"]

        if not formats:
            list_widget.addItem("No formats found in this category.")
            return

        for f in formats:
            # UI Fix: Increased font size to 12pt for better clarity
            html_content = (
                f'<div style="display: flex; justify-content: space-between; width: 100%;">'
                f'  <span style="font-weight: bold; font-size: 12pt; color: {PALETTES[theme]["TEXT_PRIMARY"]};">{f["display_quality"]}</span>'
                f'  <span style="font-weight: bold; font-size: 12pt; color: {PALETTES[theme]["ACCENT_GREEN"]};">{f["size"]}</span>'
                f"</div>"
            )

            content_label = QLabel(html_content)

            list_item = QListWidgetItem(list_widget)
            # UI Fix: Increased list item height to 50px for more space
            list_item.setSizeHint(QSize(list_widget.width(), 50))
            list_item.setData(Qt.UserRole, f)
            list_widget.setItemWidget(list_item, content_label)

    def on_video_format_selected(self):
        """Handles selection in the video list."""
        self.audio_list_widget.clearSelection()
        selected_items = self.video_list_widget.selectedItems()
        self._handle_format_selection(selected_items)

    def on_audio_format_selected(self):
        """Handles selection in the audio list."""
        self.video_list_widget.clearSelection()
        selected_items = self.audio_list_widget.selectedItems()
        self._handle_format_selection(selected_items)

    def _handle_format_selection(self, selected_items):
        """Stores the selected format and enables the download button."""
        if selected_items:
            self.selected_format = selected_items[0].data(Qt.UserRole)
            self.download_button.setEnabled(True)
            self.status_label.setText(
                f"Status: Selected format {self.selected_format.get('display_quality', 'N/A')}. Ready to download."
            )
        else:
            self.selected_format = None
            self.download_button.setEnabled(False)
            self.status_label.setText("Status: Select a format to proceed.")

    def start_download(self):
        """Starts the download thread (media or image)."""
        if not self.metadata or not self.selected_format:
            self.status_label.setText(
                "Error: Please fetch link details and select a format first."
            )
            return

        url = self.url_input.text().strip()

        self.status_label.setText("Status: Download starting...")
        self.download_button.setEnabled(False)
        self.fetch_button.setEnabled(False)

        if self.is_image_mode:
            filename_template = self.metadata["filename"]
            download_worker = DownloadWorker(
                url,
                "image_original",
                None,
                None,
                self.media_folder,
                filename_template,
                is_image=True,
            )
        else:
            format_id = self.selected_format["format_id"]
            start_time = self.start_time_input.text().strip()
            end_time = self.end_time_input.text().strip()

            if start_time == "00:00:00" and not end_time:
                start_time = end_time = None

            filename_template = f"%(title)s.%(ext)s"

            download_worker = DownloadWorker(
                url,
                format_id,
                start_time,
                end_time,
                self.media_folder,
                filename_template,
            )

        self.download_thread = download_worker
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.error_signal.connect(self.handle_download_error)
        self.download_thread.start()

    def update_progress(self, percent, status_text):
        """Updates the progress bar and status label during download."""
        self.progress_bar.setValue(int(percent))
        self.status_label.setText(f"Downloading... {int(percent)}% ({status_text})")

    def download_finished(self, filepath, filename, size_str, format_id):
        """Handles post-download logic: saving history and resetting UI."""
        self.status_label.setText(f"✅ Download Complete! File size: {size_str}")
        self.progress_bar.setValue(100)

        db = load_db()
        history_item = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "original_url": self.url_input.text().strip(),
            "title": self.metadata.get("title", "Unknown Title"),
            "format": format_id,
            "filename": filename,
            "size": size_str,
            "is_image": self.is_image_mode,
        }
        db.append(history_item)
        save_db(db)

        self.download_button.setEnabled(True)
        self.fetch_button.setEnabled(True)

        QMessageBox.information(
            self,
            "Download Complete",
            f"Download of '{history_item['title']}' finished successfully!\nSize: {size_str}",
        )

    def handle_download_error(self, error_message):
        """Handles errors during the download process."""
        self.status_label.setText(f"❌ Download Failed: {error_message}")
        self.progress_bar.setValue(0)
        self.download_button.setEnabled(True)
        self.fetch_button.setEnabled(True)

    # --- History Tab UI and Logic ---

    def create_history_tab(self):
        history_widget = QWidget()
        vbox = QVBoxLayout(history_widget)
        vbox.setContentsMargins(20, 20, 20, 20)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels(
            ["Date", "Title", "Type", "Format", "Size", "Status", "Action"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        self.history_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch
        )
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        vbox.addWidget(self.history_table)

        # History Controls
        controls_hbox = QHBoxLayout()
        self.clear_history_button = QPushButton("Clear ALL History & Files")
        self.clear_history_button.setObjectName("DangerButton")
        self.clear_history_button.clicked.connect(self.clear_history_prompt)

        controls_hbox.addStretch(1)
        controls_hbox.addWidget(self.clear_history_button)
        vbox.addLayout(controls_hbox)

        return history_widget

    def load_history(self):
        """Fetches and populates the history table."""
        db = load_db()
        self.history_table.setRowCount(len(db))

        for row, item in enumerate(reversed(db)):
            date_item = QTableWidgetItem(item.get("timestamp", "N/A").split(" ")[0])
            self.history_table.setItem(row, 0, date_item)

            title_item = QTableWidgetItem(item.get("title", "Unknown Title"))
            self.history_table.setItem(row, 1, title_item)

            type_text = "Image" if item.get("is_image") else "Media"
            type_item = QTableWidgetItem(type_text)
            self.history_table.setItem(row, 2, type_item)

            format_item = QTableWidgetItem(item.get("format", "N/A"))
            self.history_table.setItem(row, 3, format_item)

            size_item = QTableWidgetItem(item.get("size", "N/A"))
            self.history_table.setItem(row, 4, size_item)

            status_item = QTableWidgetItem("Completed")
            status_item.setForeground(
                QColor(PALETTES[self.config["theme"]]["ACCENT_GREEN"])
            )
            self.history_table.setItem(row, 5, status_item)

            # Action Button
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 5, 5, 5)
            action_layout.setSpacing(5)

            delete_btn = QPushButton("Delete Record")
            delete_btn.setObjectName("SecondaryButton")
            delete_btn.clicked.connect(lambda _, r=row: self.delete_history_item(r))
            action_layout.addWidget(delete_btn)

            open_btn = QPushButton("Open File")
            open_btn.clicked.connect(lambda _, r=row: self.open_downloaded_file(r))
            action_layout.addWidget(open_btn)

            self.history_table.setCellWidget(row, 6, action_widget)
            self.history_table.setRowHeight(row, 45)

    def delete_history_item(self, row_index):
        """Deletes a single history record and updates the display."""
        db = load_db()
        db_index = len(db) - 1 - row_index

        if db_index < 0 or db_index >= len(db):
            self.status_label.setText("Error: History item not found.")
            return

        item_to_delete = db[db_index]

        msg = QMessageBox(self)
        msg.setWindowTitle("Confirm Deletion")
        msg.setText(
            f"Are you sure you want to delete the history record for:\n'{item_to_delete.get('title', 'Unknown')}'?"
        )
        msg.setInformativeText("This will NOT delete the actual file, only the record.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec_() == QMessageBox.Yes:
            db.pop(db_index)
            save_db(db)
            self.load_history()

    def open_downloaded_file(self, row_index):
        """Opens the downloaded file using the system's default application."""
        db = load_db()
        db_index = len(db) - 1 - row_index

        if db_index < 0 or db_index >= len(db):
            return

        item = db[db_index]
        filename = item.get("filename")
        if not filename:
            QMessageBox.warning(self, "Error", "File path missing in history record.")
            return

        filepath = os.path.join(get_media_folder(), filename)

        if not os.path.exists(filepath):
            QMessageBox.warning(
                self,
                "File Error",
                f"File not found: {filepath}\nIt may have been moved or deleted manually.",
            )
            return

        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(filepath))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not open file: {e}")

    # --- Settings Tab UI and Logic ---

    def create_settings_tab(self):
        settings_widget = QWidget()
        vbox = QVBoxLayout(settings_widget)
        vbox.setContentsMargins(20, 20, 20, 20)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea {border: none;}")
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        scroll_vbox = QVBoxLayout(scroll_content)
        scroll_vbox.setSpacing(20)

        # 1. Theme Settings
        theme_group = QGroupBox("UI Appearance & Color Palette")
        theme_vbox = QVBoxLayout(theme_group)
        self.theme_radio_group = QButtonGroup(self)

        for key, palette_data in PALETTES.items():
            # FIX: Use QLabel and QHBoxLayout to display the swatch and text cleanly
            color_swatch = QLabel(
                f"<span style='color: {palette_data['SWATCH_COLOR']}; font-size: 14pt;'>■</span>"
            )
            radio = QRadioButton(palette_data["name"])
            radio.setProperty("theme_key", key)
            if key == self.config["theme"]:
                radio.setChecked(True)

            radio_hbox = QHBoxLayout()
            radio_hbox.addWidget(radio)
            radio_hbox.addWidget(color_swatch)
            radio_hbox.addStretch(1)

            self.theme_radio_group.addButton(radio)
            theme_vbox.addLayout(radio_hbox)

        self.theme_radio_group.buttonClicked.connect(self.change_theme_from_radio)
        scroll_vbox.addWidget(theme_group)

        # 2. Download Folder Settings
        folder_group = QGroupBox("Download Workspace")
        folder_vbox = QVBoxLayout(folder_group)

        folder_hbox = QHBoxLayout()
        self.folder_path_label = QLineEdit(self.config["media_folder"])
        self.folder_path_label.setReadOnly(True)

        self.change_folder_button = QPushButton("Change Folder")
        self.change_folder_button.setObjectName("SecondaryButton")
        self.change_folder_button.clicked.connect(self.change_download_folder)

        folder_hbox.addWidget(QLabel("Current Workspace Path:"))
        folder_hbox.addWidget(self.folder_path_label)
        folder_hbox.addWidget(self.change_folder_button)
        folder_vbox.addLayout(folder_hbox)
        scroll_vbox.addWidget(folder_group)

        # 3. Download Preferences
        pref_group = QGroupBox("Download Preferences")
        pref_vbox = QVBoxLayout(pref_group)

        self.compress_checkbox = QCheckBox(
            "Default: Embed metadata and optimize for compression (Recommended for final files)."
        )
        self.compress_checkbox.setChecked(self.config.get("default_compress", True))
        self.compress_checkbox.stateChanged.connect(self.save_download_preferences)
        pref_vbox.addWidget(self.compress_checkbox)

        scroll_vbox.addWidget(pref_group)

        scroll_vbox.addStretch(1)
        vbox.addWidget(scroll_area)

        return settings_widget

    def change_theme_from_radio(self, radio_button):
        """Changes the application theme based on radio button selection."""
        theme_name = radio_button.property("theme_key")
        self.apply_theme(theme_name)

    def change_download_folder(self):
        """Opens a dialog to select a new download folder."""
        new_folder = QFileDialog.getExistingDirectory(
            self,
            "Select New Download Workspace",
            QDir.homePath(),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )

        if new_folder:
            self.config["media_folder"] = new_folder
            save_config(self.config)
            self.media_folder = new_folder
            self.folder_path_label.setText(new_folder)
            QMessageBox.information(
                self,
                "Workspace Changed",
                f"Download workspace successfully set to:\n{new_folder}",
            )

    def save_download_preferences(self):
        """Saves the checkbox state for download preferences."""
        self.config["default_compress"] = self.compress_checkbox.isChecked()
        save_config(self.config)

    def on_tab_change(self, index):
        """Handles actions when the tab changes (e.g., refreshing history)."""
        if self.tab_widget.tabText(index) == "History":
            self.load_history()

    def clear_history_prompt(self):
        """Prompts the user for confirmation before clearing history and files."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Clear All History & Files")
        dialog_layout = QVBoxLayout(dialog)

        dialog_layout.addWidget(
            QLabel(
                "WARNING: This will delete ALL download history records AND all downloaded media files in the media folder."
            )
        )
        dialog_layout.addWidget(
            QLabel("<b>Type 'DELETE ALL' below to confirm this permanent action:</b>")
        )

        text_input = QLineEdit()
        text_input.setPlaceholderText("DELETE ALL")
        dialog_layout.addWidget(text_input)

        ok_button = QPushButton("Confirm Delete")
        cancel_button = QPushButton("Cancel")

        ok_button.setObjectName("DangerButton")
        cancel_button.setObjectName("SecondaryButton")

        def check_and_accept():
            if text_input.text() == "DELETE ALL":
                dialog.accept()
            else:
                QMessageBox.warning(
                    dialog,
                    "Confirmation Failed",
                    "Input did not match 'DELETE ALL'. Please try again.",
                )

        ok_button.clicked.connect(check_and_accept)
        cancel_button.clicked.connect(dialog.reject)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)

        dialog_layout.addLayout(button_layout)

        if dialog.exec_() == QDialog.Accepted:
            db = load_db()
            deleted_count = 0

            # Delete files
            media_folder = get_media_folder()
            for item in db:
                filepath = os.path.join(media_folder, item.get("filename", ""))
                if os.path.exists(filepath):
                    try:
                        os.remove(filepath)
                        deleted_count += 1
                    except Exception as e:
                        print(f"Failed to delete file {item.get('filename')}: {e}")
                        pass

            # Clear history database
            save_db([])
            self.load_history()

            QMessageBox.information(
                self,
                "History Cleared",
                f"✅ History and files cleared successfully!\nDeleted {deleted_count} file(s).",
            )


# --- Main Execution ---


def main():
    config = load_config()
    Path(get_media_folder()).mkdir(exist_ok=True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    font = QFont("Segoe UI", 11)
    app.setFont(font)

    window = ClipShrApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
