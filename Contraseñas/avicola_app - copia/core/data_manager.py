import json
import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

class DataManager:
    def __init__(self, data_file):
        self.data_file = data_file
        self.modules = self.load_data()
    
    def load_data(self):
        """Carga los datos desde el archivo JSON (versión más tolerante)"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Si la validación falla, intentamos migrar igual
                    migrated = self.migrate_old_data(data)
                    
                    # Validación básica después de migración
                    if not isinstance(migrated, dict):
                        raise ValueError("Datos migrados no válidos")
                    
                    return migrated
            return {}
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}\nSe creará una nueva estructura.")
            return {}

    def _validate_structure(self, data):
        """Valida que la estructura de datos sea correcta (versión más flexible)"""
        if not isinstance(data, dict):
            return False
        
        for module_name, lots in data.items():
            if not isinstance(lots, dict):
                return False
                
            for lote_name, lote_data in lots.items():
                if not isinstance(lote_data, dict):
                    return False
                    
                # Verificar estructura básica pero no requerir 'casetas' o 'produccion'
                # Si existen, deben ser del tipo correcto
                if 'casetas' in lote_data and not isinstance(lote_data['casetas'], dict):
                    return False
                    
                if 'produccion' in lote_data and not isinstance(lote_data['produccion'], dict):
                    return False
                    
                # Verificar estructura antigua compatible
                if 'casetas' not in lote_data:
                    for key, value in lote_data.items():
                        if key != '_info' and not isinstance(value, (dict, list)):
                            return False
                            
        return True

    def migrate_old_data(self, data):
        """Versión definitiva para migración de datos"""
        if not isinstance(data, dict):
            return {}

        migrated_data = {}
        for module_name, lots in data.items():
            migrated_data[module_name] = {}
            for lote_name, lote_data in lots.items():
                # Si ya es la estructura nueva correcta
                if isinstance(lote_data, dict) and 'casetas' in lote_data and isinstance(lote_data['casetas'], dict):
                    # Aseguramos que cada corral tenga los campos necesarios
                    casetas_corregidas = {}
                    for caseta_name, corrales in lote_data['casetas'].items():
                        if isinstance(corrales, list):
                            casetas_corregidas[caseta_name] = [
                                {
                                    'nombre': str(corral.get('nombre', f'Corral {i+1}')),
                                    'hembras': int(corral.get('hembras', 0)),
                                    'machos': int(corral.get('machos', 0)),
                                    'huevos_nido': int(corral.get('huevos_nido', 0)),
                                    'huevos_piso': int(corral.get('huevos_piso', 0))
                                }
                                for i, corral in enumerate(corrales)
                            ]
                    
                    migrated_data[module_name][lote_name] = {
                        '_info': lote_data.get('_info', {'fecha_alojamiento': 'Sin fecha'}),
                        'casetas': casetas_corregidas,
                        'produccion': lote_data.get('produccion', {})
                    }
                    continue

                # Si es estructura antigua
                nuevas_casetas = {}
                if isinstance(lote_data, dict):
                    for key, value in lote_data.items():
                        if key == '_info':
                            continue
                        if isinstance(value, list):
                            nuevas_casetas[key] = [
                                {
                                    'nombre': str(corral.get('nombre', f'Corral {i+1}')),
                                    'hembras': int(corral.get('hembras', 0)),
                                    'machos': int(corral.get('machos', 0)),
                                    'huevos_nido': int(corral.get('huevos_nido', 0)),
                                    'huevos_piso': int(corral.get('huevos_piso', 0))
                                }
                                for i, corral in enumerate(value)
                            ]

                migrated_data[module_name][lote_name] = {
                    '_info': lote_data.get('_info', {'fecha_alojamiento': 'Sin fecha'}),
                    'casetas': nuevas_casetas,
                    'produccion': lote_data.get('produccion', {})
                }

        return migrated_data
    
    def save_data(self):
        """Guarda los datos en el archivo JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.clean_data(self.modules.copy()), f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
            return False
    
    def clean_data(self, data):
        """Limpia los datos removiendo objetos no serializables"""
        if isinstance(data, dict):
            return {k: self.clean_data(v) for k, v in data.items() 
                    if not k.startswith('_') and not isinstance(v, (tk.Entry, tk.StringVar))}
        elif isinstance(data, list):
            return [self.clean_data(item) for item in data 
                    if not isinstance(item, (tk.Entry, tk.StringVar))]
        return data
    
    def get_production_data(self, module, lote, fecha):
        """Obtiene los datos de producción para una fecha específica"""
        try:
            return self.modules[module][lote].get('produccion', {}).get(fecha, {})
        except KeyError:
            return {}
    
    def save_production_data(self, module, lote, fecha, data):
        """Guarda los datos de producción para una fecha específica"""
        try:
            # Inicializar estructura si no existe
            if module not in self.modules:
                self.modules[module] = {}
            if lote not in self.modules[module]:
                self.modules[module][lote] = {'casetas': {}, 'produccion': {}}
            
            # Guardar datos de producción
            if 'produccion' not in self.modules[module][lote]:
                self.modules[module][lote]['produccion'] = {}
            
            self.modules[module][lote]['produccion'][fecha] = data
            return self.save_data()
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar producción: {str(e)}")
            return False