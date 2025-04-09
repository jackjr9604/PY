import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any, Union
from datetime import datetime


class EditTab:
    """Interfaz para editar la estructura jerárquica avícola (Módulos > Lotes > Casetas > Corrales)"""

    def __init__(self, parent, data_manager):
        """
        Inicializa la pestaña de edición.

        Args:
            parent: Widget padre contenedor
            data_manager: Gestor de datos que implementa:
                - modules: diccionario con la estructura de datos
                - save_data(): método para guardar cambios
        """
        self.data_manager = data_manager
        self.frame = ttk.Frame(parent, style="Normal.TFrame")
        self.edit_mode = False
        self.current_edit_entry = None
        self.style = ttk.Style()

        # Configuración inicial
        self._setup_styles()
        self._create_main_ui()
        self._setup_tree_bindings()
        self.migrar_lotes_antiguos()
        self.migrar_estructura_urgente()
        
    def migrar_estructura_urgente(self):
        """Corrige inmediatamente la estructura de datos"""
        for module_name, module_data in self.data_manager.modules.items():
            for lote_name, lote_data in list(module_data.items()):
                if isinstance(lote_data, dict):
                    # Migrar casetas al nuevo formato
                    if 'casetas' not in lote_data:
                        nuevas_casetas = {}
                        for key, value in list(lote_data.items()):
                            if key != '_info':  # Excluir metadatos
                                nuevas_casetas[key] = value
                                del lote_data[key]
                        lote_data['casetas'] = nuevas_casetas
                    
                    # Migrar corrales a la nueva estructura
                    for caseta_name, corrales in lote_data.get('casetas', {}).items():
                        if isinstance(corrales, list):
                            nuevos_corrales = []
                            for corral in corrales:
                                if isinstance(corral, dict):
                                    nuevos_corrales.append(corral)
                                else:
                                    nuevos_corrales.append({
                                        'nombre': str(corral),
                                        'hembras': 0,
                                        'machos': 0,
                                        'total': 0
                                    })
                            lote_data['casetas'][caseta_name] = nuevos_corrales
        
        self.data_manager.save_data()

    # ------------------------- Configuración de Estilos -------------------------
    def _setup_styles(self):
        """Configura todos los estilos visuales para la interfaz"""
        self.style.theme_use("clam")

        # Colores base
        self._configure_frame_styles()
        self._configure_base_styles()
        self._configure_button_styles()
        self._configure_button_states()

    def _configure_frame_styles(self):
        """Configura estilos para frames"""
        self.style.configure(
            "EditMode.TFrame",
            background="#f0f0f0",
            bordercolor="#3498db",  # Color azul
            borderwidth=3,  # Aumentar grosor del borde
            relief="solid",  # Estilo del borde
            padding=2,  # Espacio interno
        )
        self.style.configure(
            "Normal.TFrame", background="#f0f0f0", bordercolor="#f0f0f0", borderwidth=0
        )

    def _configure_base_styles(self):
        """Configura estilos base para todos los widgets"""
        self.style.configure(
            ".", background="#f0f0f0", foreground="black", font=("Helvetica", 10)
        )

    def _configure_button_styles(self):
        """Configura estilos para diferentes tipos de botones"""
        button_config = {
            "Custom.TButton": {"bg": "#2ecc71", "text": "black"},
            "Edit.TButton": {"bg": "#3498db", "text": "black"},
            "Delete.TButton": {"bg": "#e74c3c", "text": "black"},
            "ActiveEdit.TButton": {
                "bg": "#2ecc71",
                "text": "black",
                "font": ("Helvetica", 10, "bold"),
            },
        }

        for style, params in button_config.items():
            self.style.configure(
                style,
                background=params["bg"],
                foreground=params["text"],
                relief="raised",
                padding=6,
                borderwidth=2,
                **({"font": params["font"]} if "font" in params else {}),
            )

    def _configure_button_states(self):
        """Configura el comportamiento de botones en diferentes estados"""
        button_states = {
            "Custom.TButton": {"active": "#27ae60", "disabled": "#a0d8b3"},
            "Edit.TButton": {"active": "#2980b9", "disabled": "#9fc5e8"},
            "Delete.TButton": {"active": "#c0392b", "disabled": "#f2a097"},
        }

        for style, states in button_states.items():
            self.style.map(
                style,
                background=[
                    ("active", states["active"]),
                    ("disabled", states["disabled"]),
                ],
                foreground=[("active", "black"), ("disabled", "#666666")],
                relief=[("pressed", "sunken"), ("disabled", "flat")],
            )

    # ------------------------- Interfaz Principal -------------------------
    def _create_main_ui(self):
        """Construye la interfaz gráfica principal"""
        main_frame = ttk.Frame(self.frame, padding=(10, 10, 10, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)

        self._create_title_bar(main_frame)
        self._create_content_area(main_frame)
        self._create_action_buttons(main_frame)

        # Eventos iniciales
        self.populate_tree()
        self._setup_tree_bindings()

    def _create_title_bar(self, parent):
        """Crea la barra de título con botón de agregar módulo"""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(title_frame, text="Estructura Avícola").pack(side=tk.LEFT)

        ttk.Button(
            title_frame,
            text="+ Agregar Módulo",
            style="Custom.TButton",
            command=self.add_module,
        ).pack(side=tk.RIGHT)

    def _create_content_area(self, parent):
        """Crea el área de contenido con el Treeview"""
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Configuración del Treeview
        self.tree = ttk.Treeview(
            content_frame,
            columns=("type", "details"),
            show="tree headings",
            selectmode="browse",
        )
        self._configure_tree_columns()

        # Scrollbars
        vsb = ttk.Scrollbar(content_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(content_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

    def _center_window(self, window, width, height):
        """Centra una ventana en la pantalla"""
        # Obtener dimensiones de la pantalla
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # Calcular posición x, y
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        # Establecer geometría
        window.geometry(f"{width}x{height}+{x}+{y}")

    def _configure_tree_columns(self):
        """Configura las columnas del Treeview"""
        columns = {
            "#0": {"text": "Nombre", "anchor": tk.W, "width": 200, "stretch": tk.YES},
            "type": {"text": "Tipo", "anchor": tk.W, "width": 100, "stretch": tk.NO},
            "details": {
                "text": "Detalles",
                "anchor": tk.W,
                "width": 150,
                "stretch": tk.YES,
            },
        }

        for col, params in columns.items():
            self.tree.heading(col, text=params["text"], anchor=params["anchor"])
            self.tree.column(col, width=params["width"], stretch=params["stretch"])

    def _create_action_buttons(self, parent):
        """Crea la barra de botones de acciones"""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=(10, 0))

        # Botones con sus configuraciones
        buttons = [
            ("+ Agregar Lote", "Custom.TButton", tk.DISABLED, self.add_lote),
            ("+ Agregar Caseta", "Custom.TButton", tk.DISABLED, self.add_caseta),
            ("✏ Editar", "Edit.TButton", tk.DISABLED, self.toggle_edit_mode),
            ("🗑 Eliminar", "Delete.TButton", tk.DISABLED, self.delete_item),
        ]

        # Crear botones y guardar referencias
        self.btn_add_lote, self.btn_add_caseta, self.btn_edit, self.btn_delete = [
            ttk.Button(action_frame, text=text, style=style, state=state, command=cmd)
            for text, style, state, cmd in buttons
        ]

        # Empaquetar botones
        for btn in [
            self.btn_add_lote,
            self.btn_add_caseta,
            self.btn_edit,
            self.btn_delete,
        ]:
            btn.pack(side=tk.LEFT, padx=5)

    def _setup_tree_bindings(self):
        """Configura los eventos del Treeview"""
        self.tree.bind("<<TreeviewSelect>>", self._handle_selection)
        self.tree.bind("<Double-1>", self._handle_double_click)
        self.tree.bind("<Button-1>", self._handle_single_click)
        self.tree.bind("<Button-3>", self._show_context_menu)#clic derecho

        # Binding separado para modo edición vs modo normal
        self.tree.bind("<Double-1>", self._handle_double_click)
        
    def _show_context_menu(self, event):
        """Muestra el menu contextual al hacer clic derecho"""
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        tags = self.tree.item(item, "tags")
        
        #crear menu
        menu = tk.Menu(self.frame, tearoff=0)
        
        if "lote" in tags:
            menu.add_command(label="editar Fecha de alojamiento",
                             command=lambda: self.editar_fecha_lote())
            menu.add_separator()

        #otros items del menu..
        
        try:
            menu.tk_popup(event.x_root, event.y_root)# Muestra el menú en la posición del clic
        finally:
            menu.grab_release()# Libera el menú al hacer clic fuera

    def _handle_selection(self, event):
        """Maneja cambios en la selección"""
        self.update_buttons()

    def _handle_single_click(self, event):
        """Permite deseleccionar haciendo click en área vacía"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "nothing":
            self.tree.selection_remove(self.tree.selection())
        self.update_buttons()

    def _handle_double_click(self, event):
        """Maneja doble click solo en items válidos"""
        region = self.tree.identify("region", event.x, event.y)
        item = self.tree.identify_row(event.y)

        # Solo procesar si es sobre un item
        if region == "cell" and item:
            if self.edit_mode:
                self.edit_item()
                return "break"
            else:
                tags = self.tree.item(item, "tags")
                if "caseta" in tags:
                    self._open_caseta_management(item)
                    return "break"
        return None

    def _handle_double_click(self, event):
        """Maneja el doble click según el modo actual"""
        if self.edit_mode:
            # En modo edición, solo editar y evitar propagación del evento
            self.edit_item()
            return "break"  # Esto detiene la propagación del evento
        else:
            # Fuera de modo edición, comportamiento original para casetas
            item = self.tree.focus()
            if item:
                tags = self.tree.item(item, "tags")
                if "caseta" in tags:
                    self._open_caseta_management(item)
                    return "break"
        return None

    # ------------------------- Funcionalidades Principales -------------------------
    def toggle_edit_mode(self):
        """Alterna entre modo normal y modo edición con feedback visual"""
        self.edit_mode = not self.edit_mode

        # Actualizar apariencia según el modo
        frame_style = "EditMode.TFrame" if self.edit_mode else "Normal.TFrame"
        btn_style = "ActiveEdit.TButton" if self.edit_mode else "Edit.TButton"

        # Aplicar el estilo al frame y sus hijos
        self.frame.config(style=frame_style)
        for child in self.frame.winfo_children():
            child.config(style=frame_style)

        self.btn_edit.config(style=btn_style)

        # Guardar cambios si salimos del modo edición
        if not self.edit_mode and self.current_edit_entry:
            self._save_current_edit()

        self.update_buttons()

    def update_buttons(self, event=None):
        """Actualiza el estado de los botones según la selección actual"""
        selected = self.tree.selection()

        if not selected:
            self._disable_all_buttons()
            return

        self._update_buttons_based_on_selection(selected)

    def _disable_all_buttons(self):
        """Deshabilita todos los botones de acción excepto el de edición en modo edición"""
        self.btn_add_lote.config(state=tk.DISABLED)
        self.btn_add_caseta.config(state=tk.DISABLED)
        self.btn_delete.config(state=tk.DISABLED)

        # Mantener el botón de edición habilitado si estamos en modo edición
        if not self.edit_mode:
            self.btn_edit.config(state=tk.DISABLED)

    def _update_buttons_based_on_selection(self, selected_item):
        """Habilita botones según el tipo de elemento seleccionado"""
        tags = self.tree.item(selected_item, "tags")

        button_states = {
            "module": (tk.NORMAL, tk.DISABLED, tk.NORMAL, tk.NORMAL),
            "lote": (tk.DISABLED, tk.NORMAL, tk.NORMAL, tk.NORMAL),
            "caseta": (tk.DISABLED, tk.DISABLED, tk.NORMAL, tk.NORMAL),
        }

        for tag in tags:
            if tag in button_states:
                states = button_states[tag]
                self.btn_add_lote.config(state=states[0])
                self.btn_add_caseta.config(state=states[1])
                self.btn_edit.config(state=states[2])
                self.btn_delete.config(state=states[3])
                break
            
    def migrar_lotes_antiguos(self):
        """Actualiza la estructura de lotes antiguos para que tengan '_info'"""
        for module_name, lots in self.data_manager.modules.items():
            for lote_name, lote_data in lots.items():
                if not isinstance(lote_data, dict) or '_info' not in lote_data:
                    # Si es una estructura antigua (solo contiene casetas)
                    casetas = lote_data if isinstance(lote_data, dict) else {}
                    self.data_manager.modules[module_name][lote_name] = {
                        '_info': {
                            'fecha_alojamiento': 'Sin fecha',
                            'fecha_migracion': datetime.now().strftime("%d/%m/%Y")
                        },
                        'casetas': casetas
                    }
        self.data_manager.save_data()

    def populate_tree(self):
        """Llena el Treeview con la estructura actual de datos"""
        self.tree.delete(*self.tree.get_children())

        for module_name, lots in self.data_manager.modules.items():
            module_id = self._add_tree_item(
                "", "end", module_name, "Módulo", f"{len(lots)} lotes", "module"
            )

            for lote_name, lote_data in lots.items():
                fecha = lote_data.get('_info', {}).get('fecha_alojamiento', 'Sin fecha')
                num_casetas = len(lote_data.get('casetas', {}))

                lote_id = self._add_tree_item(
                    module_id,
                    "end",
                    lote_name,
                    "Lote",
                    f"Alojado: {fecha} | {num_casetas} casetas", #info combinada
                    "lote",
                )

                for caseta_name, corrales in lote_data.get('casetas', {}).items():
                    self._add_tree_item(
                        lote_id,
                        "end",
                        caseta_name,
                        "Caseta",
                        f"{len(corrales)} corrales",
                        "caseta",
                    )

    def _add_tree_item(self, parent, position, text, item_type, details, tags):
        """Añade un ítem al Treeview con formato consistente"""
        return self.tree.insert(
            parent, position, text=text, values=(item_type, details), tags=(tags,)
        )

    # ------------------------- Operaciones CRUD -------------------------
    def add_module(self):
        """Añade un nuevo módulo a la estructura"""
        name = self._get_user_input("Nuevo Módulo", "Nombre del módulo:")
        if not name:
            return

        if name in self.data_manager.modules:
            self._show_error("Ya existe un módulo con ese nombre")
            return

        self.data_manager.modules[name] = {}
        self._save_and_refresh()
        self._expand_new_item(name)

    def add_lote(self):
        """Añade un nuevo lote al módulo seleccionado"""
        selected = self._validate_selection()
        if not selected:
            return

        module_name = self.tree.item(selected, "text")
        
        # Pedir nombre del lote
        name = self._get_user_input(
            "Nuevo Lote", 
            f"Nombre del lote para {module_name}:"
        )
        if not name:
            return

        if name in self.data_manager.modules[module_name]:
            self._show_error(f"El lote '{name}' ya existe en este módulo")
            return

        # Pedir fecha de alojamiento
        fecha = self._get_user_input(
            "Fecha de Alojamiento", 
            f"Ingrese la fecha de alojamiento para {name} (DD/MM/AAAA):"
        )
        if not fecha:
            return

        # Crear el lote con estructura consistente
        self.data_manager.modules[module_name][name] = {
            '_info': {
                'fecha_alojamiento': fecha,
                'fecha_creacion': datetime.now().strftime("%d/%m/%Y")
            },
            'casetas': {}  # Diccionario para las casetas
        }
        
        self._save_and_refresh()
        self._expand_new_item(module_name, name)

    #Método para Editar la Fecha       
    def editar_fecha_lote(self):
        """permitir editar la fecha de alojamiento de un lote seleccionado"""
        selected = self.tree.focus()
        if not selected:
            self._show_warning("seleccione un lote primero")
            return
        
        #verificar que el item deleccionado es un lote
        tags = self.tree.item(selected, "tags")
        if "lote" not in tags:
            self._show_warning("Por favor seleccione un lote")
            return
        
        #obtener la estructura completa
        module_item = self.tree.parent(selected)
        module_name = self.tree.item(module_item, "text")
        lote_name = self.tree.item(selected, "text")
        
        #obtener datos del lote con estructura segura
        lote_data = self.data_manager.modules[module_name][lote_name]

        #verificar y crear la estructura '_info' si no existe
        
        if '_info' not in lote_data:
            lote_data['_info'] = {}
            
        #obtener la fecha actual con un valor por defecteco
        fecha_actual = lote_data['_info'].get('fecha_alojamiento', 'Sin fecha')
        
        #Pedir la nueva fecha
        nueva_fecha = self._get_user_input(
            "editar Fecha de Alojamiento",
            f"Ingrese la nueva fecha para el lote {lote_name} (DD/MM/AAA):",
            default=fecha_actual
        )
        
        if nueva_fecha and nueva_fecha != fecha_actual:
            #actualizar fecha
            lote_data['_info']['fecha_alojamiento'] = nueva_fecha
            self._save_and_refresh()
        

    def add_caseta(self):
        """Añade una nueva caseta al lote seleccionado"""
        selected = self._validate_selection()
        if not selected:
            return

        parent = self.tree.parent(selected)
        module_name = self.tree.item(parent, "text")
        lote_name = self.tree.item(selected, "text")

        name = self._get_user_input(
            "Nueva Caseta", 
            f"Nombre de caseta para {lote_name}:"
        )
        if not name:
            return

        # Acceso CORREGIDO a las casetas
        lote_data = self.data_manager.modules[module_name][lote_name]
        
        # Si por algún error no existe 'casetas', lo creamos
        if 'casetas' not in lote_data:
            lote_data['casetas'] = {}

        # Verificar si la caseta ya existe
        if name in lote_data['casetas']:
            self._show_error(f"La caseta '{name}' ya existe en este lote")
            return

        # Añadir la nueva caseta
        lote_data['casetas'][name] = []  # Lista vacía para los corrales
        self._save_and_refresh()
        self._expand_new_item(module_name, lote_name, name)

    def delete_item(self):
        """Elimina el elemento seleccionado y su contenido"""
        selected = self._validate_selection()
        if not selected:
            return

        item_text = self.tree.item(selected, "text")
        tags = self.tree.item(selected, "tags")

        if not self._confirm_action(f"¿Eliminar '{item_text}' y todo su contenido?"):
            return

        try:
            self._delete_item_from_structure(selected, tags, item_text)
            self._save_and_refresh()
        except KeyError as e:
            self._show_error(f"No se pudo eliminar el elemento: {str(e)}")
            
            # Acceso corregido:
            del self.data_manager.modules[module][lote]['casetas'][caseta_name]

    def _delete_item_from_structure(self, item_id, tags, item_text):
        """Elimina un elemento de la estructura de datos según su tipo"""
        if "module" in tags:
            del self.data_manager.modules[item_text]
        elif "lote" in tags:
            module = self.tree.item(self.tree.parent(item_id), "text")
            del self.data_manager.modules[module][item_text]
        elif "caseta" in tags:
            lote = self.tree.item(self.tree.parent(item_id), "text")
            module = self.tree.item(self.tree.parent(self.tree.parent(item_id)), "text")
            del self.data_manager.modules[module][lote][item_text]

    def edit_item(self):
        """Permite editar directamente los nombres en el Treeview"""
        if not self.edit_mode:
            return

        selected = self._validate_selection()
        if not selected:
            return

        column = self.tree.identify_column(
            self.tree.winfo_pointerx() - self.tree.winfo_rootx()
        )
        if column != "#0":
            return

        self._create_edit_entry(selected)

    def _create_edit_entry(self, item_id):
        """Crea un Entry para edición in-place de un ítem del Treeview"""
        if hasattr(self, "edit_entry") and self.edit_entry:
            self.edit_entry.destroy()

        tags = self.tree.item(item_id, "tags")
        old_name = self.tree.item(item_id, "text")
        bbox = self.tree.bbox(item_id, "#0")

        if not bbox:
            return

        self.edit_entry = ttk.Entry(self.tree)
        self.edit_entry.insert(0, old_name)
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus_set()
        self.edit_entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])

        self._setup_edit_entry_events(item_id, tags, old_name)

    def _setup_edit_entry_events(self, item_id, tags, old_name):
        """Configura los eventos para el Entry de edición"""

        def save_edit(event=None):
            new_name = self.edit_entry.get().strip()
            self.edit_entry.destroy()
            self.edit_entry = None

            if not new_name or new_name == old_name:
                return

            try:
                expanded = self._get_expanded_items()
                self._update_item_name_in_structure(tags, old_name, new_name)
                self._save_and_refresh()
                self._restore_expansion(expanded)
            except ValueError as e:
                self._show_error(str(e))
                self.frame.after(100, lambda: self._create_edit_entry(item_id))

        def cancel_edit(event=None):
            if hasattr(self, "edit_entry") and self.edit_entry:
                self.edit_entry.destroy()
                self.edit_entry = None

        self.edit_entry.bind("<Return>", save_edit)
        self.edit_entry.bind("<FocusOut>", save_edit)
        self.edit_entry.bind("<Escape>", cancel_1edit)

    def _update_item_name_in_structure(self, tags, old_name, new_name):
        """Actualiza el nombre de un elemento en la estructura de datos"""
        if "module" in tags:
            if new_name in self.data_manager.modules:
                raise ValueError("Ya existe un módulo con ese nombre")
            self.data_manager.modules[new_name] = self.data_manager.modules.pop(
                old_name
            )
        elif "lote" in tags:
            parent = self.tree.focus()
            module_name = self.tree.item(self.tree.parent(parent), "text")
            if new_name in self.data_manager.modules[module_name]:
                raise ValueError("Ya existe un lote con ese nombre")
            self.data_manager.modules[module_name][new_name] = (
                self.data_manager.modules[module_name].pop(old_name)
            )
        elif "caseta" in tags:
            parent = self.tree.focus()
            grandparent = self.tree.parent(parent)
            module_name = self.tree.item(self.tree.parent(grandparent), "text")
            lote_name = self.tree.item(grandparent, "text")
            if new_name in self.data_manager.modules[module_name][lote_name]:
                raise ValueError("Ya existe una caseta con ese nombre")
            self.data_manager.modules[module_name][lote_name][new_name] = (
                self.data_manager.modules[module_name][lote_name].pop(old_name)
            )

    def _open_caseta_management(self, item_id):
        """Abre la ventana de gestión de corrales para una caseta"""
        parent = self.tree.parent(item_id)
        grandparent = self.tree.parent(parent)

        module = self.tree.item(grandparent, "text")
        lote = self.tree.item(parent, "text")
        caseta = self.tree.item(item_id, "text")

        # Acceso CORREGIDO a los corrales
        try:
            lote_data = self.data_manager.modules[module][lote]
            if 'casetas' not in lote_data:
                lote_data['casetas'] = {}
            
            if caseta not in lote_data['casetas']:
                lote_data['casetas'][caseta] = []  # Inicializar si no existe
                
            corrales = lote_data['casetas'][caseta]
            self.manage_caseta(module, lote, caseta, corrales)
        except KeyError as e:
            self._show_error(f"Error al acceder a los datos: {str(e)}")

    def _setup_corrales_tree_bindings(self, tree):
        """Configura los eventos para selección por celdas"""
        tree.bind("<Button-1>", lambda e: self._handle_corrales_click(e, tree))
        
    def _highlight_hovered_row(self, event, tree):
        """Resalta la fila sobre la que está el cursor"""
        item = tree.identify_row(event.y)
        if item:
            tree.tk.call(tree, "tag", "remove", "hover")
            tree.tk.call(tree, "tag", "add", "hover", item)
            tree.tk.call(tree, "tag", "configure", "hover", background="#e6e6e6")

    def _handle_corrales_click(self, event, tree):
        """Maneja los clicks en el Treeview de corrales"""
        item = tree.identify_row(event.y)
        if item:
            tree.selection_set(item)  # Selecciona el item clickeado

    # ------------------------- Gestión de Corrales -------------------------
    def manage_caseta(self, module_name, lote_name, caseta_name, corrales):
        """Muestra la ventana de gestión de corrales para una caseta específica"""
        # Asegurarnos que corrales es una lista
        if not isinstance(corrales, list):
            corrales = []
            
        # Actualizar la estructura de datos
        self.data_manager.modules[module_name][lote_name]['casetas'][caseta_name] = corrales
        self.data_manager.save_data()
            
        caseta_window = tk.Toplevel(self.frame)
        caseta_window.title(
            f"Gestión de Corrales: {module_name} > {lote_name} > {caseta_name}"
        )
        caseta_window.transient(self.frame)
        caseta_window.grab_set()

        # Tamaño deseado de la ventana
        window_width = 800
        window_height = 600

        # Centrar la ventana
        self._center_window(caseta_window, window_width, window_height)

        # Frame principal
        main_frame = ttk.Frame(caseta_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        ttk.Label(main_frame, text=f"Gestión de Corrales - {caseta_name}").pack(
            pady=(0, 10)
        )

        # Treeview para corrales
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        corrales_tree = ttk.Treeview(
            tree_frame,
            columns=("corral", "hembras", "machos", "total"),
            show="headings",
            selectmode="none",  # Permite selección múltiple
        )

        # Añadir esta configuración adicional:
        corrales_tree.tag_configure(
            "selected_cell", background="#3498db", foreground="white"
        )
        corrales_tree.tag_configure("row_indicator", background="#f0f0f0")

        # Treeview con selección por ítems completos
        corrales_tree = ttk.Treeview(
            tree_frame,
            columns=("corral", "hembras", "machos", "total"),
            show="headings",
            selectmode="extended",  # Permite selección múltiple
        )

        # Configurar columnas (modificar para incluir tags)
        self._configure_corrales_tree_columns(corrales_tree)

        # Configurar bindings para selección por celdas
        self._setup_corrales_tree_bindings(corrales_tree)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=corrales_tree.yview)
        hsb = ttk.Scrollbar(
            tree_frame, orient="horizontal", command=corrales_tree.xview
        )
        corrales_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Layout
        corrales_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Panel de botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        # Botones de acciones
        self._create_corrales_action_buttons(
            btn_frame, module_name, lote_name, caseta_name, corrales_tree
        )

        # Cargar datos
        self.load_corrales_data(module_name, lote_name, caseta_name, corrales_tree)

        # Evento de doble click para editar
        corrales_tree.bind(
            "<Double-1>",
            lambda e: self.edit_corral(
                module_name, lote_name, caseta_name, corrales_tree
            ),
        )

    def _configure_corrales_tree_columns(self, tree):
        """Configura las columnas del Treeview de corrales con selección por celdas"""
        columns = {
            "corral": {"text": "Corral", "width": 150, "anchor": "center"},
            "hembras": {"text": "Hembras", "width": 100, "anchor": "center"},
            "machos": {"text": "Machos", "width": 100, "anchor": "center"},
            "total": {"text": "Total", "width": 100, "anchor": "center"},
        }

        for col, params in columns.items():
            tree.heading(col, text=params["text"])
            tree.column(col, width=params["width"], anchor=params["anchor"])

        # Configuración adicional para selección por celdas
        tree["selectmode"] = "none"
        tree["show"] = "headings"

    def _create_corrales_action_buttons(self, parent, module, lote, caseta, tree):
        """Crea los botones de acción para la gestión de corrales (sin botón de edición)"""
        buttons = [
            (
                "+ Agregar Corrales",
                "Custom.TButton",
                lambda: self.add_corrales(module, lote, caseta, tree),
            ),
            (
                "🗑 Eliminar",
                "Delete.TButton",
                lambda: self.delete_corrales(module, lote, caseta, tree),
            ),
        ]

        for text, style, cmd in buttons:
            ttk.Button(parent, text=text, style=style, command=cmd).pack(
                side=tk.LEFT, padx=5
            )

    def load_corrales_data(self, module_name, lote_name, caseta_name, tree):
        """Carga los datos de corrales en el Treeview"""
        tree.delete(*tree.get_children())
        
        try:
            # Acceso seguro a los corrales
            lote_data = self.data_manager.modules[module_name][lote_name]
            corrales = lote_data.get('casetas', {}).get(caseta_name, [])
            
            for corral in corrales:
                if isinstance(corral, dict):  # Estructura nueva
                    hembras = corral.get('hembras', 0)
                    machos = corral.get('machos', 0)
                    nombre = corral.get('nombre', '?')
                else:  # Compatibilidad con estructura antigua
                    nombre = str(corral)
                    hembras = machos = 0
                    
                total = hembras + machos
                tree.insert("", "end", values=(nombre, hembras, machos, total))
        except KeyError:
            self._show_error("Error al cargar los corrales")

    def add_corrales(self, module_name, lote_name, caseta_name, tree):
        """Añade nuevos corrales a una caseta"""
        count = self._get_user_input(
            "Agregar Corrales", 
            "Cantidad de corrales a agregar:", 
            number=True
        )
        
        if not count or count <= 0:
            return
        
        # Acceso seguro a los datos
        lote_data = self.data_manager.modules[module_name][lote_name]
        if 'casetas' not in lote_data:
            lote_data['casetas'] = {}
        if caseta_name not in lote_data['casetas']:
            lote_data['casetas'][caseta_name] = []
        
        corrales = lote_data['casetas'][caseta_name]
        next_num = len(corrales) + 1
        
        for _ in range(count):
            corral_data = {"nombre": str(next_num), "hembras": 0, "machos": 0}
            corrales.append(corral_data)
            tree.insert("", "end", values=(corral_data["nombre"], 0, 0, 0))
            next_num += 1
        
        self.data_manager.save_data()

    def delete_corrales(self, module_name, lote_name, caseta_name, tree):
        """Elimina los corrales seleccionados"""
        selected_items = tree.selection()  # Obtener todos los items seleccionados
        
        if not selected_items:
            self._show_warning("Seleccione al menos un corral haciendo clic en él")
            return

        # Obtener los nombres de los corrales a eliminar
        corrales_a_eliminar = []
        for item in selected_items:
            values = tree.item(item, 'values')
            if values:  # Asegurarse que el item tiene valores
                corrales_a_eliminar.append(values[0])  # El nombre está en la primera columna

        if not corrales_a_eliminar:
            self._show_warning("No se pudieron obtener los corrales seleccionados")
            return

        if not self._confirm_action(f"¿Eliminar {len(corrales_a_eliminar)} corral(es)?"):
            return

        try:
            # Acceder a los corrales de la caseta
            lote_data = self.data_manager.modules[module_name][lote_name]
            if 'casetas' not in lote_data or caseta_name not in lote_data['casetas']:
                self._show_error("La caseta no existe o no tiene corrales")
                return

            # Filtrar los corrales que no están seleccionados
            corrales_originales = lote_data['casetas'][caseta_name]
            corrales_actualizados = [
                corral for corral in corrales_originales 
                if str(corral.get('nombre', '')) not in corrales_a_eliminar
            ]

            # Actualizar la estructura de datos
            lote_data['casetas'][caseta_name] = corrales_actualizados

            # Eliminar de la vista
            for item in selected_items:
                tree.delete(item)

            self.data_manager.save_data()
            self._show_success(f"{len(corrales_a_eliminar)} corral(es) eliminados correctamente")

        except Exception as e:
            self._show_error(f"Error al eliminar corrales: {str(e)}")
            
    def _show_success(self, message):
        """Muestra un mensaje de éxito"""
        messagebox.showinfo("Éxito", message, parent=self.frame)

    def edit_corral(self, module_name, lote_name, caseta_name, tree):
        """Permite editar los datos de un corral"""
        item = tree.identify_row(tree.winfo_pointery() - tree.winfo_rooty())
        column = tree.identify_column(tree.winfo_pointerx() - tree.winfo_rootx())

        if not item or column == "#0":
            return

        col_index = int(column[1]) - 1
        values = list(tree.item(item, "values"))
        corral_name = values[0]

        column_mapping = {
            "#1": ("nombre", 0),
            "#2": ("hembras", 1),
            "#3": ("machos", 2),
        }

        if column not in column_mapping:
            return

        col_name, value_index = column_mapping[column]
        current_value = values[value_index]

        bbox = tree.bbox(item, column)
        if not bbox:
            return

        entry = ttk.Entry(tree)
        entry.insert(0, current_value)
        entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        entry.select_range(0, tk.END)
        entry.focus_set()

        def save_edit():
            try:
                new_value = entry.get() if col_name == "nombre" else int(entry.get())
                
                if col_name != "nombre" and new_value < 0:
                    raise ValueError

                # Actualizar los datos
                lote_data = self.data_manager.modules[module_name][lote_name]
                corrales = lote_data.get('casetas', {}).get(caseta_name, [])
                
                for corral_data in corrales:
                    if str(corral_data.get('nombre')) == str(corral_name):
                        corral_data[col_name] = new_value
                        
                        # Actualizar total si es hembras/machos
                        if col_name in ('hembras', 'machos'):
                            total = int(corral_data.get('hembras', 0)) + int(corral_data.get('machos', 0))
                            values[3] = total
                        
                        # Actualizar todos los valores en el Treeview
                        tree.item(item, values=(
                            corral_data.get('nombre', ''),
                            corral_data.get('hembras', 0),
                            corral_data.get('machos', 0),
                            int(corral_data.get('hembras', 0)) + int(corral_data.get('machos', 0))
                        ))
                        
                        self.data_manager.save_data()
                        break
                
                entry.destroy()
                tree.update_idletasks()  # Forzar actualización visual
            except ValueError:
                self._show_error("Ingrese un valor válido")
                entry.focus_set()

        # Configurar los eventos (bindings)
        entry.bind("<Return>", lambda e: save_edit())  # Enter guarda
        entry.bind("<FocusOut>", lambda e: save_edit())  # Clic fuera guarda
        entry.bind("<Escape>", lambda e: entry.destroy())  # ESC cancela
        
        # Estos son los bindings adicionales para mejor control
        entry.bind("<Tab>", lambda e: (save_edit(), tree.focus_set()))  # TAB guarda y pasa al tree
        entry.bind("<Up>", lambda e: (save_edit(), self._move_to_adjacent_cell(tree, item, column, "up")))
        entry.bind("<Down>", lambda e: (save_edit(), self._move_to_adjacent_cell(tree, item, column, "down")))

    def _update_corral_data(self, module, lote, caseta, corral, field, value, values, index):
        """Actualiza los datos y la visualización completa"""
        try:
            # Acceso a los datos
            lote_data = self.data_manager.modules[module][lote]
            corrales = lote_data.get('casetas', {}).get(caseta, [])
            
            for corral_data in corrales:
                if str(corral_data.get('nombre')) == str(corral):
                    # Actualizar el campo modificado
                    corral_data[field] = value
                    
                    # Crear nueva lista de valores completa
                    new_values = [
                        corral_data.get('nombre', ''),
                        corral_data.get('hembras', 0),
                        corral_data.get('machos', 0),
                        int(corral_data.get('hembras', 0)) + int(corral_data.get('machos', 0))
                    ]
                    
                    # Si estamos en modo de edición, actualizar la referencia values
                    if hasattr(self, 'edit_entry') and self.edit_entry:
                        for i, val in enumerate(new_values):
                            values[i] = val
                    
                    self.data_manager.save_data()
                    return new_values
            return values
        except Exception as e:
            self._show_error(f"Error al actualizar: {str(e)}")
            return values

    # ------------------------- Métodos Auxiliares -------------------------
    def _save_current_edit(self):
        """Guarda la edición actual si existe"""
        if self.current_edit_entry:
            self.current_edit_entry.event_generate("<Return>")
            self.current_edit_entry = None

    def _get_expanded_items(self):
        """Devuelve una lista con los nodos actualmente expandidos"""
        expanded = []
        for child in self.tree.get_children():
            if self.tree.item(child, "open"):
                expanded.append(self.tree.item(child, "text"))
                for grandchild in self.tree.get_children(child):
                    if self.tree.item(grandchild, "open"):
                        expanded.append(
                            f"{self.tree.item(child, 'text')}/{self.tree.item(grandchild, 'text')}"
                        )
        return expanded

    def _restore_expansion(self, items):
        """Restaura los nodos expandidos basado en una lista de items"""
        for child in self.tree.get_children():
            if self.tree.item(child, "text") in items:
                self.tree.item(child, open=True)
                for grandchild in self.tree.get_children(child):
                    path = f"{self.tree.item(child, 'text')}/{self.tree.item(grandchild, 'text')}"
                    if path in items:
                        self.tree.item(grandchild, open=True)

    def _expand_new_item(self, module_name=None, lote_name=None, caseta_name=None):
        """Expande los nodos para mostrar el nuevo elemento añadido"""
        if not module_name:
            return

        for child in self.tree.get_children():
            if self.tree.item(child, "text") == module_name:
                self.tree.item(child, open=True)

                if lote_name:
                    for lote_child in self.tree.get_children(child):
                        if self.tree.item(lote_child, "text") == lote_name:
                            self.tree.item(lote_child, open=True)

                            if caseta_name:
                                for caseta_child in self.tree.get_children(lote_child):
                                    if (
                                        self.tree.item(caseta_child, "text")
                                        == caseta_name
                                    ):
                                        self.tree.selection_set(caseta_child)
                                        self.tree.focus(caseta_child)
                                        break
                            break
                break

    def _save_and_refresh(self):
        """Guarda los datos y actualiza la vista"""
        self.data_manager.save_data()
        self.populate_tree()

    def _validate_selection(self):
        """Valida que haya un elemento seleccionado y lo devuelve"""
        selected = self.tree.focus()
        if not selected:
            self._show_warning("Seleccione un elemento primero")
            return None
        return selected

    def _get_user_input(self, title, prompt, number=False, default=""):
        """Muestra un diálogo para obtener entrada del usuario"""
        dialog = tk.Toplevel(self.frame)
        dialog.title(title)
        dialog.transient(self.frame)
        dialog.grab_set()

        self._center_window(dialog, 400, 150)

        ttk.Label(dialog, text=prompt).pack(padx=10, pady=5)
        entry = ttk.Entry(dialog)
        entry.pack(padx=10, pady=5)
        entry.insert(0, default)
        entry.focus_set()

        result = []

        def on_ok():
            try:
                val = int(entry.get()) if number else entry.get().strip()
                if number and val < 0:
                    raise ValueError
                result.append(val)
                dialog.grab_release()
                dialog.destroy()
            except ValueError:
                msg = (
                    "Ingrese un número válido" if number else "Ingrese un valor válido"
                )
                self._show_error(msg, dialog)
                entry.focus_set()

        ttk.Button(dialog, text="Aceptar", command=on_ok).pack(pady=5)
        dialog.bind("<Return>", lambda e: on_ok())

        def on_close():
            dialog.grab_release()
            dialog.destroy()

        dialog.protocol("WM_DELETE_WINDOW", on_close)
        dialog.wait_window()

        return result[0] if result else None

    def _confirm_action(self, message):
        """Muestra un diálogo de confirmación y devuelve la respuesta"""
        return messagebox.askyesno("Confirmar", message, parent=self.frame)

    def _show_error(self, message, parent=None):
        """Muestra un mensaje de error"""
        parent = parent or self.frame
        messagebox.showerror("Error", message, parent=parent)

    def _show_warning(self, message):
        """Muestra un mensaje de advertencia"""
        messagebox.showwarning("Advertencia", message, parent=self.frame)