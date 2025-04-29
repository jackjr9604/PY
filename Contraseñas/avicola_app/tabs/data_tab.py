import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry


class DataTab:
    def __init__(self, parent, data_manager):
        self.data_manager = data_manager
        self.frame = ttk.Frame(parent)

        # Variables para los dropdowns
        self.selected_module = tk.StringVar()
        self.selected_lot = tk.StringVar()
        self.production_date = tk.StringVar(value=datetime.now().strftime("%d/%m/%Y"))

        # Inicializar widgets
        self._initialize_widgets()

    def _initialize_widgets(self):
        """Inicializa todos los widgets y componentes de la interfaz"""
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Panel principal dividido
        self.main_panel = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        self.main_panel.pack(fill=tk.BOTH, expand=True)

        # Panel izquierdo (menú)
        self.left_panel = ttk.Frame(self.main_panel, width=200)
        self.main_panel.add(self.left_panel)

        # Panel derecho (contenido)
        self.right_panel = ttk.Frame(self.main_panel)
        self.main_panel.add(self.right_panel, weight=1)

        # Crear el menú de secciones
        self._create_sections_menu()

        # Mostrar la sección de producción por defecto
        self._show_production_section()

    def _create_sections_menu(self):
        """Crea el menú de secciones en el panel izquierdo"""
        lbl_menu = ttk.Label(self.left_panel, text="MENÚ", font=("Arial", 10, "bold"))
        lbl_menu.pack(pady=(10, 5))

        btn_production = ttk.Button(
            self.left_panel, text="Producción", command=self._show_production_section
        )
        btn_production.pack(fill=tk.X, padx=5, pady=2)

    def _show_production_section(self):
        """Muestra la sección de producción con fecha"""
        # Limpiar el panel derecho
        for widget in self.right_panel.winfo_children():
            widget.destroy()

        # Frame principal
        production_frame = ttk.Frame(self.right_panel)
        production_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ---------------------------
        # Parte SUPERIOR - Controles
        # ---------------------------
        top_control_frame = ttk.LabelFrame(
            production_frame, text="Controles de Producción", padding=10
        )
        top_control_frame.pack(fill=tk.X, pady=(0, 10))

        # Botón unificado para cargar módulo, lote y producción
        ttk.Button(
            top_control_frame,
            text="Cargar Datos",
            command=self._load_all_data,
            style="Primary.TButton",
        ).pack(side=tk.LEFT, padx=5)

        # Selector de fecha usando DateEntry
        ttk.Label(top_control_frame, text="Fecha (DD/MM/AAAA):").pack(
            side=tk.LEFT, padx=5
        )
        self.date_entry = DateEntry(
            top_control_frame,
            width=12,
            date_pattern="dd/MM/yyyy",
            background="navy",  # Color del botón de calendario
            foreground="white",  # Color del texto
            borderwidth=2,
            selectbackground="skyblue",  # Día seleccionado
            selectforeground="black",
            font=("Helvetica", 10),
            mindate=datetime(2020, 1, 1),
            maxdate=datetime(2030, 12, 31),
            state="readonly",  # No deja escribir, solo elegir
        )
        self.date_entry.pack(side=tk.LEFT, padx=5)

        # Dropdown para módulos
        ttk.Label(top_control_frame, text="Módulo:").pack(side=tk.LEFT, padx=5)
        self.module_dropdown = ttk.Combobox(
            top_control_frame,
            textvariable=self.selected_module,
            state="readonly",
            width=15,
        )
        self.module_dropdown.pack(side=tk.LEFT, padx=5)
        self.module_dropdown.bind("<<ComboboxSelected>>", self._update_lots_dropdown)

        # Dropdown para lotes
        ttk.Label(top_control_frame, text="Lote:").pack(side=tk.LEFT, padx=5)
        self.lot_dropdown = ttk.Combobox(
            top_control_frame,
            textvariable=self.selected_lot,
            state="readonly",
            width=15,
        )
        self.lot_dropdown.pack(side=tk.LEFT, padx=5)

        # ---------------------------
        # Separador visual más evidente
        # ---------------------------
        separator = ttk.Separator(production_frame, orient="horizontal")
        separator.pack(fill=tk.X, pady=10)

        # ---------------------------
        # Parte CENTRAL - Corrales con scroll
        # ---------------------------
        corrals_container = ttk.LabelFrame(
            production_frame, text="Datos de Producción", padding=10
        )
        corrals_container.pack(fill=tk.BOTH, expand=True)

        self.corrals_frame = ttk.Frame(corrals_container)
        self.corrals_frame.pack(fill=tk.BOTH, expand=True)

        # ---------------------------
        # Separador visual más evidente
        # ---------------------------
        separator2 = ttk.Separator(production_frame, orient="horizontal")
        separator2.pack(fill=tk.X, pady=10)

        # ---------------------------
        # Parte INFERIOR - Solo botón Guardar
        # ---------------------------
        bottom_btn_frame = ttk.Frame(production_frame)
        bottom_btn_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            bottom_btn_frame,
            text="Guardar Producción",
            command=self._save_production_data,
            style="Primary.TButton",
        ).pack(side=tk.RIGHT, padx=5)

        # Actualizar dropdowns
        self._update_modules_dropdown()

    def _load_all_data(self):
        """Carga módulo, lote y producción en un solo paso"""
        # Validar selección
        module = self.selected_module.get()
        lot = self.selected_lot.get()
        fecha = self.date_entry.get()

        if not module:
            messagebox.showwarning("Advertencia", "Seleccione un módulo")
            return

        if not lot:
            messagebox.showwarning("Advertencia", "Seleccione un lote")
            return

        try:
            # Validar formato de fecha
            datetime.strptime(fecha, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/AAAA")
            return

        # Limpiar corrales anteriores
        for widget in self.corrals_frame.winfo_children():
            widget.destroy()

        # Cargar estructura de corrales
        self._show_corrals()

        # Cargar datos de producción existentes
        production_data = self.data_manager.get_production_data(module, lot, fecha)
        if production_data:
            self._show_corrals(production_data=production_data)

    def _validate_date(self, proposed_text, new_char, action_type, cursor_pos):
        """Mantiene el formato 00/00/0000 convirtiendo borrados a ceros"""
        # Si es borrado (backspace/delete), convertir a '0' en lugar de borrar
        if action_type == "0" and len(new_char) == 0:
            # Determinar posición del cursor
            if cursor_pos in (0, 1):  # Día
                pos = cursor_pos
            elif cursor_pos in (3, 4):  # Mes
                pos = cursor_pos + 1  # Ajustar por la barra
            elif cursor_pos >= 6:  # Año
                pos = cursor_pos + 2  # Ajustar por las dos barras
            else:  # Posición de barras
                return False

            # Construir nuevo texto con '0' en la posición borrada
            current = self.production_date.get()
            new_text = current[:pos] + "0" + current[pos + 1 :]
            self.production_date.set(new_text)
            return False

        # Solo permitir dígitos (no borrados)
        if not new_char.isdigit():
            return False

        # Mantener el formato fijo DD/MM/AAAA
        current = self.production_date.get()

        # Determinar dónde insertar el nuevo dígito
        if cursor_pos in (0, 1):  # Día
            pos = cursor_pos
        elif cursor_pos in (3, 4):  # Mes
            pos = cursor_pos + 1  # Ajustar por la barra
        elif cursor_pos >= 6:  # Año
            pos = cursor_pos + 2  # Ajustar por las dos barras
        else:  # Posición de barras
            return False

        # Insertar nuevo dígito
        new_text = current[:pos] + new_char + current[pos + 1 :]
        self.production_date.set(new_text)

        # Validar rangos básicos
        day = int(new_text[:2])
        month = int(new_text[3:5])
        year = int(new_text[6:])

        if day < 1 or day > 31:
            return False
        if month < 1 or month > 12:
            return False
        if year < 1900 or year > 2100:
            return False

        return False  # Siempre False porque manejamos la actualización manual

    def _load_module_and_lot(self):
        """Carga el módulo y lote seleccionado mostrando los corrales"""
        module = self.selected_module.get()
        lot = self.selected_lot.get()

        if not module:
            messagebox.showwarning("Advertencia", "Seleccione un módulo")
            return

        if not lot:
            messagebox.showwarning("Advertencia", "Seleccione un lote")
            return

        # Limpiar corrales anteriores
        for widget in self.corrals_frame.winfo_children():
            widget.destroy()

        # Mostrar los corrales
        self._show_corrals()

    def _update_lots_dropdown(self, event=None):
        """Actualiza el dropdown de lotes sin cargar automáticamente"""
        selected_module = self.selected_module.get()
        if selected_module in self.data_manager.modules:
            lots = list(self.data_manager.modules[selected_module].keys())
            self.lot_dropdown["values"] = lots
            if lots:
                self.lot_dropdown.current(0)

    def _update_modules_dropdown(self):
        """Actualiza el dropdown de módulos"""
        modules = list(self.data_manager.modules.keys())
        self.module_dropdown["values"] = modules
        if modules:
            self.module_dropdown.current(0)
            self._update_lots_dropdown()

    def _load_production_data(self):
        """Carga los datos de producción existentes para la fecha seleccionada"""
        fecha = self.production_date.get()
        module = self.selected_module.get()
        lot = self.selected_lot.get()

        if not all([fecha, module, lot]):
            messagebox.showwarning("Advertencia", "Seleccione fecha, módulo y lote")
            return

        # Cargar datos existentes
        production_data = self.data_manager.get_production_data(module, lot, fecha)

        if not production_data:
            messagebox.showinfo("Información", "No hay datos guardados para esta fecha")
            return

        # Mostrar los datos en los campos correspondientes
        self._show_corrals(production_data=production_data)

    def _show_corrals(self, production_data=None):
        """Versión con scrollbar para mostrar todos los corrales"""
        # Limpiar frame anterior
        for widget in self.corrals_frame.winfo_children():
            widget.destroy()

        module = self.selected_module.get()
        lot = self.selected_lot.get()

        if not module or not lot or module not in self.data_manager.modules:
            return

        try:
            # Crear un canvas con scrollbar
            container = ttk.Frame(self.corrals_frame)
            container.pack(fill=tk.BOTH, expand=True)

            canvas = tk.Canvas(container)
            scrollbar = ttk.Scrollbar(
                container, orient="vertical", command=canvas.yview
            )
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Usar grid para mejor disposición
            canvas.grid(row=0, column=0, sticky="nsew")
            scrollbar.grid(row=0, column=1, sticky="ns")
            container.grid_rowconfigure(0, weight=1)
            container.grid_columnconfigure(0, weight=1)

            # Configurar el mouse wheel para scroll
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

            canvas.bind_all("<MouseWheel>", _on_mousewheel)

            lote_data = self.data_manager.modules[module].get(lot, {})
            casetas = lote_data.get("casetas", {})

            # Lista global para mantener el orden de todos los campos
            all_entries = []

            # Mostrar cada caseta en el frame con scroll
            for caseta_name, corrales in casetas.items():
                # Obtener datos de producción para esta caseta
                prod_data_for_caseta = {}
                if production_data and isinstance(production_data, dict):
                    prod_data_for_caseta = production_data.get(caseta_name, [])
                    if isinstance(prod_data_for_caseta, list):
                        prod_data_for_caseta = {
                            str(corral.get("nombre", "")): corral
                            for corral in prod_data_for_caseta
                            if isinstance(corral, dict) and "nombre" in corral
                        }

                caseta_frame = self._create_caseta_section(
                    scrollable_frame,  # Usamos el frame scrollable
                    caseta_name,
                    corrales,
                    prod_data_for_caseta,
                    all_entries,
                )

            # Configurar navegación con Enter para todos los campos
            for i, (nido, piso) in enumerate(all_entries):
                nido.bind("<Return>", lambda e, entry=piso: entry.focus())

                if i < len(all_entries) - 1:
                    next_entry = all_entries[i + 1][0]
                else:
                    next_entry = all_entries[0][0] if all_entries else None

                if next_entry:
                    piso.bind("<Return>", lambda e, entry=next_entry: entry.focus())

        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudieron cargar los corrales: {str(e)}"
            )
            import traceback

            traceback.print_exc()

    def _create_caseta_section(
        self, parent, caseta_name, corrales, production_map, all_entries_ref
    ):
        """Crea una sección para una caseta con navegación completa por Enter"""
        caseta_frame = ttk.LabelFrame(parent, text=f"Caseta: {caseta_name}")
        caseta_frame.pack(fill=tk.X, padx=5, pady=5, ipadx=5, ipady=5)

        # Cabecera
        header_frame = ttk.Frame(caseta_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(header_frame, text="Corral", width=10).pack(side=tk.LEFT)
        ttk.Label(header_frame, text="Huevos Nido", width=15).pack(
            side=tk.LEFT, padx=10
        )
        ttk.Label(header_frame, text="Huevos Piso", width=15).pack(side=tk.LEFT)

        ttk.Separator(caseta_frame).pack(fill=tk.X, pady=2)

        # Lista de campos en esta caseta
        caseta_entries = []

        for corral in corrales:
            if not isinstance(corral, dict):
                continue

            corral_name = str(corral.get("nombre", "Corral"))
            # Acceso seguro a los datos de producción
            prod_data = {}
            if isinstance(production_map, dict):
                prod_data = production_map.get(corral_name, {})
            elif hasattr(production_map, "get"):
                prod_data = production_map.get(corral_name, {})

            row_frame = ttk.Frame(caseta_frame)
            row_frame.pack(fill=tk.X, pady=2)

            # Nombre del corral
            ttk.Label(row_frame, text=corral_name, width=10).pack(side=tk.LEFT)

            # Campo huevos nido
            eggs_nest_var = tk.StringVar(value=str(prod_data.get("huevos_nido", 0)))
            eggs_nest = ttk.Entry(row_frame, textvariable=eggs_nest_var, width=15)
            eggs_nest.pack(side=tk.LEFT, padx=10)

            # Campo huevos piso
            eggs_floor_var = tk.StringVar(value=str(prod_data.get("huevos_piso", 0)))
            eggs_floor = ttk.Entry(row_frame, textvariable=eggs_floor_var, width=15)
            eggs_floor.pack(side=tk.LEFT)

            # Guardar referencias
            caseta_entries.append((eggs_nest, eggs_floor))
            corral["_eggs_nest_var"] = eggs_nest_var
            corral["_eggs_floor_var"] = eggs_floor_var

        # Agregar campos de esta caseta a la lista global
        all_entries_ref.extend(caseta_entries)

        # Configurar selección al hacer clic (como antes)
        for eggs_nest, eggs_floor in caseta_entries:
            eggs_nest.bind(
                "<FocusIn>", lambda e, entry=eggs_nest: entry.select_range(0, tk.END)
            )
            eggs_nest.bind(
                "<Button-1>",
                lambda e, entry=eggs_nest: (
                    entry.select_range(0, tk.END)
                    if not entry.selection_present()
                    else None
                ),
            )

            eggs_floor.bind(
                "<FocusIn>", lambda e, entry=eggs_floor: entry.select_range(0, tk.END)
            )
            eggs_floor.bind(
                "<Button-1>",
                lambda e, entry=eggs_floor: (
                    entry.select_range(0, tk.END)
                    if not entry.selection_present()
                    else None
                ),
            )

        return caseta_frame

    def _find_next_caseta(self, current_caseta):
        """Busca la siguiente caseta en la interfaz"""
        # Obtener todos los widgets hermanos
        siblings = current_caseta.master.winfo_children()

        # Encontrar la posición de la caseta actual
        try:
            current_index = siblings.index(current_caseta)
        except ValueError:
            return None

        # Buscar la siguiente caseta
        for sibling in siblings[current_index + 1 :]:
            if isinstance(sibling, ttk.LabelFrame):
                # Encontrar el primer campo de entrada en la siguiente caseta
                for child in sibling.winfo_children():
                    if isinstance(child, ttk.Frame):
                        for subchild in child.winfo_children():
                            if isinstance(subchild, ttk.Entry):
                                return subchild
        return None

    def _focus_next_entry(self, event, current_index, all_entries, field_type):
        """Maneja la navegación entre campos al presionar Enter"""
        if field_type == "nido":
            # Desde nido, ir al piso del mismo corral
            next_entry = all_entries[current_index][1]  # Campo piso del mismo corral
        elif field_type == "piso":
            # Desde piso, ir al nido del siguiente corral
            if current_index + 1 < len(all_entries):
                next_entry = all_entries[current_index + 1][
                    0
                ]  # Campo nido del siguiente corral
            else:
                # Si es el último corral, volver al primero
                next_entry = all_entries[0][0] if all_entries else None

        if next_entry:
            next_entry.focus()
            next_entry.select_range(0, tk.END)
        return "break"  # Evita el comportamiento por defecto de Enter

    def _save_production_data(self):
        """Guarda los datos con validación de fecha corregida"""
        # Obtener la fecha como string
        fecha_str = self.production_date.get()
        if not fecha_str:
            messagebox.showerror(
                "Error", "Complete todos los campos de fecha (DD/MM/AAAA)"
            )
            return False

        try:
            # Convertir a objeto datetime para validación
            fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y")

            # Verificar que no sean placeholders
            if "DD" in fecha_str or "MM" in fecha_str or "AAAA" in fecha_str:
                raise ValueError("Fecha incompleta")

        except ValueError as e:
            messagebox.showerror("Error", f"Fecha inválida: {str(e)}")
            return False

        # Obtener módulo y lote
        module = self.selected_module.get()
        lot = self.selected_lot.get()
        fecha = self.date_entry.get()

        if not all([module, lot]):
            messagebox.showwarning("Advertencia", "Seleccione un módulo y un lote")
            return False

        try:
            # Validar formato de fecha
            datetime.strptime(fecha, "%d/%m/%Y")
        except ValueError:
            messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/AAAA")
            return

        try:
            # Verificar si ya existen datos para esta fecha
            existing_data = self.data_manager.get_production_data(module, lot, fecha)
            if existing_data:
                # Preguntar si desea sobrescribir
                if not messagebox.askyesno(
                    "Confirmar Sobrescritura",
                    f"Ya existen datos guardados para la fecha {fecha}.\n¿Desea sobrescribirlos?",
                ):
                    return False

            # Recopilar datos de producción
            production_data = {}
            casetas = self.data_manager.modules[module][lot].get("casetas", {})

            for caseta_name, corrales in casetas.items():
                production_data[caseta_name] = []
                for corral in corrales:
                    if isinstance(corral, dict):
                        # Obtener valores de los campos de entrada directamente
                        eggs_nest = 0
                        eggs_floor = 0

                        # Manejar ambos casos: con StringVar o con Entry directo
                        if "_eggs_nest_var" in corral:
                            eggs_nest = int(corral["_eggs_nest_var"].get() or 0)
                        elif "_entry_nido" in corral:
                            eggs_nest = int(corral["_entry_nido"].get() or 0)

                        if "_eggs_floor_var" in corral:
                            eggs_floor = int(corral["_eggs_floor_var"].get() or 0)
                        elif "_entry_piso" in corral:
                            eggs_floor = int(corral["_entry_piso"].get() or 0)

                        corral_data = {
                            "nombre": corral.get("nombre"),
                            "huevos_nido": eggs_nest,
                            "huevos_piso": eggs_floor,
                        }
                        production_data[caseta_name].append(corral_data)

            # Guardar en el data_manager
            if self.data_manager.save_production_data(
                module, lot, fecha, production_data
            ):
                messagebox.showinfo("Éxito", "Producción guardada correctamente")
            else:
                messagebox.showerror("Error", "No se pudo guardar la producción")

        except ValueError:
            messagebox.showerror("Error", "Ingrese valores numéricos válidos")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
