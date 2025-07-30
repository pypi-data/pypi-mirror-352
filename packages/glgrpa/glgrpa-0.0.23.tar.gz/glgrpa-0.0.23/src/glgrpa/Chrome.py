# src/Chrome/Chrome.py

# Librerías para el manejo de la consola
from .Terminal import Terminal

# Librerías para el manejo de ventanas
from .Windows import Windows

# Librerías para el manejo de elementos web
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException

# Librerías para el manejo de datos
import pandas as pd


class Chrome(Windows, Terminal):
    def __init__(self, dev:bool=False, mostrar_mensajes_por_consola:bool=False, modo_oculto:bool=False, modo_minimizado:bool=False):
        super().__init__(dev=dev)
        self.dev = dev
        
        self.tiempo_espera = 1 if self.dev else 5
        self.reintentos = 3
        
        self.chrome_options = self.__configuracion_driver(
            mostrar_mensajes_por_consola=mostrar_mensajes_por_consola,
            modo_oculto=modo_oculto,
            modo_minimizado=modo_minimizado
        )
        
        self.Mostrar("Iniciando navegador Chrome")        
        
    def __configuracion_driver(self, mostrar_mensajes_por_consola:bool=False, modo_oculto:bool=False, modo_minimizado:bool=False) -> Options:
        """ Configuración del driver """
        chrome_options = Options()
        
        if not mostrar_mensajes_por_consola:
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')
            chrome_options.add_argument('--log-level=3')
        if modo_oculto:
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')  # Necesario para Windows
        if modo_minimizado:
            chrome_options.add_argument('--start-minimized')
        else:
            chrome_options.add_argument('--start-maximized')
            
        prefs = {
            "download.default_directory": self.carpeta_descargas_personalizada, # Carpeta de descargas
            "download.prompt_for_download": False, # No preguntar por la descarga
            "download.directory_upgrade": True, # Actualizar automaticamente la carpeta de descargas
            "safebrowsing.enabled": True # Habilitar navegacion segura
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        return chrome_options
        
    def obtener_driver(self) -> WebDriver:
        """ Obtiene el driver de Chrome """
        return self.driver if self.driver else self.__iniciar_driver()
    
    def __iniciar_driver(self) -> WebDriver:
        """ Inicia el driver de Chrome """
        self.driver = webdriver.Chrome(service=Service(), options=self.chrome_options)
        self.driver.implicitly_wait(self.tiempo_espera)
        self.driver.set_page_load_timeout(self.tiempo_espera)
        self.driver.set_script_timeout(self.tiempo_espera)
        
        return self.driver
    
    def abrir_navegador(self) -> None:
        """ Abre el navegador """
        self.driver = self.__iniciar_driver()
        self.Mostrar("Navegador abierto")
        
    def cerrar_navegador(self) -> None:
        """ Cierra el navegador """
        self.driver.quit()
        self.Fin_ejecucion()
        exit()
        
    def navegar(self, url:str) -> None:
        """ Navega a la URL """
        self.driver.get(url)
        self.Mostrar(f"Navegando a {url}")
        self.Tiempo_espera()
        
    def ScrollToUp(self):
        """ Hace scroll hasta el principio de la página """
        self.driver.execute_script("window.scrollTo(0, 0);")   
        self.Tiempo_espera() 
        
    def esperar_elemento_clickeable(self, metodo_busqueda:By, texto_busqueda:str, tiene_que_estar:bool=True, elemento_padre:WebElement=None) -> WebElement | None:
        """ Espera a que el elemento sea clickeable, opcionalmente dentro de un elemento padre """
        try:
            if elemento_padre:
                elemento = WebDriverWait(elemento_padre, self.tiempo_espera).until(
                    EC.element_to_be_clickable((metodo_busqueda, texto_busqueda))
                )
                elemento = self.encontrar_elemento_desde_elemento(elemento_padre, metodo_busqueda, texto_busqueda, tiene_que_estar)
            else:
                elemento = WebDriverWait(self.driver, self.tiempo_espera).until(
                    EC.element_to_be_clickable((metodo_busqueda, texto_busqueda))
                )
                elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda, tiene_que_estar)
        except Exception as e:
            return None
        
        return elemento
    
    def click_elemento(self, metodo_busqueda:By, texto_busqueda:str) -> bool:
        """ Clickea el elemento """
        elemento = self.esperar_elemento_clickeable(metodo_busqueda, texto_busqueda)
        if not elemento: return False
        
        try:
            self.__desplazar_elemento_a_vista(elemento)
            elemento.click()
            return True
        except ElementClickInterceptedException:
            self.Mostrar(f"El elemento {texto_busqueda} está siendo interceptado.")
        
    def click_elemento_desde_elemento(self, elemento_padre:WebElement, metodo_busqueda:By, texto_busqueda:str) -> bool:
        """ Clickea el elemento hijo """
        elemento = self.encontrar_elemento_desde_elemento(elemento_padre, metodo_busqueda, texto_busqueda, False)
        elemento = self.esperar_elemento_clickeable(metodo_busqueda, texto_busqueda, elemento_padre=elemento_padre)
        if not elemento: return False
        
        try:
            self.__desplazar_elemento_a_vista(elemento)
            elemento.click()
            return True
        except ElementClickInterceptedException:
            self.Mostrar(f"El elemento {texto_busqueda} está siendo interceptado.")
        
    def click_button(self, texto_descripcion:str, metodo_busqueda:By, texto_busqueda:str) -> None:
        """ Clickea el botón primero por su texto_descripcion y sino encuentra por el texto_busqueda """
        if not self.click_elemento(By.XPATH, f"//button[text()='{texto_descripcion}']"):
            if not self.click_elemento(metodo_busqueda, texto_busqueda):
                self.Mostrar(f"No se encontró el botón {texto_descripcion} o {texto_busqueda}", True)
                self.cerrar_navegador()
            
    def __desplazar_elemento_a_vista(self, elemento: WebElement) -> None:
        """ Se desplaza la vista hasta el elemento """
        self.driver.execute_script("""arguments[0].scrollIntoView({block: 'center', inline: 'center'});""", elemento)
        self.Tiempo_espera()
        
    def encontrar_elemento(self, metodo_busqueda:By, texto_busqueda:str, tiene_que_estar:bool=True) -> WebElement | None:
        """ Encuentra el elemento y espera a que esté presente """
        try:
            elemento = WebDriverWait(self.driver, self.tiempo_espera).until(
                EC.visibility_of_element_located((metodo_busqueda, texto_busqueda))
            )
            elemento = WebDriverWait(self.driver, self.tiempo_espera).until(
                EC.presence_of_element_located((metodo_busqueda, texto_busqueda))
            )
            self.__desplazar_elemento_a_vista(elemento)
        except TimeoutException as e:
            if tiene_que_estar: self.Mostrar(f"No se encontró el elemento {texto_busqueda} en el tiempo previsto", True)
            elemento = None
        except Exception as e:
            # if tiene_que_estar: self.Mostrar(f"No se encontró el elemento {texto_busqueda} por el metodo {metodo_busqueda}", True)
            elemento = None
        finally:
            return elemento
    
    def encontrar_elemento_desde_elemento(self, elemento_padre:WebElement, metodo_busqueda:By, texto_busqueda:str, tiene_que_estar:bool=True) -> WebElement | None:
        """ Encuentra el elemento hijo"""
        try:
            elemento = elemento_padre.find_element(metodo_busqueda, texto_busqueda)
        except NoSuchElementException as e:
            if tiene_que_estar: self.Mostrar(f"No se encontró el elemento {texto_busqueda} con el metodo {metodo_busqueda}", True)
            return None
        except Exception as e:
            if tiene_que_estar: self.Mostrar(f"Ocurrió un error al buscar {texto_busqueda}", True)
            return None
        return elemento
    
    def encontrar_elemento_y_elementos(self, metodo_busqueda:By, texto_busqueda:str, tiene_que_estar:bool=True) -> list[WebElement] | None:
        """ Encuentra al elemento padre desde el metodo y el texto introducido y retorna los elementos hijos cuando estén presentes """
        elemento_padre = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        try:
            if elemento_padre:
                elementos = WebDriverWait(self.driver, self.tiempo_espera).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//*"))
                )
                elementos = elemento_padre.find_elements(By.XPATH, ".//*")
            else:
                elementos = []
            
        except Exception as e:
            if tiene_que_estar: self.Mostrar(f"No se encontraron los elementos en {texto_busqueda}", True)
            return None
        return elementos 
    
    def encontrar_elementos_desde_elemento(self, elemento_padre:WebElement, metodo_busqueda:By, texto_busqueda:str, tiene_que_estar:bool=True) -> list[WebElement] | None:
        """ Encuentra los elementos hijos """
        try:
            elementos = WebDriverWait(self.driver, self.tiempo_espera).until(
                EC.presence_of_all_elements_located((metodo_busqueda, texto_busqueda))
            )
            elementos = elemento_padre.find_elements(metodo_busqueda, texto_busqueda)
        except NoSuchElementException as e:
            if tiene_que_estar: self.Mostrar(f"No se encontraron los elementos {texto_busqueda}", True)
            return None
        return elementos   
    
    def encontrar_elementos(self, metodo_busqueda:By, texto_busqueda:str, tiene_que_estar:bool=True) -> list[WebElement] | None:
        """ Encuentra los elementos y espera a que estén presentes """
        try:
            elementos = WebDriverWait(self.driver, self.tiempo_espera).until(
                EC.presence_of_all_elements_located((metodo_busqueda, texto_busqueda))
            )
        except Exception as e:
            if tiene_que_estar: self.Mostrar(f"No se encontraron los elementos {texto_busqueda}", True)
            return None
        return elementos    
        
    def ingresar_texto(self, metodo_busqueda:By, texto_busqueda:str, texto_a_ingresar:str) -> None:
        """ Ingresa texto en el elemento """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if elemento:
            elemento.clear()
            elemento.send_keys(texto_a_ingresar)
            self.Tiempo_espera()
            
    def ingresar_comando(self, comando:str) -> None:
        """ Ingresa un comando en la consola """
        self.driver.execute_script(comando)
        
    def presionar_enter(self, metodo_busqueda: By, texto_busqueda: str) -> None:
        """ Presiona la tecla Enter en el elemento """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if elemento:
            elemento.send_keys(Keys.ENTER)
            
    def presionar_tecla(self, metodo_busqueda: By, texto_busqueda: str, tecla: Keys) -> None:
        """ Presiona una tecla en el elemento """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if elemento:
            elemento.send_keys(tecla)     
   
    def seleccionar_opcion_en_desplegable(self, metodo_busqueda: By, texto_busqueda: str, nombre_opcion: str, valor_opcion: str=None, reintentos: int=0) -> bool:
        """ Selecciona una opción en un desplegable """
        if reintentos >= self.reintentos:
            self.Mostrar(f"No se encontró la opción {nombre_opcion} después de varios intentos", True)
            return False
        
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if not elemento: 
            self.Tiempo_espera()
            self.seleccionar_opcion_en_desplegable(metodo_busqueda, texto_busqueda, nombre_opcion, valor_opcion, reintentos + 1)
            
        desplegable = Select(elemento)
        
        if valor_opcion: 
            try:
                desplegable.select_by_value(valor_opcion)
                if self.__verificar_opcion_seleccionada(metodo_busqueda, texto_busqueda, nombre_opcion): 
                    return True
            except NoSuchElementException as e:
                # self.Mostrar(f"No se encontró la opción por su valor {valor_opcion}", True)
                self.Tiempo_espera()
                
            self.seleccionar_opcion_en_desplegable(metodo_busqueda, texto_busqueda, nombre_opcion, valor_opcion, reintentos + 1)
        
        try:
            desplegable.select_by_visible_text(nombre_opcion)
            if self.__verificar_opcion_seleccionada(metodo_busqueda, texto_busqueda, nombre_opcion): 
                return True
        except NoSuchElementException as e:
            # self.Mostrar(f"No se encontró la opción {nombre_opcion}", True)
            pass
            
        self.Tiempo_espera()
        self.seleccionar_opcion_en_desplegable(metodo_busqueda, texto_busqueda, nombre_opcion, valor_opcion, reintentos + 1)
        
    def __verificar_opcion_seleccionada(self, metodo_busqueda: By, texto_busqueda: str, nombre_opcion: str) -> bool:
        """ Verifica que la opción seleccionada sea la correcta """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        desplegable = Select(elemento)
        return desplegable.first_selected_option.text == nombre_opcion
            
    def valor_en_elemento(self, metodo_busqueda: By, texto_busqueda: str) -> str:
        """ Obtiene el valor de un elemento """
        elemento = self.encontrar_elemento(metodo_busqueda, texto_busqueda)
        if elemento:
            return elemento.get_attribute("value")
        return ""
   
    def cambiar_ventana(self):
        """ Cambia a la última ventana del navegador """
        ventanas = self.esperar_nueva_pestaña(self.driver.window_handles)
        self.driver.switch_to.window(ventanas[-1])
        self.Mostrar(f"Cambiando a la ventana {self.driver.title}")
        self.Tiempo_espera()
        
    def esperar_nueva_pestaña(self, ventanas: list[str]) -> list[str]:
        """ Espera a que se abra una nueva pestaña """
        WebDriverWait(self.driver, self.tiempo_espera).until(
            EC.new_window_is_opened(ventanas)
        )
        return self.driver.window_handles
    
    def cambiar_directorio_descargas(self):
        """ Cambia el directorio de descargas """
        pass

    def obtener_tabla_en_data_frame(self, metedo_busqueda: By, texto_busqueda: str) -> pd.DataFrame:
        """ Obtiene una tabla en un DataFrame """
        tabla = self.encontrar_elemento(metedo_busqueda, texto_busqueda)
        if not tabla: return None
        return pd.read_html(tabla.get_attribute('outerHTML'))[0]
    
    def obtener_filas_tabla(self, metedo_busqueda: By, texto_busqueda: str) -> list[WebElement]:
        """ Obtiene las filas de una tabla """
        tabla = self.encontrar_elemento(metedo_busqueda, texto_busqueda)
        if not tabla: return []
        self.Tiempo_espera()
        self.__desplazar_elemento_a_vista(tabla)
        return self.encontrar_elementos_desde_elemento(tabla, By.TAG_NAME, "tr")
    
    def obtener_columnas_fila(self, fila: WebElement) -> list[str]:
        """ Obtiene las columnas de una fila """
        return self.encontrar_elementos_desde_elemento(fila, By.TAG_NAME, "th")
    
    def click_boton_en_celda(self, fila: WebElement) -> None:
        """ Clickea un botón en una celda """
        celdas = self.encontrar_elementos_desde_elemento(fila, By.TAG_NAME, "td")
        if len(celdas) == 0: return
        
        for celda in celdas:
            if not self.click_elemento_desde_elemento(celda, By.CLASS_NAME, "fa-print"):
                self.Mostrar("No se encontró el botón de descarga", True)
                self.Tiempo_espera()
                
            return