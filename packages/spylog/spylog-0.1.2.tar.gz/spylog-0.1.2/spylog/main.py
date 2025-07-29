#!/usr/bin/env python3
"""
Główny moduł Spylog - Python Validator Proxy
"""

import sys
import os
import subprocess
from typing import List, Optional

from .config import config
from .validator import validate_python_file, is_python_file


def find_python_file_in_args(args: List[str]) -> Optional[str]:
    """
    Znajdź plik Python w argumentach

    Args:
        args: Lista argumentów

    Returns:
        Ścieżka do pliku Python lub None
    """
    for arg in args:
        # Pomijaj flagi (zaczynające się od -)
        if arg.startswith("-"):
            continue

        # Sprawdź czy to plik Python
        if os.path.isfile(arg) and (arg.endswith(".py") or is_python_file(arg)):
            return arg

    return None


def should_validate(args: List[str]) -> bool:
    """
    Sprawdź czy powinniśmy walidować

    Args:
        args: Argumenty wiersza poleceń

    Returns:
        True jeśli należy walidować
    """
    if not args:
        return False

    # Pomijaj niektóre flagi które nie wymagają walidacji
    skip_flags = ["-c", "--command", "-m", "--module", "-h", "--help", "-V", "--version"]

    for flag in skip_flags:
        if flag in args:
            return False

    return find_python_file_in_args(args) is not None


def execute_python(args: List[str]) -> int:
    """
    Wykonaj oryginalny Python z argumentami

    Args:
        args: Argumenty do przekazania

    Returns:
        Kod wyjścia
    """
    original_python = config.original_python

    try:
        result = subprocess.run([original_python] + args, stdout=sys.stdout, stderr=sys.stderr, stdin=sys.stdin)
        return result.returncode
    except KeyboardInterrupt:
        return 130  # Standardowy kod dla Ctrl+C
    except Exception as e:
        print(f"❌ Błąd uruchamiania: {e}", file=sys.stderr)
        return 1


def print_banner():
    """Wyświetl banner Spylog"""
    print("🔍 Spylog Python Validator")


def print_validation_result(python_file: str, result):
    """Wyświetl wynik walidacji"""
    print(f"📁 Walidacja: {python_file}")

    if result.is_valid:
        print(f"✅ {result.message}")
        if result.warnings:
            print("⚠️  Ostrzeżenia:")
            for warning in result.warnings:
                print(f"   • {warning}")
    else:
        print(f"❌ {result.message}")
        return False

    return True


def main():
    """Główna funkcja spylog"""
    args = sys.argv[1:]

    # Sprawdź czy potrzebujemy walidacji
    if not should_validate(args):
        # Przekaż bezpośrednio do Pythona
        return execute_python(args)

    # Znajdź plik Python
    python_file = find_python_file_in_args(args)
    if not python_file:
        # Nie ma pliku do walidacji
        return execute_python(args)

    # Wyświetl banner
    print_banner()

    # Waliduj plik
    result = validate_python_file(python_file)

    # Wyświetl wyniki
    if not print_validation_result(python_file, result):
        return 1

    # Uruchom Python
    print(f"🚀 Uruchamiam: python {' '.join(args)}")
    print("-" * 50)

    return execute_python(args)


def cli():
    """Entry point dla konsoli"""
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Przerwano przez użytkownika")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Nieoczekiwany błąd: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli()
