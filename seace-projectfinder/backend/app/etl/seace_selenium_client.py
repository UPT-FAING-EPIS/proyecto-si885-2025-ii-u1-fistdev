import asyncio
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, date
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from app.core.config import settings
from app.core.exceptions import ETLException

logger = logging.getLogger(__name__)


class SEACESeleniumClient:
    """Cliente SEACE usando Selenium para manejo completo de JavaScript"""
    
    def __init__(self):
        self.base_url = "https://prod2.seace.gob.pe"
        self.search_url = f"{self.base_url}/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml"
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None
        
        # Términos de búsqueda específicos para TI y sistemas
        self.ti_keywords = [
            # Términos principales
            "sistema",
            "software",
            "aplicativo",
            "plataforma digital",
            "tecnologia",
            "informatica",
            
            # Ingeniería y desarrollo
            "ingenieria de sistemas",
            "desarrollo de software",
            "desarrollo web",
            "aplicacion web",
            "sistema web",
            "portal web",
            
            # Infraestructura TI
            "infraestructura tecnologica",
            "servidor",
            "base de datos",
            "red informatica",
            "centro de datos",
            "datacenter",
            
            # Servicios TI específicos
            "soporte tecnico",
            "mantenimiento de sistemas",
            "hosting",
            "cloud",
            "nube",
            "virtualizacion",
            
            # Software específico
            "erp",
            "crm",
            "sap",
            "oracle",
            "microsoft",
            "windows",
            "linux",
            
            # Seguridad informática
            "ciberseguridad",
            "seguridad informatica",
            "firewall",
            "antivirus",
            "backup",
            
            # Conectividad y comunicaciones
            "internet",
            "wifi",
            "telecomunicaciones",
            "videoconferencia",
            "telefonia ip",
            
            # Automatización y procesos
            "automatizacion",
            "digitalizacion",
            "transformacion digital",
            "gobierno digital",
            "interoperabilidad"
        ]
        
    async def __aenter__(self):
        """Inicializar driver de Selenium"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Ejecutar en modo headless
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            # Usar webdriver-manager para instalar automáticamente ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            logger.warning(f"Error con webdriver-manager, usando driver del sistema: {e}")
            # Fallback al driver del sistema
            self.driver = webdriver.Chrome(options=chrome_options)
        
        self.wait = WebDriverWait(self.driver, 30)  # 30 segundos de timeout
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cerrar driver de Selenium"""
        if self.driver:
            self.driver.quit()
    
    async def navigate_to_procesos_tab(self) -> bool:
        """Navegar a la pestaña de Procedimientos de Selección"""
        try:
            logger.info("Navegando a portal SEACE")
            self.driver.get(self.search_url)
            
            # Esperar a que la página cargue completamente
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            
            # Buscar y hacer clic en la pestaña "Buscador de Procedimientos de Selección"
            logger.info("Buscando pestaña 'Procedimientos de Selección'")
            
            # Varios selectores posibles para la pestaña
            tab_selectors = [
                "//a[contains(text(), 'Procedimientos de Selección')]",
                "//li[contains(text(), 'Procedimientos de Selección')]",
                "//span[contains(text(), 'Procedimientos de Selección')]",
                "//div[contains(text(), 'Procedimientos de Selección')]",
                "//a[contains(@title, 'Procedimientos')]",
                "//li[contains(@class, 'ui-tabs-tab')][position()=2]"  # Segunda pestaña
            ]
            
            tab_element = None
            for selector in tab_selectors:
                try:
                    tab_element = self.driver.find_element(By.XPATH, selector)
                    if tab_element.is_displayed():
                        logger.info(f"Pestaña encontrada con selector: {selector}")
                        break
                except NoSuchElementException:
                    continue
            
            if tab_element:
                # Hacer clic en la pestaña
                self.driver.execute_script("arguments[0].click();", tab_element)
                logger.info("Clic realizado en pestaña de Procedimientos de Selección")
                
                # Esperar a que el contenido de la pestaña cargue
                time.sleep(3)
                return True
            else:
                logger.warning("No se pudo encontrar la pestaña de Procedimientos de Selección")
                return False
                
        except Exception as e:
            logger.error(f"Error navegando a pestaña de procesos: {e}")
            return False
    
    async def search_ti_opportunities(self, 
                                    max_keywords: int = 10,
                                    include_custom_keywords: List[str] = None) -> Dict[str, Any]:
        """Buscar específicamente oportunidades de TI usando múltiples términos"""
        try:
            all_results = []
            keywords_used = []
            search_summary = {}
            
            # Combinar keywords predefinidas con las personalizadas
            search_keywords = self.ti_keywords[:max_keywords]
            if include_custom_keywords:
                search_keywords.extend(include_custom_keywords)
            
            logger.info(f"Iniciando búsqueda TI con {len(search_keywords)} términos")
            
            for i, keyword in enumerate(search_keywords):
                try:
                    logger.info(f"Búsqueda {i+1}/{len(search_keywords)}: '{keyword}'")
                    
                    # Realizar búsqueda individual
                    result = await self.search_processes(
                        objeto_contratacion=keyword,
                        año_convocatoria=2024  # Usar 2024 por defecto ya que es más probable que tenga datos
                    )
                    
                    if result.get("processes"):
                        # Agregar metadatos de búsqueda a cada proceso
                        for process in result["processes"]:
                            process["keyword_found"] = keyword
                            process["search_order"] = i + 1
                        
                        all_results.extend(result["processes"])
                        keywords_used.append(keyword)
                        search_summary[keyword] = len(result["processes"])
                        
                        logger.info(f"✓ '{keyword}': {len(result['processes'])} procesos encontrados")
                    else:
                        search_summary[keyword] = 0
                        logger.info(f"✗ '{keyword}': sin resultados")
                    
                    # Pequeña pausa entre búsquedas para no sobrecargar el servidor
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.warning(f"Error buscando '{keyword}': {e}")
                    search_summary[keyword] = f"Error: {str(e)}"
                    continue
            
            # Eliminar duplicados basado en número de proceso
            unique_results = {}
            for process in all_results:
                proceso_key = process.get("numero_proceso", "")
                if proceso_key and proceso_key not in unique_results:
                    unique_results[proceso_key] = process
                elif proceso_key:
                    # Si ya existe, mantener el que tiene más información
                    existing = unique_results[proceso_key]
                    if len(str(process)) > len(str(existing)):
                        unique_results[proceso_key] = process
            
            final_results = list(unique_results.values())
            
            return {
                "total_searches": len(search_keywords),
                "successful_searches": len(keywords_used),
                "keywords_used": keywords_used,
                "search_summary": search_summary,
                "total_found": len(final_results),
                "unique_processes": len(final_results),
                "processes": final_results,
                "method": "selenium_multi_ti"
            }
            
        except Exception as e:
            logger.error(f"Error en búsqueda TI múltiple: {e}")
            raise ETLException(f"Error búsqueda TI: {e}")
    
    async def search_by_categories(self) -> Dict[str, Any]:
        """Buscar por categorías específicas de TI"""
        categories = {
            "desarrollo_software": ["desarrollo de software", "aplicativo", "sistema web", "portal web"],
            "infraestructura": ["servidor", "infraestructura tecnologica", "centro de datos", "red informatica"],
            "seguridad": ["ciberseguridad", "seguridad informatica", "firewall", "backup"],
            "servicios_ti": ["soporte tecnico", "mantenimiento de sistemas", "hosting", "cloud"],
            "software_empresarial": ["erp", "crm", "sap", "oracle"],
            "comunicaciones": ["telecomunicaciones", "videoconferencia", "telefonia ip", "internet"],
            "transformacion_digital": ["digitalizacion", "transformacion digital", "gobierno digital", "automatizacion"]
        }
        
        category_results = {}
        all_processes = []
        
        for category, keywords in categories.items():
            logger.info(f"Buscando categoría: {category}")
            category_processes = []
            
            for keyword in keywords:
                try:
                    result = await self.search_processes(
                        objeto_contratacion=keyword,
                        año_convocatoria=2024  # Usar 2024 por defecto
                    )
                    if result.get("processes"):
                        for process in result["processes"]:
                            process["category"] = category
                            process["category_keyword"] = keyword
                        category_processes.extend(result["processes"])
                    
                    await asyncio.sleep(1)  # Pausa entre búsquedas
                    
                except Exception as e:
                    logger.warning(f"Error en categoría {category} con keyword '{keyword}': {e}")
                    continue
            
            category_results[category] = {
                "count": len(category_processes),
                "processes": category_processes
            }
            all_processes.extend(category_processes)
            
            logger.info(f"Categoría {category}: {len(category_processes)} procesos")
        
        # Eliminar duplicados
        unique_processes = {}
        for process in all_processes:
            key = process.get("numero_proceso", "")
            if key and key not in unique_processes:
                unique_processes[key] = process
        
        return {
            "categories": category_results,
            "total_by_category": {cat: data["count"] for cat, data in category_results.items()},
            "total_unique": len(unique_processes),
            "unique_processes": list(unique_processes.values()),
            "method": "selenium_categories"
        }
    
    async def search_processes(self, 
                             objeto_contratacion: str = "",
                             entidad: str = "",
                             fecha_desde: Optional[date] = None,
                             fecha_hasta: Optional[date] = None,
                             tipo_proceso: str = "",
                             estado: str = "",
                             año_convocatoria: int = None,
                             page: int = 1) -> Dict[str, Any]:
        """Buscar procesos usando Selenium con JavaScript completo"""
        try:
            # Paso 1: Navegar a la pestaña correcta
            if not await self.navigate_to_procesos_tab():
                raise ETLException("No se pudo activar la pestaña de Procedimientos de Selección")
            
            logger.info("Iniciando búsqueda de procesos con Selenium")
            
            # Paso 2: CONFIGURAR FILTROS OBLIGATORIOS PRIMERO
            from datetime import datetime, date
            current_year = datetime.now().year
            
            # 2.1: Seleccionar "Servicio" en Objeto de Contratación (OBLIGATORIO)
            logger.info("Configurando filtro de Objeto de Contratación = Servicio")
            objeto_contratacion_selectors = [
                "tbBuscador:idFormBuscarProceso:j_idt234_input",  # ID real encontrado
                "tbBuscador:idFormBuscarProceso:objetoContratacion",
                "objetoContratacion",
                "//select[contains(@name, 'objetoContratacion')]",
                "//select[contains(@id, 'objetoContratacion')]"
            ]
            
            for selector in objeto_contratacion_selectors:
                try:
                    if selector.startswith("//"):
                        dropdown = self.driver.find_element(By.XPATH, selector)
                    else:
                        dropdown = self.driver.find_element(By.ID, selector)
                    
                    if dropdown.is_displayed() and dropdown.is_enabled():
                        # Seleccionar "Servicio" del dropdown
                        from selenium.webdriver.support.ui import Select
                        select = Select(dropdown)
                        
                        # Intentar diferentes valores para "Servicio"
                        servicio_options = ["Servicio", "SERVICIO", "servicio", "4"]
                        for option in servicio_options:
                            try:
                                select.select_by_visible_text(option)
                                logger.info(f"✓ Objeto de Contratación = Servicio seleccionado por texto: {option}")
                                break
                            except:
                                try:
                                    select.select_by_value(option)
                                    logger.info(f"✓ Objeto de Contratación = Servicio seleccionado con valor: {option}")
                                    break
                                except:
                                    continue
                        break
                except:
                    continue
            
            # 2.2: Configurar AÑO DE LA CONVOCATORIA (OBLIGATORIO)
            # Usar el año pasado como parámetro o el año actual por defecto
            target_year = año_convocatoria if año_convocatoria else current_year
            logger.info(f"Configurando Año de la Convocatoria = {target_year}")
            
            año_convocatoria_selectors = [
                "tbBuscador:idFormBuscarProceso:anioConvocatoria_input",  # ID real encontrado
                "tbBuscador:idFormBuscarProceso:anioConvocatoria",
                "anioConvocatoria", 
                "//select[contains(@name, 'anioConvocatoria')]",
                "//select[contains(@id, 'anio')]",
                "//select[contains(@name, 'año')]"
            ]
            
            for selector in año_convocatoria_selectors:
                try:
                    if selector.startswith("//"):
                        dropdown = self.driver.find_element(By.XPATH, selector)
                    else:
                        dropdown = self.driver.find_element(By.ID, selector)
                    
                    if dropdown.is_displayed() and dropdown.is_enabled():
                        select = Select(dropdown)
                        
                        # Intentar seleccionar el año objetivo, luego alternativas
                        year_options = [str(target_year), "2024", "2023", str(current_year)]
                        for year_opt in year_options:
                            try:
                                select.select_by_visible_text(year_opt)
                                logger.info(f"✓ Año de Convocatoria = {year_opt} seleccionado por texto")
                                break
                            except:
                                try:
                                    select.select_by_value(year_opt)
                                    logger.info(f"✓ Año de Convocatoria = {year_opt} seleccionado por valor")
                                    break
                                except:
                                    continue
                        break
                except:
                    continue
            
            # 2.3: Configurar fechas de publicación (opcionales pero recomendadas)
            # Si no se especifican fechas, usar el año actual
            if not fecha_desde:
                fecha_desde = date(current_year, 1, 1)  # 1 de enero del año actual
            if not fecha_hasta:
                fecha_hasta = date(current_year, 12, 31)  # 31 de diciembre del año actual
            
            logger.info(f"Configurando fechas de publicación: desde {fecha_desde} hasta {fecha_hasta}")
            
            # Configurar fecha DESDE
            fecha_desde_selectors = [
                "tbBuscador:idFormBuscarProceso:fechaPublicacionDesde_input",
                "fechaPublicacionDesde",
                "//input[contains(@name, 'fechaPublicacionDesde')]",
                "//input[contains(@id, 'fechaDesde')]"
            ]
            
            for selector in fecha_desde_selectors:
                try:
                    if selector.startswith("//"):
                        field = self.driver.find_element(By.XPATH, selector)
                    else:
                        field = self.driver.find_element(By.ID, selector)
                    
                    if field.is_displayed() and field.is_enabled():
                        field.clear()
                        field.send_keys(fecha_desde.strftime("%d/%m/%Y"))
                        logger.info(f"✓ Fecha desde configurada: {fecha_desde.strftime('%d/%m/%Y')}")
                        break
                except:
                    continue
            
            # Configurar fecha HASTA
            fecha_hasta_selectors = [
                "tbBuscador:idFormBuscarProceso:fechaPublicacionHasta_input",
                "fechaPublicacionHasta",
                "//input[contains(@name, 'fechaPublicacionHasta')]",
                "//input[contains(@id, 'fechaHasta')]"
            ]
            
            for selector in fecha_hasta_selectors:
                try:
                    if selector.startswith("//"):
                        field = self.driver.find_element(By.XPATH, selector)
                    else:
                        field = self.driver.find_element(By.ID, selector)
                    
                    if field.is_displayed() and field.is_enabled():
                        field.clear()
                        field.send_keys(fecha_hasta.strftime("%d/%m/%Y"))
                        logger.info(f"✓ Fecha hasta configurada: {fecha_hasta.strftime('%d/%m/%Y')}")
                        break
                except:
                    continue
            
            # Paso 3: Llenar el campo de descripción del objeto (SI SE ESPECIFICA)
            if objeto_contratacion:
                logger.info(f"Configurando descripción del objeto: {objeto_contratacion}")
                description_selectors = [
                    "tbBuscador:idFormBuscarProceso:descripcionObjeto",
                    "descripcionObjeto",
                    "//input[@placeholder='Descripción del Objeto']",
                    "//input[contains(@name, 'descripcion')]"
                ]
                
                for selector in description_selectors:
                    try:
                        if selector.startswith("//"):
                            field = self.driver.find_element(By.XPATH, selector)
                        else:
                            field = self.driver.find_element(By.ID, selector)
                        
                        if field.is_displayed() and field.is_enabled():
                            field.clear()
                            field.send_keys(objeto_contratacion)
                            logger.info(f"✓ Descripción '{objeto_contratacion}' ingresada en campo: {selector}")
                            break
                    except:
                        continue
            
            # Paso 4: Buscar y hacer clic en el botón de búsqueda
            logger.info("Ejecutando búsqueda...")
            search_button_selectors = [
                "tbBuscador:idFormBuscarProceso:btnBuscarSelToken",
                "//button[contains(text(), 'Buscar')]",
                "//input[@value='Buscar']",
                "//button[contains(@class, 'btnBuscar')]"
            ]
            
            button_clicked = False
            for selector in search_button_selectors:
                try:
                    if selector.startswith("//"):
                        button = self.driver.find_element(By.XPATH, selector)
                    else:
                        button = self.driver.find_element(By.ID, selector)
                    
                    if button.is_displayed() and button.is_enabled():
                        self.driver.execute_script("arguments[0].click();", button)
                        logger.info(f"✓ Botón de búsqueda clickeado: {selector}")
                        button_clicked = True
                        break
                except:
                    continue
            
            if not button_clicked:
                logger.warning("No se pudo encontrar botón de búsqueda")
            
            # Paso 5: Esperar resultados y parsear
            logger.info("Esperando resultados de búsqueda...")
            
            # Esperar a que aparezcan los resultados o un mensaje de "no encontrado"
            try:
                # Esperar elementos que indican que la búsqueda terminó
                WebDriverWait(self.driver, 15).until(
                    lambda driver: (
                        driver.find_elements(By.XPATH, "//table[contains(@class, 'ui-datatable')]") or
                        driver.find_elements(By.XPATH, "//*[contains(text(), 'No se encontraron')]") or
                        driver.find_elements(By.XPATH, "//table//td[contains(text(), 'SEL-')]")  # Nomenclaturas típicas
                    )
                )
                logger.info("Resultados de búsqueda cargados")
            except TimeoutException:
                logger.warning("Timeout esperando resultados, continuando con el HTML actual")
            
            # Esperar un poco más para asegurar que el contenido esté completamente cargado
            time.sleep(3)
            
            # Obtener HTML actualizado después de la búsqueda
            html = self.driver.page_source
            return await self._parse_search_results(html)
            
        except Exception as e:
            logger.error(f"Error en búsqueda SEACE con Selenium: {e}")
            raise ETLException(f"Error en búsqueda: {e}")
    
    async def _parse_search_results(self, html: str) -> Dict[str, Any]:
        """Parsear resultados usando BeautifulSoup"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        logger.info(f"HTML recibido: {len(html)} caracteres")
        
        # Buscar mensajes de error o sin resultados DE MANERA MÁS ESPECÍFICA
        # Primero verificar si hay tabla de datos
        seace_data_table = soup.find('tbody', {'id': 'tbBuscador:idFormBuscarProceso:dtProcesos_data'})
        has_data_table = bool(seace_data_table)
        
        # Solo buscar indicadores de "sin datos" si NO hay tabla de datos o si está vacía
        if not has_data_table:
            no_data_indicators = [
                'no se encontraron datos',
                'sin resultados',
                'no hay datos',
                '0 registros',
                'mostrando de 0 a 0'
            ]
            
            html_lower = html.lower()
            for indicator in no_data_indicators:
                if indicator in html_lower:
                    logger.info(f"Indicador de sin datos encontrado (sin tabla): '{indicator}'")
                    return {
                        "total_found": 0,
                        "processes": [],
                        "message": f"No se encontraron datos - detectado: {indicator}"
                    }
        
        # Si hay tabla de datos, procesar directamente
        if seace_data_table:
            logger.info("Tabla específica de SEACE encontrada")
            rows = seace_data_table.find_all('tr', {'data-ri': True})
            logger.info(f"Filas de datos encontradas en tabla SEACE: {len(rows)}")
            
            # Si no hay filas con data-ri, verificar sin datos
            if not rows:
                logger.info("Tabla de datos encontrada pero sin filas de datos")
                return {
                    "total_found": 0,
                    "processes": [],
                    "message": "Tabla encontrada pero sin datos"
                }
            
            for row in rows:
                cells = row.find_all('td', role='gridcell')
                if len(cells) >= 6:  # Al menos 6 columnas como vemos en la estructura
                    try:
                        # Extraer datos según la estructura específica de SEACE
                        numero = cells[0].get_text(strip=True) if len(cells) > 0 else ""
                        entidad = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                        fecha_publicacion = cells[2].get_text(strip=True) if len(cells) > 2 else ""
                        nomenclatura = cells[3].get_text(strip=True) if len(cells) > 3 else ""
                        reiniciado_desde = cells[4].get_text(strip=True) if len(cells) > 4 else ""
                        objeto_contratacion = cells[5].get_text(strip=True) if len(cells) > 5 else ""
                        descripcion = cells[6].get_text(strip=True) if len(cells) > 6 else ""
                        
                        # Validar que sea una fila de datos real
                        if (numero.isdigit() and 
                            entidad and entidad != "Nombre o Sigla de la Entidad" and
                            nomenclatura and nomenclatura not in ["Nomenclatura", "Tipo de Selección"] and
                            len(descripcion) > 10):
                            
                            # Crear objeto de proceso
                            process = {
                                "numero_proceso": nomenclatura,
                                "entidad": entidad,
                                "objeto_contratacion": objeto_contratacion,
                                "fecha_publicacion": fecha_publicacion,
                                "descripcion": descripcion,
                                "reiniciado_desde": reiniciado_desde,
                                "numero_orden": numero,
                                "fecha_extraccion": datetime.now().isoformat()
                            }
                            
                            # Extraer información adicional si está disponible
                            if len(cells) > 7:
                                # Columnas adicionales según la estructura SEACE
                                valor_referencial = cells[9].get_text(strip=True) if len(cells) > 9 else ""
                                moneda = cells[10].get_text(strip=True) if len(cells) > 10 else ""
                                version_seace = cells[11].get_text(strip=True) if len(cells) > 11 else ""
                                
                                process.update({
                                    "valor_referencial": valor_referencial if valor_referencial != "---" else "",
                                    "moneda": moneda,
                                    "version_seace": version_seace
                                })
                            
                            results.append(process)
                            logger.info(f"Proceso válido encontrado: {nomenclatura}")
                        else:
                            logger.debug(f"Fila descartada - numero: {numero}, entidad: {entidad[:50]}")
                            
                    except Exception as e:
                        logger.warning(f"Error procesando fila: {e}")
                        continue
        
        # Fallback: buscar tabla por clases ui-datatable
        if not results:
            logger.info("Buscando tabla con método fallback...")
            result_tables = soup.find_all('table', class_=lambda x: x and 'ui-datatable' in x)
            
            for table in result_tables:
                tbody = table.find('tbody')
                if not tbody:
                    continue
                    
                rows = tbody.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 6:
                        try:
                            cell_texts = [cell.get_text(strip=True) for cell in cells]
                            
                            # Verificar que no sea encabezado
                            if (cell_texts[0].isdigit() and 
                                len(cell_texts[1]) > 5 and  # Entidad
                                len(cell_texts[6]) > 10):  # Descripción
                                
                                process = {
                                    "numero_proceso": cell_texts[3] if len(cell_texts) > 3 else "",
                                    "entidad": cell_texts[1] if len(cell_texts) > 1 else "",
                                    "objeto_contratacion": cell_texts[5] if len(cell_texts) > 5 else "",
                                    "fecha_publicacion": cell_texts[2] if len(cell_texts) > 2 else "",
                                    "descripcion": cell_texts[6] if len(cell_texts) > 6 else "",
                                    "numero_orden": cell_texts[0],
                                    "fecha_extraccion": datetime.now().isoformat()
                                }
                                results.append(process)
                                
                        except Exception as e:
                            logger.warning(f"Error en fallback: {e}")
                            continue
                
                break  # Solo procesar la primera tabla válida
        
        logger.info(f"Total procesos extraídos con Selenium: {len(results)}")
        
        return {
            "total_found": len(results),
            "processes": results,
            "method": "selenium_seace_specific"
        }


# Función helper para usar el cliente Selenium
async def search_with_selenium(objeto_contratacion: str, limit: int = 50) -> Dict[str, Any]:
    """Función helper para usar el cliente Selenium"""
    try:
        async with SEACESeleniumClient() as client:
            return await client.search_processes(objeto_contratacion=objeto_contratacion)
    except Exception as e:
        logger.error(f"Error en búsqueda Selenium: {e}")
        raise ETLException(f"Error Selenium: {e}")
