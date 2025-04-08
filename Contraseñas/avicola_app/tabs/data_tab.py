from tkinter import ttk

class DataTab:
    def __init__(self, parent, data_manager):
        self.frame = ttk.Frame(parent)
        ttk.Label(self.frame, text="Pestaña de Datos Productivos", font=('Arial', 12)).pack(pady=50)
        # Aquí puedes agregar más componentes para esta pestaña