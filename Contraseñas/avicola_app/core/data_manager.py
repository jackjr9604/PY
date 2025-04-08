import json
import os
from tkinter import messagebox

class DataManager:
    def __init__(self, data_file):
        self.data_file = data_file
        self.modules = self.load_data()
    
    def load_data(self):
        """Carga los datos desde el archivo JSON"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return self.migrate_old_data(data)
            return {}
        except (json.JSONDecodeError, Exception) as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
            return {}
    
    def save_data(self):
        """Guarda los datos en el archivo JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.modules, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
            return False
    
    def migrate_old_data(self, data):
        """Convierte estructura antigua a nueva"""
        for module_name, lots in data.items():
            for lote_name, casetas in lots.items():
                for caseta_name, corrales in casetas.items():
                    if isinstance(corrales, list) and len(corrales) > 0 and isinstance(corrales[0], str):
                        data[module_name][lote_name][caseta_name] = [
                            {"nombre": nombre.replace("Corral ", ""), "hembras": 0, "machos": 0} 
                            for nombre in corrales
                        ]
        return data
    
    def save_data(self):
        """Guarda los datos en el archivo JSON"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.modules, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")