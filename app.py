import streamlit as st
from pathlib import Path
import json
import csv
import pandas as pd
from datetime import datetime, date
import shutil
import os

# Importar utilidades y estilos
from utilidades import (
    get_data_path,
    cargar_configuracion,
    formato_moneda_arg,
    generar_pdf_presupuesto,
    confirmar_presupuesto_a_venta
)
from estilos import aplicar_estilos

# ============================================================
# CONFIGURACIÓN INICIAL
# ============================================================

DATA_PATH = get_data_path()
CONFIG_FILE = DATA_PATH / "config.json"

if "config" not in st.session_state:
    st.session_state.config = cargar_configuracion(CONFIG_FILE)

config = st.session_state.config
st.set_page_config(page_title=config["nombre_negocio"], layout="wide")

# Aplicar estilos
aplicar_estilos(config)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    if config.get("logo_path", "").strip():
        try:
            st.image(config["logo_path"], width=200)
        except:
            pass
    
    st.title(config["nombre_negocio"])
    
    if "base_dir" not in st.session_state:
        st.session_state.base_dir = str(DATA_PATH)
    
    st.success(f"Datos: {st.session_state.base_dir}")
    
    page = st.radio(
        "Secciones",
        ["Inventario", "Productos", "Ventas", "Presupuestos", "Respaldos", "Configuración"],
        index=0
    )

# ============================================================
# RUTAS
# ============================================================

DATA_DIR = Path(st.session_state.base_dir)
PRODUCTOS_JSON = DATA_DIR / "productos.json"
VENTAS_CSV = DATA_DIR / "ventas.csv"
PRESUP_CSV = DATA_DIR / "presupuestos.csv"
BACKUPS_DIR = DATA_DIR / "backups"
BACKUPS_DIR.mkdir(exist_ok=True)

# Control automático de mes actual
mes_actual = date.today().strftime("%Y-%m")
VENTAS_MES_ACTUAL = DATA_DIR / f"ventas_{mes_actual}.csv"

if VENTAS_CSV.exists() and not VENTAS_MES_ACTUAL.exists():
    fecha_mod = datetime.fromtimestamp(VENTAS_CSV.stat().st_mtime)
    mes_archivo = fecha_mod.strftime("%Y-%m")
    if mes_archivo != mes_actual:
        nuevo_nombre = DATA_DIR / f"ventas_{mes_archivo}.csv"
        VENTAS_CSV.rename(nuevo_nombre)

VENTAS_CSV = VENTAS_MES_ACTUAL

# ============================================================
# PÁGINA: INVENTARIO
# ============================================================

if page == "Inventario":
    st.header(f"Inventario - {config['nombre_negocio']}")
    
    try:
        with open(PRODUCTOS_JSON, "r", encoding="utf-8") as f:
            productos = json.load(f)
    except FileNotFoundError:
        st.warning("El archivo productos.json no existe.")
        st.stop()
    except json.JSONDecodeError:
        st.error("Error al leer el archivo productos.json.")
        st.stop()
    
    if not productos or not isinstance(productos, list):
        st.info("No hay productos cargados en el archivo.")
        st.stop()
    
    filtro = st.text_input("Buscar producto por nombre").strip().lower()
    if filtro:
        productos = [p for p in productos if filtro in str(p.get("producto", "")).lower()]
    
    for p in productos:
        costo = float(p.get("costo", 0))
        precio = float(p.get("precio_final", 0))
        p["ganancia_unitaria"] = round(precio - costo, 2)
    
    df = pd.DataFrame(productos)
    
    def estilo_stock(row):
        stock_min = config.get("stock_min_defecto", 5)
        if row["stock"] <= stock_min:
            return ["background-color: #ffb3b3"] * len(row)
        return [""] * len(row)
    
    st.dataframe(
        df.style.apply(estilo_stock, axis=1).format({
            "costo": lambda x: formato_moneda_arg(x, config),
            "precio_final": lambda x: formato_moneda_arg(x, config),
            "ganancia_unitaria": lambda x: formato_moneda_arg(x, config)
        }),
        use_container_width=True
    )
    
    if st.button("Actualizar inventario"):
        st.rerun()
    
    total_productos = len(df)
    stock_total = df["stock"].sum()
    valor_inventario = (df["costo"] * df["stock"]).sum()
    valor_venta = (df["precio_final"] * df["stock"]).sum()
    ganancia_potencial = valor_venta - valor_inventario
    
    st.markdown("### Resumen general del inventario")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Productos activos", f"{total_productos}")
    col2.metric("Stock total", f"{stock_total:,}")
    col3.metric("Valor de costo", formato_moneda_arg(valor_inventario, config))
    col4.metric("Valor de venta", formato_moneda_arg(valor_venta, config))
    col5.metric("Ganancia potencial", formato_moneda_arg(ganancia_potencial, config))

# ============================================================
# PÁGINA: PRODUCTOS
# ============================================================

elif page == "Productos":
    st.header(f"Gestión de Productos - {config['nombre_negocio']}")
    
    try:
        with open(PRODUCTOS_JSON, "r", encoding="utf-8") as f:
            productos = json.load(f)
    except FileNotFoundError:
        productos = []
        with open(PRODUCTOS_JSON, "w", encoding="utf-8") as f:
            json.dump(productos, f, ensure_ascii=False, indent=2)
    
    tab1, tab2 = st.tabs(["Agregar Producto", "Editar Productos"])
    
    with tab1:
        st.subheader("Nuevo producto")
        
        if "mensaje_guardado" in st.session_state:
            st.success(st.session_state.pop("mensaje_guardado"))
        
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre del producto")
            costo = st.number_input("Costo unitario", min_value=0.0, step=0.01)
            stock = st.number_input("Stock inicial", min_value=0, step=1)
        
        with col2:
            margen = st.number_input(
                "Margen de ganancia (%)",
                min_value=0.0, max_value=500.0,
                value=config.get("margen_ganancia_defecto", 0.30) * 100,
                step=1.0
            )
            stock_min = st.number_input(
                "Stock mínimo",
                min_value=0,
                value=config.get("stock_min_defecto", 5),
                step=1
            )
        
        precio_final = costo * (1 + margen / 100)
        st.info(f"Precio de venta calculado: {formato_moneda_arg(precio_final, config)}")
        
        if st.button("Guardar producto"):
            if not nombre.strip():
                st.warning("El nombre del producto no puede estar vacío.")
            elif any(p.get("producto", "").lower() == nombre.lower() for p in productos):
                st.error("Ya existe un producto con ese nombre.")
            else:
                nuevo_producto = {
                    "producto": nombre,
                    "costo": round(costo, 2),
                    "precio_final": round(precio_final, 2),
                    "stock": stock,
                    "stock_min": stock_min
                }
                productos.append(nuevo_producto)
                with open(PRODUCTOS_JSON, "w", encoding="utf-8") as f:
                    json.dump(productos, f, ensure_ascii=False, indent=2)
                
                st.session_state["mensaje_guardado"] = f"Producto '{nombre}' agregado correctamente."
                st.rerun()
    
    with tab2:
        st.subheader("Editar productos existentes")
        
        if not productos:
            st.info("No hay productos para editar.")
        else:
            nombres_productos = [p.get("producto", "Desconocido") for p in productos]
            producto_sel = st.selectbox("Seleccione un producto", nombres_productos)
            
            if producto_sel:
                producto = next((p for p in productos if p.get("producto") == producto_sel), None)
                if producto:
                    st.markdown(f"### Editando: {producto_sel}")
                    
                    if "mensaje_editado" in st.session_state:
                        st.success(st.session_state.pop("mensaje_editado"))
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        clave = producto_sel.replace(" ", "_")
                        nuevo_costo = st.number_input(
                            "Costo unitario",
                            min_value=0.0,
                            value=float(producto.get("costo", 0)),
                            step=0.01,
                            key=f"edit_costo_{clave}"
                        )
                        stock_actual = int(producto.get("stock", 0))
                        nuevo_stock = st.number_input(
                            "Stock actual",
                            value=stock_actual,
                            step=1,
                            key=f"edit_stock_{clave}"
                        )
                    
                    with col2:
                        if nuevo_costo > 0:
                            margen_actual = ((float(producto.get("precio_final", 0)) / nuevo_costo) - 1) * 100
                        else:
                            margen_actual = config.get("margen_ganancia_defecto", 0.30) * 100
                        margen_actual = max(0.0, min(margen_actual, 500.0))
                        
                        nuevo_margen = st.number_input(
                            "Margen de ganancia (%)",
                            min_value=0.0, max_value=500.0,
                            value=margen_actual,
                            step=1.0,
                            key=f"edit_margen_{clave}"
                        )
                        nuevo_stock_min = st.number_input(
                            "Stock mínimo",
                            min_value=0,
                            value=int(producto.get("stock_min", 5)),
                            step=1,
                            key=f"edit_stock_min_{clave}"
                        )
                    
                    nuevo_precio = nuevo_costo * (1 + nuevo_margen / 100)
                    st.info(f"Nuevo precio de venta: {formato_moneda_arg(nuevo_precio, config)}")
                    
                    col_guardar, col_eliminar = st.columns(2)
                    
                    with col_guardar:
                        if st.button("Guardar cambios"):
                            producto["costo"] = round(nuevo_costo, 2)
                            producto["precio_final"] = round(nuevo_precio, 2)
                            producto["stock"] = nuevo_stock
                            producto["stock_min"] = nuevo_stock_min
                            
                            with open(PRODUCTOS_JSON, "w", encoding="utf-8") as f:
                                json.dump(productos, f, ensure_ascii=False, indent=2)
                            
                            st.session_state["mensaje_editado"] = f"Cambios en '{producto_sel}' guardados correctamente."
                            st.rerun()
                    
                    with col_eliminar:
                        if st.button("Eliminar producto"):
                            productos = [p for p in productos if p.get("producto") != producto_sel]
                            with open(PRODUCTOS_JSON, "w", encoding="utf-8") as f:
                                json.dump(productos, f, ensure_ascii=False, indent=2)
                            st.warning(f"Producto '{producto_sel}' eliminado.")
                            st.rerun()

# ============================================================
# PÁGINA: VENTAS
# ============================================================

elif page == "Ventas":
    st.header(f"Registro y Análisis de Ventas - {config['nombre_negocio']}")
    
    try:
        with open(PRODUCTOS_JSON, "r", encoding="utf-8") as f:
            productos = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        st.error("No se pudieron cargar los productos.")
        st.stop()
    
    if not productos:
        st.warning("No hay productos disponibles para vender.")
        st.stop()
    
    nombres = [p.get("producto", "Desconocido") for p in productos]
    producto_sel = st.selectbox("Seleccione un producto", [""] + nombres)
    
    if producto_sel:
        producto = next((p for p in productos if p.get("producto") == producto_sel), None)
        if producto:
            if "cantidad_venta" not in st.session_state:
                st.session_state["cantidad_venta"] = 1
            
            cantidad = st.number_input("Cantidad", min_value=1, step=1, key="cantidad_venta")
            precio_unit = float(producto.get("precio_final", 0))
            subtotal = precio_unit * cantidad
            
            st.write(f"Subtotal: {formato_moneda_arg(subtotal, config)}")
            
            if st.button("Registrar venta"):
                if producto["stock"] >= cantidad:
                    producto["stock"] -= cantidad
                    total = precio_unit * cantidad
                    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    if not VENTAS_CSV.exists():
                        with open(VENTAS_CSV, "w", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)
                            writer.writerow(["Producto", "Cantidad", "PrecioUnitario", "Total", "FechaHora"])
                    
                    with open(VENTAS_CSV, "a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([producto_sel, cantidad, precio_unit, total, fecha_hora])

                    fecha_actual = datetime.now()
                    carpeta_mes = BACKUPS_DIR / fecha_actual.strftime("%Y-%m")
                    carpeta_mes.mkdir(parents=True, exist_ok=True)

                    archivo_dia = carpeta_mes / f"ventas_{fecha_actual.strftime('%Y-%m-%d')}.csv"

                    if not archivo_dia.exists():
                        with open(archivo_dia, "w", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)
                            writer.writerow(["Producto", "Cantidad", "PrecioUnitario", "Total", "FechaHora"])

                    with open(archivo_dia, "a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([producto_sel, cantidad, precio_unit, total, fecha_hora])
                    
                    with open(PRODUCTOS_JSON, "w", encoding="utf-8") as f:
                        json.dump(productos, f, ensure_ascii=False, indent=2)
                    
                    st.success(f"Venta registrada: {producto_sel} x {cantidad} (Total {formato_moneda_arg(total, config)})")
                    st.session_state["reset_key"] = st.session_state.get("reset_key", 0) + 1
                    st.rerun()
                else:
                    st.warning(f"Stock insuficiente. Solo quedan {producto['stock']} unidades.")
    
    if Path(VENTAS_CSV).exists():
        try:
            df = pd.read_csv(VENTAS_CSV, encoding="utf-8")
            
            if "FechaHora" not in df.columns:
                df = pd.read_csv(
                    VENTAS_CSV,
                    names=["Producto", "Cantidad", "PrecioUnitario", "Total", "FechaHora"],
                    encoding="utf-8"
                )
            
            if df.empty:
                st.info("No hay ventas registradas todavía.")
            else:
                df["FechaHora"] = pd.to_datetime(df["FechaHora"], errors="coerce")
                
                st.markdown("### Ventas recientes")
                df_mostrar = df.tail(10).copy()
                df_mostrar["PrecioUnitario"] = df_mostrar["PrecioUnitario"].astype(float).apply(lambda x: formato_moneda_arg(x, config))
                df_mostrar["Total"] = df_mostrar["Total"].astype(float).apply(lambda x: formato_moneda_arg(x, config))
                st.dataframe(df_mostrar, use_container_width=True)
                
                st.markdown("### Resumen de ventas")
                total_ventas = df["Total"].sum()
                total_unidades = df["Cantidad"].sum()
                hoy = datetime.now().date()
                ventas_hoy = df[df["FechaHora"].dt.date == hoy]["Total"].sum()
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Ventas totales", formato_moneda_arg(total_ventas, config))
                col2.metric("Unidades vendidas", f"{int(total_unidades)}")
                col3.metric("Facturado hoy", formato_moneda_arg(ventas_hoy, config))
                
                st.markdown("### Productos más vendidos")
                df["Cantidad"] = pd.to_numeric(df["Cantidad"], errors="coerce").fillna(0)
                top5 = df.groupby("Producto")["Cantidad"].sum().nlargest(5).reset_index()
                
                if not top5.empty:
                    import matplotlib.pyplot as plt
                    plt.style.use("default")
                    
                    fig, ax = plt.subplots(figsize=(4.5, 1.6))
                    
                    bars = ax.barh(
                        top5["Producto"],
                        top5["Cantidad"],
                        color="#007BFF",
                        height=0.3
                    )
                    
                    for bar in bars:
                        width = bar.get_width()
                        ax.text(
                            width + 0.3,
                            bar.get_y() + bar.get_height() / 2,
                            f"{int(width)}",
                            va="center",
                            ha="left",
                            color="#007BFF",
                            fontsize=7.5,
                            fontweight="600"
                        )
                    
                    ax.set_title(
                        "Top 5 productos más vendidos",
                        fontsize=9.5,
                        fontweight="600",
                        color="#222",
                        pad=6
                    )
                    
                    ax.set_xlabel("Unidades vendidas", fontsize=7, color="#555", labelpad=3)
                    ax.set_ylabel("")
                    ax.tick_params(axis="x", labelsize=7, colors="#555")
                    ax.tick_params(axis="y", labelsize=7, colors="#333")
                    
                    ax.invert_yaxis()
                    
                    for spine in ["top", "right", "left", "bottom"]:
                        ax.spines[spine].set_visible(False)
                    ax.set_facecolor("white")
                    fig.patch.set_facecolor("white")
                    
                    plt.tight_layout()
                    st.pyplot(fig, use_container_width=False)
                else:
                    st.info("Aún no hay suficientes ventas para mostrar ranking.")
                
        except Exception as e:
            st.error(f"Error al leer ventas: {e}")
    else:
        st.warning("Todavía no se registraron ventas.")

# ============================================================
# PÁGINA: PRESUPUESTOS
# ============================================================

elif page == "Presupuestos":
    st.header(f"Gestión de Presupuestos - {config['nombre_negocio']}")
    
    try:
        with open(PRODUCTOS_JSON, "r", encoding="utf-8") as f:
            productos = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        st.error("No se pudieron cargar los productos.")
        productos = []
    
    if "productos_presupuesto" not in st.session_state:
        st.session_state.productos_presupuesto = []
    
    if "servicios_presupuesto" not in st.session_state:
        st.session_state.servicios_presupuesto = []
    
    if "cliente_presupuesto" not in st.session_state:
        st.session_state.cliente_presupuesto = ""
    
    cliente = st.text_input("Nombre del cliente", value=st.session_state.cliente_presupuesto)
    st.session_state.cliente_presupuesto = cliente
    
    if not productos:
        st.warning("No hay productos disponibles para presupuestar.")
    else:
        st.subheader("Agregar productos")
        nombres_productos = [p.get("producto", "Desconocido") for p in productos]
        producto_sel = st.selectbox("Seleccione un producto", [""] + nombres_productos)
        
        if producto_sel:
            producto = next((p for p in productos if p.get("producto") == producto_sel), None)
            if producto:
                cantidad = st.number_input("Cantidad", min_value=1, step=1, key=f"cantidad_presup_{st.session_state.get('reset_key', 0)}")
                precio_unitario = producto.get("precio_final", 0)
                subtotal = cantidad * precio_unitario
                
                st.write(f"Subtotal: {formato_moneda_arg(subtotal, config)}")
                
                if st.button("Agregar producto al presupuesto"):
                    st.session_state.productos_presupuesto.append({
                        "nombre": producto_sel,
                        "cantidad": cantidad,
                        "precio_unitario": precio_unitario,
                        "subtotal": subtotal
                    })
                    st.success(f"{producto_sel} agregado correctamente.")
    
    st.markdown("---")
    st.subheader("Agregar servicio / Mano de obra")
    
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        desc_servicio = st.text_input("Descripción del servicio")
    with col_s2:
        precio_servicio = st.number_input("Precio del servicio", min_value=0.0, step=10.0)
    with col_s3:
        st.write("")
        st.write("")
        if st.button("Agregar servicio"):
            if desc_servicio.strip() and precio_servicio > 0:
                st.session_state.servicios_presupuesto.append({
                    "descripcion": desc_servicio,
                    "precio": precio_servicio
                })
                st.success(f"Servicio '{desc_servicio}' agregado.")
            else:
                st.warning("Complete descripción y precio del servicio.")
    
    if st.session_state.productos_presupuesto or st.session_state.servicios_presupuesto:
        st.subheader("Detalle del presupuesto:")
        
        total_productos = 0
        total_servicios = 0
        
        if st.session_state.productos_presupuesto:
            st.markdown("**Productos:**")
            df_temp = pd.DataFrame(st.session_state.productos_presupuesto)
            df_temp["precio_unitario"] = df_temp["precio_unitario"].astype(float).apply(lambda x: formato_moneda_arg(x, config))
            df_temp["subtotal"] = df_temp["subtotal"].astype(float).apply(lambda x: formato_moneda_arg(x, config))
            st.dataframe(df_temp, use_container_width=True)
            total_productos = sum(p["subtotal"] for p in st.session_state.productos_presupuesto)
        
        if st.session_state.servicios_presupuesto:
            st.markdown("**Servicios / Mano de obra:**")
            df_serv = pd.DataFrame(st.session_state.servicios_presupuesto)
            df_serv["precio"] = df_serv["precio"].astype(float).apply(lambda x: formato_moneda_arg(x, config))
            st.dataframe(df_serv, use_container_width=True)
            total_servicios = sum(s["precio"] for s in st.session_state.servicios_presupuesto)
        
        total = total_productos + total_servicios
        
        col_tot1, col_tot2 = st.columns(2)
        col_tot1.write(f"**Subtotal productos: {formato_moneda_arg(total_productos, config)}**")
        col_tot2.write(f"**Subtotal servicios: {formato_moneda_arg(total_servicios, config)}**")
        st.write(f"### **Total general: {formato_moneda_arg(total, config)}**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Finalizar y guardar presupuesto"):
                if not cliente.strip():
                    st.warning("Debe ingresar el nombre del cliente antes de guardar.")
                else:
                    nuevo = {
                        "id": int(datetime.now().timestamp()),
                        "cliente": cliente,
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "productos": st.session_state.productos_presupuesto,
                        "servicios": st.session_state.servicios_presupuesto,
                        "total_final": total,
                        "estado": "pendiente"
                    }
                    
                    if not PRESUP_CSV.exists():
                        with open(PRESUP_CSV, "w", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)
                            writer.writerow(["ID", "Cliente", "Fecha", "Total", "Estado", "Productos", "Servicios"])
                    
                    with open(PRESUP_CSV, "a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            nuevo["id"],
                            nuevo["cliente"],
                            nuevo["fecha"],
                            nuevo["total_final"],
                            nuevo["estado"],
                            json.dumps(nuevo["productos"], ensure_ascii=False),
                            json.dumps(nuevo["servicios"], ensure_ascii=False)
                        ])
                        f.flush()
                        os.fsync(f.fileno())

                    st.success(f"Presupuesto guardado para {cliente}.")

                    fecha_actual = datetime.now()
                    carpeta_mes = BACKUPS_DIR / fecha_actual.strftime("%Y-%m")
                    carpeta_mes.mkdir(parents=True, exist_ok=True)

                    import time
                    time.sleep(0.2)

                    if PRESUP_CSV.exists():
                        presupuesto_backup = carpeta_mes / f"presupuestos_{fecha_actual.strftime('%Y-%m-%d')}.csv"
                        try:
                            shutil.copy2(PRESUP_CSV, presupuesto_backup)
                        except Exception as e:
                            st.warning(f"No se pudo copiar el respaldo de presupuestos: {e}")

                    st.session_state.productos_presupuesto = []
                    st.session_state.servicios_presupuesto = []
                    st.session_state.cliente_presupuesto = ""
                    st.rerun()
        
        with col2:
            if st.button("Cancelar presupuesto actual"):
                st.session_state.productos_presupuesto = []
                st.session_state.servicios_presupuesto = []
                st.session_state.cliente_presupuesto = ""
                st.info("Presupuesto actual cancelado.")
                st.rerun()
    
    if Path(PRESUP_CSV).exists():
        try:
            df_pres = pd.read_csv(PRESUP_CSV, encoding="utf-8")
            
            if "ID" not in df_pres.columns:
                df_pres = pd.read_csv(
                    PRESUP_CSV,
                    header=None,
                    names=["ID", "Cliente", "Fecha", "Total", "Estado", "Productos", "Servicios"],
                    encoding="utf-8"
                )
            
            if df_pres.empty:
                st.info("No hay presupuestos registrados todavía.")
            else:
                df_pres["ID"] = pd.to_numeric(df_pres["ID"], errors="coerce")
                df_pres = df_pres.dropna(subset=["ID"])
                df_pres["ID"] = df_pres["ID"].astype(int)
                
                st.markdown("### Buscar presupuesto")
                clientes_unicos = sorted(set(df_pres["Cliente"].dropna().astype(str).str.strip()))
                cliente_sel = st.selectbox("Filtrar por cliente", ["(Todos)"] + clientes_unicos)
                
                tab_p, tab_c = st.tabs(["Pendientes", "Confirmados"])
                
                for tab, estado in [(tab_p, "pendiente"), (tab_c, "confirmado")]:
                    with tab:
                        df_state = df_pres.copy()
                        if cliente_sel != "(Todos)":
                            df_state = df_state[df_state["Cliente"].str.lower() == cliente_sel.lower()]
                        df_state = df_state[df_state["Estado"] == estado]
                        
                        if df_state.empty:
                            st.info(f"Sin presupuestos {estado}.")
                            continue
                        
                        vista = df_state[["ID", "Cliente", "Fecha", "Total"]].copy()
                        def safe_float_convert(value):
                            try:
                                return float(value)
                            except (ValueError, TypeError):
                                return 0.0

                        vista["Total"] = vista["Total"].apply(safe_float_convert)
                        vista["Total"] = vista["Total"].apply(lambda x: formato_moneda_arg(x, config))
                        st.dataframe(vista.sort_values("Fecha", ascending=False), use_container_width=True)
                        
                        for _, row in df_state.iterrows():
                            header = f"#{int(row['ID'])} — {row['Cliente']} — {row['Fecha']} — {formato_moneda_arg(row['Total'], config)}"
                            with st.expander(header):
                                try:
                                    prods = json.loads(row["Productos"])
                                except Exception:
                                    st.error("Productos mal formateados.")
                                    prods = []
                                
                                if prods:
                                    st.markdown("**Productos:**")
                                    dfp = pd.DataFrame(prods)
                                    dfp["precio_unitario"] = dfp["precio_unitario"].astype(float).apply(lambda x: formato_moneda_arg(x, config))
                                    dfp["subtotal"] = dfp["subtotal"].astype(float).apply(lambda x: formato_moneda_arg(x, config))
                                    st.dataframe(dfp[["nombre", "cantidad", "precio_unitario", "subtotal"]], use_container_width=True)
                                
                                try:
                                    servs = json.loads(row.get("Servicios", "[]"))
                                    if servs:
                                        st.markdown("**Servicios / Mano de obra:**")
                                        dfs = pd.DataFrame(servs)
                                        dfs["precio"] = dfs["precio"].astype(float).apply(lambda x: formato_moneda_arg(x, config))
                                        st.dataframe(dfs, use_container_width=True)
                                except:
                                    pass
                                
                                col_pdf, col_conf = st.columns(2)
                                
                                if col_pdf.button("Generar PDF", key=f"pdf_{row['ID']}_{estado}"):
                                    try:
                                        servs_pdf = json.loads(row.get("Servicios", "[]"))
                                    except:
                                        servs_pdf = []
                                    
                                    presupuesto = {
                                        "id": int(row["ID"]),
                                        "cliente": row["Cliente"],
                                        "fecha": row["Fecha"],
                                        "total_final": float(row["Total"]),
                                        "productos": prods,
                                        "servicios": servs_pdf,
                                    }
                                    ruta_pdf = DATA_DIR / f"presupuesto_{int(row['ID'])}.pdf"
                                    generar_pdf_presupuesto(presupuesto, str(ruta_pdf), config)
                                    st.session_state["pdf_generado"] = str(ruta_pdf)
                                    st.session_state["pdf_id"] = int(row["ID"])
                                    st.success(f"PDF generado: {ruta_pdf}")
                                
                                if ("pdf_generado" in st.session_state and 
                                    st.session_state.get("pdf_id") == int(row["ID"])):
                                    with open(st.session_state["pdf_generado"], "rb") as f:
                                        st.download_button(
                                            "Descargar PDF",
                                            f,
                                            file_name=f"presupuesto_{int(row['ID'])}.pdf",
                                            mime="application/pdf",
                                        )
                                
                                if estado == "pendiente":
                                    col_conf, col_cancel = st.columns(2)
                                    
                                    with col_conf:
                                        if st.button("Confirmar Venta", key=f"conf_{row['ID']}"):
                                            try:
                                                df_pres_actual = pd.read_csv(PRESUP_CSV, encoding="utf-8")
                                                if "ID" not in df_pres_actual.columns:
                                                    df_pres_actual = pd.read_csv(
                                                        PRESUP_CSV,
                                                        header=None,
                                                        names=["ID", "Cliente", "Fecha", "Total", "Estado", "Productos", "Servicios"],
                                                        encoding="utf-8"
                                                    )
                                                
                                                df_pres_actual["ID"] = pd.to_numeric(df_pres_actual["ID"], errors="coerce")
                                                df_pres_actual = df_pres_actual.dropna(subset=["ID"])
                                                df_pres_actual["ID"] = df_pres_actual["ID"].astype(int)
                                                
                                                ok, msg = confirmar_presupuesto_a_venta(
                                                    int(row["ID"]),
                                                    df_pres_actual,
                                                    PRODUCTOS_JSON,
                                                    VENTAS_CSV,
                                                    PRESUP_CSV,
                                                    BACKUPS_DIR
                                                )
                                                if ok:
                                                    st.success(msg)
                                                    st.rerun()
                                                else:
                                                    st.warning(msg)
                                            except Exception as e:
                                                st.error(f"Error al confirmar: {e}")
                                    
                                    with col_cancel:
                                        if st.button("Cancelar presupuesto", key=f"cancel_{row['ID']}"):
                                            try:
                                                df_pres_actual = pd.read_csv(PRESUP_CSV, encoding="utf-8")
                                                if "ID" not in df_pres_actual.columns:
                                                    df_pres_actual = pd.read_csv(
                                                        PRESUP_CSV,
                                                        header=None,
                                                        names=["ID", "Cliente", "Fecha", "Total", "Estado", "Productos", "Servicios"],
                                                        encoding="utf-8"
                                                    )
                                                
                                                df_pres_actual["ID"] = pd.to_numeric(df_pres_actual["ID"], errors="coerce")
                                                df_pres_actual = df_pres_actual.dropna(subset=["ID"])
                                                df_pres_actual["ID"] = df_pres_actual["ID"].astype(int)
                                                
                                                df_pres_actual.loc[df_pres_actual["ID"] == int(row["ID"]), "Estado"] = "cancelado"
                                                df_pres_actual.to_csv(PRESUP_CSV, index=False, encoding="utf-8")
                                                st.success(f"Presupuesto #{int(row['ID'])} cancelado correctamente.")
                                                st.rerun()
                                            except Exception as e:
                                                st.error(f"Error al cancelar: {e}")
                                            
        except Exception as e:
            st.error(f"Error al leer presupuestos: {e}")

# ============================================================
# PÁGINA: RESPALDOS
# ============================================================

elif page == "Respaldos":
    st.header(f"Respaldos Mensuales - {config['nombre_negocio']}")
    
    st.write("""
    Esta sección muestra los respaldos automáticos de tus ventas y presupuestos.
    Los respaldos se organizan automáticamente por mes en carpetas separadas.
    """)
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.metric("Carpeta de respaldos", str(BACKUPS_DIR.name))
    
    st.markdown("---")
    st.subheader("Respaldos disponibles")
    
    carpetas_mes = sorted([d for d in BACKUPS_DIR.iterdir() if d.is_dir()], reverse=True)
    
    if not carpetas_mes:
        st.info("No hay respaldos disponibles todavía.")
    else:
        for carpeta in carpetas_mes:
            mes_nombre = carpeta.name
            archivos = list(carpeta.glob("*.csv"))
            
            with st.expander(f"{mes_nombre} ({len(archivos)} archivo(s))"):
                for archivo in archivos:
                    try:
                        df = pd.read_csv(archivo, encoding="utf-8")
                        
                        col_info, col_descarga = st.columns([3, 1])
                        
                        with col_info:
                            st.write(f"**{archivo.name}**")
                            if "Total" in df.columns:
                                total_ventas = df["Total"].sum()
                                total_unidades = df["Cantidad"].sum() if "Cantidad" in df.columns else 0
                                st.write(f"Ventas: {formato_moneda_arg(total_ventas, config)} | Unidades: {int(total_unidades)}")
                            else:
                                st.write(f"Registros: {len(df)}")
                        
                        with col_descarga:
                            with open(archivo, "rb") as f:
                                st.download_button(
                                    "Descargar",
                                    f,
                                    file_name=archivo.name,
                                    mime="text/csv",
                                    key=f"download_{archivo.stem}"
                                )
                    except Exception as e:
                        st.error(f"Error al leer {archivo.name}: {e}")

# ============================================================
# PÁGINA: CONFIGURACIÓN
# ============================================================

elif page == "Configuración":
    st.header("Configuración general")
    
    st.subheader("Información del negocio")
    nombre = st.text_input("Nombre del comercio", value=config.get("nombre_negocio", ""))
    moneda = st.selectbox(
        "Moneda principal",
        ["ARS", "USD", "EUR"],
        index=["ARS", "USD", "EUR"].index(config.get("moneda", "ARS"))
    )
    
    st.subheader("Inventario y ventas")
    margen = st.number_input(
        "Margen de ganancia por defecto (%)",
        min_value=0.0, max_value=500.0,
        value=config.get("margen_ganancia_defecto", 0.30) * 100,
        step=1.0
    )
    stock_min = st.number_input(
        "Stock mínimo por defecto",
        min_value=0,
        value=config.get("stock_min_defecto", 5),
        step=1
    )
    
    st.subheader("Apariencia")
    tema = st.radio(
        "Tema de la aplicación",
        ["claro", "oscuro"],
        index=0 if config.get("tema", "claro") == "claro" else 1
    )
    
    nuevos_valores = {
        "nombre_negocio": nombre,
        "moneda": moneda,
        "logo_path": config.get("logo_path", ""),
        "margen_ganancia_defecto": margen / 100,
        "stock_min_defecto": stock_min,
        "tema": tema
    }
    
    if nuevos_valores != config:
        st.session_state.config = nuevos_valores
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(nuevos_valores, f, ensure_ascii=False, indent=2)
        st.success("Configuración actualizada.")
        st.rerun()

