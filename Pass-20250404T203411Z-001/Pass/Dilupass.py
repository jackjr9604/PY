import json
import hashlib
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog, scrolledtext
from tkinter import font as tkfont
from datetime import datetime

DATABASE_FILE = "password_manager.json"

class PasswordManager:
    def __init__(self, root):
        self.root = root
        self.root.title("dilupass")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Variables para configuración
        self.show_password = tk.BooleanVar(value=False)
        self.visible_columns = {
            'Sitio': True,
            'Usuario': True,
            'Contraseña': False,
            'Fecha': False,
            'Categoría': False
        }
        
        self.setup_menu()
        self.setup_ui()
        self.initialize_database()
        
        if not self.check_master_password_set():
            self.setup_master_password()
        else:
            self.ask_master_password()

    def setup_menu(self):
        """Configura la barra de menú"""
        menubar = tk.Menu(self.root)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exportar a TXT", command=self.export_to_txt)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        
        # Menú Editar
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Añadir Contraseña", command=self.show_add_password_dialog)
        edit_menu.add_command(label="Editar Contraseña", command=self.edit_password)
        edit_menu.add_command(label="Eliminar Contraseña", command=self.delete_password)
        edit_menu.add_separator()
        edit_menu.add_command(label="Reordenar Contraseñas", command=self.reorder_passwords)
        menubar.add_cascade(label="Editar", menu=edit_menu)
        
        # Menú Ver
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_checkbutton(label="Mostrar Contraseñas", variable=self.show_password, 
                                command=self.toggle_password_visibility)
        view_menu.add_separator()
        view_menu.add_command(label="Configurar Columnas", command=self.configure_columns)
        menubar.add_cascade(label="Ver", menu=view_menu)
        
        # Menú Opciones
        options_menu = tk.Menu(menubar, tearoff=0)
        options_menu.add_command(label="Cambiar Clave Maestra", command=self.change_master_password)
        options_menu.add_command(label="Configuración Avanzada", command=self.show_advanced_options)
        menubar.add_cascade(label="Opciones", menu=options_menu)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Manual de Uso", command=self.show_help)
        help_menu.add_command(label="Acerca de", command=self.show_about)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        
        self.root.config(menu=menubar)

    def setup_ui(self):
        """Configura la interfaz de usuario con tabla"""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para botones
        self.btn_frame = ttk.Frame(self.main_frame)
        self.btn_frame.pack(fill=tk.X, pady=5)
        
        # Barra de búsqueda
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.btn_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_passwords)
        
        # Botón de búsqueda
        ttk.Button(self.btn_frame, text="Buscar", 
                  command=self.search_passwords).pack(side=tk.LEFT, padx=5)
        
        # Frame para la tabla
        self.table_frame = ttk.Frame(self.main_frame)
        self.table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear tabla (Treeview)
        self.tree = ttk.Treeview(self.table_frame, columns=('Sitio', 'Usuario', 'Contraseña', 'Fecha', 'Categoría'), 
                                selectmode='browse')
        
        # Configurar columnas
        self.tree.heading('#0', text='ID')
        self.tree.heading('Sitio', text='Sitio Web/Aplicación')
        self.tree.heading('Usuario', text='Nombre de Usuario')
        self.tree.heading('Contraseña', text='Contraseña')
        self.tree.heading('Fecha', text='Fecha Creación')
        self.tree.heading('Categoría', text='Categoría')
        
        self.tree.column('#0', width=50, stretch=tk.NO)
        self.tree.column('Sitio', width=200, anchor=tk.W)
        self.tree.column('Usuario', width=150, anchor=tk.W)
        self.tree.column('Contraseña', width=150, anchor=tk.W)
        self.tree.column('Fecha', width=100, anchor=tk.W)
        self.tree.column('Categoría', width=100, anchor=tk.W)
        
        # Ocultar columnas por defecto
        self.tree.column('Contraseña', stretch=tk.NO, width=0, minwidth=0)
        self.tree.column('Fecha', stretch=tk.NO, width=0, minwidth=0)
        self.tree.column('Categoría', stretch=tk.NO, width=0, minwidth=0)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", 
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Empaquetar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind doble click para mostrar contraseña
        self.tree.bind("<Double-1>", self.show_password_details)

    def initialize_database(self):
        """Inicializa la base de datos si no existe"""
        if not os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, 'w') as f:
                json.dump({"master_hash": "", "passwords": {}}, f)

    def check_master_password_set(self):
        """Verifica si la contraseña maestra está configurada"""
        with open(DATABASE_FILE, 'r') as f:
            data = json.load(f)
        return bool(data["master_hash"])

    def hash_password(self, password):
        """Retorna el hash SHA-256 de la contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()

    def setup_master_password(self):
        """Configura la contraseña maestra inicial"""
        password = simpledialog.askstring("Configuración Inicial", 
                                        "Cree una clave maestra segura (mínimo 8 caracteres):", 
                                        show='*')
        if not password or len(password) < 8:
            messagebox.showerror("Error", "La clave debe tener al menos 8 caracteres")
            return self.setup_master_password()
        
        confirm = simpledialog.askstring("Confirmación", 
                                       "Confirme su clave maestra:", 
                                       show='*')
        if password != confirm:
            messagebox.showerror("Error", "Las claves no coinciden")
            return self.setup_master_password()
        
        with open(DATABASE_FILE, 'r+') as f:
            data = json.load(f)
            data["master_hash"] = self.hash_password(password)
            f.seek(0)
            json.dump(data, f)
            f.truncate()
        
        messagebox.showinfo("Éxito", "Clave maestra configurada correctamente")
        self.load_passwords()

    def ask_master_password(self):
        """Pide la contraseña maestra"""
        attempts = 3
        with open(DATABASE_FILE, 'r') as f:
            stored_hash = json.load(f)["master_hash"]
        
        while attempts > 0:
            password = simpledialog.askstring("Autenticación", 
                                            "Ingrese su clave maestra:", 
                                            show='*')
            if password and self.hash_password(password) == stored_hash:
                self.load_passwords()
                return True
            
            attempts -= 1
            if attempts > 0:
                messagebox.showerror("Error", 
                                   f"Clave incorrecta. Intentos restantes: {attempts}")
        
        messagebox.showerror("Error", "Demasiados intentos fallidos. Saliendo...")
        self.root.destroy()
        return False

    def show_add_password_dialog(self):
        """Muestra el diálogo para añadir una nueva contraseña"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Añadir Nueva Contraseña")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        
        # Variables para los campos
        self.website_var = tk.StringVar()
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.category_var = tk.StringVar(value="General")
        
        # Formulario
        ttk.Label(dialog, text="Sitio Web/Aplicación:").pack(pady=(10, 0))
        ttk.Entry(dialog, textvariable=self.website_var, width=40).pack()
        
        ttk.Label(dialog, text="Nombre de Usuario:").pack(pady=(10, 0))
        ttk.Entry(dialog, textvariable=self.username_var, width=40).pack()
        
        ttk.Label(dialog, text="Contraseña:").pack(pady=(10, 0))
        ttk.Entry(dialog, textvariable=self.password_var, width=40, show='*').pack()
        
        ttk.Label(dialog, text="Categoría:").pack(pady=(10, 0))
        ttk.Entry(dialog, textvariable=self.category_var, width=40).pack()
        
        # Botones
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Guardar", 
                  command=lambda: self.save_password(dialog)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def save_password(self, dialog):
        """Guarda la nueva contraseña en la base de datos"""
        website = self.website_var.get()
        username = self.username_var.get()
        password = self.password_var.get()
        category = self.category_var.get()
        
        if not all([website, username, password]):
            messagebox.showerror("Error", "Todos los campos son obligatorios")
            return
        
        with open(DATABASE_FILE, 'r+') as f:
            data = json.load(f)
            data["passwords"][website] = {
                "username": username,
                "password": password,
                "category": category,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            f.seek(0)
            json.dump(data, f)
            f.truncate()
        
        messagebox.showinfo("Éxito", "Contraseña guardada correctamente")
        dialog.destroy()
        self.load_passwords()

    def load_passwords(self):
        """Carga las contraseñas en la tabla"""
        with open(DATABASE_FILE, 'r') as f:
            data = json.load(f)
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Llenar tabla
        for idx, (website, creds) in enumerate(data["passwords"].items(), 1):
            values = [
                website,
                creds.get("username", ""),
                creds.get("password", "") if self.show_password.get() else "••••••••",
                creds.get("date", ""),
                creds.get("category", "")
            ]
            self.tree.insert('', 'end', iid=idx, text=str(idx), values=values)

    def show_password_details(self, event):
        """Muestra los detalles de la contraseña al hacer doble click"""
        item = self.tree.selection()[0]
        website = self.tree.item(item, 'values')[0]
        
        with open(DATABASE_FILE, 'r') as f:
            data = json.load(f)
        
        if website in data["passwords"]:
            creds = data["passwords"][website]
            
            # Crear ventana de detalles
            detail_win = tk.Toplevel(self.root)
            detail_win.title(f"Detalles: {website}")
            detail_win.geometry("400x250")
            
            # Fuente para la contraseña
            bold_font = tkfont.Font(weight="bold", size=10)
            
            # Mostrar detalles
            ttk.Label(detail_win, text=f"Sitio Web/Aplicación:").pack(pady=(10, 0))
            ttk.Label(detail_win, text=website, font=bold_font).pack()
            
            ttk.Label(detail_win, text="Nombre de Usuario:").pack(pady=(10, 0))
            ttk.Label(detail_win, text=creds["username"], font=bold_font).pack()
            
            ttk.Label(detail_win, text="Contraseña:").pack(pady=(10, 0))
            ttk.Label(detail_win, text=creds["password"], font=bold_font).pack()
            
            if 'category' in creds:
                ttk.Label(detail_win, text="Categoría:").pack(pady=(10, 0))
                ttk.Label(detail_win, text=creds["category"], font=bold_font).pack()
            
            # Botón para copiar contraseña
            ttk.Button(detail_win, text="Copiar Contraseña", 
                      command=lambda: self.copy_to_clipboard(creds["password"])).pack(pady=10)

    def copy_to_clipboard(self, text):
        """Copia texto al portapapeles"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copiado", "La contraseña ha sido copiada al portapapeles")

    def search_passwords(self, event=None):
        """Busca contraseñas según el texto ingresado"""
        search_term = self.search_var.get().lower()
        
        with open(DATABASE_FILE, 'r') as f:
            data = json.load(f)
        
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Llenar tabla con resultados de búsqueda
        for idx, (website, creds) in enumerate(data["passwords"].items(), 1):
            if (search_term in website.lower() or 
                search_term in creds.get("username", "").lower() or 
                search_term in creds.get("category", "").lower()):
                
                values = [
                    website,
                    creds.get("username", ""),
                    creds.get("password", "") if self.show_password.get() else "••••••••",
                    creds.get("date", ""),
                    creds.get("category", "")
                ]
                self.tree.insert('', 'end', iid=idx, text=str(idx), values=values)

    def edit_password(self):
        """Edita una contraseña existente"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una contraseña para editar")
            return
        
        item = selected[0]
        website = self.tree.item(item, 'values')[0]
        
        with open(DATABASE_FILE, 'r') as f:
            data = json.load(f)
        
        if website not in data["passwords"]:
            messagebox.showerror("Error", "Contraseña no encontrada")
            return
        
        creds = data["passwords"][website]
        
        # Diálogo de edición
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Editar: {website}")
        dialog.geometry("400x300")
        
        # Variables
        website_var = tk.StringVar(value=website)
        username_var = tk.StringVar(value=creds.get("username", ""))
        password_var = tk.StringVar(value=creds.get("password", ""))
        category_var = tk.StringVar(value=creds.get("category", "General"))
        
        # Formulario
        ttk.Label(dialog, text="Sitio Web/Aplicación:").pack(pady=(10, 0))
        ttk.Entry(dialog, textvariable=website_var, width=40).pack()
        
        ttk.Label(dialog, text="Nombre de Usuario:").pack(pady=(10, 0))
        ttk.Entry(dialog, textvariable=username_var, width=40).pack()
        
        ttk.Label(dialog, text="Contraseña:").pack(pady=(10, 0))
        ttk.Entry(dialog, textvariable=password_var, width=40, show='*').pack()
        
        ttk.Label(dialog, text="Categoría:").pack(pady=(10, 0))
        ttk.Entry(dialog, textvariable=category_var, width=40).pack()
        
        # Botones
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Guardar", 
                  command=lambda: self.save_edited_password(
                      website, website_var.get(), username_var.get(), 
                      password_var.get(), category_var.get(), dialog)
                  ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="Cancelar", 
                  command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def save_edited_password(self, old_website, new_website, username, password, category, dialog):
        """Guarda los cambios de la contraseña editada"""
        if not all([new_website, username, password]):
            messagebox.showerror("Error", "Sitio, usuario y contraseña son obligatorios")
            return
        
        with open(DATABASE_FILE, 'r+') as f:
            data = json.load(f)
            
            # Si cambió el nombre del sitio, eliminar el viejo
            if old_website != new_website:
                if new_website in data["passwords"]:
                    messagebox.showerror("Error", "Ya existe una entrada para este sitio web")
                    return
                data["passwords"].pop(old_website, None)
            
            # Guardar los nuevos datos
            data["passwords"][new_website] = {
                "username": username,
                "password": password,
                "category": category if category else "General",
                "date": data["passwords"].get(old_website, {}).get("date", datetime.now().strftime("%Y-%m-%d"))
            }
            
            f.seek(0)
            json.dump(data, f)
            f.truncate()
        
        messagebox.showinfo("Éxito", "Contraseña actualizada correctamente")
        dialog.destroy()
        self.load_passwords()

    def delete_password(self):
        """Elimina una contraseña seleccionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Por favor seleccione una contraseña para eliminar")
            return
        
        item = selected[0]
        website = self.tree.item(item, 'values')[0]
        
        if not messagebox.askyesno("Confirmar", f"¿Está seguro de eliminar las credenciales para {website}?"):
            return
        
        with open(DATABASE_FILE, 'r+') as f:
            data = json.load(f)
            data["passwords"].pop(website, None)
            f.seek(0)
            json.dump(data, f)
            f.truncate()
        
        messagebox.showinfo("Éxito", "Contraseña eliminada correctamente")
        self.load_passwords()

    def reorder_passwords(self):
        """Reordena las contraseñas alfabéticamente"""
        with open(DATABASE_FILE, 'r+') as f:
            data = json.load(f)
            sorted_passwords = dict(sorted(data["passwords"].items()))
            data["passwords"] = sorted_passwords
            f.seek(0)
            json.dump(data, f)
            f.truncate()
        
        messagebox.showinfo("Éxito", "Contraseñas reordenadas alfabéticamente")
        self.load_passwords()

    def toggle_password_visibility(self):
        """Muestra u oculta las contraseñas en la tabla"""
        self.load_passwords()

    def configure_columns(self):
        """Configura qué columnas mostrar"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Configurar Columnas")
        dialog.geometry("300x250")
        
        ttk.Label(dialog, text="Seleccione las columnas a mostrar:").pack(pady=10)
        
        # Variables para los checkbuttons
        self.col_vars = {
            'Sitio': tk.BooleanVar(value=self.visible_columns['Sitio']),
            'Usuario': tk.BooleanVar(value=self.visible_columns['Usuario']),
            'Contraseña': tk.BooleanVar(value=self.visible_columns['Contraseña']),
            'Fecha': tk.BooleanVar(value=self.visible_columns['Fecha']),
            'Categoría': tk.BooleanVar(value=self.visible_columns['Categoría'])
        }
        
        # Checkbuttons para cada columna
        for col, var in self.col_vars.items():
            cb = ttk.Checkbutton(dialog, text=col, variable=var)
            cb.pack(anchor=tk.W, padx=20)
        
        ttk.Button(dialog, text="Aplicar", 
                  command=lambda: self.apply_column_config(dialog)).pack(pady=10)

    def apply_column_config(self, dialog):
        """Aplica la configuración de columnas"""
        for col, var in self.col_vars.items():
            self.visible_columns[col] = var.get()
            if self.visible_columns[col]:
                self.tree.column(col, stretch=tk.NO, width=100 if col != 'Sitio' else 200)
            else:
                self.tree.column(col, stretch=tk.NO, width=0, minwidth=0)
        
        dialog.destroy()
        self.load_passwords()

    def export_to_txt(self):
        """Exporta todas las contraseñas a un archivo TXT"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Guardar contraseñas como"
        )
        
        if not file_path:
            return
        
        with open(DATABASE_FILE, 'r') as f:
            data = json.load(f)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("=== CONTRASEÑAS EXPORTADAS ===\n")
            f.write(f"Fecha exportación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for website, creds in data["passwords"].items():
                f.write(f"Sitio: {website}\n")
                f.write(f"Usuario: {creds.get('username', '')}\n")
                f.write(f"Contraseña: {creds.get('password', '')}\n")
                if 'category' in creds:
                    f.write(f"Categoría: {creds['category']}\n")
                if 'date' in creds:
                    f.write(f"Fecha creación: {creds['date']}\n")
                f.write("-" * 50 + "\n")
        
        messagebox.showinfo("Éxito", f"Contraseñas exportadas correctamente a:\n{file_path}")

    def change_master_password(self):
        """Cambia la contraseña maestra"""
        if not self.ask_master_password():
            return
        
        new_password = simpledialog.askstring("Cambiar Clave", 
                                            "Ingrese la nueva clave maestra (mínimo 8 caracteres):", 
                                            show='*')
        if not new_password or len(new_password) < 8:
            messagebox.showerror("Error", "La clave debe tener al menos 8 caracteres")
            return
        
        confirm = simpledialog.askstring("Confirmar", 
                                       "Confirme la nueva clave maestra:", 
                                       show='*')
        if new_password != confirm:
            messagebox.showerror("Error", "Las claves no coinciden")
            return
        
        with open(DATABASE_FILE, 'r+') as f:
            data = json.load(f)
            data["master_hash"] = self.hash_password(new_password)
            f.seek(0)
            json.dump(data, f)
            f.truncate()
        
        messagebox.showinfo("Éxito", "Clave maestra cambiada correctamente")

    def show_advanced_options(self):
        """Muestra opciones avanzadas"""
        messagebox.showinfo("Opciones Avanzadas", 
                          "Configuración avanzada del gestor de contraseñas.\n\n"
                          "Aquí podrías añadir más opciones de configuración.")

    def show_help(self):
        """Muestra el manual de ayuda"""
        help_text = """MANUAL DE USO - GESTOR DE CONTRASEÑAS

1. Añadir Contraseña:
   - Use el menú Editar > Añadir Contraseña
   - Complete todos los campos obligatorios

2. Ver Contraseñas:
   - Las contraseñas se muestran en la tabla
   - Doble click para ver detalles completos

3. Editar/Eliminar:
   - Seleccione una contraseña y use las opciones del menú Editar

4. Exportar:
   - Menú Archivo > Exportar a TXT

5. Configuración:
   - Cambie la clave maestra en Opciones
   - Configure las columnas visibles en Ver > Configurar Columnas

Seguridad:
- Nunca comparta su clave maestra
- Mantenga su archivo de contraseñas en un lugar seguro"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Manual de Ayuda")
        help_window.geometry("500x400")
        
        text_area = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, width=60, height=20)
        text_area.pack(fill=tk.BOTH, expand=True)
        text_area.insert(tk.INSERT, help_text)
        text_area.config(state=tk.DISABLED)

    def show_about(self):
        """Muestra información acerca del programa"""
        messagebox.showinfo("Acerca de", 
                          "Gestor de Contraseñas Seguro\n\n"
                          "Versión 2.0\n"
                          "© 2023 - Todos los derechos reservados\n\n"
                          "Un gestor de contraseñas local y seguro.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordManager(root)
    root.mainloop()