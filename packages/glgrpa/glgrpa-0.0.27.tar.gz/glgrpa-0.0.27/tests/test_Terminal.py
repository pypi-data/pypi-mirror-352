# src/tests/test_Terminal.py
# Pruebas unitarias para la clase Terminal

# Librerías para pruebas unitarias
import pytest
from unittest.mock import patch, Mock

# Librerías propias
from src.glgrpa.Terminal import Terminal

# Librerías para controlar el tiempo
from datetime import datetime
import time

@pytest.fixture
def terminal_dev():
    """Fixture para inicializar la clase Terminal en modo dev"""
    return Terminal(dev=True)

@pytest.fixture
def terminal_prod():
    """Fixture para inicializar la clase Terminal en modo producción"""
    return Terminal(dev=False)

def test_obtener_hora_actual(terminal_dev: Terminal):
    """Prueba para verificar el formato de la hora actual"""
    formato = "%Y-%m-%d %H:%M:%S"
    hora_actual = terminal_dev.obtener_hora_actual(formato)
    assert datetime.strptime(hora_actual, formato), "El formato de la hora no es válido"

@patch("builtins.print")
def test_mostrar(mock_print: Mock, terminal_dev: Terminal):
    """Prueba para verificar que se imprime el mensaje correctamente"""
    mensaje = "Mensaje de prueba"
    terminal_dev.mostrar(mensaje)
    mock_print.assert_called_once()
    assert mensaje in mock_print.call_args[0][0]

@patch("builtins.print")
def test_mostrar_error(mock_print: Mock, terminal_dev: Terminal):
    """Prueba para verificar que se imprime un mensaje de error correctamente"""
    mensaje = "Mensaje de error"
    terminal_dev.mostrar(mensaje, isError=True)
    mock_print.assert_called_once()
    assert mensaje in mock_print.call_args[0][0]

@patch("builtins.print")
def test_inicio_ejecucion(mock_print: Mock, terminal_dev: Terminal):
    """Prueba para verificar que se imprime el mensaje de inicio de ejecución"""
    terminal_dev.inicio_ejecucion()
    mock_print.assert_called_once()
    assert "Iniciando ejecución" in mock_print.call_args[0][0]

@patch("builtins.print")
def test_fin_ejecucion(mock_print: Mock, terminal_dev: Terminal):
    """Prueba para verificar que se imprime el mensaje de fin de ejecución"""
    terminal_dev.fin_ejecucion()
    mock_print.assert_called_once()
    assert "Ejecución finalizada" in mock_print.call_args[0][0]

@patch("time.sleep", return_value=None)
def test_tiempo_espera_dev(mock_sleep: Mock, terminal_dev: Terminal):
    """Prueba para verificar que el tiempo de espera es 1 segundo en modo dev"""
    terminal_dev.demora()
    mock_sleep.assert_called_once_with(1)

@patch("time.sleep", return_value=None)
def test_tiempo_espera_prod(mock_sleep: Mock, terminal_prod: Terminal):
    """Prueba para verificar que el tiempo de espera es 5 segundos en modo producción"""
    terminal_prod.demora()
    mock_sleep.assert_called_once_with(5)