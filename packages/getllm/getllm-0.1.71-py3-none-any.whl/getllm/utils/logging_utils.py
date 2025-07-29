#!/usr/bin/env python3

"""
Rozbudowany moduł logowania dla getLLM.

Zawiera funkcje do konfiguracji i zarządzania logowaniem w aplikacji.
"""

import os
import sys
import logging
import datetime
import traceback
from pathlib import Path
from typing import Optional, Dict, Any, List, Union

# Stałe konfiguracyjne
DEFAULT_LOG_LEVEL = logging.INFO
DEBUG_LOG_LEVEL = logging.DEBUG
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DETAILED_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'

# Globalne zmienne dla modułu
_initialized = False
_log_file = None
_debug_mode = False
_log_dir = None

def get_log_dir() -> Path:
    """
    Pobiera ścieżkę do katalogu z logami.
    
    Returns:
        Path: Ścieżka do katalogu z logami.
    """
    global _log_dir
    if _log_dir is None:
        from ..utils.config import get_getllm_dir
        _log_dir = get_getllm_dir() / 'logs'
        _log_dir.mkdir(parents=True, exist_ok=True)
    return _log_dir

def get_log_file(custom_log_file: Optional[str] = None) -> str:
    """
    Pobiera ścieżkę do pliku logów.
    
    Args:
        custom_log_file: Opcjonalna niestandardowa ścieżka do pliku logów.
        
    Returns:
        str: Ścieżka do pliku logów.
    """
    global _log_file
    if custom_log_file:
        return custom_log_file
    
    if _log_file is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        _log_file = str(get_log_dir() / f'getllm_{timestamp}.log')
    
    return _log_file

def configure_logging(debug: bool = False, log_file: Optional[str] = None, 
                     log_to_console: bool = True, log_to_file: bool = True,
                     log_level: Optional[int] = None) -> None:
    """
    Konfiguruje system logowania dla getLLM.
    
    Args:
        debug: Czy włączyć tryb debugowania.
        log_file: Opcjonalna niestandardowa ścieżka do pliku logów.
        log_to_console: Czy logować do konsoli.
        log_to_file: Czy logować do pliku.
        log_level: Opcjonalny poziom logowania.
    """
    global _initialized, _debug_mode
    
    # Ustaw globalną flagę trybu debugowania
    _debug_mode = debug
    
    # Określ poziom logowania
    if log_level is None:
        log_level = DEBUG_LOG_LEVEL if debug else DEFAULT_LOG_LEVEL
    
    # Skonfiguruj główny logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Usuń istniejące handlery
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Format logów
    log_format = DETAILED_LOG_FORMAT if debug else LOG_FORMAT
    formatter = logging.Formatter(log_format)
    
    # Logowanie do konsoli
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Logowanie do pliku
    if log_to_file:
        log_file_path = get_log_file(log_file)
        try:
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            sys.stderr.write(f"Błąd podczas konfiguracji logowania do pliku: {e}\n")
    
    # Ustaw flagę inicjalizacji
    _initialized = True
    
    # Zaloguj informację o rozpoczęciu logowania
    logger = logging.getLogger('getllm.utils.logging')
    logger.debug(f"Logowanie skonfigurowane. Tryb debug: {debug}, Plik logów: {log_file_path if log_to_file else 'brak'}")

def is_debug_mode() -> bool:
    """
    Sprawdza, czy aplikacja działa w trybie debugowania.
    
    Returns:
        bool: True, jeśli tryb debugowania jest włączony.
    """
    return _debug_mode

def get_current_log_file() -> Optional[str]:
    """
    Zwraca aktualną ścieżkę do pliku logów.
    
    Returns:
        Optional[str]: Ścieżka do pliku logów lub None, jeśli logowanie do pliku jest wyłączone.
    """
    return _log_file if _initialized else None

def log_exception(logger: logging.Logger, exception: Exception, message: str = "Wystąpił wyjątek:") -> None:
    """
    Loguje wyjątek z pełnym stacktrace.
    
    Args:
        logger: Logger do użycia.
        exception: Wyjątek do zalogowania.
        message: Opcjonalna wiadomość poprzedzająca stacktrace.
    """
    logger.error(f"{message} {str(exception)}")
    if is_debug_mode():
        logger.debug(traceback.format_exc())

def log_function_call(logger: logging.Logger, function_name: str, args: List[Any] = None, kwargs: Dict[str, Any] = None) -> None:
    """
    Loguje wywołanie funkcji z argumentami.
    
    Args:
        logger: Logger do użycia.
        function_name: Nazwa wywoływanej funkcji.
        args: Lista argumentów pozycyjnych.
        kwargs: Słownik argumentów nazwanych.
    """
    if not is_debug_mode():
        return
    
    args_str = ", ".join([str(arg) for arg in args]) if args else ""
    kwargs_str = ", ".join([f"{k}={v}" for k, v in kwargs.items()]) if kwargs else ""
    params = ", ".join(filter(None, [args_str, kwargs_str]))
    
    logger.debug(f"Wywołanie funkcji: {function_name}({params})")

def log_api_request(logger: logging.Logger, url: str, method: str = "GET", params: Dict[str, Any] = None, 
                   headers: Dict[str, Any] = None, response_code: int = None, 
                   response_size: int = None, error: str = None) -> None:
    """
    Loguje żądanie API.
    
    Args:
        logger: Logger do użycia.
        url: URL żądania.
        method: Metoda HTTP.
        params: Parametry żądania.
        headers: Nagłówki żądania.
        response_code: Kod odpowiedzi HTTP.
        response_size: Rozmiar odpowiedzi w bajtach.
        error: Opcjonalny komunikat błędu.
    """
    # Podstawowe informacje o żądaniu
    log_msg = f"API {method} {url}"
    
    # Dodaj parametry w trybie debug
    if is_debug_mode() and params:
        # Ukryj wrażliwe dane jak klucze API
        safe_params = {}
        for k, v in params.items():
            if 'key' in k.lower() or 'token' in k.lower() or 'secret' in k.lower() or 'password' in k.lower():
                safe_params[k] = '***HIDDEN***'
            else:
                safe_params[k] = v
        log_msg += f", params: {safe_params}"
    
    # Dodaj informacje o odpowiedzi
    if response_code is not None:
        log_msg += f", status: {response_code}"
    
    if response_size is not None:
        log_msg += f", size: {response_size} bytes"
    
    # Loguj na odpowiednim poziomie
    if error:
        logger.error(f"{log_msg}, error: {error}")
    elif response_code and response_code >= 400:
        logger.warning(log_msg)
    else:
        logger.debug(log_msg)

def log_performance(logger: logging.Logger, operation: str, duration_ms: float) -> None:
    """
    Loguje wydajność operacji.
    
    Args:
        logger: Logger do użycia.
        operation: Nazwa operacji.
        duration_ms: Czas trwania w milisekundach.
    """
    if duration_ms > 1000:  # Ponad 1 sekunda
        logger.warning(f"Wydajność: {operation} zajęło {duration_ms:.2f} ms")
    else:
        logger.debug(f"Wydajność: {operation} zajęło {duration_ms:.2f} ms")

def log_memory_usage(logger: logging.Logger, context: str = "Aktualne zużycie pamięci") -> None:
    """
    Loguje zużycie pamięci.
    
    Args:
        logger: Logger do użycia.
        context: Kontekst pomiaru zużycia pamięci.
    """
    if not is_debug_mode():
        return
    
    try:
        import psutil
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        logger.debug(f"{context}: {memory_info.rss / (1024 * 1024):.2f} MB")
    except ImportError:
        logger.debug(f"Nie można zalogować zużycia pamięci - moduł psutil nie jest dostępny")
    except Exception as e:
        logger.debug(f"Błąd podczas logowania zużycia pamięci: {e}")

def log_model_operation(logger: logging.Logger, operation: str, model_name: str, 
                       source: str = None, success: bool = True, error: str = None) -> None:
    """
    Loguje operację na modelu.
    
    Args:
        logger: Logger do użycia.
        operation: Rodzaj operacji (np. 'update', 'install', 'search').
        model_name: Nazwa modelu.
        source: Źródło modelu (np. 'huggingface', 'ollama').
        success: Czy operacja zakończyła się sukcesem.
        error: Opcjonalny komunikat błędu.
    """
    log_msg = f"Model {operation}: {model_name}"
    if source:
        log_msg += f" (źródło: {source})"
    
    if success:
        logger.info(log_msg)
    else:
        logger.error(f"{log_msg} - BŁĄD: {error if error else 'Nieznany błąd'}")

# Inicjalizacja domyślnego loggera
def initialize_default_logging():
    """
    Inicjalizuje domyślne logowanie, jeśli nie zostało jeszcze skonfigurowane.
    """
    if not _initialized:
        configure_logging(debug=False)
