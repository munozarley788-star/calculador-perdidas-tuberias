"""
=============================================================================
SISTEMA PROFESIONAL DE CÁLCULO DE PÉRDIDAS DE CARGA EN REDES DE TUBERÍAS
=============================================================================
Módulo de cálculo hidrodinámico sin simplificaciones para ingeniería industrial.
Apto para integración con Streamlit, Flask, Django o Dash en entornos Web/GitHub.

Autor: AI Collaborator
Año: 2026
=============================================================================
"""

import math

# =============================================================================
# 1. BASE DE DATOS MAESTRA DE MATERIALES (Rugosidad Absoluta 'ε' en metros)
# =============================================================================
RUGOSIDAD_MATERIALES = {
    # Plásticos y Polímeros (Tuberías consideradas lisas)
    "pvc_plastico": 1.5e-6,          # PVC Comercial estándar
    "hdpe_polietileno": 1.5e-6,      # Polietileno de Alta Densidad
    "ppr_polipropileno": 1.5e-6,     # Polipropileno Copolímero Random (Termofusión)
    "fibra_de_vidrio_grp": 5.0e-6,   # Plástico reforzado con fibra de vidrio

    # Metales Aleados y No Ferrosos
    "acero_inoxidable_nuevo": 1.5e-5, # Acero Inoxidable (SS304 / SS316) limpio
    "cobre_sin_costura": 1.5e-6,      # Tubería de cobre para agua o refrigeración
    "laton_bronce": 1.5e-6,          # Latón o Bronce estirado

    # Aceros y Hierros Industriales
    "acero_comercial_nuevo": 4.6e-5,  # Acero al carbono estándar (Sch 40 / Sch 80)
    "acero_galvanizado": 1.5e-4,      # Acero con recubrimiento de zinc
    "hierro_fundido_ductil": 2.6e-4,  # Hierro dúctil para acueductos e incendios
    "hierro_fundido_asfaltado": 1.2e-4, # Hierro con recubrimiento asfáltico
    "hierro_forjado": 4.6e-5,         # Hierro forjado comercial

    # Materiales Especiales y Obra Civil
    "concreto_centrifugado": 3.0e-4,  # Concreto liso de alta calidad
    "concreto_frotachado_basto": 3.0e-3, # Concreto rugoso / canales cerrados
    "arcilla_vitrificada": 4.0e-5,    # Tuberías de gres para alcantarillado

    # Condiciones de Envejecimiento (Para análisis de desgaste de planta)
    "acero_con_incrustaciones": 2.5e-3, # Tubería con obstrucciones o sarro severo
    "acero_corroido_viejo": 1.5e-3,    # Acero al carbono tras años de servicio de agua
    "hierro_fundido_oxidado": 1.0e-3    # Hierro fundido viejo
}

# =============================================================================
# 2. CATÁLOGO COMPLETO DE COEFICIENTES DE PÉRDIDA MENOR (K) (Estático)
# =============================================================================
ACCESORIOS_K = {
    # --- CODOS Y CURVAS DE 90 GRADOS ---
    "codo_90_radio_corto": 0.90,             # R/D = 1
    "codo_90_radio_estandar": 0.75,          # R/D = 1.2
    "codo_90_radio_largo_1.5d": 0.45,        # R/D = 1.5 (Muy común en procesos)
    "codo_90_gran_radio_3d": 0.30,           # R/D = 3
    "codo_90_gran_radio_5d": 0.20,           # R/D = 5 (Transporte neumático/husos)
    "codo_90_inglete_1_mitra": 1.20,         # Codo fabricado a 90° (un corte)
    "codo_90_inglete_2_mitras": 0.60,        # Codo fabricado a 90° (dos cortes)

    # --- CODOS Y CURVAS DE 45 Y 180 GRADOS ---
    "codo_45_estandar": 0.35,                # R/D = 1
    "codo_45_radio_largo_1.5d": 0.20,        # R/D = 1.5
    "codo_45_gran_radio_5d": 0.10,           # R/D = 5
    "curva_180_retorno_corto": 1.50,         # Retorno cerrado de 180°
    "curva_180_retorno_largo": 0.70,         # Retorno de 180° radio largo

    # --- DERIVACIONES, TEES Y BIFURCACIONES (PANTALONES) ---
    "tee_flujo_directo": 0.30,               # Pasa recto por la carrera principal
    "tee_flujo_por_ramal_90": 1.40,          # Desvío a 90° por el ramal
    "tee_entrada_linea_bifurcada": 1.00,     # Flujo entra por ramal y divide a los lados
    "pantalon_Y_45_directo": 0.35,           # Tipo pantalón: Flujo por la sección recta
    "pantalon_Y_45_ramal": 0.75,             # Tipo pantalón: Desvío a 45°
    "pantalon_Y_bifurcacion_simetrica": 0.50,# División simétrica exacta a ambos lados
    "union_boca_de_pescado": 0.85,           # Injerto soldado directo tubo a tubo

    # --- VÁLVULAS TOTALMENTE ABIERTAS ---
    "valvula_compuerta_paso_total": 0.15,    # Gate Valve (Mínima obstrucción)
    "valvula_bola_paso_total": 0.05,        # Ball Valve (Flujo prácticamente libre)
    "valvula_bola_paso_reducido": 0.25,      # Ball Valve (Económica, estrangula un poco)
    "valvula_mariposa_asiento_resiliente": 0.50, # Butterfly Valve estándar
    "valvula_globo_estandar": 10.00,         # Globe Valve (Alta pérdida para regulación)
    "valvula_globo_tipo_Y": 2.00,            # Globe Valve angular de flujo suave
    "valvula_angulo_90_grados": 4.00,        # Válvula de ángulo a 90°
    "valvula_diafragma_abierta": 2.30,       # Válvula de diafragma (procesos sanitarios)

    # --- VÁLVULAS DE RETENCIÓN / CHECK ---
    "valvula_check_columpio": 2.00,          # Swing Check Valve
    "valvula_check_elevacion_disco": 12.00,  # Lift Check Valve
    "valvula_check_doble_plato_mariposa": 2.50,# Dual Plate Check
    "valvula_check_de_bola": 4.50,           # Ball Check Valve

    # --- CONEXIONES A TANQUES / EMBOCADURAS ---
    "entrada_tanque_hacia_adentro": 0.78,    # Tubo que sobresale dentro del tanque (Borda)
    "entrada_tanque_borde_vivo": 0.50,       # Tubo raso perpendicular perfecto
    "entrada_tanque_achaflanada": 0.25,     # Borde con chaflán angular
    "entrada_tanque_redondeada_suave": 0.04, # Embocadura con radio hidrodinámico
    "salida_tanque_todas_las_formas": 1.00,  # Pérdida cinética de descarga total

    # --- ACCESORIOS DE CONTROL Y OTROS ---
    "filtro_en_Y_malla_limpia": 2.00,        # Y-Strainer estándar
    "filtro_en_Y_malla_semi_obstruida": 6.00,# Simulación operativa real de taponamiento
    "junta_de_expansion_fuelle": 0.30,       # Junta antivibratoria metálica
    "medidor_orificio_placa": 2.50,          # Elemento primario de medición
    "medidor_venturi": 0.25                  # Medidor de flujo de recuperación alta
}

# =============================================================================
# 3. FUNCIONES DE CÁLCULO FÍSICO Y DINÁMICO
# =============================================================================

def calcular_k_reduccion_dinamica(d_menor_mm: float, D_mayor_mm: float) -> float:
    """
    Calcula dinámicamente el K de una reducción cónica estándar basada en la
    velocidad en el extremo MENOR (d). Ángulo de contracción comercial típico de ~45-60°.
    """
    if D_mayor_mm <= d_menor_mm or D_mayor_mm <= 0:
        return 0.0
    relacion = d_menor_mm / D_mayor_mm
    k_reduccion = 0.5 * (1.0 - (relacion ** 2))
    return k_reduccion

def calcular_k_ampliacion_dinamica(d_menor_mm: float, D_mayor_mm: float) -> float:
    """
    Calcula dinámicamente el K de una ampliación cónica gradual basada en la
    velocidad en el extremo MENOR (d). Ángulo de expansión suave de ~20°.
    Ecuación de Borda-Carnot adaptada.
    """
    if D_mayor_mm <= d_menor_mm or d_menor_mm <= 0:
        return 0.0
    relacion = d_menor_mm / D_mayor_mm
    k_ampliacion = (1.0 - (relacion ** 2)) ** 2
    return k_ampliacion

def calcular_velocidad(caudal_m3h: float, diametro_int_mm: float) -> float:
    """Calcula la velocidad del fluido dentro de la sección de la tubería en m/s."""
    if diametro_int_mm <= 0:
        return 0.0
    caudal_m3s = caudal_m3h / 3600.0
    di_m = diametro_int_mm / 1000.0
    area_m2 = (math.pi * (di_m ** 2)) / 4.0
    return caudal_m3s / area_m2

def calcular_reynolds(densidad_kgm3: float, velocidad_ms: float, diametro_int_mm: float, viscosidad_pas: float) -> float:
    """Calcula el número adimensional de Reynolds para evaluar el régimen dinámico."""
    if viscosidad_pas <= 0 or diametro_int_mm <= 0:
        return float('inf')
    di_m = diametro_int_mm / 1000.0
    return (densidad_kgm3 * velocidad_ms * di_m) / viscosidad_pas

def calcular_factor_friccion_darcy(reynolds: float, rugosidad_m: float, diametro_int_mm: float) -> float:
    """
    Determina de manera exacta el factor de fricción de Darcy 'f'.
    Evalúa régimen Laminar, Crítico (Transición) o Turbulento mediante la ecuación de Haaland.
    """
    if diametro_int_mm <= 0 or reynolds <= 0:
        return 0.0
    
    di_m = diametro_int_mm / 1000.0
    
    # 1. Régimen Laminar Puro
    if reynolds <= 2300:
        return 64.0 / reynolds
    
    # 2. Régimen Crítico / Transición Inestable (Interpolación polinómica entre leyes)
    elif 2300 < reynolds < 4000:
        f_laminar_limite = 64.0 / 2300.0
        # Evaluar Haaland en la frontera turbulenta (Re=4000)
        termino_frontera = (((rugosidad_m / di_m) / 3.7) ** 1.11) + (6.9 / 4000.0)
        f_turbulento_limite = 1.0 / (-1.8 * math.log10(termino_frontera)) ** 2
        
        # Factor ponderado de transición lineal
        ponderador = (reynolds - 2300.0) / (4000.0 - 2300.0)
        return f_laminar_limite + ponderador * (f_turbulento_limite - f_laminar_limite)
    
    # 3. Régimen Turbulento Completo (Ecuación Explícita de Haaland)
    else:
        rugosidad_relativa = rugosidad_m / di_m
        argumento_log = ((rugosidad_relativa / 3.7) ** 1.11) + (6.9 / reynolds)
        
        if argumento_log <= 0:
            return 0.02 # Salvaguarda física ante indeterminaciones matemáticas
            
        denominador = -1.8 * math.log10(argumento_log)
        return float(1.0 / (denominador ** 2))

# =============================================================================
# 4. FUNCIÓN CENTRALIZADA DE EVALUACIÓN HIDRÁULICA
# =============================================================================
def calcular_perdidas_ruta_tuberias(
    fluido_densidad: float,
    fluido_viscosidad: float,
    caudal_m3h: float,
    material_clave: str,
    diametro_int_mm: float,
    longitud_recta_m: float,
    diccionario_accesorios_estatitcos: dict,
    lista_reducciones: list = None,
    lista_ampliaciones: list = None
) -> dict:
    """
    Ejecuta el cálculo holístico de caídas de presión en un tramo o ruta.
    Permite el ingreso de accesorios comunes, reducciones y ampliaciones dinámicas.
    """
    g_gravedad = 9.80665 # m/s^2
    di_m = diametro_int_mm / 1000.0
    
    # Resolver rugosidad
    rugosidad_m = RUGOSIDAD_MATERIALES.get(material_clave, 1.5e-5)
    
    # Dinámica cinemática básica
    v_velocidad = calcular_velocidad(caudal_m3h, diametro_int_mm)
    re_numero = calcular_reynolds(fluido_densidad, v_velocidad, diametro_int_mm, fluido_viscosidad)
    f_friccion = calcular_factor_friccion_darcy(re_numero, rugosidad_m, diametro_int_mm)
    
    # A. Pérdidas Mayores (Darcy-Weisbach)
    altura_perdida_mayores = f_friccion * (longitud_recta_m / di_m) * ((v_velocidad ** 2) / (2 * g_gravedad))
    
    # B. Pérdidas Menores (Accesorios Estáticos)
    suma_k_total = 0.0
    desglose_salida = {}
    
    for item, cant in diccionario_accesorios_estatitcos.items():
        if item in ACCESORIOS_K and cant > 0:
            k_u = ACCESORIOS_K[item]
            k_t = k_u * cant
            suma_k_total += k_t
            desglose_salida[item] = {"tipo": "Estático", "K_u": k_u, "K_t": k_t, "cantidad": cant}
            
    # C. Pérdidas Menores (Reducciones Dinámicas)
    if lista_reducciones:
        for index, red in enumerate(lista_reducciones):
            # Formato esperado de red: {"d_menor_mm": X, "D_mayor_mm": Y, "cantidad": Z}
            k_red_din = calcular_k_reduccion_dinamica(red["d_menor_mm"], red["D_mayor_mm"])
            k_t_red = k_red_din * red.get("cantidad", 1)
            suma_k_total += k_t_red
            desglose_salida[f"reduccion_dinamica_{index+1}"] = {
                "tipo": f"Reducción ({red['D_mayor_mm']}mm -> {red['d_menor_mm']}mm)",
                "K_u": round(k_red_din, 4),
                "K_t": round(k_t_red, 4),
                "cantidad": red.get("cantidad", 1)
            }

    # D. Pérdidas Menores (Ampliaciones Dinámicas)
    if lista_ampliaciones:
        for index, amp in enumerate(lista_ampliaciones):
            # Formato esperado de amp: {"d_menor_mm": X, "D_mayor_mm": Y, "cantidad": Z}
            k_amp_din = calcular_k_ampliacion_dinamica(amp["d_menor_mm"], amp["D_mayor_mm"])
            k_t_amp = k_amp_din * amp.get("cantidad", 1)
            suma_k_total += k_t_amp
            desglose_salida[f"ampliacion_dinamica_{index+1}"] = {
                "tipo": f"Ampliación ({amp['d_menor_mm']}mm -> {amp['D_mayor_mm']}mm)",
                "K_u": round(k_amp_din, 4),
                "K_t": round(k_t_amp, 4),
                "cantidad": amp.get("cantidad", 1)
            }
            
    # Calcular altura de pérdidas menores total
    altura_perdida_menores = suma_k_total * ((v_velocidad ** 2) / (2 * g_gravedad))
    
    # E. Consolidación de Resultados Energéticos
    altura_perdida_total = altura_perdida_mayores + altura_perdida_menores
    
    # Caídas de presión en unidades métricas e imperiales
    caida_presion_pa = altura_perdida_total * fluido_densidad * g_gravedad
    caida_presion_psi = caida_presion_pa / 6894.75729
    caida_presion_bar = caida_presion_pa / 100000.0
    
    # Potencia hidráulica neta demandada (Watts y Horsepower)
    caudal_m3s = caudal_m3h / 3600.0
    potencia_watts = caudal_m3s * caida_presion_pa
    potencia_hp = potencia_watts / 745.69987
    
    return {
        "velocidad_m_s": round(v_velocidad, 3),
        "reynolds": round(re_numero, 1),
        "regimen_flujo": "Laminar" if re_numero <= 2300 else "Transición" if re_numero < 4000 else "Turbulento",
        "factor_darcy_f": round(f_friccion, 5),
        "perdidas_mayores_mcf": round(altura_perdida_mayores, 4),
        "perdidas_menores_mcf": round(altura_perdida_menores, 4),
        "perdida_total_mcf": round(altura_perdida_total, 4),
        "caida_presion_psi": round(caida_presion_psi, 4),
        "caida_presion_bar": round(caida_presion_bar, 4),
        "caida_presion_pa": round(caida_presion_pa, 2),
        "potencia_hidraulica_hp": round(potencia_hp, 4),
        "sumatoria_k_global": round(suma_k_total, 4),
        "reporte_accesorios": desglose_salida
    }

# =============================================================================
# 5. BLOQUE DE EJECUCIÓN EJEMPLO (VALIDACIÓN DE COMPILACIÓN)
# =============================================================================
if __name__ == "__main__":
    print("-" * 70)
    print("EJECUCIÓN DE PRUEBA DEL MOTOR DE CÁLCULO DE TUBERÍAS")
    print("-" * 70)
    
    # Configuración de un tramo de proceso industrial simulado:
    # Fluido: Salmuera / Agua industrial densa a baja temperatura
    densidad_fluido = 1050.0      # kg/m3
    viscosidad_fluido = 0.0012    # Pa·s (un poco más viscoso que el agua pura)
    caudal_operacion = 55.0       # m3/h
    
    # Geometría del tramo analizado
    material = "acero_inoxidable_nuevo"
    diametro_interior = 102.26    # mm (Corresponde a una tubería de 4" Sch 40S)
    longitud_linea_recta = 60.0   # metros
    
    # Inventario de accesorios instalados en la ruta
    accesorios_ruta = {
        "codo_90_radio_largo_1.5d": 6,
        "pantalon_Y_45_ramal": 1,
        "valvula_mariposa_asiento_resiliente": 3,
        "valvula_check_columpio": 1,
        "salida_tanque_todas_las_formas": 1
    }
    
    # Transiciones de diámetro en la misma línea
    reducciones_ruta = [
        {"d_menor_mm": 77.92, "D_mayor_mm": 102.26, "cantidad": 1} # Reducción de 4" a 3"
    ]
    
    # Ejecución del algoritmo maestro
    reporte_final = calcular_perdidas_ruta_tuberias(
        fluido_densidad=densidad_fluido,
        fluido_viscosidad=viscosidad_fluido,
        caudal_m3h=caudal_operacion,
        material_clave=material,
        diametro_int_mm=diametro_interior,
        longitud_recta_m=longitud_linea_recta,
        diccionario_accesorios_estatitcos=accesorios_ruta,
        lista_reducciones=reducciones_ruta,
        lista_ampliaciones=None
    )
    
    # Despliegue del reporte detallado por consola
    print(f"Propiedades del Fluido: {densidad_fluido} kg/m3 | Viscosidad: {viscosidad_fluido} Pa·s")
    print(f"Ruta Analizada: Tubería {diametro_interior} mm en Material: {material}")
    print(f"Velocidad de paso resultante: {reporte_final['velocidad_m_s']} m/s")
    print(f"Número de Reynolds calculado: {reporte_final['reynolds']} -> ({reporte_final['regimen_flujo']})")
    print(f"Coeficiente de fricción teórica de Darcy (f): {reporte_final['factor_darcy_f']}")
    print("-" * 70)
    print("RESUMEN DE PÉRDIDAS DE ENERGÍA:")
    print(f"[-] Pérdidas por Fricción Línea Recta:  {reporte_final['perdidas_mayores_mcf']} mcf")
    print(f"[-] Pérdidas por Accesorios (Suma K={reporte_final['sumatoria_k_global']}): {reporte_final['perdidas_menores_mcf']} mcf")
    print(f"[=] PÉRDIDA TOTAL DEL SISTEMA:          {reporte_final['perdida_total_mcf']} mcf (metros columna fluido)")
    print("-" * 70)
    print("CAÍDA DE PRESIÓN REQUERIDA DE BOMBEO:")
    print(f"➡ Presión en PSI:   {reporte_final['caida_presion_psi']} psi")
    print(f"➡ Presión en BAR:   {reporte_final['caida_presion_bar']} bar")
    print(f"➡ Presión en PA:    {reporte_final['caida_presion_pa']} Pa")
    print(f"➡ POTENCIA HIDRÁULICA REQUERIDA: {reporte_final['potencia_hidraulica_hp']} HP")
    print("-" * 70)
