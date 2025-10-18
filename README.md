
# Sistema de Control de Stock

Aplicación web completa para gestión de inventario, ventas y presupuestos desarrollada con Python y Streamlit.

## Características

- **Gestión de Inventario**: Control completo de stock con alertas de stock mínimo
- **Registro de Ventas**: Sistema de ventas con historial y estadísticas
- **Presupuestos**: Creación y gestión de presupuestos con generación de PDF
- **Respaldos Automáticos**: Sistema de backup mensual automático
- **Reportes**: Análisis de productos más vendidos y métricas de ventas
- **Interfaz Moderna**: Diseño responsive con temas claro/oscuro

## Capturas de Pantalla

_(Agregar capturas aquí próximamente)_

## Tecnologías Utilizadas

- **Python 3.8+**
- **Streamlit** - Framework para aplicaciones web
- **Pandas** - Análisis y manipulación de datos
- **ReportLab** - Generación de documentos PDF
- **Matplotlib** - Visualización de datos

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/GMZepeda/control-stock-app.git
cd control-stock-app
```

2. Crear un entorno virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

Ejecutar la aplicación:
```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## Estructura del Proyecto
```
control-stock-app/
├── app.py                      # Aplicación principal
├── utilidades.py               # Funciones auxiliares
├── estilos.py                  # Estilos CSS de la aplicación
├── requirements.txt            # Dependencias del proyecto
├── .gitignore                 # Archivos ignorados por Git
├── assets/                    # Recursos (imágenes, logos)
├── data_ejemplo/              # Datos de ejemplo
│   └── productos_ejemplo.json
└── README.md                  # Este archivo
```

## Funcionalidades Principales

### Inventario
- Visualización completa del stock
- Búsqueda de productos
- Alertas de stock bajo
- Cálculo automático de ganancias

### Productos
- Agregar nuevos productos
- Editar productos existentes
- Cálculo automático de precios con margen
- Eliminación de productos

### Ventas
- Registro rápido de ventas
- Descuento automático de stock
- Historial de ventas
- Estadísticas y gráficos
- Top 5 productos más vendidos

### Presupuestos
- Creación de presupuestos con múltiples productos
- Inclusión de servicios/mano de obra
- Generación de PDF profesional
- Conversión directa a venta
- Gestión de estados (pendiente/confirmado)

### Respaldos
- Backup automático mensual
- Organización por fechas
- Descarga de respaldos históricos

## Configuración

La aplicación permite personalizar:
- Nombre del negocio
- Moneda (ARS, USD, EUR)
- Margen de ganancia por defecto
- Stock mínimo por defecto
- Tema (claro/oscuro)

## Datos de Ejemplo

Para probar la aplicación, podés usar los archivos de ejemplo en la carpeta `data_ejemplo/`.

## Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork del proyecto
2. Crear una rama para tu feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit de tus cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Autor

**Germán M. Zepeda**

- GitHub: [@GMZepeda](https://github.com/GMZepeda)

## Proyecto Vendido

Este proyecto fue desarrollado y vendido exitosamente como solución comercial para gestión de inventario.

---

Si te resultó útil este proyecto, dale una estrella en GitHub!
