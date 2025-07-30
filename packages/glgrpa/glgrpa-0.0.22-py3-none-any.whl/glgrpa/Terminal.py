# src/Terminal/Terminal.py

from datetime import datetime
from colorama import Fore, init, Style
import time

class Terminal:
    def __init__(self, dev:bool=False):
        self.dev = dev
        init()
        self.Inicio_ejecucion()

    def Obtener_hora_actual(self, format:str) -> str: 
        fecha = datetime.now()
        return fecha.strftime(format)

    def Mostrar(self, mensaje:str, isError: bool=False) -> None:
        color_fecha = Fore.GREEN if not isError else Fore.RED
        print(color_fecha + f"[{self.Obtener_hora_actual(r"%Y-%m-%d %H:%M:%S")}]" + Style.RESET_ALL + f"\t{mensaje}")
        
    def Mostrar_misma_linea(self, mensaje:str, isError: bool=False) -> None:
        color_fecha = Fore.GREEN if not isError else Fore.RED
        print('\r' + color_fecha + f"[{self.Obtener_hora_actual(r"%Y-%m-%d %H:%M:%S")}]" + Style.RESET_ALL + f"\t{mensaje}", end='', flush=True)
        
    def Inicio_ejecucion(self) -> None:
        self.Mostrar("Iniciando ejecución")
        
    def Fin_ejecucion(self) -> None:
        self.Mostrar("Ejecución finalizada")
        
    def Tiempo_espera(self, tiempoEspera:int=5) -> None:
        if self.dev: tiempoEspera = 1
        time.sleep(tiempoEspera)