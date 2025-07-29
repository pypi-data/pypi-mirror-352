"""
Moduł walidacji plików Python
"""

import ast
import os
from typing import Tuple, List
from .config import config


class ValidationResult:
    """Wynik walidacji"""

    def __init__(self, is_valid: bool, message: str, warnings: List[str] = None):
        self.is_valid = is_valid
        self.message = message
        self.warnings = warnings or []


class SecurityChecker(ast.NodeVisitor):
    """Checker bezpieczeństwa dla AST"""

    def __init__(self):
        self.warnings = []

    def visit_Call(self, node):
        """Sprawdź wywołania funkcji"""
        if isinstance(node.func, ast.Name):
            # Sprawdź niebezpieczne funkcje
            if node.func.id in config.dangerous_functions:
                self.warnings.append(f"Znaleziono wywołanie '{node.func.id}' w linii {node.lineno}")

        elif isinstance(node.func, ast.Attribute):
            # Sprawdź wywołania modułów
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id
                func_name = node.func.attr

                for dangerous_module, dangerous_func in config.dangerous_modules:
                    if module_name == dangerous_module and func_name == dangerous_func:
                        self.warnings.append(f"Znaleziono {module_name}.{func_name}() w linii {node.lineno}")

        self.generic_visit(node)

    def visit_Import(self, node):
        """Sprawdź importy"""
        for alias in node.names:
            if alias.name in ["os", "subprocess", "sys"]:
                # Można dodać ostrzeżenia o importach systemowych
                pass
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Sprawdź importy from"""
        if node.module in ["os", "subprocess", "sys"]:
            for alias in node.names:
                if alias.name in ["system", "call", "run", "Popen"]:
                    self.warnings.append(
                        f"Import niebezpiecznej funkcji '{alias.name}' z modułu '{node.module}' w linii {node.lineno}"
                    )
        self.generic_visit(node)


def validate_syntax(content: str) -> Tuple[bool, str]:
    """Waliduj składnię Python"""
    try:
        ast.parse(content)
        return True, "Składnia poprawna"
    except SyntaxError as e:
        return False, f"Błąd składni w linii {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Błąd parsowania: {e}"


def check_security(content: str) -> List[str]:
    """Sprawdź bezpieczeństwo kodu"""
    if not config.security_enabled:
        return []

    try:
        tree = ast.parse(content)
        checker = SecurityChecker()
        checker.visit(tree)
        return checker.warnings
    except Exception:
        # Jeśli nie można sprawdzić bezpieczeństwa, zwróć pustą listę
        return []


def check_code_quality(content: str) -> List[str]:
    """Sprawdź jakość kodu"""
    warnings = []

    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        # Sprawdź długość linii
        if len(line) > config.max_line_length:
            warnings.append(f"Linia {i} przekracza maksymalną długość ({len(line)} > {config.max_line_length} znaków)")

        # Sprawdź tabulatory vs spacje (PEP 8)
        if "\t" in line and "    " in line:
            warnings.append(f"Linia {i} miesza tabulatory i spacje")

    return warnings


def validate_python_file(file_path: str) -> ValidationResult:
    """
    Główna funkcja walidacji pliku Python

    Args:
        file_path: Ścieżka do pliku Python

    Returns:
        ValidationResult: Wynik walidacji
    """
    # Sprawdź czy plik istnieje
    if not os.path.exists(file_path):
        return ValidationResult(False, f"Plik '{file_path}' nie istnieje")

    # Odczytaj plik
    try:
        with open(file_path, "r", encoding=config.encoding) as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            # Spróbuj inne kodowanie
            with open(file_path, "r", encoding="latin-1") as f:
                content = f.read()
        except Exception as e:
            return ValidationResult(False, f"Błąd odczytu pliku: {e}")
    except Exception as e:
        return ValidationResult(False, f"Błąd odczytu pliku: {e}")

    # Waliduj składnię
    syntax_valid, syntax_message = validate_syntax(content)
    if not syntax_valid:
        return ValidationResult(False, syntax_message)

    # Sprawdzenia bezpieczeństwa
    security_warnings = check_security(content)

    # Sprawdzenia jakości kodu
    quality_warnings = check_code_quality(content)

    # Wszystkie ostrzeżenia
    all_warnings = security_warnings + quality_warnings

    # Jeśli są ostrzeżenia bezpieczeństwa i tryb interaktywny włączony
    if security_warnings and config.interactive_warnings:
        print(f"\n⚠️  OSTRZEŻENIA BEZPIECZEŃSTWA:")
        for warning in security_warnings:
            print(f"   • {warning}")

        if quality_warnings:
            print(f"\n📋 OSTRZEŻENIA JAKOŚCI KODU:")
            for warning in quality_warnings:
                print(f"   • {warning}")

        print()
        response = input("Czy kontynuować mimo ostrzeżeń? (t/n): ").lower()
        if response not in ["t", "tak", "y", "yes"]:
            return ValidationResult(False, "Wykonanie przerwane przez użytkownika z powodu ostrzeżeń", all_warnings)

    return ValidationResult(True, "Plik jest poprawny", all_warnings)


def is_python_file(file_path: str) -> bool:
    """
    Sprawdź czy plik to prawdopodobnie plik Python

    Args:
        file_path: Ścieżka do pliku

    Returns:
        bool: True jeśli to plik Python
    """
    # Sprawdź rozszerzenie
    if file_path.endswith(".py"):
        return True

    # Sprawdź shebang i zawartość
    try:
        with open(file_path, "r", encoding=config.encoding) as f:
            first_line = f.readline().strip()
            if first_line.startswith("#!") and "python" in first_line:
                return True

            # Spróbuj sparsować jako Python
            f.seek(0)
            content = f.read()
            ast.parse(content)
            return True
    except:
        return False
