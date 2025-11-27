import tkinter as tk
    from tkinter import ttk, messagebox
    import geopandas as gpd
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    import urllib.request, os

    # =============================
    # ALGORITMOS DIVIDE Y VENCERÁS
    # =============================

    def encontrar_maximo_DyV(arr, inicio, fin):
        """Encuentra el máximo usando divide y vencerás"""
        if inicio == fin:
            return arr[inicio], inicio

        if fin - inicio == 1:
            if arr[inicio] > arr[fin]:
                return arr[inicio], inicio
            return arr[fin], fin

        medio = (inicio + fin) // 2
        max_izq, idx_izq = encontrar_maximo_DyV(arr, inicio, medio)
        max_der, idx_der = encontrar_maximo_DyV(arr, medio + 1, fin)

        if max_izq > max_der:
            return max_izq, idx_izq
        return max_der, idx_der

    def encontrar_minimo_DyV(arr, inicio, fin):
        """Encuentra el mínimo usando divide y vencerás"""
        if inicio == fin:
            return arr[inicio], inicio

        if fin - inicio == 1:
            if arr[inicio] < arr[fin]:
                return arr[inicio], inicio
            return arr[fin], fin

        medio = (inicio + fin) // 2
        min_izq, idx_izq = encontrar_minimo_DyV(arr, inicio, medio)
        min_der, idx_der = encontrar_minimo_DyV(arr, medio + 1, fin)

        if min_izq < min_der:
            return min_izq, idx_izq
        return min_der, idx_der

    def merge_sort_DyV(arr, indices, descendente=True):
        """Ordena usando merge sort (divide y vencerás)"""
        if len(arr) <= 1:
            return arr, indices

        medio = len(arr) // 2
        izq_arr, izq_idx = merge_sort_DyV(arr[:medio], indices[:medio], descendente)
        der_arr, der_idx = merge_sort_DyV(arr[medio:], indices[medio:], descendente)

        return merge(izq_arr, izq_idx, der_arr, der_idx, descendente)

    def merge(izq_arr, izq_idx, der_arr, der_idx, descendente):
        """Combina dos arrays ordenados"""
        resultado = []
        indices = []
        i = j = 0

        while i < len(izq_arr) and j < len(der_arr):
            if (izq_arr[i] > der_arr[j]) if descendente else (izq_arr[i] < der_arr[j]):
                resultado.append(izq_arr[i])
                indices.append(izq_idx[i])
                i += 1
            else:
                resultado.append(der_arr[j])
                indices.append(der_idx[j])
                j += 1

        resultado.extend(izq_arr[i:])
        indices.extend(izq_idx[i:])
        resultado.extend(der_arr[j:])
        indices.extend(der_idx[j:])

        return resultado, indices

    # =============================
    # DATOS REALISTAS: POBLACIÓN POR PAÍS (2023)
    # =============================

    poblacion_paises = {
        "Albania": 2746000,
        "Austria": 9027000,
        "Belarus": 9230000,
        "Belgium": 11632000,
        "Bosnia and Herz.": 3151000,
        "Bulgaria": 6808000,
        "Croatia": 3856000,
        "Czechia": 10496000,
        "Denmark": 5933000,
        "Estonia": 1331000,
        "Finland": 5541000,
        "France": 68073000,
        "Germany": 83295000,
        "Greece": 10373000,
        "Hungary": 9604000,
        "Ireland": 5123000,
        "Italy": 58851000,
        "Latvia": 1863000,
        "Lithuania": 2795000,
        "Luxembourg": 654000,
        "Moldova": 2513000,
        "Netherlands": 17767000,
        "Norway": 5466000,
        "Poland": 37551000,
        "Portugal": 10247000,
        "Romania": 19052000,
        "Russia": 144444000,
        "Serbia": 6655000,
        "Slovakia": 5422000,
        "Slovenia": 2117000,
        "Spain": 47558000,
        "Sweden": 10528000,
        "Switzerland": 8797000,
        "Ukraine": 36755000,
        "United Kingdom": 67736000,
    }

    # =============================
    # SIMULACIÓN Y CONFIGURACIÓN
    # =============================

    url = "https://github.com/nvkelso/natural-earth-vector/raw/master/geojson/ne_110m_admin_0_countries.geojson"
    geojson_path = "ne_110m_admin_0_countries.geojson"

    if not os.path.exists(geojson_path):
        print("Descargando mapa base de Europa...")
        urllib.request.urlretrieve(url, geojson_path)

    world = gpd.read_file(geojson_path)
    europa = world[world['CONTINENT'] == 'Europe']
    paises = sorted(europa['NAME'].tolist())

    # Sistemas sanitarios por país
    sistemas_sanitarios = {
        "Norway": "desarrollado", "Switzerland": "desarrollado", "Germany": "desarrollado",
        "Sweden": "desarrollado", "Netherlands": "desarrollado", "Denmark": "desarrollado",
        "Austria": "desarrollado", "Finland": "desarrollado", "Belgium": "desarrollado",
        "France": "desarrollado", "United Kingdom": "desarrollado", "Ireland": "desarrollado",
        "Luxembourg": "desarrollado",

        "Spain": "normal", "Italy": "normal", "Portugal": "normal", "Greece": "normal",
        "Czechia": "normal", "Slovenia": "normal", "Estonia": "normal", "Poland": "normal",
        "Slovakia": "normal", "Lithuania": "normal", "Latvia": "normal", "Croatia": "normal",
        "Hungary": "normal",

        "Romania": "precario", "Bulgaria": "precario", "Serbia": "precario",
        "Bosnia and Herz.": "precario", "Albania": "precario", "Moldova": "precario",
        "Ukraine": "precario", "Belarus": "precario", "Russia": "precario",
    }

    # Parámetros del modelo SIR por sistema sanitario
    PARAMS_SISTEMA = {
        "desarrollado": {
            "beta": 0.08,           # Tasa de transmisión
            "gamma": 0.00,          # Sin recuperación inicial
            "gamma_post": 0.10,     # Recuperación después del día crítico
            "mu": 0.00015,           # Tasa de mortalidad (0.15%)
            "dia_recuperacion": 235,
            "vac_inicio": 250,
            "vac_rate": 0.010,
            "umbral_contagiar": 20000,      # Necesita 15k infectados para contagiar
            "umbral_ser_contagiado": 20000, # Se infecta cuando vecino tiene 20k
        },
        "normal": {
            "beta": 0.15,           # Crecimiento moderado
            "gamma": 0.00,
            "gamma_post": 0.06,
            "mu": 0.0004,            # 0.4%
            "dia_recuperacion": 235,
            "vac_inicio": 240,
            "vac_rate": 0.007,
            "umbral_contagiar": 5000,      # Necesita 10k infectados para contagiar
            "umbral_ser_contagiado": 5000, # Se infecta cuando vecino tiene 20k
        },
        "precario": {
            "beta": 0.3,           # Más rápido
            "gamma": 0.00,
            "gamma_post": 0.05,
            "mu": 0.0008,            # 1.0%
            "dia_recuperacion": 235,
            "vac_inicio": 250,
            "vac_rate": 0.003,
            "umbral_contagiar": 1000,       # Necesita 5k infectados para contagiar
            "umbral_ser_contagiado": 1000, # Se infecta cuando vecino tiene 10k
        }
    }

    config_paises = {}
    for pais in paises:
        sistema = sistemas_sanitarios.get(pais, "normal")
        poblacion = poblacion_paises.get(pais, 5000000)
        params = PARAMS_SISTEMA[sistema]

        config_paises[pais] = {
            "sistema": sistema,
            "poblacion": poblacion,
            "beta": params["beta"],
            "gamma": params["gamma"],
            "gamma_post": params["gamma_post"],
            "mu": params["mu"],
            "dia_recuperacion": params["dia_recuperacion"],
            "vac_inicio": params["vac_inicio"],
            "vac_rate": params["vac_rate"],
            "umbral_contagiar": params["umbral_contagiar"],
            "umbral_ser_contagiado": params["umbral_ser_contagiado"],
        }

    dias = 300
    dt = 1.0  # Paso de tiempo (1 día)
    TASA_CONTAGIO_BASE = 0.90  # Aumentada de 0.04 
    INFECCION_INICIAL = 30

    # Vecinos (relaciones geográficas)
    vecinos = {
        "France": ["Spain", "Italy", "Germany", "Belgium", "Switzerland"],
        "Spain": ["France", "Portugal"],
        "Italy": ["France", "Switzerland", "Austria", "Slovenia"],
        "Germany": ["France", "Poland", "Czechia", "Austria", "Switzerland", "Belgium", "Netherlands", "Denmark"],
        "Portugal": ["Spain"],
        "United Kingdom": ["Ireland"],
        "Ireland": ["United Kingdom"],
        "Belgium": ["France", "Germany", "Netherlands"],
        "Netherlands": ["Belgium", "Germany"],
        "Poland": ["Germany", "Czechia", "Slovakia", "Ukraine", "Belarus", "Lithuania"],
        "Czechia": ["Germany", "Poland", "Slovakia", "Austria"],
        "Austria": ["Germany", "Czechia Rep.", "Slovakia", "Hungary", "Slovenia", "Italy", "Switzerland"],
        "Switzerland": ["France", "Germany", "Austria", "Italy"],
        "Greece": ["Albania", "Bulgaria"],
        "Romania": ["Hungary", "Serbia", "Bulgaria", "Ukraine", "Moldova"],
        "Hungary": ["Austria", "Slovakia", "Ukraine", "Romania", "Serbia", "Croatia", "Slovenia"],
        "Sweden": ["Norway", "Finland"],
        "Norway": ["Sweden", "Finland"],
        "Finland": ["Sweden", "Norway", "Russia"],
        "Denmark": ["Germany", "Sweden"],
        "Croatia": ["Slovenia", "Hungary", "Serbia", "Bosnia and Herz."],
        "Serbia": ["Hungary", "Romania", "Bulgaria", "Croatia", "Bosnia and Herz."],
        "Bulgaria": ["Romania", "Serbia", "Greece"],
        "Ukraine": ["Poland", "Slovakia", "Hungary", "Romania", "Moldova", "Russia", "Belarus"],
        "Belarus": ["Poland", "Lithuania", "Latvia", "Russia", "Ukraine"],
        "Lithuania": ["Poland", "Belarus", "Latvia", "Russia"],
        "Latvia": ["Lithuania", "Belarus", "Russia", "Estonia"],
        "Estonia": ["Latvia", "Russia"],
        "Slovakia": ["Poland", "Czechia", "Austria", "Hungary", "Ukraine"],
        "Slovenia": ["Italy", "Austria", "Hungary", "Croatia"],
        "Albania": ["Greece", "Serbia"],
        "Bosnia and Herz.": ["Croatia", "Serbia"],
        "Moldova": ["Romania", "Ukraine"],
        "Russia": ["Norway", "Finland", "Estonia", "Latvia", "Lithuania", "Belarus", "Ukraine"]
    }

    def iniciar_simulacion(pais_inicial):
        """
        Modelo SIRD (Susceptible-Infectado-Recuperado-Muerto) con vacunación
        y RECUPERACIÓN RETARDADA
        
        Ecuaciones diferenciales:
        dS/dt = -β*S*I/N - ν(t)
        dI/dt = β*S*I/N - γ(t)*I - μ*I
        dR/dt = γ(t)*I + ν(t)
        dD/dt = μ*I
        
        donde γ(t) = 0 si t < día_recuperación, sino γ_post
        """
        
        # Inicializar compartimentos
        datos_S = {pais: np.zeros(dias) for pais in paises}
        datos_I = {pais: np.zeros(dias) for pais in paises}
        datos_R = {pais: np.zeros(dias) for pais in paises}
        datos_D = {pais: np.zeros(dias) for pais in paises}
        datos_V = {pais: np.zeros(dias) for pais in paises}

        print(f"\n{'='*70}")
        print(f"INICIANDO SIMULACIÓN - MODELO SIRD CON UMBRALES PERSONALIZADOS")
        print(f"País inicial: {pais_inicial}")
        print(f"Población: {config_paises[pais_inicial]['poblacion']:,}")
        print(f"Sistema: {config_paises[pais_inicial]['sistema'].upper()}")
        print(f"Umbral para contagiar: {config_paises[pais_inicial]['umbral_contagiar']:,}")
        print(f"Umbral de resistencia: {config_paises[pais_inicial]['umbral_ser_contagiado']:,}")
        print(f"")
        print(f"UMBRALES POR SISTEMA:")
        print(f"🟢 Desarrollado: contagia a 15k | se infecta a 40k")
        print(f"🟡 Normal:        contagia a 10k | se infecta a 20k")
        print(f"🔴 Precario:      contagia a  5k | se infecta a 10k")
        print(f"{'='*70}\n")

        # Condiciones iniciales
        for pais in paises:
            config = config_paises[pais]
            N = config["poblacion"]
            datos_I[pais] = [0 for _ in range(dias)]
            datos_S[pais] = [N for _ in range(dias)]
            if pais == pais_inicial:
                datos_I[pais][0] = INFECCION_INICIAL
                print(datos_I[pais])
                datos_S[pais][0] = N - INFECCION_INICIAL
                print(datos_S[pais])
            
            datos_R[pais] = [0 for _ in range(dias)]
            datos_D[pais] = [0 for _ in range(dias)]
            datos_V[pais] = [0 for _ in range(dias)]

        np.random.seed()  # Semilla aleatoria - cada simulación será diferente
        paises_infectados = {pais_inicial}
        
        # Bandera para mostrar mensaje de recuperación una sola vez
        recuperacion_iniciada = False

        # Integración temporal (Método de Euler)
        for dia in range(1, dias):
            # FASE 1: Verificar contagios ANTES de actualizar ecuaciones
            nuevos_contagios = []
            
            for pais in paises:
                if pais not in paises_infectados:
                    continue
                    
                config = config_paises[pais]
                
                # Contagio a países vecinos (evaluar con datos del día anterior)
                if datos_I[pais][dia - 1] >= config["umbral_contagiar"] and pais in vecinos:
                    for vecino in vecinos[pais]:
                        if vecino in paises and vecino not in paises_infectados:
                            config_vecino = config_paises[vecino]
                            
                            # Verificar si el país vecino es vulnerable
                            if datos_I[pais][dia - 1] >= config_vecino["umbral_ser_contagiado"]:
                                # Probabilidad de contagio ajustada por sistema sanitario
                                prob_contagio = TASA_CONTAGIO_BASE
                                
                                if config_vecino["sistema"] == "desarrollado":
                                    prob_contagio *= 0.4   # 10% para desarrollados
                                elif config_vecino["sistema"] == "precario":
                                    prob_contagio *= 2.0   # 50% para precarios
                                
                                if np.random.random() < prob_contagio:
                                    nuevos_contagios.append((pais, vecino))
                                    print(pais, vecino)
            
            # Aplicar contagios (inicializar ANTES del bucle de ecuaciones)
            print(nuevos_contagios)
            for pais_origen, vecino in nuevos_contagios:
                print(vecino)
                if vecino not in paises_infectados:
                    paises_infectados.add(vecino)
                    # Inicializar el país recién infectado CON DATOS DEL DÍA 0
                    config_vecino = config_paises[vecino]
                    N_vecino = config_vecino["poblacion"]
                    datos_I[vecino][dia] = INFECCION_INICIAL
                    datos_S[vecino][dia] = N_vecino - INFECCION_INICIAL
                    datos_R[vecino][dia] = 0
                    datos_D[vecino][dia] = 0
                    datos_V[vecino][dia] = 0
                    
                    print(f"Día {dia}: {pais_origen} ({int(datos_I[pais_origen][dia-1]):,} inf.) → {vecino} "
                        f"[{config_paises[vecino]['sistema']}] (inicializado con {INFECCION_INICIAL} inf.)")
            
            # Verificar si algún país ha alcanzado su día de recuperación
            if not recuperacion_iniciada:
                for pais in paises:
                    if pais in paises_infectados:
                        config = config_paises[pais]
                        if dia >= config["dia_recuperacion"]:
                            print(f"\n{'*'*70}")
                            print(f"🏥 DÍA {dia}: ¡FASE DE RECUPERACIÓN INICIADA!")
                            print(f"Los sistemas de salud comienzan a recuperar pacientes")
                            print(f"{'*'*70}\n")
                            recuperacion_iniciada = True
                            break
            
            # FASE 2: Actualizar ecuaciones diferenciales para países PREVIAMENTE infectados
            for pais in paises:
                # Solo SALTAR países que se contagiaron HOY (ya tienen valores inicializados)
                if pais in [vecino for _, vecino in nuevos_contagios]:
                    continue
                
                # Si el país NO está infectado, saltar
                if pais not in paises_infectados:
                    continue
                config = config_paises[pais]
                N = config["poblacion"]
                
                # Estado actual
                S = max(0, min(datos_S[pais][dia - 1], N-INFECCION_INICIAL))
                I = max(INFECCION_INICIAL, datos_I[pais][dia - 1])
                R = max(0, datos_R[pais][dia - 1])
                D = max(0, datos_D[pais][dia - 1])
                V_acum = datos_V[pais][dia - 1]

                # Parámetros del modelo
                beta = config["beta"]
                mu = config["mu"]
                
                # Tasa de recuperación variable
                if dia < config["dia_recuperacion"]:
                    gamma = 0.0  # SIN RECUPERACIÓN
                else:
                    gamma = config["gamma_post"]

                # Vacunación
                vac_inicio = config["vac_inicio"]
                vac_rate = config["vac_rate"]
                
                if dia >= vac_inicio and S > 0:
                    nu = min(vac_rate * N, S)
                else:
                    nu = 0

                # Ecuaciones diferenciales del modelo SIRD
                dS = -(beta * S * I / N) - nu
                dI = (beta * S * I / N) - gamma * I - mu * I
                dR = gamma * I + nu
                dD = mu * I

                # Actualizar estados (Método de Euler)
                if dia%10 == 0:
                    print(f'Pais: {pais}, dia: {dia}, beta: {beta}, S: {S}, I: {I}, N: {N}')
                datos_S[pais][dia] = max(0, S + dS * dt)
                datos_I[pais][dia] = max(0, I + dI * dt)
                datos_R[pais][dia] = max(0, R + dR * dt)
                datos_D[pais][dia] = max(0, D + dD * dt)
                datos_V[pais][dia] = V_acum + nu

                # Contagio a países vecinos
                if pais in paises_infectados and datos_I[pais][dia] >= config["umbral_contagiar"]:
                    if pais in vecinos:
                        for vecino in vecinos[pais]:
                            if vecino in paises and vecino not in paises_infectados:
                                config_vecino = config_paises[vecino]
                                
                                # Verificar si el país vecino es vulnerable
                                if datos_I[pais][dia] >= config_vecino["umbral_ser_contagiado"]:
                                    # Probabilidad de contagio ajustada por sistema sanitario
                                    prob_contagio = TASA_CONTAGIO_BASE
                                    
                                    if config_vecino["sistema"] == "desarrollado":
                                        prob_contagio *= 0.5   # 7.5% para desarrollados (antes 1%)
                                    elif config_vecino["sistema"] == "precario":
                                        prob_contagio *= 2.0   # 30% para precarios (antes 10%)
                                    
                                    if np.random.random() < prob_contagio:
                                        paises_infectados.add(vecino)
                                        # Introducir infectados en el país vecino
                                        # CORRECCIÓN: Usar datos del día anterior para evitar conflictos
                                        S_vecino = datos_S[vecino][dia - 1] if dia > 0 else config_paises[vecino]["poblacion"]
                                        casos_importados = min(INFECCION_INICIAL, S_vecino)
                                        
                                        # Asegurar que haya al menos infectados iniciales
                                        if casos_importados < INFECCION_INICIAL:
                                            casos_importados = INFECCION_INICIAL
                                        
                                        datos_I[vecino][dia] = max(datos_I[vecino][dia], casos_importados)
                                        datos_S[vecino][dia] = max(0, datos_S[vecino][dia] - casos_importados)
                                        
                                        print(f"Día {dia}: {pais} ({int(datos_I[pais][dia]):,} inf.) → {vecino} "
                                            f"[{config_vecino['sistema']}] ({int(casos_importados)} inf. iniciales)")

        print(f"\n{'='*70}")
        print(f"SIMULACIÓN COMPLETADA")
        print(f"Total de días simulados: {dias}")
        print(f"Países infectados: {len(paises_infectados)}/{len(paises)}")
        print(f"{'='*70}\n")
        
        return datos_I, datos_D, datos_R, datos_S, datos_V

    # =============================
    # INTERFAZ PRINCIPAL
    # =============================

    class SimuladorPandemia:
        def __init__(self, root):
            self.root = root
            self.root.title("Simulador de Pandemia COVID-19 - Modelo SIRD")
            
            ancho_pantalla = root.winfo_screenwidth()
            alto_pantalla = root.winfo_screenheight()
            self.root.geometry(f"{int(ancho_pantalla*0.9)}x{int(alto_pantalla*0.9)}")
            
            self.pausado = True
            self.datos_infectados = None
            self.datos_muertes = None
            self.datos_recuperados = None
            self.datos_susceptibles = None
            self.datos_vacunados = None
            
            self.frame_principal = tk.PanedWindow(root, orient=tk.HORIZONTAL)
            self.frame_principal.pack(fill="both", expand=True, padx=10, pady=10)
            
            # ===== COLUMNA IZQUIERDA =====
            self.frame_izquierdo = tk.Frame(self.frame_principal)
            self.frame_principal.add(self.frame_izquierdo, width=450)
            
            tk.Label(self.frame_izquierdo, text="🦠 País Inicial:", font=("Arial", 12, "bold")).pack(pady=5)
            self.combo_pais = ttk.Combobox(self.frame_izquierdo, values=paises, state="readonly", font=("Arial", 11))
            self.combo_pais.set("Italy")
            self.combo_pais.pack(pady=5, padx=10, fill="x")
            
            self.boton_iniciar = tk.Button(self.frame_izquierdo, text="▶️ Iniciar Simulación", 
                                        font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
                                        command=self.iniciar_simulacion, height=2)
            self.boton_iniciar.pack(pady=10, padx=10, fill="x")
            
            # Separador
            ttk.Separator(self.frame_izquierdo, orient='horizontal').pack(fill='x', pady=10)
            
            tk.Label(self.frame_izquierdo, text="📊 Análisis (Divide y Vencerás)", 
                    font=("Arial", 12, "bold")).pack(pady=5)
            
            frame_botones_analisis = tk.Frame(self.frame_izquierdo)
            frame_botones_analisis.pack(pady=5, fill="x", padx=10)
            
            tk.Button(frame_botones_analisis, text="🔴 Mayor Infectados", 
                    command=lambda: self.analizar("max_infectados"), font=("Arial", 10)).pack(fill="x", pady=2)
            tk.Button(frame_botones_analisis, text="⚫ Mayor Muertes", 
                    command=lambda: self.analizar("max_muertes"), font=("Arial", 10)).pack(fill="x", pady=2)
            tk.Button(frame_botones_analisis, text="🟢 Mayor Recuperados", 
                    command=lambda: self.analizar("max_recuperados"), font=("Arial", 10)).pack(fill="x", pady=2)
            tk.Button(frame_botones_analisis, text="📅 Día Pico Infecciones", 
                    command=lambda: self.analizar("dia_pico"), font=("Arial", 10)).pack(fill="x", pady=2)
            tk.Button(frame_botones_analisis, text="🔽 Ordenar: Infectados", 
                    command=lambda: self.ordenar_tabla("infectados"), font=("Arial", 10)).pack(fill="x", pady=2)
            tk.Button(frame_botones_analisis, text="🔽 Ordenar: Muertes", 
                    command=lambda: self.ordenar_tabla("muertes"), font=("Arial", 10)).pack(fill="x", pady=2)
            tk.Button(frame_botones_analisis, text="🔽 Ordenar: Recuperados", 
                    command=lambda: self.ordenar_tabla("recuperados"), font=("Arial", 10)).pack(fill="x", pady=2)
            
            # Separador
            ttk.Separator(self.frame_izquierdo, orient='horizontal').pack(fill='x', pady=10)
            
            tk.Label(self.frame_izquierdo, text="📋 Datos por País", 
                    font=("Arial", 12, "bold")).pack(pady=5)
            
            style = ttk.Style()
            style.configure("Treeview", font=("Arial", 9), rowheight=22)
            style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
            
            self.tabla = ttk.Treeview(self.frame_izquierdo, 
                                    columns=("Pais", "Sistema", "I", "M", "R"), 
                                    show="headings", height=12)
            self.tabla.heading("Pais", text="País")
            self.tabla.heading("Sistema", text="Sist.")
            self.tabla.heading("I", text="Infectados")
            self.tabla.heading("M", text="Muertes")
            self.tabla.heading("R", text="Recuperados")
            self.tabla.column("Pais", width=110)
            self.tabla.column("Sistema", width=70, anchor="center")
            self.tabla.column("I", width=80, anchor="center")
            self.tabla.column("M", width=70, anchor="center")
            self.tabla.column("R", width=90, anchor="center")
            self.tabla.pack(fill="both", expand=True, pady=5, padx=10, side="left")
            
            scrollbar_tabla = ttk.Scrollbar(self.frame_izquierdo, orient="vertical", command=self.tabla.yview)
            self.tabla.configure(yscroll=scrollbar_tabla.set)
            scrollbar_tabla.pack(side="right", fill="y")
            
            # ===== COLUMNA DERECHA =====
            self.frame_derecho = tk.Frame(self.frame_principal)
            self.frame_principal.add(self.frame_derecho)
            
            self.titulo = tk.Label(self.frame_derecho, text="🗺️ Visualización Geográfica", 
                                font=("Arial", 14, "bold"))
            self.titulo.pack(pady=5)
            
            frame_controles = tk.Frame(self.frame_derecho)
            frame_controles.pack(pady=5)
            
            tk.Button(frame_controles, text="🔴 Infectados", width=13, 
                    command=lambda: self.cambiar_mapa("infectados"), font=("Arial", 10)).pack(side="left", padx=3)
            tk.Button(frame_controles, text="⚫ Muertes", width=13, 
                    command=lambda: self.cambiar_mapa("muertes"), font=("Arial", 10)).pack(side="left", padx=3)
            tk.Button(frame_controles, text="🟢 Recuperados", width=13,
                    command=lambda: self.cambiar_mapa("recuperados"), font=("Arial", 10)).pack(side="left", padx=3)
            tk.Button(frame_controles, text="🔵 Susceptibles", width=13,
                    command=lambda: self.cambiar_mapa("susceptibles"), font=("Arial", 10)).pack(side="left", padx=3)
            self.boton_pausa = tk.Button(frame_controles, text="▶️ Play", width=13, 
                                        command=self.toggle_pausa, font=("Arial", 10))
            self.boton_pausa.pack(side="left", padx=3)
            
            self.fig, self.ax = plt.subplots(figsize=(10, 7))
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_derecho)
            self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)
            
            self.dia_actual = tk.IntVar(value=0)
            self.slider = ttk.Scale(self.frame_derecho, from_=0, to=dias-1, 
                                orient="horizontal", variable=self.dia_actual,
                                command=self.actualizar_dia)
            self.slider.pack(fill="x", padx=20, pady=5)
            
            self.label_dia = tk.Label(self.frame_derecho, text="Día: 0 / 300", font=("Arial", 11, "bold"))
            self.label_dia.pack(pady=5)
            
            self.tipo_mapa = "infectados"
            self.dia_simulacion = 0
            self.colorbar = None
            
            self.mostrar_mensaje_inicial()
        
        def mostrar_mensaje_inicial(self):
            self.ax.clear()
            self.ax.text(0.5, 0.5, "Selecciona un país inicial\ny presiona 'Iniciar Simulación'", 
                        ha='center', va='center', fontsize=16, transform=self.ax.transAxes)
            self.ax.axis('off')
            self.canvas.draw()
        
        def iniciar_simulacion(self):
            pais_inicial = self.combo_pais.get()
            if not pais_inicial:
                messagebox.showwarning("Advertencia", "Selecciona un país inicial")
                return
            
            self.boton_iniciar.config(state="disabled", text="⏳ Calculando...")
            self.root.update()
            
            self.datos_infectados, self.datos_muertes, self.datos_recuperados, \
            self.datos_susceptibles, self.datos_vacunados = iniciar_simulacion(pais_inicial)
            
            self.dia_simulacion = 0
            self.slider.set(0)
            self.pausado = False
            self.boton_pausa.config(text="⏸️ Pausar")
            self.boton_iniciar.config(state="normal", text="▶️ Iniciar Simulación")
            
            self.actualizar_mapa(inicial=True)
            self.simular_tiempo()
            
            config = config_paises[pais_inicial]
            messagebox.showinfo("✅ Simulación Iniciada", 
                            f"País de origen: {pais_inicial}\n"
                            f"Sistema: {config['sistema'].capitalize()}\n"
                            f"Población: {config['poblacion']:,}\n\n"
                            f"UMBRALES:\n"
                            f"Contagia a vecinos: {config['umbral_contagiar']:,} infectados\n"
                            f"Se infecta cuando vecino tiene: {config['umbral_ser_contagiado']:,}")
        
        def analizar(self, tipo):
            if self.datos_infectados is None:
                messagebox.showwarning("Advertencia", "Inicia la simulación primero")
                return
            
            if tipo == "max_infectados":
                valores = [max(self.datos_infectados[p]) for p in paises]
                max_val, idx = encontrar_maximo_DyV(valores, 0, len(valores)-1)
                pais = paises[idx]
                pct = (max_val / config_paises[pais]["poblacion"]) * 100
                messagebox.showinfo("📊 Análisis - Máximo", 
                    f"País con MAYOR pico de infectados:\n\n"
                    f"🔴 {pais}\n"
                    f"Infectados pico: {int(max_val):,}\n"
                    f"Porcentaje población: {pct:.2f}%\n"
                    f"Sistema: {config_paises[pais]['sistema'].capitalize()}")
            
            elif tipo == "max_muertes":
                valores = [max(self.datos_muertes[p]) for p in paises]
                max_val, idx = encontrar_maximo_DyV(valores, 0, len(valores)-1)
                pais = paises[idx]
                messagebox.showinfo("⚫ Análisis - Máximo", 
                    f"País con MÁS muertes acumuladas:\n\n"
                    f"⚫ {pais}\n"
                    f"Muertes: {int(max_val):,}\n"
                    f"Letalidad: {(max_val/max(self.datos_infectados[pais]))*100:.2f}%")
            
            elif tipo == "max_recuperados":
                valores = [max(self.datos_recuperados[p]) for p in paises]
                max_val, idx = encontrar_maximo_DyV(valores, 0, len(valores)-1)
                pais = paises[idx]
                messagebox.showinfo("🟢 Análisis - Máximo", 
                    f"País con MÁS recuperados:\n\n"
                    f"🟢 {pais}\n"
                    f"Recuperados: {int(max_val):,}")
            
            elif tipo == "dia_pico":
                infectados_diarios = [sum(self.datos_infectados[p][d] for p in paises) for d in range(dias)]
                max_val, dia = encontrar_maximo_DyV(infectados_diarios, 0, len(infectados_diarios)-1)
                messagebox.showinfo("📅 Análisis - Día Pico", 
                    f"Día con MÁS infectados activos en toda Europa:\n\n"
                    f"📅 Día {dia+1}\n"
                    f"Total infectados: {int(max_val):,}\n"
                    f"Fecha aprox: {dia+1} días después del brote inicial")
        
        def ordenar_tabla(self, criterio):
            if self.datos_infectados is None:
                return
            
            if criterio == "infectados":
                valores = [self.datos_infectados[p][self.dia_simulacion] for p in paises]
            elif criterio == "muertes":
                valores = [self.datos_muertes[p][self.dia_simulacion] for p in paises]
            elif criterio == "recuperados":
                valores = [self.datos_recuperados[p][self.dia_simulacion] for p in paises]
            
            indices = list(range(len(paises)))
            valores_ordenados, indices_ordenados = merge_sort_DyV(valores.copy(), indices, descendente=True)
            
            for i in self.tabla.get_children():
                self.tabla.delete(i)
            
            total_inf = total_mue = total_rec = 0
            for idx in indices_ordenados:
                pais = paises[idx]
                sistema = config_paises[pais]["sistema"]
                emoji = "🟢" if sistema == "desarrollado" else ("🟡" if sistema == "normal" else "🔴")
                inf = int(self.datos_infectados[pais][self.dia_simulacion])
                mue = int(self.datos_muertes[pais][self.dia_simulacion])
                rec = int(self.datos_recuperados[pais][self.dia_simulacion])
                self.tabla.insert("", "end", values=(pais, emoji, inf, mue, rec))
                total_inf += inf
                total_mue += mue
                total_rec += rec
            
            self.tabla.insert("", "end", values=("═══ TOTAL ═══", "", total_inf, total_mue, total_rec))
        
        def cambiar_mapa(self, tipo):
            if self.datos_infectados is None:
                return
            self.tipo_mapa = tipo
            self.actualizar_mapa(inicial=True)
        
        def toggle_pausa(self):
            if self.datos_infectados is None:
                return
            self.pausado = not self.pausado
            self.boton_pausa.config(text="▶️ Play" if self.pausado else "⏸️ Pausar")
        
        def actualizar_dia(self, _=None):
            if self.datos_infectados is None:
                return
            self.dia_simulacion = int(self.dia_actual.get())
            self.actualizar_mapa()
        
        def actualizar_mapa(self, inicial=False):
            if self.datos_infectados is None:
                return

            if self.tipo_mapa == "infectados":
                valores_dict = {pais: self.datos_infectados[pais][self.dia_simulacion] for pais in paises}
                vmax = max(config_paises[p]["poblacion"] * 0.05 for p in paises)
                color = "Reds"
                titulo = "Infectados Activos"
            elif self.tipo_mapa == "muertes":
                valores_dict = {pais: self.datos_muertes[pais][self.dia_simulacion] for pais in paises}
                vmax = max(config_paises[p]["poblacion"] * 0.003 for p in paises)
                color = "Greys"
                titulo = "Muertes Acumuladas"
            elif self.tipo_mapa == "recuperados":
                valores_dict = {pais: self.datos_recuperados[pais][self.dia_simulacion] for pais in paises}
                vmax = max(config_paises[p]["poblacion"] * 0.15 for p in paises)
                color = "Greens"
                titulo = "Recuperados"
            elif self.tipo_mapa == "susceptibles":
                valores_dict = {pais: self.datos_susceptibles[pais][self.dia_simulacion] for pais in paises}
                vmax = max(config_paises[p]["poblacion"] for p in paises)
                color = "Blues"
                titulo = "Susceptibles"

            europa_plot = europa.copy()
            europa_plot["valor"] = europa_plot['NAME'].map(valores_dict).fillna(0)

            self.ax.clear()
            europa_plot.plot(column="valor", cmap=color, linewidth=0.8, ax=self.ax,
                            edgecolor="black", legend=False, vmin=0, vmax=vmax)

            self.ax.set_xlim(-25, 60)
            self.ax.set_ylim(34, 72)
            self.ax.set_title(f"{titulo} - Día {self.dia_simulacion + 1}", fontsize=14, fontweight='bold')
            self.ax.axis("off")

            if inicial:
                if self.colorbar:
                    self.colorbar.remove()
                norm = plt.Normalize(vmin=0, vmax=vmax)
                sm = plt.cm.ScalarMappable(cmap=color, norm=norm)
                sm._A = []
                self.colorbar = self.fig.colorbar(sm, ax=self.ax, fraction=0.03, pad=0.04)

            self.canvas.draw()
            self.label_dia.config(text=f"Día: {self.dia_simulacion + 1} / {dias}")

            # Actualizar tabla
            for i in self.tabla.get_children():
                self.tabla.delete(i)

            total_inf = total_mue = total_rec = 0
            paises_mostrados = 0
            for pais in paises:
                sistema = config_paises[pais]["sistema"]
                emoji = "🟢" if sistema == "desarrollado" else ("🟡" if sistema == "normal" else "🔴")
                inf = int(self.datos_infectados[pais][self.dia_simulacion])
                mue = int(self.datos_muertes[pais][self.dia_simulacion])
                rec = int(self.datos_recuperados[pais][self.dia_simulacion])
                
                # Mostrar TODOS los países (no solo con casos activos)
                if inf > 0 or mue > 0 or rec > 0:
                    self.tabla.insert("", "end", values=(pais, emoji, inf, mue, rec))
                    total_inf += inf
                    total_mue += mue
                    total_rec += rec
                    paises_mostrados += 1
                    
                    # DEBUG: Imprimir en consola países con infectados
                    if inf > 0 and self.dia_simulacion % 10 == 0:
                        print(f"DEBUG Día {self.dia_simulacion}: {pais} tiene {inf} infectados")

            self.tabla.insert("", "end", values=(f"═══ TOTAL ({paises_mostrados} países) ═══", "", total_inf, total_mue, total_rec))

        def simular_tiempo(self):
            if self.datos_infectados is None:
                return
            
            if not self.pausado:
                self.dia_simulacion = (self.dia_simulacion + 1) % dias
                self.slider.set(self.dia_simulacion)
                self.actualizar_mapa()
                
                # Mostrar alerta cuando inicie la recuperación
                if self.dia_simulacion >= 235 and self.dia_simulacion <= 250:
                    if self.dia_simulacion == 235:
                        self.titulo.config(text="🏥 ¡FASE DE RECUPERACIÓN INICIADA! 🏥", fg="green")
                    elif self.dia_simulacion == 250:
                        self.titulo.config(text="🗺️ Visualización Geográfica", fg="black")
            
            if self.datos_infectados is not None:
                self.root.after(150, self.simular_tiempo)

    if __name__ == "__main__":
        root = tk.Tk()
        app = SimuladorPandemia(root)
        root.mainloop()
