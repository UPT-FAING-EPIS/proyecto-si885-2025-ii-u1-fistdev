[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/VMb-1xPS)
[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-2972f46106e565e64193e422d61a12cf1da4916b45550586e14ef0a7c637dd04.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=20085849)
# proyecto-formatos-01
# SEACE ProjectFinder

**Subtítulo:** Generador y recomendador de proyectos para Ingenieros de Sistemas del Perú a partir de SEACE

---

## Resumen ejecutivo
SEACE ProjectFinder transforma procesos y convocatorias públicas del **SEACE / OSCE** en un **catálogo** de ideas de proyectos de software y un **dashboard** interactivo (Power BI) que facilita la **identificación visual de los datos más relevantes**. La plataforma está diseñada para **Ingenieros de Sistemas del Perú**, para que profesionales puedan encontrar, priorizar y comenzar proyectos reales basados en necesidades públicas.

---

# 1. Problema
Los procesos y requerimientos publicados en SEACE contienen problemas y demandas concretas del Estado, pero:
- Están dispersos y en formato técnico (pliegos, anexos).  
- Ingenieros de Sistemas no disponen de una interfaz visual que resuma y priorice estas oportunidades.  
- Falta un mecanismo rápido para transformar esos registros en enunciados y acciones técnicas viables.

---

# 2. Objetivo general
Proveer a los Ingenieros de Sistemas del Perú una **herramienta visual** que permita identificar, priorizar y convertir procesos SEACE en resúmenes de proyecto accionables y listos para iniciar (MVP, entregables y Sprint 1).

## Objetivos específicos
- Extraer y almacenar registros públicos relevantes del SEACE (convocatorias, objetos, anexos).  
- Procesar descripciones con NLP para clasificar rubros y extraer requerimientos técnicos.  
- Generar mappings automáticos “registro SEACE → 1–3 ideas de proyecto” con entregables y Sprint 1.  
- Implementar un catálogo consultable con filtros avanzados (rubros, complejidad, anexos, monto).  
- Implementar un chatbot recomendador (RAG + embeddings) que sugiera proyectos según perfil profesional y recursos.  
- Desplegar un dashboard Power BI que muestre KPIs y facilite la priorización de oportunidades.  
- Documentar trazabilidad (id_proceso + URL) y supuestos técnicos.

---

# 3. Alcance
- **Fuente única:** SEACE / OSCE (registros públicos).  
- Cobertura: nacional (Perú), con historial (últimos 3–5 años según disponibilidad).  
- Complejidad técnica: media — incluye ETL, modelado, Power BI y prototipo de recomendador.  
- No integra sistemas internos de entidades ni datos privados.

---

# 4. Usuarios objetivo (generalizado)
- **Ingenieros de Sistemas del Perú** — profesionales que buscan oportunidades reales para desarrollar soluciones, consultorías, productos o MVPs basados en la demanda pública.  
- **Usuarios secundarios:** docentes, grupos de investigación y empresas que quieran alinear propuestas con necesidades estatales.

---

# 5. Fuente de datos
- **SEACE / OSCE:** descripciones de procesos, pliegos, anexos, adjudicaciones y documentación pública.  
- Cada registro será trazable mediante `id_proceso` y `URL` a SEACE.

---
