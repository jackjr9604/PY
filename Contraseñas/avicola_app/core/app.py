import tkinter as tk
from tkinter import ttk
from .data_manager import DataManager
from tabs.edit_tab import EditTab
from tabs.data_tab import DataTab
from tabs.report_tab import ReportTab  # Nueva importación


class AvicolaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión Avícola - Versión Mejorada")
        self.root.geometry("1200x800")  # Aumenté el tamaño para mejor visualización

        self.data_manager = DataManager("avicola_data.json")
        self.create_main_ui()

    def create_main_ui(self):
        """Interfaz principal con pestañas"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Crear instancias de las pestañas
        self.edit_tab = EditTab(self.notebook, self.data_manager)
        self.data_tab = DataTab(self.notebook, self.data_manager)
        self.report_tab = ReportTab(self.notebook, self.data_manager)  # Nueva pestaña

        # Añadir las pestañas al notebook
        self.notebook.add(self.edit_tab.frame, text="Editar Estructura")
        self.notebook.add(self.data_tab.frame, text="Datos Productivos")
        self.notebook.add(
            self.report_tab.frame, text="Reportes Detallados"
        )  # Nueva pestaña
