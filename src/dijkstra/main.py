import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import math
import time
import random
import threading
from collections import defaultdict
import json

class DijkstraVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Visualizador de Dijkstra con Fuerza Bruta")
        self.root.geometry("1200x800")
        
        # Variables del grafo
        self.vertices = {}  # {id: {'x': x, 'y': y, 'property': value}}
        self.edges = defaultdict(list)  # {vertex_id: [(neighbor_id, weight), ...]}
        self.vertex_counter = 0
        
        # Variables de visualización
        self.canvas_width = 800
        self.canvas_height = 600
        self.vertex_radius = 20
        self.selected_vertex = None
        self.creating_edge = False
        self.edge_start = None
        
        # Variables del algoritmo
        self.algorithm_running = False
        self.animation_speed = 1.0
        self.current_distances = {}
        self.visited_vertices = set()
        self.current_vertex = None
        self.target_property = None
        self.found_vertices = []
        self.algorithm_thread = None
        
        # Propiedades disponibles
        self.properties = ["Rojo", "Azul", "Verde", "Amarillo", "Morado", "Naranja"]
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame izquierdo para controles
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Controles de velocidad
        speed_frame = ttk.LabelFrame(control_frame, text="Velocidad de Animación")
        speed_frame.pack(fill=tk.X, pady=5)
        
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(speed_frame, from_=0.1, to=5.0, variable=self.speed_var,
                               orient=tk.HORIZONTAL, command=self.update_speed)
        speed_scale.pack(fill=tk.X, padx=5, pady=5)
        
        self.speed_label = ttk.Label(speed_frame, text="Velocidad: 1.0x")
        self.speed_label.pack()
        
        # Controles de vértices
        vertex_frame = ttk.LabelFrame(control_frame, text="Gestión de Vértices")
        vertex_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(vertex_frame, text="Agregar Vértice", 
                  command=self.add_vertex_mode).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(vertex_frame, text="Crear Arista", 
                  command=self.create_edge_mode).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(vertex_frame, text="Eliminar Seleccionado", 
                  command=self.delete_selected).pack(fill=tk.X, padx=5, pady=2)
        
        # Control de propiedades
        property_frame = ttk.LabelFrame(control_frame, text="Búsqueda por Propiedad")
        property_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(property_frame, text="Buscar vértices con:").pack()
        self.property_var = tk.StringVar()
        property_combo = ttk.Combobox(property_frame, textvariable=self.property_var,
                                     values=self.properties, state="readonly")
        property_combo.pack(fill=tk.X, padx=5, pady=2)
        property_combo.set(self.properties[0])
        
        ttk.Button(property_frame, text="Asignar Propiedades Aleatorias",
                  command=self.assign_random_properties).pack(fill=tk.X, padx=5, pady=2)
        
        # Controles del algoritmo
        algo_frame = ttk.LabelFrame(control_frame, text="Algoritmo de Dijkstra")
        algo_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(algo_frame, text="Vértice inicial:").pack()
        self.start_var = tk.StringVar()
        self.start_combo = ttk.Combobox(algo_frame, textvariable=self.start_var,
                                       state="readonly")
        self.start_combo.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(algo_frame, text="Iniciar Búsqueda (Fuerza Bruta)",
                  command=self.start_dijkstra).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(algo_frame, text="Detener Algoritmo",
                  command=self.stop_algorithm).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(algo_frame, text="Reiniciar",
                  command=self.reset_algorithm).pack(fill=tk.X, padx=5, pady=2)
        
        # Controles de archivo
        file_frame = ttk.LabelFrame(control_frame, text="Archivo")
        file_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(file_frame, text="Cargar desde TXT",
                  command=self.load_from_file).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(file_frame, text="Guardar Grafo",
                  command=self.save_to_file).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(file_frame, text="Limpiar Todo",
                  command=self.clear_all).pack(fill=tk.X, padx=5, pady=2)
        
        # Información
        info_frame = ttk.LabelFrame(control_frame, text="Información")
        info_frame.pack(fill=tk.X, pady=5)
        
        self.info_text = tk.Text(info_frame, height=8, width=30, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5, padx=(0, 5))
        
        # Canvas para el grafo
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, width=self.canvas_width, 
                               height=self.canvas_height, bg="white", bd=2, relief=tk.SUNKEN)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Eventos del canvas
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        
        # Inicializar
        self.update_vertex_list()
        self.log_info("Aplicación iniciada. Agregue vértices haciendo clic en 'Agregar Vértice'.")
        
    def update_speed(self, value):
        self.animation_speed = float(value)
        self.speed_label.config(text=f"Velocidad: {self.animation_speed:.1f}x")
        
    def add_vertex_mode(self):
        if not self.algorithm_running:
            self.log_info("Modo: Agregar vértice. Haga clic en el canvas para agregar un vértice.")
            self.creating_edge = False
            self.canvas.configure(cursor="crosshair")
            
    def create_edge_mode(self):
        if not self.algorithm_running:
            self.log_info("Modo: Crear arista. Seleccione dos vértices para conectarlos.")
            self.creating_edge = True
            self.edge_start = None
            self.canvas.configure(cursor="hand2")
            
    def on_canvas_click(self, event):
        if self.algorithm_running:
            return
            
        if not self.creating_edge:
            # Agregar nuevo vértice
            self.add_vertex(event.x, event.y)
        else:
            # Crear arista entre vértices
            vertex_id = self.get_vertex_at_position(event.x, event.y)
            if vertex_id is not None:
                if self.edge_start is None:
                    self.edge_start = vertex_id
                    self.log_info(f"Vértice inicial seleccionado: {vertex_id}")
                elif self.edge_start != vertex_id:
                    self.create_edge(self.edge_start, vertex_id)
                    self.edge_start = None
                else:
                    self.log_info("No se puede crear una arista con el mismo vértice.")
                    
    def on_canvas_motion(self, event):
        vertex_id = self.get_vertex_at_position(event.x, event.y)
        if vertex_id is not None:
            self.canvas.configure(cursor="hand1" if self.creating_edge else "crosshair")
        else:
            self.canvas.configure(cursor="hand2" if self.creating_edge else "crosshair")
            
    def add_vertex(self, x, y):
        vertex_id = self.vertex_counter
        self.vertices[vertex_id] = {
            'x': x, 'y': y, 
            'property': random.choice(self.properties)
        }
        self.vertex_counter += 1
        self.draw_graph()
        self.update_vertex_list()
        self.log_info(f"Vértice {vertex_id} agregado en ({x}, {y}) con propiedad '{self.vertices[vertex_id]['property']}'")
        
    def create_edge(self, v1, v2):
        # Solicitar peso de la arista
        weight = tk.simpledialog.askfloat("Peso de la Arista", 
                                         f"Ingrese el peso de la arista entre {v1} y {v2}:",
                                         minvalue=0.1, maxvalue=1000.0)
        if weight is not None:
            self.edges[v1].append((v2, weight))
            self.edges[v2].append((v1, weight))  # Grafo no dirigido
            self.draw_graph()
            self.log_info(f"Arista creada entre {v1} y {v2} con peso {weight}")
            
    def get_vertex_at_position(self, x, y):
        for vertex_id, vertex in self.vertices.items():
            dx = x - vertex['x']
            dy = y - vertex['y']
            if math.sqrt(dx*dx + dy*dy) <= self.vertex_radius:
                return vertex_id
        return None
        
    def delete_selected(self):
        if self.selected_vertex is not None:
            # Eliminar aristas conectadas
            if self.selected_vertex in self.edges:
                for neighbor, _ in self.edges[self.selected_vertex]:
                    self.edges[neighbor] = [(v, w) for v, w in self.edges[neighbor] 
                                          if v != self.selected_vertex]
                del self.edges[self.selected_vertex]
            
            # Eliminar vértice
            del self.vertices[self.selected_vertex]
            self.selected_vertex = None
            self.draw_graph()
            self.update_vertex_list()
            self.log_info(f"Vértice eliminado")
            
    def assign_random_properties(self):
        for vertex_id in self.vertices:
            self.vertices[vertex_id]['property'] = random.choice(self.properties)
        self.draw_graph()
        self.log_info("Propiedades aleatorias asignadas a todos los vértices")
        
    def update_vertex_list(self):
        vertex_ids = [str(v) for v in self.vertices.keys()]
        self.start_combo['values'] = vertex_ids
        if vertex_ids and not self.start_var.get():
            self.start_combo.set(vertex_ids[0])
            
    def draw_graph(self):
        self.canvas.delete("all")
        
        # Dibujar aristas
        for vertex_id, neighbors in self.edges.items():
            if vertex_id in self.vertices:
                x1, y1 = self.vertices[vertex_id]['x'], self.vertices[vertex_id]['y']
                for neighbor_id, weight in neighbors:
                    if neighbor_id in self.vertices and neighbor_id > vertex_id:  # Evitar duplicados
                        x2, y2 = self.vertices[neighbor_id]['x'], self.vertices[neighbor_id]['y']
                        
                        # Color de la arista
                        color = "black"
                        width = 1
                        if (self.current_vertex == vertex_id and neighbor_id in [n[0] for n in neighbors]) or \
                           (self.current_vertex == neighbor_id and vertex_id in [n[0] for n in self.edges.get(neighbor_id, [])]):
                            color = "red"
                            width = 3
                            
                        self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)
                        
                        # Etiqueta del peso
                        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                        self.canvas.create_text(mid_x, mid_y, text=str(weight), 
                                              fill="blue", font=("Arial", 9))
        
        # Dibujar vértices
        for vertex_id, vertex in self.vertices.items():
            x, y = vertex['x'], vertex['y']
            
            # Color del vértice
            if vertex_id in self.found_vertices:
                color = "gold"
            elif vertex_id == self.current_vertex:
                color = "red"
            elif vertex_id in self.visited_vertices:
                color = "lightblue"
            else:
                color = "lightgray"
                
            # Borde especial si tiene la propiedad buscada
            outline = "black"
            width = 2
            if (self.target_property and 
                vertex['property'] == self.target_property):
                outline = "green"
                width = 4
                
            self.canvas.create_oval(x - self.vertex_radius, y - self.vertex_radius,
                                  x + self.vertex_radius, y + self.vertex_radius,
                                  fill=color, outline=outline, width=width)
            
            # ID del vértice
            self.canvas.create_text(x, y - 8, text=str(vertex_id), 
                                  font=("Arial", 10, "bold"))
            
            # Propiedad del vértice
            self.canvas.create_text(x, y + 8, text=vertex['property'], 
                                  font=("Arial", 8))
            
            # Distancia (si está calculándose)
            if vertex_id in self.current_distances:
                dist_text = "∞" if self.current_distances[vertex_id] == float('inf') else str(round(self.current_distances[vertex_id], 1))
                self.canvas.create_text(x, y + 25, text=f"d:{dist_text}", 
                                      font=("Arial", 8), fill="purple")
                
    def start_dijkstra(self):
        if self.algorithm_running:
            return
            
        start_vertex_str = self.start_var.get()
        if not start_vertex_str:
            messagebox.showerror("Error", "Seleccione un vértice inicial")
            return
            
        try:
            start_vertex = int(start_vertex_str)
        except ValueError:
            messagebox.showerror("Error", "Vértice inicial debe ser un número")
            return
            
        if start_vertex not in self.vertices:
            messagebox.showerror("Error", "Vértice inicial no existe en el grafo")
            return
            
        self.target_property = self.property_var.get()
        if not self.target_property:
            messagebox.showerror("Error", "Seleccione una propiedad a buscar")
            return
            
        # Limpiar estado anterior
        self.reset_algorithm()
        
        # Limpiar log anterior
        self.info_text.delete(1.0, tk.END)
        
        self.algorithm_running = True
        
        # Ejecutar algoritmo usando after() en lugar de threading
        self.root.after(100, lambda: self.dijkstra_bruteforce(start_vertex))
        
    def stop_algorithm(self):
        """Detener el algoritmo en ejecución"""
        if self.algorithm_running:
            self.algorithm_running = False
            self.current_vertex = None
            self.log_info("🛑 Algoritmo detenido por el usuario")
            self.draw_graph()
        
    def dijkstra_bruteforce(self, start_vertex):
        """Implementación de Dijkstra con fuerza bruta para encontrar vértices con una propiedad específica"""
        
        if not self.algorithm_running:
            return
            
        # Inicializar en el primer paso
        if not hasattr(self, '_algo_initialized') or not self._algo_initialized:
            # Inicializar distancias
            self.current_distances = {v: float('inf') for v in self.vertices}
            self.current_distances[start_vertex] = 0
            
            self.visited_vertices = set()
            self.found_vertices = []
            self.unvisited = set(self.vertices.keys())
            self.step = 1
            self._algo_initialized = True
            
            self.log_info(f"🚀 Iniciando búsqueda desde vértice {start_vertex}")
            self.log_info(f"🎯 Buscando vértices con propiedad: '{self.target_property}'")
            
            # Mostrar estado inicial
            total_vertices = len(self.vertices)
            vertices_with_property = sum(1 for v in self.vertices.values() if v['property'] == self.target_property)
            self.log_info(f"📊 Total de vértices: {total_vertices}")
            self.log_info(f"📊 Vértices con propiedad '{self.target_property}': {vertices_with_property}")
            self.log_info("-" * 50)
            
            self.draw_graph()
            self.root.after(int(1000 / self.animation_speed), self.dijkstra_step)
            return
            
        self.dijkstra_step()
    
    def dijkstra_step(self):
        """Un paso del algoritmo de Dijkstra"""
        if not self.algorithm_running or not self.unvisited:
            self.finish_algorithm()
            return
            
        self.log_info(f"\n🔄 === PASO {self.step} ===")
        
        # Fuerza bruta: revisar TODOS los vértices no visitados
        self.log_info("🔍 Búsqueda por fuerza bruta del vértice con menor distancia...")
        
        current_vertex = None
        min_distance = float('inf')
        
        # Mostrar el proceso de búsqueda por fuerza bruta
        self.brute_force_index = 0
        self.brute_force_vertices = sorted(list(self.unvisited))
        self.brute_force_current = None
        self.brute_force_min = None
        
        self.brute_force_step(current_vertex, min_distance)
        
    def brute_force_step(self, current_best, min_dist):
        """Un paso de la búsqueda por fuerza bruta"""
        if not self.algorithm_running:
            return
            
        if self.brute_force_index < len(self.brute_force_vertices):
            vertex = self.brute_force_vertices[self.brute_force_index]
            distance = self.current_distances[vertex]
            property_name = self.vertices[vertex]['property']
            
            # Resaltar el vértice actual en la búsqueda
            self.current_vertex = vertex
            self.draw_graph()
            
            dist_text = "∞" if distance == float('inf') else str(round(distance, 1))
            self.log_info(f"  🔸 Revisando vértice {vertex}: distancia = {dist_text}, propiedad = '{property_name}'")
            
            if distance < min_dist:
                min_dist = distance
                current_best = vertex
                self.brute_force_min = vertex
                self.log_info(f"    ✅ Nuevo mínimo encontrado!")
            else:
                self.log_info(f"    ❌ No es menor que el mínimo actual")
                
            self.brute_force_index += 1
            self.root.after(int(800 / self.animation_speed), 
                          lambda: self.brute_force_step(current_best, min_dist))
        else:
            # Terminar búsqueda por fuerza bruta
            self.continue_dijkstra_step(current_best, min_dist)
    
    def continue_dijkstra_step(self, current_vertex, min_distance):
        """Continuar con el paso de Dijkstra después de la búsqueda por fuerza bruta"""
        if not self.algorithm_running:
            return
            
        if current_vertex is None or min_distance == float('inf'):
            self.log_info("⚠️ No hay más vértices alcanzables. Terminando algoritmo.")
            self.finish_algorithm()
            return
            
        # Marcar como visitado
        self.visited_vertices.add(current_vertex)
        self.unvisited.remove(current_vertex)
        self.current_vertex = current_vertex
        
        dist_text = "∞" if min_distance == float('inf') else str(round(min_distance, 1))
        self.log_info(f"\n🎯 Vértice seleccionado: {current_vertex} (distancia: {dist_text})")
        
        # Verificar si tiene la propiedad buscada
        vertex_property = self.vertices[current_vertex]['property']
        if vertex_property == self.target_property:
            self.found_vertices.append(current_vertex)
            self.log_info(f"🎉 ¡ENCONTRADO! Vértice {current_vertex} tiene la propiedad '{self.target_property}'")
        else:
            self.log_info(f"🔍 Vértice {current_vertex} tiene propiedad '{vertex_property}' (buscamos '{self.target_property}')")
            
        self.draw_graph()
        self.root.after(int(1500 / self.animation_speed), self.relax_edges)
        
    def relax_edges(self):
        """Relajar las aristas del vértice actual"""
        if not self.algorithm_running:
            return
            
        current_vertex = self.current_vertex
        
        if current_vertex in self.edges:
            self.log_info(f"📏 Actualizando distancias desde vértice {current_vertex}:")
            
            edges_to_process = [(neighbor, weight) for neighbor, weight in self.edges[current_vertex] 
                              if neighbor not in self.visited_vertices]
            
            if edges_to_process:
                self.edge_index = 0
                self.edges_to_relax = edges_to_process
                self.relax_next_edge()
            else:
                self.log_info("  ℹ️ No hay vecinos sin visitar para actualizar")
                self.finish_step()
        else:
            self.log_info(f"  ℹ️ Vértice {current_vertex} no tiene aristas")
            self.finish_step()
            
    def relax_next_edge(self):
        """Relajar la siguiente arista"""
        if not self.algorithm_running or self.edge_index >= len(self.edges_to_relax):
            self.finish_step()
            return
            
        neighbor, weight = self.edges_to_relax[self.edge_index]
        current_vertex = self.current_vertex
        
        new_distance = self.current_distances[current_vertex] + weight
        old_distance = self.current_distances[neighbor]
        
        old_text = "∞" if old_distance == float('inf') else str(round(old_distance, 1))
        new_text = str(round(new_distance, 1))
        
        if new_distance < old_distance:
            self.current_distances[neighbor] = new_distance
            self.log_info(f"  ✅ Vértice {neighbor}: {old_text} → {new_text} (mejora)")
        else:
            self.log_info(f"  ❌ Vértice {neighbor}: {new_text} ≥ {old_text} (no mejora)")
            
        self.draw_graph()
        self.edge_index += 1
        self.root.after(int(1000 / self.animation_speed), self.relax_next_edge)
        
    def finish_step(self):
        """Terminar el paso actual y continuar"""
        if not self.algorithm_running:
            return
            
        self.step += 1
        self.current_vertex = None
        self.draw_graph()
        
        remaining = len(self.unvisited)
        found_so_far = len(self.found_vertices)
        self.log_info(f"📈 Progreso: {found_so_far} encontrados, {remaining} vértices restantes")
        
        # Continuar con el siguiente paso
        self.root.after(int(1500 / self.animation_speed), self.dijkstra_step)
        
    def finish_algorithm(self):
        """Finalizar el algoritmo y mostrar resultados"""
        self.current_vertex = None
        self.algorithm_running = False
        self._algo_initialized = False
        
        # Mostrar resultados finales
        self.log_info("\n" + "="*50)
        if self.found_vertices:
            self.log_info(f"🎉 ¡BÚSQUEDA COMPLETADA!")
            self.log_info(f"🎯 Vértices encontrados con propiedad '{self.target_property}': {len(self.found_vertices)}")
            for vertex in self.found_vertices:
                distance = self.current_distances[vertex]
                dist_text = "∞" if distance == float('inf') else str(round(distance, 1))
                self.log_info(f"   • Vértice {vertex}: distancia {dist_text}")
        else:
            self.log_info(f"❌ Búsqueda completada")
            self.log_info(f"🔍 No se encontraron vértices con propiedad '{self.target_property}'")
            
        visited_count = len(self.visited_vertices)
        total_count = len(self.vertices)
        self.log_info(f"📊 Vértices visitados: {visited_count}/{total_count}")
        self.log_info(f"📊 Vértices visitados: {sorted(list(self.visited_vertices))}")
        
        self.draw_graph()
        
    def reset_algorithm(self):
        self.algorithm_running = False
        self.current_distances = {}
        self.visited_vertices = set()
        self.current_vertex = None
        self.found_vertices = []
        if hasattr(self, 'algorithm_thread') and self.algorithm_thread and self.algorithm_thread.is_alive():
            self.algorithm_thread.join(timeout=1.0)
        self.draw_graph()
        
    def clear_all(self):
        self.vertices = {}
        self.edges = defaultdict(list)
        self.vertex_counter = 0
        self.reset_algorithm()
        self.update_vertex_list()
        self.log_info("Grafo limpiado")
        
    def load_from_file(self):
        """Cargar grafo desde archivo TXT
        Formato: vertex_id x y property
                edge vertex1 vertex2 weight
        """
        filename = filedialog.askopenfilename(
            title="Cargar Grafo",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not filename:
            return
            
        try:
            self.clear_all()
            
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                        
                    parts = line.split()
                    
                    if parts[0] == 'vertex' and len(parts) >= 5:
                        vertex_id = int(parts[1])
                        x = float(parts[2])
                        y = float(parts[3])
                        property_name = ' '.join(parts[4:])
                        
                        self.vertices[vertex_id] = {
                            'x': x, 'y': y, 'property': property_name
                        }
                        self.vertex_counter = max(self.vertex_counter, vertex_id + 1)
                        
                    elif parts[0] == 'edge' and len(parts) >= 4:
                        v1 = int(parts[1])
                        v2 = int(parts[2])
                        weight = float(parts[3])
                        
                        self.edges[v1].append((v2, weight))
                        self.edges[v2].append((v1, weight))
                        
            self.draw_graph()
            self.update_vertex_list()
            self.log_info(f"Grafo cargado desde {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar archivo: {str(e)}")
            
    def save_to_file(self):
        """Guardar grafo a archivo TXT"""
        filename = filedialog.asksaveasfilename(
            title="Guardar Grafo",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write("# Formato: vertex vertex_id x y property\n")
                file.write("# Formato: edge vertex1 vertex2 weight\n\n")
                
                # Guardar vértices
                for vertex_id, vertex in self.vertices.items():
                    file.write(f"vertex {vertex_id} {vertex['x']} {vertex['y']} {vertex['property']}\n")
                
                file.write("\n")
                
                # Guardar aristas (evitar duplicados)
                saved_edges = set()
                for vertex_id, neighbors in self.edges.items():
                    for neighbor_id, weight in neighbors:
                        edge = tuple(sorted([vertex_id, neighbor_id]))
                        if edge not in saved_edges:
                            file.write(f"edge {vertex_id} {neighbor_id} {weight}\n")
                            saved_edges.add(edge)
                            
            self.log_info(f"Grafo guardado en {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar archivo: {str(e)}")
            
    def log_info(self, message):
        self.info_text.insert(tk.END, message + "\n")
        self.info_text.see(tk.END)
        self.root.update_idletasks()

# Importar simpledialog al inicio
import tkinter.simpledialog

def main():
    root = tk.Tk()
    app = DijkstraVisualizer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
