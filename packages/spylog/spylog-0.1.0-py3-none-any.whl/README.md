# 🔍 Spylog - Python Validator Proxy

Spylog to zaawansowane narzędzie walidujące pliki Python przed ich uruchomieniem. Działa jako proxy dla interpretera Pythona, sprawdzając składnię, bezpieczeństwo i jakość kodu.

## 🚀 Instalacja

### Wymagania
- Python 3.8+
- Poetry (zalecane) lub pip

### Instalacja z Poetry (zalecane)

```bash
# Klonuj repozytorium
git clone https://github.com/your-username/spylog.git
cd spylog

# Zainstaluj zależności i paczkę
poetry install

# Aktywuj środowisko
poetry shell
```

### Instalacja z pip

```bash
# Z PyPI (gdy opublikowane)
pip install spylog

# Z kodu źródłowego
git clone https://github.com/your-username/spylog.git
cd spylog
pip install .
```

### Automatyczna instalacja z aliasem

```bash
# Użyj skryptu instalacyjnego
chmod +x install.sh
./install.sh
```

## ⚙️ Konfiguracja aliasu

Aby Spylog działał jako zamiennik dla komendy `python`, skonfiguruj alias:

### Bash/Zsh
```bash
# Dodaj do ~/.bashrc lub ~/.zshrc
export SPYLOG_ORIGINAL_PYTHON=$(which python)
alias python='spylog'
```

### Fish
```fish
# Dodaj do ~/.config/fish/config.fish
set -gx SPYLOG_ORIGINAL_PYTHON (which python)
alias python='spylog'
```

## 📖 Użytkowanie

Po skonfigurowaniu aliasu, Spylog automatycznie waliduje pliki Python:

```bash
# Waliduje script.py przed uruchomieniem
python script.py

# Waliduje z argumentami
python my_script.py --arg1 value --verbose

# Tryb interaktywny (bez walidacji)
python

# Flagi Pythona (bez walidacji)
python -c "print('Hello')"
python -m module
python --help
```

## ✅ Co sprawdza Spylog?

### 🔍 Sprawdzenia podstawowe
- **Składnia Python** - używa AST do wykrywania błędów składni
- **Kodowanie plików** - obsługuje UTF-8 i fallback do Latin-1
- **Możliwość odczytu** - sprawdza uprawnienia i dostępność pliku

### 🛡️ Sprawdzenia bezpieczeństwa
- `eval()` i `exec()` - potencjalnie niebezpieczne funkcje
- `os.system()` - bezpośrednie wywołania systemowe
- `subprocess` - wywołania zewnętrznych procesów
- Dynamiczne importy `__import__()`

### 📊 Sprawdzenia jakości kodu
- **Długość linii** - domyślnie max 120 znaków
- **Mieszanie wcięć** - wykrywa tabulatory vs spacje
- **Rozszerzalne** - łatwo dodać własne reguły

## 🖥️ Przykład działania

```bash
$ python bad_script.py
🔍 Spylog Python Validator
📁 Walidacja: bad_script.py

⚠️  OSTRZEŻENIA BEZPIECZEŃSTWA:
   • Znaleziono os.system() w linii 5
   • Znaleziono wywołanie 'eval' w linii 8

📋 OSTRZEŻENIA JAKOŚCI KODU:
   • Linia 12 przekracza maksymalną długość (145 > 120 znaków)

Czy kontynuować mimo ostrzeżeń? (t/n): n
❌ Wykonanie przerwane przez użytkownika z powodu ostrzeżeń

$ python good_script.py
🔍 Spylog Python Validator
📁 Walidacja: good_script.py
✅ Plik jest poprawny
🚀 Uruchamiam: python good_script.py
--------------------------------------------------
Hello, World!
```

## 🔧 Rozwój z Poetry

### Podstawowe komendy Poetry

```bash
# Instalacja w trybie deweloperskim
poetry install

# Dodanie nowej zależności
poetry add requests

# Dodanie zależności deweloperskiej
poetry add --group dev pytest

# Aktywacja środowiska
poetry shell

# Uruchomienie skryptu
poetry run python script.py

# Budowanie paczki
poetry build

# Publikacja na PyPI
poetry publish
```

### Uruchamianie testów

```bash
# Z Poetry
poetry run pytest

# Z aktywowanym środowiskiem
pytest

# Z pokryciem kodu
poetry run pytest --cov=spylog
```

### Formatowanie i linting

```bash
# Black - formatowanie
poetry run black spylog tests

# Flake8 - linting
poetry run flake8 spylog tests

# MyPy - sprawdzanie typów
poetry run mypy spylog
```

## 🛠️ Makefile (opcjonalny)

```bash
# Wszystkie sprawdzenia
make check

# Tylko testy
make test

# Formatowanie
make format

# Instalacja
make install
```

## ⚙️ Konfiguracja

Spylog tworzy plik konfiguracyjny w `~/.spylog/config.json`:

```json
{
  "original_python": "/usr/bin/python3",
  "dangerous_functions": ["eval", "exec", "__import__"],
  "dangerous_modules": [
    ["os", "system"],
    ["subprocess", "call"]
  ],
  "security_enabled": true,
  "interactive_warnings": true,
  "max_line_length": 120,
  "encoding": "utf-8"
}
```

### Dostosowywanie przez API

```python
from spylog import SpylogConfig

config = SpylogConfig()
config.security_enabled = False
config.max_line_length = 100
config.save_config()
```

## 🔌 Rozszerzanie

Dodaj własne sprawdzenia w `spylog/validator.py`:

```python
def check_custom_rules(content: str) -> List[str]:
    """Własne reguły walidacji"""
    warnings = []
    
    if "TODO" in content:
        warnings.append("Znaleziono TODO w kodzie")
    
    if "print(" in content:
        warnings.append("Używanie print() w kodzie produkcyjnym")
    
    return warnings
```

## 📁 Struktura projektu

```
spylog/
├── spylog/              # Główny pakiet
│   ├── __init__.py      # Metadane i eksporty
│   ├── main.py          # Logika proxy
│   ├── validator.py     # Walidacja i sprawdzenia
│   └── config.py        # Zarządzanie konfiguracją
├── tests/               # Testy jednostkowe
├── pyproject.toml       # Konfiguracja Poetry
├── README.md            # Dokumentacja
└── install.sh           # Skrypt instalacyjny
```

## 🤝 Współpraca

1. **Fork** repozytorium
2. **Utwórz branch**: `git checkout -b feature/nowa-funkcjonalność`
3. **Commituj**: `git commit -am 'Dodaj nową funkcjonalność'`
4. **Push**: `git push origin feature/nowa-funkcjonalność`
5. **Pull Request**

## 🐛 Zgłaszanie błędów

- Użyj GitHub Issues
- Podaj wersję Python i Spylog (`spylog --version`)
- Dołącz przykład problematycznego kodu
- Opisz oczekiwane vs rzeczywiste zachowanie

## 📝 Licencja

MIT License - projekt open source, darmowy do użytku komercyjnego i prywatnego.

## 🎯 Roadmapa

### v0.2.0
- [ ] Plugin system
- [ ] GUI konfiguracji
- [ ] Integracja z pre-commit
- [ ] Cache wyników walidacji

### v0.3.0
- [ ] VS Code extension
- [ ] Integracja z CI/CD
- [ ] Raportowanie metryk
- [ ] Wsparcie dla więcej języków

---

**🐍 Bezpieczniejszy Python z Spylog! ✨**