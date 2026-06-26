# Motor de Cálculo Hidrodinámico - Caídas de Presión en Tuberías

Este es el backend y motor matemático para una aplicación de ingeniería diseñada para calcular las pérdidas de carga mayores (por fricción en tubería recta) y menores (en accesorios, válvulas y transiciones dinámicas) en sistemas de tuberías industriales.

## Características Principales
- **Base de Datos de Materiales Extensa:** Soporta rugosidades absolutas para PVC, Acero Inoxidable, Acero al Carbono, Cobre, Hierro Dúctil, entre otros.
- **Catálogo Completo de Coeficientes K:** Incluye valores estándar para codos (desde radio corto hasta gran radio 5D), tees, pantalones/bifurcaciones, y múltiples tipos de válvulas.
- **Cálculo Dinámico de Transiciones:** Algoritmos matemáticos exactos para determinar el coeficiente K variable en reducciones y ampliaciones.
- **Análisis de Fricción Exacto:** Implementación de la ecuación de **Haaland** para régimen turbulento y automatización para régimen laminar y de transición.

## Arquitectura del Proyecto
Actualmente, el proyecto cuenta con el núcleo de cálculo en `tuberias_engine.py`. Está desacoplado y estructurado modularmente para integrarse fácilmente con interfaces gráficas como **Streamlit** o frameworks web como **Flask/Django**.

## Próximos Pasos
- [ ] Integrar interfaz gráfica interactiva (Frontend).
- [ ] Añadir base de datos comercial de diámetros de tubería (NPS / Schedules / ISO).
