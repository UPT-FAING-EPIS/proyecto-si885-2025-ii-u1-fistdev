from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import logging
import time
from bs4 import BeautifulSoup
from datetime import datetime

from app.core.database import get_db
from app.etl.etl_processor import ETLProcessor
from app.etl.seace_client import SEACEClient
from app.etl.seace_selenium_client import search_with_selenium, SEACESeleniumClient
from app.models.process import Process
from app.core.exceptions import ETLException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/run")
async def run_etl_process(
    background_tasks: BackgroundTasks,
    process_type: str = "daily_sync",
    db: Session = Depends(get_db)
):
    """Ejecutar proceso ETL"""
    
    try:
        processor = ETLProcessor()
        
        if process_type == "daily_sync":
            # Ejecutar en background
            background_tasks.add_task(processor.run_daily_sync)
            return {
                "message": "Proceso ETL iniciado en segundo plano",
                "process_type": process_type,
                "status": "running"
            }
        
        elif process_type == "it_opportunities":
            # Ejecutar inmediatamente para oportunidades TI
            results = await processor.extract_it_opportunities(days_back=7)
            return {
                "message": "Extracción de oportunidades TI completada",
                "results": results,
                "status": "completed"
            }
        
        else:
            raise HTTPException(status_code=400, detail=f"Tipo de proceso no válido: {process_type}")
            
    except Exception as e:
        logger.error(f"Error en proceso ETL: {e}")
        raise HTTPException(status_code=500, detail=f"Error en ETL: {str(e)}")


@router.get("/status")
async def get_etl_status(db: Session = Depends(get_db)):
    """Obtener estado del ETL y estadísticas"""
    
    try:
        processor = ETLProcessor()
        stats = processor.get_sync_stats(db)
        
        return {
            "status": "active",
            "last_update": stats.get("last_update"),
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estado ETL: {e}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo estado: {str(e)}")


@router.post("/search")
async def search_seace_processes(
    keyword: str,
    limit: int = 50,
    save_to_db: bool = False,
    db: Session = Depends(get_db)
):
    """Buscar procesos en SEACE por palabra clave"""
    
    try:
        processor = ETLProcessor()
        results = await processor.search_processes_by_keyword(keyword, limit)
        
        response = {
            "keyword": keyword,
            "total_found": len(results),
            "processes": results,
            "saved_to_db": False
        }
        
        if save_to_db and results:
            # Guardar resultados en la base de datos
            for process_data in results:
                try:
                    await processor._process_single_record(db, process_data)
                except Exception as e:
                    logger.warning(f"Error guardando proceso: {e}")
            
            db.commit()
            response["saved_to_db"] = True
        
        return response
        
    except Exception as e:
        logger.error(f"Error en búsqueda SEACE: {e}")
        raise HTTPException(status_code=500, detail=f"Error en búsqueda: {str(e)}")


@router.get("/test-connection")
async def test_seace_connection():
    """Probar conexión con el portal SEACE"""
    
    try:
        async with SEACEClient() as client:
            # Intentar obtener el formulario de búsqueda
            form_fields = await client.get_search_form()
            
            return {
                "status": "success",
                "message": "Conexión exitosa con portal SEACE",
                "form_fields_found": len(form_fields),
                "sample_fields": list(form_fields.keys())[:5]
            }
            
    except Exception as e:
        logger.error(f"Error probando conexión SEACE: {e}")
        raise HTTPException(status_code=500, detail=f"Error de conexión: {str(e)}")


@router.get("/debug-seace")
async def debug_seace_structure():
    """Debugging detallado de la estructura de SEACE"""
    try:
        client = SEACEClient()
        debug_info = await client.debug_seace_structure()
        return {
            "status": "success",
            "debug_info": debug_info
        }
    except Exception as e:
        logger.error(f"Error en debugging SEACE: {e}")
        raise HTTPException(status_code=500, detail=f"Error en debugging: {str(e)}")


@router.post("/extract-it")
async def extract_it_processes(
    days_back: int = 7,
    save_to_db: bool = True,
    db: Session = Depends(get_db)
):
    """Extraer específicamente procesos de TI/Sistemas"""
    
    try:
        processor = ETLProcessor()
        results = await processor.extract_it_opportunities(days_back)
        
        response = {
            "extraction_date": results.get("search_date"),
            "days_searched": results.get("days_searched"),
            "total_found": results.get("total_found"),
            "opportunities": results.get("opportunities", []),
            "saved_to_db": False
        }
        
        if save_to_db and results.get("opportunities"):
            # Guardar en base de datos
            saved_count = 0
            for process_data in results["opportunities"]:
                try:
                    result = await processor._process_single_record(db, process_data)
                    if result in ["new", "updated"]:
                        saved_count += 1
                except Exception as e:
                    logger.warning(f"Error guardando proceso TI: {e}")
            
            db.commit()
            response["saved_to_db"] = True
            response["saved_count"] = saved_count
        
        return response
        
    except Exception as e:
        logger.error(f"Error extrayendo procesos TI: {e}")
        raise HTTPException(status_code=500, detail=f"Error en extracción TI: {str(e)}")


@router.post("/search-selenium")
async def search_seace_selenium(
    keyword: str = "software",
    limit: int = 50
):
    """Buscar procesos SEACE usando Selenium (JavaScript completo)"""
    
    try:
        logger.info(f"Iniciando búsqueda SEACE con Selenium para: {keyword}")
        
        results = await search_with_selenium(keyword, limit)
        
        return {
            "keyword": keyword,
            "total_found": results.get("total", 0),
            "processes": results.get("processes", []),
            "method": "selenium",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error en búsqueda Selenium: {e}")
        raise HTTPException(status_code=500, detail=f"Error Selenium: {str(e)}")


@router.get("/debug-selenium")
async def debug_selenium_search(keyword: str = "software"):
    """Debug de búsqueda Selenium para ver el HTML completo"""
    
    try:
        from app.etl.seace_selenium_client import SEACESeleniumClient
        from selenium.webdriver.common.by import By
        
        async with SEACESeleniumClient() as client:
            # Navegar a la pestaña
            await client.navigate_to_procesos_tab()
            
            # Llenar formulario si hay keyword
            if keyword:
                description_selectors = [
                    "tbBuscador:idFormBuscarProceso:descripcionObjeto",
                    "descripcionObjeto",
                    "//input[@placeholder='Descripción del Objeto']",
                    "//input[contains(@name, 'descripcion')]"
                ]
                
                for selector in description_selectors:
                    try:
                        if selector.startswith("//"):
                            field = client.driver.find_element(By.XPATH, selector)
                        else:
                            field = client.driver.find_element(By.ID, selector)
                        
                        if field.is_displayed() and field.is_enabled():
                            field.clear()
                            field.send_keys(keyword)
                            break
                    except:
                        continue
            
            # Hacer clic en buscar
            search_button_selectors = [
                "tbBuscador:idFormBuscarProceso:btnBuscarSelToken",
                "//button[contains(text(), 'Buscar')]",
                "//input[@value='Buscar']"
            ]
            
            for selector in search_button_selectors:
                try:
                    if selector.startswith("//"):
                        button = client.driver.find_element(By.XPATH, selector)
                    else:
                        button = client.driver.find_element(By.ID, selector)
                    
                    if button.is_displayed() and button.is_enabled():
                        client.driver.execute_script("arguments[0].click();", button)
                        break
                except:
                    continue
            
            # Esperar resultados
            time.sleep(5)
            
            # Obtener HTML completo
            html = client.driver.page_source
            
            # Buscar todas las tablas
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            tables = soup.find_all('table')
            
            table_info = []
            for i, table in enumerate(tables):
                table_text = table.get_text()[:200]  # Primeros 200 caracteres
                table_info.append({
                    "table_index": i,
                    "table_preview": table_text,
                    "has_tbody": bool(table.find('tbody')),
                    "row_count": len(table.find_all('tr')),
                    "table_id": table.get('id', ''),
                    "table_class": table.get('class', [])
                })
            
            # Buscar mensajes específicos
            no_data_found = "No se encontraron Datos" in html
            
            return {
                "keyword": keyword,
                "html_length": len(html),
                "tables_found": len(tables),
                "table_details": table_info,
                "no_data_message": no_data_found,
                "sample_html": html[:1000]  # Primeros 1000 caracteres para debug
            }
            
    except Exception as e:
        logger.error(f"Error en debug Selenium: {e}")
        return {
            "error": str(e),
            "keyword": keyword
        }


@router.get("/search-ti-opportunities")
async def search_ti_opportunities(
    max_keywords: int = 10,
    custom_keywords: Optional[str] = None
):
    """Buscar específicamente oportunidades de TI usando múltiples términos"""
    try:
        # Convertir custom_keywords string a lista si se proporciona
        custom_keywords_list = []
        if custom_keywords:
            custom_keywords_list = [k.strip() for k in custom_keywords.split(",")]
        
        async with SEACESeleniumClient() as client:
            results = await client.search_ti_opportunities(
                max_keywords=max_keywords,
                include_custom_keywords=custom_keywords_list
            )
            return results
            
    except Exception as e:
        logger.error(f"Error en búsqueda TI: {e}")
        raise HTTPException(status_code=500, detail=f"Error búsqueda TI: {str(e)}")


@router.post("/search-by-categories")
async def search_by_categories():
    """Buscar por categorías específicas de TI"""
    try:
        async with SEACESeleniumClient() as client:
            results = await client.search_by_categories()
            return results
            
    except Exception as e:
        logger.error(f"Error en búsqueda por categorías: {e}")
        raise HTTPException(status_code=500, detail=f"Error búsqueda categorías: {str(e)}")


@router.get("/search-custom-terms")
async def search_custom_terms(
    keywords: str,
    search_mode: str = "individual"  # "individual" o "combined"
):
    """Buscar usando términos personalizados"""
    try:
        # Convertir string separado por comas a lista
        keywords_list = [k.strip() for k in keywords.split(",")]
        
        async with SEACESeleniumClient() as client:
            if search_mode == "individual":
                # Búsqueda individual por cada término
                all_results = []
                search_summary = {}
                
                for keyword in keywords_list:
                    result = await client.search_processes(
                        objeto_contratacion=keyword,
                        año_convocatoria=2024  # Usar 2024 por defecto
                    )
                    if result.get("processes"):
                        for process in result["processes"]:
                            process["search_keyword"] = keyword
                        all_results.extend(result["processes"])
                        search_summary[keyword] = len(result["processes"])
                    else:
                        search_summary[keyword] = 0
                
                # Eliminar duplicados
                unique_results = {}
                for process in all_results:
                    key = process.get("numero_proceso", "")
                    if key and key not in unique_results:
                        unique_results[key] = process
                
                return {
                    "search_mode": "individual",
                    "keywords_searched": keywords_list,
                    "search_summary": search_summary,
                    "total_found": len(list(unique_results.values())),
                    "processes": list(unique_results.values())
                }
            
            else:  # combined mode
                # Búsqueda combinada con todos los términos
                combined_keyword = " ".join(keywords_list)
                result = await client.search_processes(
                    objeto_contratacion=combined_keyword,
                    año_convocatoria=2024  # Usar 2024 por defecto
                )
                
                return {
                    "search_mode": "combined",
                    "combined_keyword": combined_keyword,
                    "total_found": len(result.get("processes", [])),
                    "processes": result.get("processes", [])
                }
                
    except Exception as e:
        logger.error(f"Error en búsqueda personalizada: {e}")
        raise HTTPException(status_code=500, detail=f"Error búsqueda personalizada: {str(e)}")


@router.get("/ti-keywords")
async def get_ti_keywords():
    """Obtener lista de keywords de TI disponibles"""
    try:
        client = SEACESeleniumClient()
        return {
            "total_keywords": len(client.ti_keywords),
            "keywords": client.ti_keywords,
            "categories": {
                "desarrollo": ["desarrollo de software", "aplicativo", "sistema web", "portal web"],
                "infraestructura": ["servidor", "infraestructura tecnologica", "centro de datos", "red informatica"],
                "seguridad": ["ciberseguridad", "seguridad informatica", "firewall", "backup"],
                "servicios_ti": ["soporte tecnico", "mantenimiento de sistemas", "hosting", "cloud"],
                "software_empresarial": ["erp", "crm", "sap", "oracle"],
                "comunicaciones": ["telecomunicaciones", "videoconferencia", "telefonia ip", "internet"],
                "transformacion_digital": ["digitalizacion", "transformacion digital", "gobierno digital", "automatizacion"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo keywords TI: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/search-with-filters")
async def search_with_proper_filters(
    keyword: str = "sistema",
    year: int = 2025
):
    """Buscar con filtros obligatorios: Servicio + Año específico"""
    try:
        from datetime import date
        
        async with SEACESeleniumClient() as client:
            # Configurar fechas del año específico
            fecha_desde = date(year, 1, 1)
            fecha_hasta = date(year, 12, 31)
            
            results = await client.search_processes(
                objeto_contratacion=keyword,
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                año_convocatoria=year
            )
            
            return {
                "keyword": keyword,
                "year_searched": year,
                "date_range": f"{fecha_desde} to {fecha_hasta}",
                "filters_applied": {
                    "objeto_contratacion_type": "Servicio",
                    "fecha_desde": str(fecha_desde),
                    "fecha_hasta": str(fecha_hasta),
                    "descripcion": keyword
                },
                "total_found": len(results.get("processes", [])),
                "processes": results.get("processes", []),
                "method": "selenium_with_proper_filters"
            }
            
    except Exception as e:
        logger.error(f"Error en búsqueda con filtros: {e}")
        raise HTTPException(status_code=500, detail=f"Error búsqueda con filtros: {str(e)}")


@router.post("/save-processes-from-data")
async def save_processes_from_data(
    processes: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """Recibir datos de procesos y guardarlos en la base de datos"""
    
    try:
        processes_saved = 0
        processes_skipped = 0
        errors = []
        
        for process_data in processes:
            try:
                # Verificar si ya existe el proceso
                existing = db.query(Process).filter(
                    Process.id_proceso == process_data.get("numero_proceso")
                ).first()
                
                if existing:
                    processes_skipped += 1
                    continue
                
                # Parsear fecha
                fecha_pub = None
                if process_data.get("fecha_publicacion"):
                    try:
                        # Formato: "22/08/2025 22:51"
                        fecha_str = process_data.get("fecha_publicacion", "").split()[0]
                        fecha_pub = datetime.strptime(fecha_str, "%d/%m/%Y")
                    except:
                        pass
                
                # Parsear monto
                monto = None
                if (process_data.get("valor_referencial") and 
                    process_data.get("valor_referencial") != "---" and
                    process_data.get("valor_referencial") != ""):
                    try:
                        monto_str = process_data.get("valor_referencial").replace(",", "")
                        monto = float(monto_str)
                    except:
                        pass
                
                # Crear nuevo proceso
                new_process = Process(
                    id_proceso=process_data.get("numero_proceso", ""),
                    entidad_nombre=process_data.get("entidad", ""),
                    objeto_contratacion=process_data.get("descripcion", ""),
                    tipo_proceso=process_data.get("objeto_contratacion", ""),
                    fecha_publicacion=fecha_pub,
                    monto_referencial=monto,
                    moneda=process_data.get("moneda", ""),
                    categoria_proyecto="TI" if any(term in process_data.get("descripcion", "").lower() 
                                                for term in ["sistema", "software", "aplicativo", "tecnologia", "informatica"]) else "General"
                )
                
                db.add(new_process)
                processes_saved += 1
                
            except Exception as e:
                errors.append(f"Error proceso {process_data.get('numero_proceso', 'N/A')}: {str(e)}")
                continue
        
        if processes_saved > 0:
            try:
                db.commit()
                logger.info(f"Guardados {processes_saved} procesos en base de datos")
            except Exception as e:
                db.rollback()
                logger.error(f"Error al hacer commit: {e}")
                raise HTTPException(status_code=500, detail=f"Error guardando en BD: {e}")
        
        return {
            "processes_received": len(processes),
            "processes_saved": processes_saved,
            "processes_skipped": processes_skipped,
            "errors": errors[:5],  # Solo mostrar primeros 5 errores
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error en save-processes-from-data: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@router.post("/save-search-results")
async def save_search_results_to_db(
    keyword: str = "",
    year: int = 2025,
    db: Session = Depends(get_db)
):
    """Buscar con search-with-filters y guardar resultados en BD"""
    
    try:
        # Primero hacer la búsqueda que sabemos que funciona
        client = SEACESeleniumClient()
        
        result = await client.search_processes(
            objeto_contratacion=keyword if keyword else None,
            año_convocatoria=year,
            fecha_desde=f"{year}-01-01",
            fecha_hasta=f"{year}-12-31"
        )
        
        await client.close()
        
        processes_saved = 0
        processes_skipped = 0
        errors = []
        
        if result.get("processes"):
            for process_data in result["processes"]:
                try:
                    # Verificar si ya existe el proceso
                    existing = db.query(Process).filter(
                        Process.id_proceso == process_data.get("numero_proceso")
                    ).first()
                    
                    if existing:
                        processes_skipped += 1
                        continue
                    
                    # Parsear fecha
                    fecha_pub = None
                    if process_data.get("fecha_publicacion"):
                        try:
                            # Formato: "22/08/2025 22:51"
                            fecha_str = process_data.get("fecha_publicacion", "").split()[0]
                            fecha_pub = datetime.strptime(fecha_str, "%d/%m/%Y")
                        except:
                            pass
                    
                    # Parsear monto
                    monto = None
                    if (process_data.get("valor_referencial") and 
                        process_data.get("valor_referencial") != "---" and
                        process_data.get("valor_referencial") != ""):
                        try:
                            monto_str = process_data.get("valor_referencial").replace(",", "")
                            monto = float(monto_str)
                        except:
                            pass
                    
                    # Crear nuevo proceso
                    new_process = Process(
                        id_proceso=process_data.get("numero_proceso", ""),
                        entidad_nombre=process_data.get("entidad", ""),
                        objeto_contratacion=process_data.get("descripcion", ""),
                        tipo_proceso=process_data.get("objeto_contratacion", ""),
                        fecha_publicacion=fecha_pub,
                        monto_referencial=monto,
                        moneda=process_data.get("moneda", ""),
                        categoria_proyecto="TI" if any(term in process_data.get("descripcion", "").lower() 
                                                    for term in ["sistema", "software", "aplicativo", "tecnologia", "informatica"]) else "General"
                    )
                    
                    db.add(new_process)
                    processes_saved += 1
                    
                except Exception as e:
                    errors.append(f"Error proceso {process_data.get('numero_proceso', 'N/A')}: {str(e)}")
                    continue
            
            if processes_saved > 0:
                try:
                    db.commit()
                    logger.info(f"Guardados {processes_saved} procesos en base de datos")
                except Exception as e:
                    db.rollback()
                    logger.error(f"Error al hacer commit: {e}")
                    raise HTTPException(status_code=500, detail=f"Error guardando en BD: {e}")
        
        return {
            "keyword": keyword,
            "year_searched": year,
            "total_found": result.get("total_found", 0),
            "processes_saved": processes_saved,
            "processes_skipped": processes_skipped,
            "errors": errors[:5],  # Solo mostrar primeros 5 errores
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error en save-search-results: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {e}")

@router.post("/search-and-save")
async def search_and_save_processes(
    keyword: str = "",
    year: int = 2025,
    save_to_db: bool = True,
    db: Session = Depends(get_db)
):
    """Buscar procesos con Selenium y guardar en base de datos"""
    
    try:
        # Usar nuestro cliente Selenium que ya funciona
        client = SEACESeleniumClient()
        
        # Realizar búsqueda
        result = await client.search_processes(
            objeto_contratacion=keyword if keyword else None,
            año_convocatoria=year
        )
        
        await client.close()
        
        processes_saved = 0
        processes_skipped = 0
        
        if save_to_db and result.get("processes"):
            for process_data in result["processes"]:
                try:
                    # Verificar si ya existe el proceso
                    existing = db.query(Process).filter(
                        Process.id_proceso == process_data.get("numero_proceso")
                    ).first()
                    
                    if existing:
                        processes_skipped += 1
                        continue
                    
                    # Crear nuevo proceso
                    new_process = Process(
                        id_proceso=process_data.get("numero_proceso"),
                        entidad_nombre=process_data.get("entidad"),
                        objeto_contratacion=process_data.get("descripcion"),
                        tipo_proceso=process_data.get("objeto_contratacion"),
                        fecha_publicacion=datetime.strptime(
                            process_data.get("fecha_publicacion", "").split()[0], 
                            "%d/%m/%Y"
                        ) if process_data.get("fecha_publicacion") else None,
                        monto_referencial=float(
                            process_data.get("valor_referencial", "0").replace(",", "")
                        ) if process_data.get("valor_referencial") and process_data.get("valor_referencial") != "---" else None,
                        moneda=process_data.get("moneda"),
                        categoria_proyecto="TI" if any(term in process_data.get("descripcion", "").lower() 
                                                    for term in ["sistema", "software", "aplicativo", "tecnologia", "informatica"]) else "General"
                    )
                    
                    db.add(new_process)
                    processes_saved += 1
                    
                except Exception as e:
                    logger.warning(f"Error guardando proceso individual: {e}")
                    continue
            
            try:
                db.commit()
                logger.info(f"Guardados {processes_saved} procesos en base de datos")
            except Exception as e:
                db.rollback()
                logger.error(f"Error al hacer commit: {e}")
                raise HTTPException(status_code=500, detail=f"Error guardando en BD: {e}")
        
        return {
            "keyword": keyword,
            "year_searched": year,
            "total_found": result.get("total_found", 0),
            "processes_saved": processes_saved,
            "processes_skipped": processes_skipped,
            "saved_to_db": save_to_db,
            "processes": result.get("processes", []),
            "method": result.get("method", "selenium")
        }
        
    except Exception as e:
        logger.error(f"Error en search-and-save: {e}")
        raise HTTPException(status_code=500, detail=f"Error en búsqueda y guardado: {e}")

@router.get("/debug-html-analysis")
async def debug_html_analysis():
    """Debug específico para analizar la estructura HTML que recibe el sistema"""
    try:
        client = SEACESeleniumClient()
        
        # Navegar a la página y realizar búsqueda
        await client.search_processes(
            objeto_contratacion="servicio",
            año_convocatoria=2025
        )
        
        # Obtener HTML actual
        html = client.driver.page_source
        
        # Análisis de la estructura
        soup = BeautifulSoup(html, 'html.parser')
        
        analysis = {
            "html_length": len(html),
            "contains_data_table": bool(soup.find('tbody', {'id': 'tbBuscador:idFormBuscarProceso:dtProcesos_data'})),
            "tables_found": len(soup.find_all('table')),
            "ui_datatable_found": len(soup.find_all('table', class_=lambda x: x and 'ui-datatable' in x))
        }
        
        # Buscar elementos específicos
        data_table = soup.find('tbody', {'id': 'tbBuscador:idFormBuscarProceso:dtProcesos_data'})
        if data_table:
            rows_with_data_ri = data_table.find_all('tr', {'data-ri': True})
            analysis["seace_data_rows_found"] = len(rows_with_data_ri)
            
            if rows_with_data_ri:
                # Analizar primera fila
                first_row = rows_with_data_ri[0]
                cells = first_row.find_all('td', role='gridcell')
                analysis["first_row_cells"] = len(cells)
                analysis["first_row_sample"] = [cell.get_text(strip=True)[:50] for cell in cells[:7]]
        
        # Buscar indicadores de "no datos"
        no_data_found = []
        no_data_indicators = ['no se encontraron datos', 'no se encontraron', 'sin resultados', 'mostrando de 0 a 0']
        for indicator in no_data_indicators:
            if indicator in html.lower():
                no_data_found.append(indicator)
        
        analysis["no_data_indicators_found"] = no_data_found
        
        # Buscar paginador para ver total
        paginator = soup.find('span', class_='ui-paginator-current')
        if paginator:
            analysis["paginator_text"] = paginator.get_text(strip=True)
        
        await client.close()
        
        return {
            "analysis": analysis,
            "html_sample": html[html.find('<tbody id="tbBuscador:idFormBuscarProceso:dtProcesos_data"'):html.find('<tbody id="tbBuscador:idFormBuscarProceso:dtProcesos_data"') + 2000] if 'tbBuscador:idFormBuscarProceso:dtProcesos_data' in html else html[:2000]
        }
        
    except Exception as e:
        logger.error(f"Error en debug HTML: {e}")
        return {"error": str(e)}

@router.get("/debug-form-fields")
async def debug_form_fields(year: int = 2024):
    """Debug detallado de todos los campos del formulario SEACE"""
    try:
        from app.etl.seace_selenium_client import SEACESeleniumClient
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import Select
        
        async with SEACESeleniumClient() as client:
            # Navegar a la pestaña
            await client.navigate_to_procesos_tab()
            
            # Esperar que la página cargue
            time.sleep(3)
            
            # Obtener HTML y analizar campos disponibles
            html = client.driver.page_source
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Buscar todos los campos de formulario
            form_fields = {
                "select_elements": [],
                "input_elements": [],
                "button_elements": []
            }
            
            # Analizar dropdowns/selects
            selects = soup.find_all('select')
            for select in selects:
                options = [opt.get_text().strip() for opt in select.find_all('option')]
                form_fields["select_elements"].append({
                    "id": select.get('id', ''),
                    "name": select.get('name', ''),
                    "class": select.get('class', []),
                    "options": options[:10]  # Primeras 10 opciones
                })
            
            # Analizar inputs
            inputs = soup.find_all('input')
            for inp in inputs:
                form_fields["input_elements"].append({
                    "id": inp.get('id', ''),
                    "name": inp.get('name', ''),
                    "type": inp.get('type', ''),
                    "placeholder": inp.get('placeholder', ''),
                    "value": inp.get('value', '')
                })
            
            # Analizar botones
            buttons = soup.find_all(['button', 'input[type="submit"]'])
            for btn in buttons:
                form_fields["button_elements"].append({
                    "id": btn.get('id', ''),
                    "name": btn.get('name', ''),
                    "type": btn.get('type', ''),
                    "text": btn.get_text().strip(),
                    "value": btn.get('value', '')
                })
            
            # Intentar configurar campos usando Selenium directamente
            configuration_results = {}
            
            # Probar configurar Objeto de Contratación
            try:
                obj_select = client.driver.find_element(By.ID, "tbBuscador:idFormBuscarProceso:j_idt234_input")
                select_obj = Select(obj_select)
                available_options = [opt.text for opt in select_obj.options]
                configuration_results["objeto_contratacion"] = {
                    "found": True,
                    "options": available_options
                }
                
                # Intentar seleccionar "Servicio"
                for opt in select_obj.options:
                    if "servicio" in opt.text.lower():
                        select_obj.select_by_visible_text(opt.text)
                        configuration_results["objeto_contratacion"]["selected"] = opt.text
                        break
                        
            except Exception as e:
                configuration_results["objeto_contratacion"] = {"found": False, "error": str(e)}
            
            # Probar configurar Año de Convocatoria
            try:
                year_select = client.driver.find_element(By.ID, "tbBuscador:idFormBuscarProceso:anioConvocatoria_input")
                select_year = Select(year_select)
                available_years = [opt.text for opt in select_year.options]
                configuration_results["año_convocatoria"] = {
                    "found": True,
                    "options": available_years
                }
                
                # Intentar seleccionar el año
                if str(year) in available_years:
                    select_year.select_by_visible_text(str(year))
                    configuration_results["año_convocatoria"]["selected"] = str(year)
                else:
                    configuration_results["año_convocatoria"]["selected"] = "not_available"
                    
            except Exception as e:
                configuration_results["año_convocatoria"] = {"found": False, "error": str(e)}
            
            return {
                "year_tested": year,
                "form_analysis": form_fields,
                "configuration_attempts": configuration_results,
                "html_sample": html[:2000]  # Primeros 2000 caracteres
            }
            
    except Exception as e:
        logger.error(f"Error en debug de campos: {e}")
        return {
            "error": str(e),
            "year_tested": year
        }
