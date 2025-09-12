import httpx
import asyncio
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from datetime import datetime, date
import re
import urllib.parse
import time

from app.core.config import settings
from app.core.exceptions import ETLException

logger = logging.getLogger(__name__)


class SEACEClient:
    """Cliente mejorado para extraer datos del portal público SEACE basado en componentes reales"""
    
    def __init__(self):
        self.base_url = "https://prod2.seace.gob.pe"
        self.search_url = f"{self.base_url}/seacebus-uiwd-pub/buscadorPublico/buscadorPublico.xhtml"
        self.session: Optional[httpx.AsyncClient] = None
        self.rate_limit_delay = 2.0  # 2 segundos entre requests para ser respetuosos
        self.view_state = None
        self.session_id = None
        
    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=60.0,  # Aumentado timeout para SEACE
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _make_request(self, url: str, params: Dict[str, Any] = None, data: Dict[str, Any] = None) -> str:
        """Realizar request con retry y rate limiting"""
        if not self.session:
            raise ETLException("Cliente SEACE no inicializado")
            
        try:
            # Rate limiting
            await asyncio.sleep(self.rate_limit_delay)
            
            if data:
                response = await self.session.post(url, data=data, params=params)
            else:
                response = await self.session.get(url, params=params)
            
            response.raise_for_status()
            return response.text
            
        except httpx.RequestError as e:
            logger.error(f"Error de conexión al portal SEACE: {e}")
            raise ETLException(f"Error de conexión: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Error HTTP {e.response.status_code}: {e.response.text}")
            raise ETLException(f"Error HTTP {e.response.status_code}")
    
    async def activate_proceso_selection_tab(self) -> Dict[str, str]:
        """Activar la pestaña 'Buscador de Procedimientos de Selección' antes de realizar búsquedas"""
        try:
            # Primero obtener la página principal para obtener el estado actual
            html = await self._make_request(self.search_url)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extraer campos ocultos necesarios para JSF
            hidden_fields = {}
            for input_field in soup.find_all('input', {'type': 'hidden'}):
                name = input_field.get('name')
                value = input_field.get('value', '')
                if name:
                    hidden_fields[name] = value
            
            # ViewState de JSF es crítico
            viewstate = soup.find('input', {'name': 'javax.faces.ViewState'})
            if viewstate:
                hidden_fields['javax.faces.ViewState'] = viewstate.get('value', '')
                
            # ClientWindow también puede ser necesario
            client_window = soup.find('input', {'name': 'javax.faces.ClientWindow'})
            if client_window:
                hidden_fields['javax.faces.ClientWindow'] = client_window.get('value', '')
            
            # Agregar parámetros para activar la pestaña de Procedimientos de Selección
            # Basado en el análisis del JSON, necesitamos activar el tab correcto
            tab_activation_data = hidden_fields.copy()
            
            # Estos parámetros son típicos para activar pestañas en JSF/PrimeFaces
            tab_activation_data['javax.faces.partial.ajax'] = 'true'
            tab_activation_data['javax.faces.source'] = 'tbBuscador'
            tab_activation_data['javax.faces.partial.execute'] = 'tbBuscador'
            tab_activation_data['javax.faces.partial.render'] = 'tbBuscador'
            tab_activation_data['tbBuscador_activeIndex'] = '1'  # Índice de la pestaña "Procedimientos de Selección" (segunda pestaña)
            tab_activation_data['tbBuscador_contentLoad'] = 'true'
            
            logger.info("Activando pestaña 'Buscador de Procedimientos de Selección'")
            
            # Realizar request para activar la pestaña
            await self._make_request(self.search_url, data=tab_activation_data)
            
            # Hacer un segundo request para obtener el estado actualizado de la pestaña activada
            await asyncio.sleep(1)  # Pequeña pausa para que el servidor procese
            updated_html = await self._make_request(self.search_url)
            updated_soup = BeautifulSoup(updated_html, 'html.parser')
            
            # Extraer campos ocultos actualizados después de activar la pestaña
            updated_hidden_fields = {}
            for input_field in updated_soup.find_all('input', {'type': 'hidden'}):
                name = input_field.get('name')
                value = input_field.get('value', '')
                if name:
                    updated_hidden_fields[name] = value
            
            # ViewState actualizado
            updated_viewstate = updated_soup.find('input', {'name': 'javax.faces.ViewState'})
            if updated_viewstate:
                updated_hidden_fields['javax.faces.ViewState'] = updated_viewstate.get('value', '')
                
            logger.info(f"Pestaña activada correctamente. Campos ocultos actualizados: {len(updated_hidden_fields)}")
            
            return updated_hidden_fields
            
        except Exception as e:
            logger.error(f"Error activando pestaña de procedimientos: {e}")
            # Fallback: si falla la activación, usar el método anterior
            return await self.get_search_form()

    async def get_search_form(self) -> Dict[str, str]:
        """Obtener el formulario de búsqueda y sus campos ocultos basado en análisis real de SEACE"""
        try:
            html = await self._make_request(self.search_url)
            soup = BeautifulSoup(html, 'html.parser')
            
            # Debugging: Buscar TODOS los input fields para entender la estructura
            all_inputs = soup.find_all('input')
            logger.info(f"Total inputs encontrados: {len(all_inputs)}")
            
            # Log los primeros 20 campos para debugging
            for i, inp in enumerate(all_inputs[:20]):
                inp_id = inp.get('id', 'N/A')
                inp_name = inp.get('name', 'N/A')
                inp_type = inp.get('type', 'N/A')
                inp_value = inp.get('value', '')[:50]
                logger.info(f"Input {i+1}: id='{inp_id}', name='{inp_name}', type='{inp_type}', value='{inp_value}'")
            
            # Buscar campos específicos para formulario de búsqueda
            search_inputs = []
            for inp in all_inputs:
                inp_id = inp.get('id', '')
                inp_name = inp.get('name', '')
                # Buscar campos que contengan palabras clave de búsqueda
                if any(keyword in (inp_id + inp_name).lower() for keyword in ['buscar', 'objeto', 'contrat', 'entidad', 'fecha']):
                    search_inputs.append(inp)
                    logger.info(f"Campo de búsqueda encontrado: id='{inp_id}', name='{inp_name}'")
            
            # Buscar todos los formularios disponibles
            forms = soup.find_all('form')
            if not forms:
                raise ETLException("No se encontraron formularios en la página SEACE")
            
            # Usar el primer formulario encontrado (generalmente el principal en SEACE)
            form = forms[0]
            
            # Extraer todos los campos ocultos y necesarios
            hidden_fields = {}
            
            # Campos ocultos
            for input_field in form.find_all('input', {'type': 'hidden'}):
                name = input_field.get('name')
                value = input_field.get('value', '')
                if name:
                    hidden_fields[name] = value
            
            # ViewState de JSF
            viewstate = soup.find('input', {'name': 'javax.faces.ViewState'})
            if viewstate:
                hidden_fields['javax.faces.ViewState'] = viewstate.get('value', '')
            
            # Campos adicionales que puede necesitar SEACE
            client_window = soup.find('input', {'name': 'javax.faces.ClientWindow'})
            if client_window:
                hidden_fields['javax.faces.ClientWindow'] = client_window.get('value', '')
                
            logger.info(f"Formulario SEACE encontrado con {len(hidden_fields)} campos ocultos")
            logger.info(f"Campos ocultos: {list(hidden_fields.keys())}")
            
            return hidden_fields
            
        except Exception as e:
            logger.error(f"Error obteniendo formulario SEACE: {e}")
            raise ETLException(f"Error obteniendo formulario: {e}")
    
    async def debug_seace_structure(self) -> Dict[str, Any]:
        """Método de debugging para entender completamente la estructura de SEACE"""
        try:
            # Hacer request directo sin retry para debugging
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.search_url, headers=headers)
                response.raise_for_status()
                html = response.text
            
            soup = BeautifulSoup(html, 'html.parser')
            
            debug_info = {
                "total_forms": 0,
                "total_inputs": 0,
                "search_related_inputs": [],
                "all_tabs": [],
                "form_actions": [],
                "title": soup.title.string if soup.title else "N/A"
            }
            
            # Analizar formularios
            forms = soup.find_all('form')
            debug_info["total_forms"] = len(forms)
            
            for i, form in enumerate(forms):
                action = form.get('action', 'N/A')
                method = form.get('method', 'N/A')
                debug_info["form_actions"].append(f"Form {i+1}: action='{action}', method='{method}'")
            
            # Analizar todas las pestañas (tabs) disponibles
            tabs = soup.find_all(['li', 'div'], class_=re.compile(r'.*tab.*', re.I))
            for tab in tabs:
                tab_text = tab.get_text(strip=True)
                if tab_text and len(tab_text) < 100:  # Evitar textos muy largos
                    debug_info["all_tabs"].append(tab_text)
            
            # Buscar inputs relacionados con búsqueda de procesos específicamente
            all_inputs = soup.find_all('input')
            debug_info["total_inputs"] = len(all_inputs)
            
            for inp in all_inputs:
                inp_id = inp.get('id', '')
                inp_name = inp.get('name', '')
                inp_type = inp.get('type', '')
                
                # Buscar específicamente campos relacionados con procesos
                if 'proceso' in (inp_id + inp_name).lower() and 'hidden' not in inp_type:
                    debug_info["search_related_inputs"].append({
                        "id": inp_id,
                        "name": inp_name,
                        "type": inp_type,
                        "value": inp.get('value', '')[:50]
                    })
            
            return debug_info
            
        except Exception as e:
            logger.error(f"Error en debugging SEACE: {e}")
            return {"error": str(e)}
    
    async def search_processes(self, 
                             objeto_contratacion: str = "",
                             entidad: str = "",
                             fecha_desde: Optional[date] = None,
                             fecha_hasta: Optional[date] = None,
                             tipo_proceso: str = "",
                             estado: str = "",
                             page: int = 1) -> Dict[str, Any]:
        """
        Buscar procesos en el portal SEACE usando componentes reales identificados
        
        Args:
            objeto_contratacion: Texto a buscar en el objeto de contratación
            entidad: Nombre de la entidad contratante
            fecha_desde: Fecha de inicio de búsqueda
            fecha_hasta: Fecha de fin de búsqueda
            tipo_proceso: Tipo de proceso de selección
            estado: Estado del proceso
            page: Página de resultados
        """
        try:
            # PASO 1: Activar la pestaña "Buscador de Procedimientos de Selección"
            logger.info("PASO 1: Activando pestaña 'Buscador de Procedimientos de Selección'")
            hidden_fields = await self.activate_proceso_selection_tab()
            
            # PASO 2: Preparar el formulario con los campos exactos
            logger.info("PASO 2: Preparando formulario de búsqueda de procesos")
            form_data = hidden_fields.copy()
            
            # ESTRATEGIA MEJORADA: Usar todos los campos posibles de descripción
            if objeto_contratacion:
                # Intentar con TODOS los campos de descripción disponibles
                form_data['tbBuscador:idFormBuscarProceso:descripcionObjeto'] = objeto_contratacion
                
                # También probar con campo de objeto de contratación si existe
                form_data['tbBuscador:idFormBuscarProceso:objetoContratacion'] = objeto_contratacion
                
                # Y otros campos relacionados que puedan existir
                form_data['descripcionObjeto'] = objeto_contratacion
                form_data['objeto'] = objeto_contratacion
                
                logger.info(f"Usando término de búsqueda en múltiples campos: '{objeto_contratacion}'")
                
            # SIMPLIFICAR: Intentar búsqueda sin fechas primero
            # Las fechas pueden estar causando conflictos
            logger.info("Omitiendo fechas para simplificar la búsqueda inicial")
                
            if entidad:
                # Campo específico para nombre de entidad
                form_data['tbBuscador:idFormBuscarProceso:nombreEntidad'] = entidad
                form_data['tbBuscador:idFormBuscarProceso:txtNombreEntidad'] = entidad
            
            # Otros campos disponibles que pueden ser útiles
            if tipo_proceso:
                form_data['tbBuscador:idFormBuscarProceso:numeroSeleccion'] = tipo_proceso
            
            # CRÍTICO: Asegurar que el botón de búsqueda está configurado correctamente
            form_data['tbBuscador:idFormBuscarProceso:btnBuscarSelToken'] = 'tbBuscador:idFormBuscarProceso:btnBuscarSelToken'
            
            # Agregar parámetros JSF adicionales que pueden ser necesarios
            form_data['javax.faces.partial.ajax'] = 'true'
            form_data['javax.faces.source'] = 'tbBuscador:idFormBuscarProceso:btnBuscarSelToken'
            form_data['javax.faces.partial.execute'] = 'tbBuscador:idFormBuscarProceso'
            form_data['javax.faces.partial.render'] = 'tbBuscador:idFormBuscarProceso:dtProcesos'
            
            # PASO 3: Realizar búsqueda POST con formulario correcto
            logger.info(f"PASO 3: Realizando búsqueda SEACE con descripcionObjeto='{objeto_contratacion}'")
            logger.info(f"Usando botón de búsqueda: tbBuscador:idFormBuscarProceso:btnBuscarSelToken")
            logger.info(f"Campos del formulario: {len(form_data)} campos")
            html = await self._make_request(self.search_url, data=form_data)
            
            # Parsear resultados
            return await self._parse_search_results(html)
            
        except Exception as e:
            logger.error(f"Error en búsqueda SEACE: {e}")
            raise ETLException(f"Error en búsqueda: {e}")
    
    async def _parse_search_results(self, html: str) -> Dict[str, Any]:
        """Parsear los resultados de búsqueda HTML con estrategias múltiples y debugging mejorado"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Debugging: Imprimir información básica del HTML
            logger.info(f"HTML recibido: {len(html)} caracteres")
            
            # Buscar mensajes de error o información
            error_messages = soup.find_all(text=re.compile(r'error|sin.*resultado|no.*encontr|no.*dato', re.I))
            for msg in error_messages[:3]:  # Solo primeros 3
                logger.info(f"Mensaje encontrado: {msg.strip()}")
            
            # Estrategias múltiples para encontrar la tabla de resultados
            datatable = None
            
            # Estrategia 1: ID exacto del JSON
            datatable = soup.find('table', id='tbBuscador:idFormBuscarProceso:dtProcesos')
            if datatable:
                logger.info("Tabla encontrada por ID exacto: tbBuscador:idFormBuscarProceso:dtProcesos")
            
            # Estrategia 2: Div contenedor con ID
            if not datatable:
                datatable = soup.find('div', id='tbBuscador:idFormBuscarProceso:dtProcesos')
                if datatable:
                    logger.info("Div contenedor encontrado, buscando tabla interna")
                    datatable = datatable.find('table')
            
            # Estrategia 3: Cualquier tabla con clase datatable
            if not datatable:
                tables = soup.find_all('table', class_=re.compile(r'.*datatable.*', re.I))
                if tables:
                    datatable = tables[0]
                    logger.info(f"Tabla encontrada por clase datatable: {datatable.get('class')}")
            
            # Estrategia 4: Tabla con thead y tbody
            if not datatable:
                tables = soup.find_all('table')
                for table in tables:
                    if table.find('thead') and table.find('tbody'):
                        datatable = table
                        logger.info("Tabla encontrada por estructura thead/tbody")
                        break
            
            if not datatable:
                logger.warning("No se encontró tabla de resultados con ninguna estrategia")
                # Buscar contenido alternativo
                content_divs = soup.find_all('div', class_=re.compile(r'.*content.*|.*result.*', re.I))
                logger.info(f"Divs de contenido encontrados: {len(content_divs)}")
                return {"total": 0, "processes": [], "message": "No se encontró tabla de resultados"}
            
            # Procesar la tabla encontrada
            processes = []
            
            # Obtener encabezados
            headers = []
            thead = datatable.find('thead')
            if thead:
                for th in thead.find_all(['th', 'td']):
                    header_text = th.get_text(strip=True)
                    if header_text:
                        headers.append(header_text)
                logger.info(f"Encabezados encontrados: {headers}")
            
            # Procesar filas de datos
            tbody = datatable.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                logger.info(f"Filas de datos encontradas: {len(rows)}")
                
                for idx, row in enumerate(rows):
                    # Saltar filas de mensaje vacío
                    if 'ui-datatable-empty-message' in str(row.get('class', [])):
                        logger.info("Saltando fila de mensaje vacío")
                        continue
                    
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 3:  # Al menos debe tener algunas columnas importantes
                        try:
                            # Mapeo dinámico de campos
                            process_data = {}
                            
                            for i, cell in enumerate(cells):
                                cell_text = self._clean_text(cell.get_text())
                                header_name = headers[i] if i < len(headers) else f'columna_{i}'
                                
                                # Mapear a campos estándar según posición
                                if i == 0:
                                    process_data['numero_proceso'] = cell_text
                                elif i == 1:
                                    process_data['entidad'] = cell_text
                                elif i == 2:
                                    process_data['objeto_contratacion'] = cell_text
                                elif i == 3:
                                    process_data['tipo_proceso'] = cell_text
                                elif i == 4:
                                    process_data['estado'] = cell_text
                                elif i == 5:
                                    process_data['fecha_publicacion'] = self._parse_date(cell_text)
                                elif i == 6:
                                    process_data['valor_referencial'] = self._parse_currency(cell_text)
                                    process_data['moneda'] = self._extract_currency(cell_text) or "PEN"
                                
                                # También guardar con el nombre del encabezado
                                if header_name:
                                    process_data[header_name] = cell_text
                                
                                # Buscar enlaces
                                links = cell.find_all('a')
                                for link in links:
                                    href = link.get('href')
                                    if href:
                                        process_data['url_detalle'] = href
                            
                            # Agregar campos adicionales
                            process_data['fecha_extraccion'] = datetime.now().isoformat()
                            
                            # Validar que tiene datos mínimos necesarios
                            if (process_data.get('numero_proceso') or 
                                process_data.get('entidad') or 
                                process_data.get('objeto_contratacion')):
                                processes.append(process_data)
                                if idx < 2:  # Log de los primeros 2 para debugging
                                    logger.info(f"Proceso {idx+1} extraído: {list(process_data.keys())}")
                        
                        except Exception as e:
                            logger.warning(f"Error procesando fila {idx}: {e}")
                            continue
            
            logger.info(f"Total de procesos extraídos: {len(processes)}")
            
            # Buscar información de paginación
            pagination_info = self._extract_pagination_info_seace(soup)
            
            return {
                "total": pagination_info.get("total", len(processes)),
                "current_page": pagination_info.get("current_page", 1),
                "total_pages": pagination_info.get("total_pages", 1),
                "processes": processes,
                "found_table": datatable is not None,
                "headers": headers
            }
            
        except Exception as e:
            logger.error(f"Error parseando resultados SEACE: {e}")
            raise ETLException(f"Error parseando resultados: {e}")
    
    def _extract_pagination_info_seace(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Extraer información de paginación específica de SEACE"""
        try:
            # Buscar el paginador usando selectores específicos de SEACE
            paginator = soup.find('div', class_='ui-paginator') or \
                       soup.find('span', class_='ui-paginator-current')
            
            if paginator:
                # Buscar texto como "1 de 5" o similar
                current_text = paginator.get_text(strip=True)
                match = re.search(r'(\d+)\s+de\s+(\d+)', current_text)
                if match:
                    current_page = int(match.group(1))
                    total_pages = int(match.group(2))
                    return {
                        "current_page": current_page,
                        "total_pages": total_pages,
                        "total": total_pages * 10  # Estimación basada en paginación típica
                    }
            
            return {"current_page": 1, "total_pages": 1, "total": 0}
            
        except Exception as e:
            logger.warning(f"Error extrayendo paginación: {e}")
            return {"current_page": 1, "total_pages": 1, "total": 0}
    
    def _clean_text(self, text: str) -> str:
        """Limpiar texto extraído del HTML"""
        if not text:
            return ""
        return re.sub(r'\s+', ' ', text.strip())
    
    def _parse_date(self, date_text: str) -> Optional[str]:
        """Parsear fecha en formato DD/MM/YYYY"""
        try:
            cleaned = self._clean_text(date_text)
            if re.match(r'\d{2}/\d{2}/\d{4}', cleaned):
                return cleaned
            return None
        except:
            return None
    
    def _parse_currency(self, currency_text: str) -> Optional[float]:
        """Extraer valor numérico de texto con moneda"""
        try:
            cleaned = self._clean_text(currency_text)
            # Buscar números con comas/puntos
            match = re.search(r'[\d,]+\.?\d*', cleaned.replace(',', ''))
            if match:
                return float(match.group().replace(',', ''))
            return None
        except:
            return None
    
    def _extract_currency(self, currency_text: str) -> str:
        """Extraer símbolo de moneda"""
        cleaned = self._clean_text(currency_text)
        if 'S/' in cleaned or 'PEN' in cleaned:
            return 'PEN'
        elif 'USD' in cleaned or '$' in cleaned:
            return 'USD'
        elif 'EUR' in cleaned or '€' in cleaned:
            return 'EUR'
        return 'PEN'  # Default
    
    def _extract_detail_url(self, row) -> Optional[str]:
        """Extraer URL de detalle del proceso"""
        try:
            link = row.find('a')
            if link and link.get('href'):
                href = link.get('href')
                if href.startswith('http'):
                    return href
                else:
                    return f"{self.base_url}{href}" if href.startswith('/') else f"{self.base_url}/{href}"
            return None
        except:
            return None
    
    def _extract_pagination_info(self, soup: BeautifulSoup) -> Dict[str, int]:
        """Extraer información de paginación"""
        try:
            # Buscar texto de paginación como "Mostrando de 1 a 20 del total 150"
            pagination_text = soup.find(text=re.compile(r'Mostrando.*del total'))
            if pagination_text:
                match = re.search(r'del total (\d+)', pagination_text)
                if match:
                    total = int(match.group(1))
                    # Estimar páginas (asumiendo 20 registros por página)
                    total_pages = (total + 19) // 20
                    return {"total": total, "total_pages": total_pages, "current_page": 1}
            
            return {"total": 0, "total_pages": 1, "current_page": 1}
        except:
            return {"total": 0, "total_pages": 1, "current_page": 1}
    
    def _extract_ruc(self, cell) -> str:
        """Extraer RUC de una celda de entidad"""
        try:
            text = cell.get_text(strip=True)
            # Buscar patrón de RUC (11 dígitos)
            ruc_match = re.search(r'\b(\d{11})\b', text)
            return ruc_match.group(1) if ruc_match else ""
        except:
            return ""
    
    async def search_it_processes(self, page: int = 1) -> Dict[str, Any]:
        """Buscar específicamente procesos relacionados con TI/Sistemas usando términos optimizados"""
        
        # Términos relacionados con TI y sistemas más específicos para SEACE
        it_terms = [
            "sistema informático",
            "software",
            "aplicación web",
            "desarrollo de software",
            "tecnología información",
            "base de datos",
            "plataforma digital",
            "infraestructura tecnológica",
            "soporte técnico",
            "mantenimiento sistema"
        ]
        
        # Buscar con términos de TI usando el término más común
        results = await self.search_processes(
            objeto_contratacion="sistema",  # Término más amplio para capturar más resultados
            page=page
        )
        
        # Filtrar resultados que realmente sean de TI
        filtered_processes = []
        for process in results.get("processes", []):
            objeto = process.get("objeto_contratacion", "").lower()
            descripcion = f"{objeto} {process.get('entidad', '').lower()}"
            
            # Calcular relevancia TI
            relevancia = 0
            for term in it_terms:
                if term.lower() in descripcion:
                    relevancia += 2
            
            # Términos adicionales
            additional_terms = ["software", "sistema", "informática", "digital", "web", "base", "datos", "tecnología"]
            for term in additional_terms:
                if term in descripcion:
                    relevancia += 1
            
            if relevancia > 0:
                process["relevancia_ti"] = relevancia
                process["categoria_ti"] = self._classify_it_category(descripcion)
                filtered_processes.append(process)
        
        # Ordenar por relevancia TI
        filtered_processes.sort(key=lambda x: x.get("relevancia_ti", 0), reverse=True)
        
        results["processes"] = filtered_processes
        results["total"] = len(filtered_processes)
        results["filtered_for_it"] = True
        
        return results
    
    def _classify_it_category(self, description: str) -> str:
        """Clasificar categoría de proceso TI"""
        description = description.lower()
        
        if any(term in description for term in ["desarrollo", "programación", "código"]):
            return "Desarrollo de Software"
        elif any(term in description for term in ["mantenimiento", "soporte", "mesa de ayuda"]):
            return "Soporte y Mantenimiento"
        elif any(term in description for term in ["base de datos", "bd", "sql"]):
            return "Base de Datos"
        elif any(term in description for term in ["web", "portal", "sitio"]):
            return "Desarrollo Web"
        elif any(term in description for term in ["infraestructura", "red", "servidor"]):
            return "Infraestructura TI"
        elif any(term in description for term in ["licencia", "software"]):
            return "Licencias de Software"
        else:
            return "Sistemas de Información"
