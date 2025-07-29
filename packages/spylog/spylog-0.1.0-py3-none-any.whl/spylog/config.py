"""
Konfiguracja dla Spylog
"""

import os
from pathlib import Path
from typing import List, Dict, Any


class SpylogConfig:
    """Klasa konfiguracji dla Spylog"""

    def __init__(self):
        self.original_python = self._find_original_python()
        self.dangerous_functions = ["eval", "exec", "__import__"]
        self.dangerous_modules = [
            ("os", "system"),
            ("subprocess", "call"),
            ("subprocess", "run"),
            ("subprocess", "Popen"),
        ]
        self.security_enabled = True
        self.interactive_warnings = True
        self.max_line_length = 120
        self.encoding = "utf-8"

    def _find_original_python(self) -> str:
        """Znajdź oryginalny interpreter Pythona"""
        # Sprawdź zmienną środowiskową
        original_python = os.environ.get("SPYLOG_ORIGINAL_PYTHON")
        if original_python and os.path.exists(original_python):
            return original_python

        # Szukaj pythona w PATH, pomijając obecny katalog
        current_dir = os.path.dirname(os.path.abspath(__file__))

        for path in os.environ.get("PATH", "").split(os.pathsep):
            if path == current_dir:
                continue
            python_path = os.path.join(path, "python")
            if os.path.exists(python_path) and os.access(python_path, os.X_OK):
                return python_path

        # Fallback - standardowe lokalizacje
        fallbacks = ["/usr/bin/python3", "/usr/bin/python", "/usr/local/bin/python3", "python3", "python"]

        for python_path in fallbacks:
            if os.path.exists(python_path):
                return python_path

        return "python3"

    def get_config_file_path(self) -> Path:
        """Zwróć ścieżkę do pliku konfiguracyjnego"""
        home = Path.home()
        return home / ".spylog" / "config.json"

    def load_config(self):
        """Załaduj konfigurację z pliku"""
        config_file = self.get_config_file_path()
        if config_file.exists():
            import json

            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)

                # Aktualizuj konfigurację
                for key, value in config_data.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
            except Exception as e:
                print(f"Ostrzeżenie: Nie udało się załadować konfiguracji: {e}")

    def save_config(self):
        """Zapisz konfigurację do pliku"""
        config_file = self.get_config_file_path()
        config_file.parent.mkdir(parents=True, exist_ok=True)

        import json

        config_data = {
            "original_python": self.original_python,
            "dangerous_functions": self.dangerous_functions,
            "dangerous_modules": self.dangerous_modules,
            "security_enabled": self.security_enabled,
            "interactive_warnings": self.interactive_warnings,
            "max_line_length": self.max_line_length,
            "encoding": self.encoding,
        }

        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ostrzeżenie: Nie udało się zapisać konfiguracji: {e}")


# Globalna instancja konfiguracji
config = SpylogConfig()
config.load_config()
