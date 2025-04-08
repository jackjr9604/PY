import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font

class EditTab:
    def __init__(self, parent, data_manager):
        self.data_manager = data_manager
        self.frame = ttk.Frame(parent)
        self.style = ttk.Style()
        self.configure_styles()
        self.create_main_ui()
        
    def configure_styles(self):
        """Configura estilos personalizados para la interfaz"""
        self.style.configure('TFrame',
                   background='#f5f5f5')  # Fondo gris claro
        
        self.style.configure('TEntry',
                   fieldbackground='white',
                   foreground='black',
                   insertcolor='black')
        
        self.style.configure('TLabel',
                   background='#f5f5f5',
                   foreground='black')
        
        # Estilo base
        self.style.theme_use('clam')  # Usamos el tema 'clam' que tiene mejor contraste
    
        # Configurar colores principales
        self.style.configure('.', 
                            background='#f0f0f0',  # Fondo general más claro
                            foreground='black')    # Texto negro por defecto
    
        # Estilo para títulos
        self.style.configure('Title.TLabel', 
                        font=('Helvetica', 14, 'bold'),
                        foreground='#2c3e50')
    
        # Estilo para el treeview de cabecera
        self.style.configure('Header.Treeview', 
                        font=('Helvetica', 10, 'bold'),
                        background='#3498db',
                        foreground='white')  # Texto blanco sobre fondo azul
    
        # Estilo para botones principales (verde)
        self.style.configure('Custom.TButton',
                        font=('Helvetica', 10, 'bold'),
                        padding=6,
                        background='#2ecc71',
                        foreground='black',  # Texto negro sobre fondo verde
                        borderwidth=1)
        self.style.map('Custom.TButton',
                    background=[('active', '#27ae60')],
                    foreground=[('active', 'black')])
    
        # Estilo para botones de edición (azul)
        self.style.configure('Edit.TButton',
                        font=('Helvetica', 10, 'bold'),
                        padding=6,
                        background='#3498db',
                        foreground='black',  # Texto negro sobre fondo azul
                        borderwidth=1)
        self.style.map('Edit.TButton',
                    background=[('active', '#2980b9')],
                    foreground=[('active', 'black')])
    
        # Estilo para botones de eliminación (rojo)
        self.style.configure('Delete.TButton',
                        font=('Helvetica', 10, 'bold'),
                        padding=6,
                        background='#e74c3c',
                        foreground='black',  # Texto negro sobre fondo rojo
                        borderwidth=1)
        self.style.map('Delete.TButton',
                    background=[('active', '#c0392b')],
                    foreground=[('active', 'black')])
    
        # Estilo para el treeview principal
        self.style.configure('Treeview',
                        background='white',
                        foreground='black',
                        fieldbackground='white',
                        rowheight=25)
        self.style.map('Treeview',
                    background=[('selected', '#3498db')],
                    foreground=[('selected', 'white')])
        

    def create_main_ui(self):
        """Crea la interfaz principal de edición"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.frame, padding=(10, 10, 10, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, 
                 text="Estructura Avícola", 
                 style='Title.TLabel').pack(side=tk.LEFT)
        
        # Botón para agregar módulo
        ttk.Button(title_frame, 
                  text="+ Agregar Módulo", 
                  style='Custom.TButton',
                  command=self.add_module).pack(side=tk.RIGHT)

        # Contenedor para árbol y botones
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview con estructura jerárquica
        self.tree = ttk.Treeview(content_frame, 
                                columns=('type', 'details'),
                                show='tree headings',
                                selectmode='browse')
        
        # Configurar columnas
        self.tree.heading('#0', text='Nombre', anchor=tk.W)
        self.tree.heading('type', text='Tipo', anchor=tk.W)
        self.tree.heading('details', text='Detalles', anchor=tk.W)
        
        self.tree.column('#0', width=200, stretch=tk.YES)
        self.tree.column('type', width=100, stretch=tk.NO)
        self.tree.column('details', width=150, stretch=tk.YES)

        # Scrollbars
        vsb = ttk.Scrollbar(content_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(content_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Layout del treeview y scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Configurar pesos de grid
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)

        # Panel de botones de acción
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))

        self.btn_add_lote = ttk.Button(action_frame, 
                                     text="+ Agregar Lote", 
                                     style='Custom.TButton',
                                     state=tk.DISABLED,
                                     command=self.add_lote)
        self.btn_add_lote.pack(side=tk.LEFT, padx=5)

        self.btn_add_caseta = ttk.Button(action_frame, 
                                       text="+ Agregar Caseta", 
                                       style='Custom.TButton',
                                       state=tk.DISABLED,
                                       command=self.add_caseta)
        self.btn_add_caseta.pack(side=tk.LEFT, padx=5)

        self.btn_edit = ttk.Button(action_frame, 
                                 text="✏ Editar", 
                                 style='Edit.TButton',
                                 state=tk.DISABLED,
                                 command=self.edit_item)
        self.btn_edit.pack(side=tk.LEFT, padx=5)

        self.btn_delete = ttk.Button(action_frame, 
                                   text="🗑 Eliminar", 
                                   style='Delete.TButton',
                                   state=tk.DISABLED,
                                   command=self.delete_item)
        self.btn_delete.pack(side=tk.LEFT, padx=5)

        # Eventos
        self.populate_tree()
        self.tree.bind("<<TreeviewSelect>>", self.update_buttons)
        self.tree.bind("<Double-1>", self.on_double_click)

    def populate_tree(self):
        """Llena el árbol con los datos actuales"""
        self.tree.delete(*self.tree.get_children())
        
        for module_name, lots in self.data_manager.modules.items():
            module_id = self.tree.insert("", "end", 
                                       text=module_name,
                                       values=("Módulo", f"{len(lots)} lotes"),
                                       tags=("module",))
            
            for lote_name, casetas in lots.items():
                lote_id = self.tree.insert(module_id, "end", 
                                         text=lote_name,
                                         values=("Lote", f"{len(casetas)} casetas"),
                                         tags=("lote",))
                
                for caseta_name, corrales in casetas.items():
                    caseta_id = self.tree.insert(lote_id, "end", 
                                               text=caseta_name,
                                               values=("Caseta", f"{len(corrales)} corrales"),
                                               tags=("caseta",))

    def update_buttons(self, event=None):
        """Actualiza el estado de los botones según la selección"""
        selected = self.tree.focus()
        if not selected:
            self.btn_add_lote.config(state=tk.DISABLED)
            self.btn_add_caseta.config(state=tk.DISABLED)
            self.btn_edit.config(state=tk.DISABLED)
            self.btn_delete.config(state=tk.DISABLED)
            return

        tags = self.tree.item(selected, "tags")
        if "module" in tags:
            self.btn_add_lote.config(state=tk.NORMAL)
            self.btn_add_caseta.config(state=tk.DISABLED)
            self.btn_edit.config(state=tk.NORMAL)
            self.btn_delete.config(state=tk.NORMAL)
        elif "lote" in tags:
            self.btn_add_lote.config(state=tk.DISABLED)
            self.btn_add_caseta.config(state=tk.NORMAL)
            self.btn_edit.config(state=tk.NORMAL)
            self.btn_delete.config(state=tk.NORMAL)
        elif "caseta" in tags:
            self.btn_add_lote.config(state=tk.DISABLED)
            self.btn_add_caseta.config(state=tk.DISABLED)
            self.btn_edit.config(state=tk.NORMAL)
            self.btn_delete.config(state=tk.NORMAL)
            self.tree.bind("<Double-1>", self.on_double_click)
        else:
            self.btn_add_lote.config(state=tk.DISABLED)
            self.btn_add_caseta.config(state=tk.DISABLED)
            self.btn_edit.config(state=tk.DISABLED)
            self.btn_delete.config(state=tk.DISABLED)

    def on_double_click(self, event):
        """Maneja el doble click en items"""
        item = self.tree.focus()
        if not item:
            return

        tags = self.tree.item(item, "tags")
        if "caseta" in tags:
            parent = self.tree.parent(item)
            grandparent = self.tree.parent(parent)
            
            module = self.tree.item(grandparent, "text")
            lote = self.tree.item(parent, "text")
            caseta = self.tree.item(item, "text")
            
            self.manage_caseta(module, lote, caseta)
        else:
            self.edit_item()

    def add_module(self):
        """Agrega un nuevo módulo"""
        name = self.get_input("Nuevo Módulo", "Nombre del módulo:")
        if name and name not in self.data_manager.modules:
            self.data_manager.modules[name] = {}
            self.data_manager.save_data()
            self.populate_tree()
            self.expand_new_item(name)

    def add_lote(self):
        """Agrega un nuevo lote"""
        selected = self.tree.focus()
        if not selected:
            return

        module_name = self.tree.item(selected, "text")
        name = self.get_input("Nuevo Lote", f"Nombre del lote para {module_name}:")
        if name and name not in self.data_manager.modules[module_name]:
            self.data_manager.modules[module_name][name] = {}
            self.data_manager.save_data()
            self.populate_tree()
            self.expand_new_item(module_name, name)

    def add_caseta(self):
        """Agrega una nueva caseta"""
        selected = self.tree.focus()
        if not selected:
            return

        parent = self.tree.parent(selected)
        module_name = self.tree.item(parent, "text")
        lote_name = self.tree.item(selected, "text")

        name = self.get_input("Nueva Caseta", f"Nombre de caseta para {lote_name}:")
        if name:
            if lote_name not in self.data_manager.modules[module_name]:
                self.data_manager.modules[module_name][lote_name] = {}
            self.data_manager.modules[module_name][lote_name][name] = []
            self.data_manager.save_data()
            self.populate_tree()
            self.expand_new_item(module_name, lote_name, name)

    def edit_item(self):
        """Edita el nombre de un elemento existente"""
        selected = self.tree.focus()
        if not selected:
            return

        old_name = self.tree.item(selected, "text")
        tags = self.tree.item(selected, "tags")
        
        if "module" in tags:
            new_name = self.get_input("Editar Módulo", "Nuevo nombre del módulo:", old_name)
            if new_name and new_name != old_name:
                if new_name in self.data_manager.modules:
                    messagebox.showerror("Error", "Ya existe un módulo con ese nombre")
                    return
                
                self.data_manager.modules[new_name] = self.data_manager.modules.pop(old_name)
                self.data_manager.save_data()
                self.populate_tree()
                self.expand_new_item(new_name)
                
        elif "lote" in tags:
            parent = self.tree.parent(selected)
            module_name = self.tree.item(parent, "text")
            
            new_name = self.get_input("Editar Lote", "Nuevo nombre del lote:", old_name)
            if new_name and new_name != old_name:
                if new_name in self.data_manager.modules[module_name]:
                    messagebox.showerror("Error", "Ya existe un lote con ese nombre")
                    return
                
                self.data_manager.modules[module_name][new_name] = self.data_manager.modules[module_name].pop(old_name)
                self.data_manager.save_data()
                self.populate_tree()
                self.expand_new_item(module_name, new_name)
                
        elif "caseta" in tags:
            parent = self.tree.parent(selected)
            grandparent = self.tree.parent(parent)
            module_name = self.tree.item(grandparent, "text")
            lote_name = self.tree.item(parent, "text")
            
            new_name = self.get_input("Editar Caseta", "Nuevo nombre de la caseta:", old_name)
            if new_name and new_name != old_name:
                if new_name in self.data_manager.modules[module_name][lote_name]:
                    messagebox.showerror("Error", "Ya existe una caseta con ese nombre")
                    return
                
                self.data_manager.modules[module_name][lote_name][new_name] = \
                    self.data_manager.modules[module_name][lote_name].pop(old_name)
                self.data_manager.save_data()
                self.populate_tree()
                self.expand_new_item(module_name, lote_name, new_name)

    def delete_item(self):
        """Elimina un elemento seleccionado"""
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un elemento para eliminar")
            return

        item_text = self.tree.item(selected, "text")
        tags = self.tree.item(selected, "tags")

        if not messagebox.askyesno("Confirmar", f"¿Eliminar '{item_text}' y todo su contenido?"):
            return

        if "module" in tags:
            del self.data_manager.modules[item_text]
        elif "lote" in tags:
            module = self.tree.item(self.tree.parent(selected), "text")
            del self.data_manager.modules[module][item_text]
        elif "caseta" in tags:
            lote = self.tree.item(self.tree.parent(selected), "text")
            module = self.tree.item(self.tree.parent(self.tree.parent(selected)), "text")
            del self.data_manager.modules[module][lote][item_text]

        self.data_manager.save_data()
        self.populate_tree()

    def expand_new_item(self, module_name=None, lote_name=None, caseta_name=None):
        """Expande los nodos para mostrar el nuevo elemento"""
        if module_name:
            for child in self.tree.get_children():
                if self.tree.item(child, "text") == module_name:
                    self.tree.item(child, open=True)
                    if lote_name:
                        for lote_child in self.tree.get_children(child):
                            if self.tree.item(lote_child, "text") == lote_name:
                                self.tree.item(lote_child, open=True)
                                if caseta_name:
                                    for caseta_child in self.tree.get_children(lote_child):
                                        if self.tree.item(caseta_child, "text") == caseta_name:
                                            self.tree.selection_set(caseta_child)
                                            self.tree.focus(caseta_child)
                                            break
                                break
                    break

    def manage_caseta(self, module_name, lote_name, caseta_name):
        """Gestiona los corrales de una caseta específica"""
        caseta_window = tk.Toplevel(self.frame)
        caseta_window.title(f"Gestión de Corrales: {module_name} > {lote_name} > {caseta_name}")
        caseta_window.geometry("800x600")
        caseta_window.transient(self.frame)
        caseta_window.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(caseta_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, 
                 text=f"Gestión de Corrales - {caseta_name}", 
                 style='Title.TLabel').pack(pady=(0, 10))
        
        # Treeview para corrales
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("corral", "hembras", "machos", "total")
        corrales_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Configurar columnas
        corrales_tree.heading("corral", text="Corral")
        corrales_tree.heading("hembras", text="Hembras")
        corrales_tree.heading("machos", text="Machos")
        corrales_tree.heading("total", text="Total")
        
        corrales_tree.column("corral", width=150, anchor="center")
        corrales_tree.column("hembras", width=100, anchor="center")
        corrales_tree.column("machos", width=100, anchor="center")
        corrales_tree.column("total", width=100, anchor="center")
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=corrales_tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=corrales_tree.xview)
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
        
        ttk.Button(btn_frame, 
                  text="+ Agregar Corrales", 
                  style='Custom.TButton',
                  command=lambda: self.add_corrales(module_name, lote_name, caseta_name, corrales_tree)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, 
                  text="✏ Editar", 
                  style='Edit.TButton',
                  command=lambda: self.edit_corral(module_name, lote_name, caseta_name, corrales_tree)).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, 
                  text="🗑 Eliminar", 
                  style='Delete.TButton',
                  command=lambda: self.delete_corrales(module_name, lote_name, caseta_name, corrales_tree)).pack(side=tk.LEFT, padx=5)
        
        # Cargar datos
        self.load_corrales_data(module_name, lote_name, caseta_name, corrales_tree)
        
        # Evento de doble click para editar
        corrales_tree.bind("<Double-1>", lambda e: self.edit_corral(module_name, lote_name, caseta_name, corrales_tree))

    def load_corrales_data(self, module_name, lote_name, caseta_name, tree):
        """Carga los corrales en el Treeview"""
        tree.delete(*tree.get_children())
        corrales = self.data_manager.modules[module_name][lote_name][caseta_name]
        
        for corral in corrales:
            hembras = corral.get("hembras", 0)
            machos = corral.get("machos", 0)
            total = hembras + machos
            tree.insert("", "end", values=(corral["nombre"], hembras, machos, total))

    def add_corrales(self, module_name, lote_name, caseta_name, tree):
        """Agrega nuevos corrales a una caseta"""
        count = self.get_input("Agregar Corrales", "Cantidad de corrales a agregar:", number=True)
        if count is None or count <= 0:
            return

        corrales = self.data_manager.modules[module_name][lote_name][caseta_name]
        next_num = len(corrales) + 1
        
        for _ in range(count):
            corral_data = {
                "nombre": str(next_num),
                "hembras": 0,
                "machos": 0
            }
            corrales.append(corral_data)
            tree.insert("", "end", values=(corral_data["nombre"], 0, 0, 0))
            next_num += 1
        
        self.data_manager.save_data()

    def delete_corrales(self, module_name, lote_name, caseta_name, tree):
        """Elimina los corrales seleccionados"""
        selected_items = tree.selection()
        if not selected_items:
            messagebox.showwarning("Advertencia", "Seleccione al menos un corral")
            return

        corrales_a_eliminar = [tree.item(item, "values")[0] for item in selected_items]
        
        if not messagebox.askyesno("Confirmar", f"¿Eliminar {len(corrales_a_eliminar)} corral(es)?"):
            return

        # Filtrar los corrales que no están seleccionados
        corrales = self.data_manager.modules[module_name][lote_name][caseta_name]
        self.data_manager.modules[module_name][lote_name][caseta_name] = [
            c for c in corrales 
            if c["nombre"] not in corrales_a_eliminar
        ]

        # Eliminar de la vista
        for item in selected_items:
            tree.delete(item)

        self.data_manager.save_data()

    def edit_corral(self, module_name, lote_name, caseta_name, tree):
        """Permite editar los datos de un corral"""
        item = tree.focus()
        column = tree.identify_column(tree.winfo_pointerx() - tree.winfo_rootx())
        
        # Obtener información del ítem seleccionado
        col_index = int(column[1]) - 1
        values = list(tree.item(item, "values"))
        corral_name = values[0]
        
        # Determinar qué estamos editando
        if column == "#1":  # Editando el nombre/número del corral
            col_name = "nombre"
            current_value = values[0]
        elif column == "#2":  # Editando hembras
            col_name = "hembras"
            current_value = values[1]
        elif column == "#3":  # Editando machos
            col_name = "machos"
            current_value = values[2]
        else:
            return  # No editable
        
        # Obtener coordenadas y dimensiones de la celda
        bbox = tree.bbox(item, column)
        if not bbox:
            return
        
        # Crear un Entry directamente sobre la celda
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
                
                # Actualizar los datos en memoria
                for corral in self.data_manager.modules[module_name][lote_name][caseta_name]:
                    if corral["nombre"] == corral_name:
                        corral[col_name] = new_value
                        break
                
                # Actualizar la vista
                if col_name == "nombre":
                    values[0] = new_value
                elif col_name == "hembras":
                    values[1] = new_value
                    values[3] = new_value + int(values[2])
                elif col_name == "machos":
                    values[2] = new_value
                    values[3] = int(values[1]) + new_value
                
                tree.item(item, values=values)
                self.data_manager.save_data()
                entry.destroy()
            except ValueError:
                messagebox.showerror("Error", "Ingrese un valor válido")
                entry.focus_set()
        
        def on_focus_out(event):
            if str(event.widget) == str(entry):
                save_edit()
        
        # Configurar eventos
        entry.bind("<Return>", lambda e: save_edit())
        entry.bind("<FocusOut>", on_focus_out)
        entry.bind("<Escape>", lambda e: entry.destroy())

    def get_input(self, title, prompt, number=False, default=""):
        """Muestra un diálogo para obtener entrada del usuario"""
        dialog = tk.Toplevel(self.frame)
        dialog.title(title)
        dialog.transient(self.frame)
        dialog.grab_set()

        ttk.Label(dialog, text=prompt).pack(padx=10, pady=5)
        entry = ttk.Entry(dialog)
        entry.pack(padx=10, pady=5)
        entry.insert(0, default)
        entry.focus_set()

        result = []
        def on_ok():
            try:
                if number:
                    val = int(entry.get())
                else:
                    val = entry.get().strip()
                result.append(val)
                dialog.grab_release()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Ingrese un valor válido", parent=dialog)
                entry.focus_set()

        ttk.Button(dialog, text="Aceptar", command=on_ok).pack(pady=5)
        dialog.bind("<Return>", lambda e: on_ok())

        def on_close():
            dialog.grab_release()
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        dialog.wait_window()
        
        return result[0] if result else None