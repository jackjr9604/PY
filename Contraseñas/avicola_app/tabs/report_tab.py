import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
import csv
import pandas as pd

class ReportTab:
    def __init__(self, parent, data_manager):
        self.data_manager = data_manager
        self.frame = ttk.Frame(parent)
        self.last_update = None
        self.create_widgets()
        self.setup_file_watcher()
        
    def create_widgets(self):
        """Crea los componentes de la pestaña de reportes"""
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel superior con controles
        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Botones
        btn_refresh = ttk.Button(control_frame, text="Actualizar", command=self.update_report)
        btn_refresh.pack(side=tk.LEFT, padx=5)
        
        btn_export = ttk.Button(control_frame, text="Exportar Reporte", command=self.ask_export_format)
        btn_export.pack(side=tk.LEFT, padx=5)
        
        # Etiqueta de última actualización
        self.lbl_update = ttk.Label(control_frame, text="Última actualización: Nunca")
        self.lbl_update.pack(side=tk.RIGHT, padx=5)
        
        # Treeview con scrollbars
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("módulo", "lote", "caseta", "corral", "hembras", "machos", "total")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=100, anchor="center")
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Panel de resumen
        summary_frame = ttk.Frame(self.frame)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Variables de resumen
        self.summary_vars = {
            "total_hembras": tk.StringVar(value="0"),
            "total_machos": tk.StringVar(value="0"),
            "total_aves": tk.StringVar(value="0"),
            "total_corrales": tk.StringVar(value="0")
        }
        
        # Labels de resumen
        ttk.Label(summary_frame, text="Resumen:").grid(row=0, column=0, sticky="w")
        ttk.Label(summary_frame, text="Hembras:").grid(row=1, column=0, sticky="e")
        ttk.Label(summary_frame, textvariable=self.summary_vars["total_hembras"]).grid(row=1, column=1, sticky="w")
        ttk.Label(summary_frame, text="Machos:").grid(row=1, column=2, sticky="e")
        ttk.Label(summary_frame, textvariable=self.summary_vars["total_machos"]).grid(row=1, column=3, sticky="w")
        ttk.Label(summary_frame, text="Total Aves:").grid(row=2, column=0, sticky="e")
        ttk.Label(summary_frame, textvariable=self.summary_vars["total_aves"]).grid(row=2, column=1, sticky="w")
        ttk.Label(summary_frame, text="Corrales:").grid(row=2, column=2, sticky="e")
        ttk.Label(summary_frame, textvariable=self.summary_vars["total_corrales"]).grid(row=2, column=3, sticky="w")
        
        # Cargar datos iniciales
        self.update_report()
    
    def setup_file_watcher(self):
        """Configura el monitoreo del archivo de datos"""
        self.last_update = os.path.getmtime(self.data_manager.data_file)
        self.frame.after(1000, self.check_data_changes)
    
    def check_data_changes(self):
        """Verifica si hubo cambios en el archivo de datos"""
        try:
            current_mtime = os.path.getmtime(self.data_manager.data_file)
            if current_mtime > self.last_update:
                self.last_update = current_mtime
                self.update_report()
        except:
            pass
        finally:
            self.frame.after(1000, self.check_data_changes)
    
    def update_report(self):
        """Actualiza el reporte con los últimos datos"""
        # Limpiar treeview
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Variables para el resumen
        total_hembras = 0
        total_machos = 0
        total_corrales = 0
        
        # Recorrer la estructura de datos
        for modulo, lotes in self.data_manager.modules.items():
            for lote, casetas in lotes.items():
                for caseta, corrales in casetas.items():
                    for corral in corrales:
                        hembras = corral.get("hembras", 0)
                        machos = corral.get("machos", 0)
                        total = hembras + machos
                        
                        self.tree.insert("", "end", values=(
                            modulo, lote, caseta, corral["nombre"],
                            hembras, machos, total
                        ))
                        
                        total_hembras += hembras
                        total_machos += machos
                        total_corrales += 1
        
        # Actualizar resumen
        self.summary_vars["total_hembras"].set(str(total_hembras))
        self.summary_vars["total_machos"].set(str(total_machos))
        self.summary_vars["total_aves"].set(str(total_hembras + total_machos))
        self.summary_vars["total_corrales"].set(str(total_corrales))
        
        # Actualizar etiqueta
        self.lbl_update.config(text=f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def ask_export_format(self):
        """Muestra diálogo para seleccionar formato de exportación"""
        popup = tk.Toplevel(self.frame)
        popup.title("Formato de Exportación")
        popup.geometry("300x200")
        popup.transient(self.frame)
        popup.grab_set()
        
        ttk.Label(popup, text="Seleccione el formato de exportación:", font=('Arial', 10)).pack(pady=10)
        
        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Excel (.xlsx)", 
                  command=lambda: [self.export_to_excel(), popup.destroy()]).pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="CSV (.csv)", 
                  command=lambda: [self.export_to_csv(), popup.destroy()]).pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Texto (.txt)", 
                  command=lambda: [self.export_to_txt(), popup.destroy()]).pack(fill=tk.X, pady=5)
        
        ttk.Button(popup, text="Cancelar", command=popup.destroy).pack(pady=10)
    
    def get_report_data(self):
        """Recopila los datos para el reporte"""
        data = []
        summary = {
            "total_hembras": 0,
            "total_machos": 0,
            "total_corrales": 0
        }
        
        for modulo, lotes in self.data_manager.modules.items():
            for lote, casetas in lotes.items():
                for caseta, corrales in casetas.items():
                    for corral in corrales:
                        hembras = corral.get("hembras", 0)
                        machos = corral.get("machos", 0)
                        
                        data.append({
                            "Módulo": modulo,
                            "Lote": lote,
                            "Caseta": caseta,
                            "Corral": corral["nombre"],
                            "Hembras": hembras,
                            "Machos": machos,
                            "Total": hembras + machos
                        })
                        
                        summary["total_hembras"] += hembras
                        summary["total_machos"] += machos
                        summary["total_corrales"] += 1
        
        return data, summary
    
    def export_to_excel(self):
        """Exporta los datos a un archivo Excel"""
        try:
            data, summary = self.get_report_data()
            df = pd.DataFrame(data)
            
            # Crear directorio si no existe
            os.makedirs("reportes", exist_ok=True)
            
            # Pedir ubicación para guardar
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialdir="reportes",
                initialfile=f"reporte_avicola_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            )
            
            if not filepath:
                return  # Usuario canceló
                
            # Crear un Excel writer
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja de detalle
                df.to_excel(writer, sheet_name='Detalle', index=False)
                
                # Hoja de resumen
                summary_df = pd.DataFrame({
                    "Metrica": ["Total Hembras", "Total Machos", "Total Aves", "Total Corrales"],
                    "Valor": [
                        summary["total_hembras"],
                        summary["total_machos"],
                        summary["total_hembras"] + summary["total_machos"],
                        summary["total_corrales"]
                    ]
                })
                summary_df.to_excel(writer, sheet_name='Resumen', index=False)
                
                # Ajustar ancho de columnas
                for sheet in writer.sheets:
                    worksheet = writer.sheets[sheet]
                    for column in worksheet.columns:
                        max_length = 0
                        column = [cell for cell in column]
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(cell.value)
                            except:
                                pass
                        adjusted_width = (max_length + 2)
                        worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
            
            messagebox.showinfo("Éxito", f"Reporte exportado a:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a Excel:\n{str(e)}")
    
    def export_to_csv(self):
        """Exporta los datos a un archivo CSV"""
        try:
            data, _ = self.get_report_data()
            
            # Pedir ubicación para guardar
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialdir="reportes",
                initialfile=f"reporte_avicola_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not filepath:
                return  # Usuario canceló
                
            # Escribir archivo CSV
            with open(filepath, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            messagebox.showinfo("Éxito", f"Reporte exportado a:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a CSV:\n{str(e)}")
    
    def export_to_txt(self):
        """Exporta los datos a un archivo de texto"""
        try:
            data, summary = self.get_report_data()
            
            # Pedir ubicación para guardar
            filepath = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialdir="reportes",
                initialfile=f"reporte_avicola_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            
            if not filepath:
                return  # Usuario canceló
                
            # Generar contenido
            lines = [
                "="*50,
                f"REPORTE AVÍCOLA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "="*50,
                "\n[RESUMEN]",
                f"Hembras: {summary['total_hembras']}",
                f"Machos: {summary['total_machos']}",
                f"Total Aves: {summary['total_hembras'] + summary['total_machos']}",
                f"Total Corrales: {summary['total_corrales']}",
                "\n[DETALLE]"
            ]
            
            # Agregar datos detallados
            for item in data:
                lines.append(
                    f"Módulo: {item['Módulo']}, Lote: {item['Lote']}, "
                    f"Caseta: {item['Caseta']}, Corral: {item['Corral']}, "
                    f"Hembras: {item['Hembras']}, Machos: {item['Machos']}, "
                    f"Total: {item['Total']}"
                )
            
            # Escribir archivo
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write("\n".join(lines))
            
            messagebox.showinfo("Éxito", f"Reporte exportado a:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar a texto:\n{str(e)}")