# Simulación Epidemiológica con Paradigmas Algorítmicos

## Descripción General
Este proyecto implementa una simulación epidemiológica basada en el modelo SIRD (Susceptibles-Infectados-Recuperados-Defunciones) para analizar la propagación de enfermedades en una red de países interconectados. El programa contrasta diferentes paradigmas algorítmicos fundamentales aplicados a problemas computacionales relevantes en el contexto de sistemas complejos.

La simulación no solo modela dinámicas biológicas, sino que sirve como caso de estudio para comprender las implicaciones prácticas de la teoría de algoritmos en problemas con impacto real. Cada paradigma implementado revela tensiones fundamentales entre eficiencia computacional, claridad conceptual y aplicabilidad práctica.

## Funcionalidades Principales
🧮 Simulación Epidemiológica SIRD
Modelo matemático: Implementación del sistema de ecuaciones diferenciales:

Red de países: Simulación de contagio entre países vecinos con probabilidades estocásticas
Visualización: Generación de gráficos temporales para cada compartimento epidemiológico
⚡ Paradigmas Algorítmicos Implementados
1. Divide y Vencerás
Búsqueda de extremos: Algoritmo recursivo para encontrar máximo/mínimo en O(n)
Ordenamiento Merge Sort: Implementación completa con complejidad O(n log n)
Aplicación práctica: Ordenamiento de países por métricas epidemiológicas (infectados, recuperados, etc.)
2. Fuerza Bruta
Simulación SIRD: Enfoque iterativo día por día sin optimizaciones
Búsqueda de vecinos: Exploración exhaustiva de conexiones entre países
Característica clave: Transparencia y facilidad de validación sobre eficiencia
3. Análisis de Programación Dinámica
Estudio teórico: Explicación detallada de por qué PD no aplica al problema actual
Condiciones necesarias: Identificación de subproblemas superpuestos y estructura óptima
Conexión conceptual: Relación entre memoria computacional y memoria inmunológica en epidemiología
Requisitos
bash
1
pip install -r requirements.txt
requirements.txt:

```
numpy>=1.21.0
matplotlib>=3.4.0
networkx>=2.6.0
python>=3.8
```
Estructura del Código
```
proyecto/
├── simulacion_sird.py        # Módulo principal de simulación
├── algoritmos.py            # Implementaciones de paradigmas algorítmicos
├── visualizacion.py         # Generación de gráficos y resultados
├── utils.py                 # Funciones auxiliares y inicialización de datos
└── main.py                  # Punto de entrada del programa
```
Cómo Ejecutar
bash
```
# Clonar el repositorio
git clone https://github.com/tu-usuario/simulacion-epidemiologica.git
cd simulacion-epidemiologica

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar simulación (ejemplo: 30 días, país inicial 0)
python main.py
```

Dentro del programa seleccionas un pais del dropdown select

<img width="1920" height="1076" alt="GUI2" src="https://github.com/user-attachments/assets/11491a53-85a1-4da6-b70c-e63d535535d9" />

Y deja que el virus se esparza!!

El programa genera:

Gráficos temporales para cada compartimento SIRD en todos los países
Métricas de rendimiento comparando los diferentes paradigmas algorítmicos
Estadísticas finales mostrando el impacto total de la simulación
Análisis de complejidad con tiempos de ejecución y uso de memoria
Conexión Teórica-Práctica
Este proyecto ejemplifica cómo los paradigmas algorítmicos abstractos se manifiestan en problemas concretos:

Divide y Vencerás ↔ Estrategias de contención epidemiológica (dividir y aislar regiones)
Fuerza Bruta ↔ Monitoreo exhaustivo de contactos en epidemiología de campo
Ausencia de Programación Dinámica ↔ Adaptación inmunológica (la memoria biológica no repite cálculos idénticos)
