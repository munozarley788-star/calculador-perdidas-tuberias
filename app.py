import streamlit as st
import tuberias_engine as eng

# Configuración de la página web
st.set_page_config(page_title="Calculador de Pérdidas Hidráulicas", layout="wide")

st.title("🧮 Calculador Profesional de Pérdidas de Carga en Tuberías")
st.markdown("Diseño de rutas de tubería, selección de materiales y análisis de accesorios K.")
st.divider()

# Crear dos columnas principales en la interfaz (Izquierda: Entradas | Derecha: Resultados)
col_izq, col_der = st.columns([1, 1])

with col_izq:
    st.header("📋 1. Parámetros de Entrada")
    
    # Sección A: Datos del Fluido
    st.subheader("💧 Propiedades del Fluido")
    densidad = st.number_input("Densidad del fluido (kg/m³):", min_value=1.0, value=1000.0, step=10.0)
    viscosidad = st.number_input("Viscosidad dinámica (Pa·s):", min_value=0.0001, value=0.001002, format="%.6f", help="Agua a 20°C es aprox. 0.001002")
    caudal = st.number_input("Caudal de operación (m³/h):", min_value=0.1, value=45.0, step=1.0)
    
    st.divider()
    
    # Sección B: Datos de la Tubería
    st.subheader("➿ Geometría de la Línea Recta")
    materiales_disponibles = list(eng.RUGOSIDAD_MATERIALES.keys())
    material_seleccionado = st.selectbox("Seleccione el Material de la Tubería:", options=materiales_disponibles, format_func=lambda x: x.replace("_", " ").title())
    
    diametro_int = st.number_input("Diámetro Interno Real de la Tubería (mm):", min_value=1.0, value=102.26, step=1.0, help="Para 4\" Sch 40S use 102.26")
    longitud_recta = st.number_input("Longitud Total de Tubería Recta (metros):", min_value=0.0, value=35.0, step=5.0)
    
    st.divider()
    
    # Sección C: Selección de Accesorios Estándares (K)
    st.subheader("🔧 Inventario de Accesorios en la Ruta")
    accesorios_seleccionados = {}
    
    # Agrupamos visualmente los accesorios en un desplegable expansible
    with st.expander("Abrir catálogo de accesorios K"):
        for acc_key in eng.ACCESORIOS_K.keys():
            nombre_legible = acc_key.replace("_", " ").title()
            cantidad = st.number_input(f"Cantidad de '{nombre_legible}':", min_value=0, value=0, step=1, key=acc_key)
            if cantidad > 0:
                accesorios_seleccionados[acc_key] = cantidad

    st.divider()
    
    # Sección D: Transiciones Dinámicas
    st.subheader("📐 Reducciones / Ampliaciones Especiales")
    reducciones_lista = []
    if st.checkbox("¿Incluye una Reducción en este tramo?"):
        d_m = st.number_input("Diámetro MENOR de la reducción (mm):", min_value=1.0, value=77.92)
        D_M = st.number_input("Diámetro MAYOR de la reducción (mm):", min_value=1.0, value=102.26, key="red_D")
        cant_red = st.number_input("Cantidad de reducciones:", min_value=1, value=1, key="red_cant")
        reducciones_lista.append({"d_menor_mm": d_m, "D_mayor_mm": D_M, "cantidad": cant_red})

with col_der:
    st.header("📊 2. Reporte Técnico de Resultados")
    
    # Ejecutar el cálculo llamando al motor de tuberias_engine
    res = eng.calcular_perdidas_ruta_tuberias(
        fluido_densidad=densidad,
        fluido_viscosidad=viscosidad,
        caudal_m3h=caudal,
        material_clave=material_seleccionado,
        diametro_int_mm=diametro_int,
        longitud_recta_m=longitud_recta,
        diccionario_accesorios_estatitcos=accesorios_seleccionados,
        lista_reducciones=reducciones_lista if len(reducciones_lista) > 0 else None
    )
    
    # Desplegar Tarjetas de Información Rápida (Kpis)
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Velocidad", f"{res['velocidad_m_s']} m/s")
    kpi2.metric("Reynolds", f"{res['reynolds']}")
    kpi3.metric("Régimen", f"{res['regimen_flujo']}")
    
    st.divider()
    
    # Resultados de Presión y Energía
    st.subheader("💥 Pérdidas de Energía y Caída de Presión")
    
    st.error(f"### 🎛️ Caída de Presión Total: **{res['caida_presion_psi']} PSI** ({res['caida_presion_bar']} bar)")
    st.info(f"⚡ **Potencia Hidráulica Mínima Requerida:** {res['potencia_hidraulica_hp']} HP")
    
    # Desglose de alturas de pérdida
    st.markdown(f"**Pérdidas Mayores (Fricción en tubo recto):** {res['perdidas_mayores_mcf']} mcf")
    st.markdown(f"**Pérdidas Menores (Accesorios y cambios de sección):** {res['perdidas_menores_mcf']} mcf (Suma K Global = {res['sumatoria_k_global']})")
    st.markdown(f"**Pérdida Total de Altura (H):** {res['perdida_total_mcf']} metros de columna de fluido")
    
    st.divider()
    
    # Mostrar tabla detallada de los accesorios que están aportando pérdidas
    if len(res['reporte_accesorios']) > 0:
        st.subheader("🔍 Desglose Técnico de Accesorios Activos")
        for acc_nombre, datos in res['reporte_accesorios'].items():
            st.text(f"• {acc_nombre.replace('_', ' ').title()}: Cantidad = {datos['cantidad']} | K Unitario = {datos['K_u']} | K Total = {datos['K_t']}")
    else:
        st.write("No se han agregado accesorios o transiciones a la ruta aún.")
