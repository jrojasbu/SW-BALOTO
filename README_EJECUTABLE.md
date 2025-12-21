# SW BALOTO - Instrucciones de Uso

## 📦 Ejecutable Generado

El archivo ejecutable `SW_BALOTO.exe` se encuentra en la carpeta `dist/`.

**Tamaño:** ~21 MB  
**Ubicación:** `c:\Users\JROJASBU\OneDrive\Documentos\PROYECTOS\SW BALOTO\dist\SW_BALOTO.exe`

## 🚀 Cómo Usar el Ejecutable

### Opción 1: Ejecución Directa
1. Navega a la carpeta `dist`
2. Haz doble clic en `SW_BALOTO.exe`
3. Se abrirá una ventana de consola y automáticamente se abrirá tu navegador predeterminado
4. La aplicación estará disponible en `http://127.0.0.2:5000`

### Opción 2: Distribuir a Otros Usuarios
1. Copia el archivo `SW_BALOTO.exe` a cualquier computadora con Windows
2. **No se requiere Python instalado** - el ejecutable es completamente independiente
3. Ejecuta el archivo y la aplicación se abrirá automáticamente

## ⚙️ Funcionalidades

- **Obtener Resultados:** Hace scraping de los últimos resultados de Baloto y MiLoto
- **Generar Predicciones:** Calcula las combinaciones más frecuentes basadas en datos históricos
- **Estadísticas:** Visualiza la frecuencia de números ganadores
- **Entrada Manual:** Permite agregar resultados manualmente

## 📝 Notas Importantes

- **Conexión a Internet:** Se requiere conexión a internet para obtener resultados actualizados
- **Ventana de Consola:** Mantén la ventana de consola abierta mientras uses la aplicación
- **Cerrar la Aplicación:** Para cerrar, simplemente cierra la ventana de consola
- **Antivirus:** Algunos antivirus pueden marcar el ejecutable como sospechoso (falso positivo). Esto es normal con ejecutables generados por PyInstaller

## 🔧 Regenerar el Ejecutable

Si necesitas regenerar el ejecutable después de hacer cambios al código:

```powershell
# Desde la carpeta del proyecto
pyinstaller build_exe.spec --clean
```

El nuevo ejecutable se generará en la carpeta `dist/`.

## 📂 Estructura del Proyecto

```
SW BALOTO/
├── app.py              # Aplicación Flask principal
├── launcher.py         # Script de inicio (usado por el .exe)
├── logic.py            # Lógica de predicciones
├── scraper.py          # Web scraping de resultados
├── build_exe.spec      # Configuración de PyInstaller
├── templates/          # Plantillas HTML
├── static/             # Archivos CSS y JS
└── dist/
    └── SW_BALOTO.exe   # ✨ Ejecutable generado
```

## 🆘 Solución de Problemas

### El navegador no se abre automáticamente
- Abre manualmente tu navegador y ve a: `http://127.0.0.2:5000`

### Error "Puerto en uso"
- Cierra cualquier otra instancia de la aplicación
- O cambia el puerto en `launcher.py` (línea 24)

### El antivirus bloquea el ejecutable
- Agrega una excepción en tu antivirus para `SW_BALOTO.exe`
- O ejecuta desde el código fuente con Python
