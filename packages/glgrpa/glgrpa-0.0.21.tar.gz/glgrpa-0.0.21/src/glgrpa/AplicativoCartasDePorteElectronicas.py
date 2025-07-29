# src/ARCA/Cartas de porte electronicas/AplicativoCartasDePorteElectronicas.py

# Librería para el manejo de la interfaz de ARCA
from .ARCA import ARCA

# Librerías para el manejo de archivos
import os

# Librerías para el manejo de elementos de la página
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

class AplicativoCartaDePorteElectronica(ARCA):
    def __init__(self, usuario: str, clave: str, dev: bool = False):
        super().__init__(dev=dev, usuario=usuario, clave=clave)    
        self.dev = dev
        self.reintentos_seleccionar_persona = 3
        self.reintentos_ingresar_fecha = 3
        
    def cambiar_relacion(self, nombreObjetivo: str, reintento:int = 0):
        """ Cambia la relación de la página """
        # Si se intenta varias veces y no se puede cambiar la relación, se cierra el navegador
        if reintento >= self.reintentos_seleccionar_persona:
            self.Mostrar("No se pudo cambiar la relación después de varios intentos", True)
            self.cerrar_navegador()
            
        self.Mostrar("Cambiando relación")
        self.navegar('https://cpea-app.afip.gob.ar/cpe-web/secure/index.html#/relation-selector')
        
        # Si no se puede seleccionar la persona, se reintenta
        if not self.__seleccionar_persona(nombreObjetivo): # Click en la persona buscada
            self.cambiar_relacion(nombreObjetivo, reintento + 1)
        
        # Si no se puede verificar la persona seleccionada, se reintenta
        if not self.__verificar_seleccion_persona(nombreObjetivo): # Click en el modal de aceptación
            self.cambiar_relacion(nombreObjetivo, reintento + 1)
            
        self.Mostrar("Relación cambiada")
        
    def __seleccionar_persona(self, nombreObjetivo: str) -> bool:
        """ Selecciona la persona en la lista desplegable """
        self.Mostrar("Seleccionando persona")
        personas = self.encontrar_elemento_y_elementos(By.XPATH, r'//*[@id="relationSelector"]/div[2]/div')
        
        if not personas: 
            self.Mostrar("No se encontraron personas", True)
            self.cerrar_navegador()
        
        for persona in personas:
            if nombreObjetivo.lower() == persona.text.lower():
                persona.click()
                self.Mostrar(f"Persona {nombreObjetivo} seleccionada")
                return True
        # self.Mostrar(f"Persona {nombreObjetivo} no encontrada", True)
        return False
    
    def __verificar_seleccion_persona(self, nombreObjetivo: str) -> bool:
        """ Verifica que la persona seleccionada sea la correcta """
        aviso_seleccion = self.encontrar_elemento(By.XPATH, r'//*[@id="modal-relacion___BV_modal_body_"]', False)
        if not aviso_seleccion: return True
        if aviso_seleccion.text.lower() == f'¿séguro que desea ingresar como {nombreObjetivo.lower()}?':
            self.click_button('Elegir relación', By.XPATH, r'//*[@id="modal-relacion___BV_modal_footer_"]/button[2]')
            return True
        self.Mostrar(f"Persona {nombreObjetivo} no es la buscada", True)
        self.click_button('Cancelar', By.XPATH, r'//*[@id="modal-relacion___BV_modal_footer_"]/button[1]')
        return False
    
    def ingresar_accion(self, nombreAccion: str):
        """ Busca todas las acciones disponibles y selecciona la deseada """
        self.Mostrar("Ingresando acción")
        acciones = self.encontrar_elementos(By.CLASS_NAME, 'a-card')
        
        for accion in acciones:
            accionH4 = self.encontrar_elemento_desde_elemento(accion, By.TAG_NAME, 'h4', False)
            if not accionH4: continue
                
            if accionH4.text.lower() == nombreAccion.lower():
                accion.click()
                self.Mostrar(f"Accion {nombreAccion} seleccionada")
                self.ScrollToUp()
                return
        
        self.Mostrar(f"Accion {nombreAccion} no encontrada", True)
        self.cerrar_navegador()
        
    def seleccionar_tipo(self, nombre_tipo: str, valor_tipo: str = None):
        """ Selecciona el tipo de carta de porte """
        self.Mostrar("Seleccionando tipo")
        if not self.seleccionar_opcion_en_desplegable(By.ID, 'tipoCpe', nombre_tipo, valor_tipo): 
            self.Mostrar(f"Tipo {nombre_tipo} no encontrado", True)
            self.cerrar_navegador()
            
        self.Mostrar(f"Tipo {nombre_tipo} seleccionado")
        
    def seleccionar_planta(self, nombre_planta: str, valor_planta: str = None) -> bool:
        """ Selecciona la planta """
        self.Mostrar("Seleccionando planta")
        if not self.seleccionar_opcion_en_desplegable(By.ID, 'plantaOrigen', nombre_planta, valor_planta):
            self.Mostrar(f"Planta {nombre_planta} no encontrada", True)
            return False
        self.Mostrar(f"Planta {nombre_planta} seleccionada")  
        return True  
    
    def ingresar_fecha_desde(self, fecha: str, reintento:int = 0):
        """ Ingresa la fecha desde """
        if reintento >= self.reintentos_ingresar_fecha:
            self.Mostrar("No se pudo ingresar la fecha desde después de varios intentos", True)
            self.cerrar_navegador()
            
        self.Mostrar("Ingresando fecha desde")
        self.ingresar_texto(By.ID, 'fechaDesde', fecha)
        
        if not self.__verificar_fecha_ingresada(fecha, By.ID, 'fechaDesde'):
            self.ingresar_fecha_desde(fecha, reintento + 1)    
       
        self.Mostrar(f"Fecha desde {fecha} ingresada")
        
    def ingresar_fecha_hasta(self, fecha: str, reintento:int = 0):
        """ Ingresa la fecha hasta """
        if reintento >= self.reintentos_ingresar_fecha:
            self.Mostrar("No se pudo ingresar la fecha hasta después de varios intentos", True)
            self.cerrar_navegador()
            
        self.Mostrar("Ingresando fecha hasta")
        self.ingresar_texto(By.ID, 'fechaHasta', fecha)
        
        if not self.__verificar_fecha_ingresada(fecha, By.ID, 'fechaHasta'):
            self.ingresar_fecha_hasta(fecha, reintento + 1)
        
        self.Mostrar(f"Fecha hasta {fecha} ingresada")
        
    def __verificar_fecha_ingresada(self, fecha: str, metodo_busqueda:str, texto_busqueda:str) -> bool:
        """ Verifica que la fecha ingresada sea la correcta """
        fecha_ingresada = self.valor_en_elemento(metodo_busqueda, texto_busqueda)
        if fecha_ingresada == fecha: return True
        return False
    
    def ingresar_cuit_destinatario(self, cuit: str) -> None:
        """ Ingresa el CUIT del destinatario """
        self.Mostrar("Ingresando CUIT destinatario")
        self.ingresar_texto(By.ID, 'cuitDestinatario', cuit)
        self.Mostrar(f"CUIT destinatario {cuit} ingresado")
    
    def buscar_cpe(self) -> None:
        """ Busca las cartas de porte electrónicas """
        self.Mostrar("Buscando CPE")
        self.click_button('Buscar', By.ID, 'btnBuscar')
        self.Mostrar("CPE buscadas")
        
    def obtener_listado_cpe(self) -> list[WebElement]:
        """ Obtiene el listado de cartas de porte electrónicas, las filas de la tabla """
        self.Mostrar("Obteniendo listado de CPE")
        self.__mostrar_elementos_por_pagina(30)
        cpe = self.obtener_filas_tabla(By.ID, '__BVID__100')
        
        # Si no se encuentran filas en la tabla, se cierra el navegador
        if not cpe or len(cpe) <= 1: 
            self.Mostrar("No se encontraron las filas de la tabla", True)
            self.cerrar_navegador()

        # Se elimina la primera fila que contiene los títulos de las columnas
        cpe = cpe[1:] 
        
        # Si no hay cartas de portes, la leyenda es 'No existe cartas de porte'
        if cpe[0].text.split()[0] == 'No': 
            self.Mostrar("Esta planta no tiene CPE")
            return []
        
        self.Mostrar(f"{len(cpe)} CPE encontradas")
        return cpe
    
    def __mostrar_elementos_por_pagina(self, cantidad: int) -> None:
        """ Muestra la cantidad de elementos por página """
        self.Mostrar("Mostrando elementos por página")
        self.seleccionar_opcion_en_desplegable(By.CLASS_NAME, 'custom-select-sm', str(cantidad), str(cantidad), 0)
        self.Mostrar(f"Mostrando {cantidad} elementos por página")
    
    def descargar_carta_de_porte(self, filaTablaCpe: WebElement) -> str:
        """ Descarga la carta de porte """
        
        # Se obtiene el número de la carta de porte
        numeroCpe = filaTablaCpe.text.split()[0]
        
        # Si no hay cartas de portes, la leyenda es 'No existe cartas de porte'
        if numeroCpe == 'No': return None
        
        if self.click_elemento_desde_elemento(filaTablaCpe, By.CLASS_NAME, 'fa-print'):
            self.Mostrar(f"CPE {numeroCpe} descargada")
            return os.path.join(self.carpeta_descargas_personalizada, f'cpe-{numeroCpe}.pdf')
        
        self.Mostrar(f"No se pudo descargar la CPE {numeroCpe}", True)
        return None