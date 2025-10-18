import json
import csv
import sys
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
import shutil
import time

def get_data_path():
    """Obtiene la ruta para datos del usuario."""
    if sys.platform == 'win32':
        docs = Path.home() / "Documents" / "ControlStock"
    else:
        docs = Path.home() / ".ControlStock"
    docs.mkdir(parents=True, exist_ok=True)
    return docs

def cargar_configuracion(config_file):
    """Carga o crea el archivo de configuración."""
    config_por_defecto = {
        "nombre_negocio": "ControlStock",
        "moneda": "ARS",
        "logo_path": "",
        "margen_ganancia_defecto": 0.30,
        "stock_min_defecto": 5,
        "tema": "claro"
    }
    
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config_por_defecto, f, ensure_ascii=False, indent=2)
    return config_por_defecto

def formato_moneda_arg(valor, config):
    """Formatea número con estilo argentino (punto miles, coma decimal)."""
    simbolo = {"ARS": "$", "USD": "US$", "EUR": "€"}.get(config["moneda"], "$")
    try:
        valor = float(valor)
        texto = f"{valor:,.2f}"
        texto = texto.replace(",", "X")
        texto = texto.replace(".", ",")
        texto = texto.replace("X", ".")
        return f"{simbolo}{texto}"
    except Exception:
        return f"{simbolo}0,00"

def generar_pdf_presupuesto(presupuesto: dict, ruta_pdf: str, config: dict):
    """Genera PDF con configuración del negocio."""
    c = canvas.Canvas(ruta_pdf, pagesize=A4)
    width, height = A4
    left = 2 * cm
    top = 27.5 * cm
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(left, top, f"Presupuesto - {config['nombre_negocio']}")
    
    c.setFont("Helvetica", 10)
    c.drawString(left, top - 0.7 * cm, f"Cliente: {presupuesto.get('cliente','')}")
    c.drawString(left, top - 1.2 * cm, f"Fecha: {presupuesto.get('fecha','')}")
    c.drawString(left, top - 1.7 * cm, f"ID: {presupuesto.get('id','')}")
    
    data = [["Producto", "Cantidad", "P. Unitario", "Subtotal"]]
    for item in presupuesto.get("productos", []):
        data.append([
            str(item.get("nombre", "")),
            str(item.get("cantidad", 0)),
            formato_moneda_arg(float(item.get('precio_unitario', 0)), config),
            formato_moneda_arg(float(item.get('subtotal', 0)), config),
        ])
    
    servicios = presupuesto.get("servicios", [])
    if servicios:
        data.append(["", "", "", ""])
        data.append(["SERVICIOS / MANO DE OBRA", "", "", ""])
        for serv in servicios:
            data.append([
                str(serv.get("descripcion", "")),
                "-",
                "-",
                formato_moneda_arg(float(serv.get('precio', 0)), config),
            ])
    
    data.append(["", "", "TOTAL", formato_moneda_arg(float(presupuesto.get('total_final', 0)), config)])
    
    table = Table(data, colWidths=[8 * cm, 3 * cm, 3 * cm, 3 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("ALIGN", (1, 1), (-1, -2), "CENTER"),
        ("FONTNAME", (-2, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (-2, -1), (-2, -1), "RIGHT"),
        ("ALIGN", (-1, -1), (-1, -1), "RIGHT"),
        ("FONTSIZE", (-2, -1), (-1, -1), 11),
    ]))
    
    filas = len(data)
    alto_aprox = (filas + 1) * 0.6 * cm
    y_table = max(5 * cm, (top - 3.3 * cm) - alto_aprox)
    
    table.wrapOn(c, width, height)
    table.drawOn(c, left, y_table)
    
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(left, 1.5 * cm, f"Generado por {config['nombre_negocio']}")
    c.save()

def confirmar_presupuesto_a_venta(pres_id: int, df_pres, productos_json_path, ventas_csv_path, presup_csv_path, backups_dir):
    """Confirma presupuesto y lo convierte en venta."""
    fila = df_pres[df_pres["ID"] == int(pres_id)]
    if fila.empty:
        return False, "No se encontró ese presupuesto."
    
    datos = fila.iloc[0]
    try:
        items = json.loads(datos["Productos"])
    except Exception:
        return False, "Productos mal formateados."
    
    try:
        with open(productos_json_path, "r", encoding="utf-8") as f:
            productos_stock = json.load(f)
    except Exception:
        return False, "No se pudo abrir productos.json"
    
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fecha_actual = datetime.now()
    carpeta_mes = backups_dir / fecha_actual.strftime("%Y-%m")
    carpeta_mes.mkdir(parents=True, exist_ok=True)
    
    archivo_dia_ventas = carpeta_mes / f"ventas_{fecha_actual.strftime('%Y-%m-%d')}.csv"
    
    if not archivo_dia_ventas.exists():
        with open(archivo_dia_ventas, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Producto", "Cantidad", "PrecioUnitario", "Total", "FechaHora"])
    
    if not ventas_csv_path.exists():
        with open(ventas_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Producto", "Cantidad", "PrecioUnitario", "Total", "FechaHora"])
    
    faltantes = []
    for item in items:
        nombre = item.get("nombre")
        cant = int(item.get("cantidad", 0))
        punit = float(item.get("precio_unitario", 0))
        
        prod = next((p for p in productos_stock if p.get("producto") == nombre), None)
        if not prod:
            faltantes.append(f"{nombre} (no existe en productos)")
            continue
        
        stock_antes = prod["stock"]
        prod["stock"] -= cant
        if stock_antes < cant:
            faltantes.append(f"{nombre} (faltan {cant - stock_antes} unidades)")
        
        total = punit * cant
        
        with open(ventas_csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([nombre, cant, punit, total, fecha_hora])
        
        with open(archivo_dia_ventas, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([nombre, cant, punit, total, fecha_hora])
    
    with open(productos_json_path, "w", encoding="utf-8") as f:
        json.dump(productos_stock, f, ensure_ascii=False, indent=2)
    
    df_pres.loc[df_pres["ID"] == int(pres_id), "Estado"] = "confirmado"
    df_pres.to_csv(presup_csv_path, index=False, header=False, encoding="utf-8")
    
    time.sleep(0.1)
    if presup_csv_path.exists():
        presupuesto_backup = carpeta_mes / f"presupuestos_{fecha_actual.strftime('%Y-%m-%d')}.csv"
        try:
            shutil.copy2(presup_csv_path, presupuesto_backup)
        except Exception:
            pass
    
    if faltantes:
        return True, "Venta confirmada con faltantes: " + ", ".join(faltantes)
    else:
        return True, "Presupuesto confirmado correctamente."