import argparse
import sys
from datetime import datetime
from pathlib import Path

# =============================================================================
# CONFIGURACIÓN
# =============================================================================
DEFAULT_OUTPUT_DIR = ".summary"
TEXT_EXTENSIONS = {'.gd', '.tscn', '.godot', '.txt', '.md', '.json', '.shader'}
IGNORE_EXTENSIONS = {'.import', '.uid'}
INCLUDE_DIRS_ROOT = {'assets', 'scripts', 'scenes', 'resources'}

def es_proyecto_valido(ruta: Path) -> bool:
    """Verifica si la ruta contiene un archivo project.godot."""
    return (ruta / "project.godot").exists()

def obtener_estructura(ruta_base: Path, nombre_salida: str):
    """
    Recorre el proyecto y genera el árbol de directorios y la lista de archivos a leer.
    """
    lineas_arbol = []
    archivos_contenido = []
    
    # Listar y ordenar para consistencia
    for path in sorted(ruta_base.rglob('*')):
        # Ignorar carpetas ocultas (excepto la de salida si está dentro)
        if any(part.startswith('.') for part in path.parts if part != DEFAULT_OUTPUT_DIR):
            continue
            
        rel_path = path.relative_to(ruta_base)
        parts = rel_path.parts
        
        # Filtro de raíz: Solo carpetas permitidas o archivos en la raíz
        if len(parts) > 0 and parts[0] not in INCLUDE_DIRS_ROOT and not path.is_file():
            if len(parts) == 1: continue 
        
        # No incluir el archivo de salida ni el script actual en el reporte
        if path.name == nombre_salida or path.name == Path(__file__).name:
            continue

        level = len(parts)
        indent = "    " * level
        prefijo = "res://" if level == 0 else ""
        
        if path.is_dir():
            lineas_arbol.append(f"{indent}{prefijo}{path.name}/")
        else:
            lineas_arbol.append(f"{indent}{path.name}")
            if path.suffix.lower() in TEXT_EXTENSIONS and path.suffix.lower() not in IGNORE_EXTENSIONS:
                archivos_contenido.append(path)
                
    return lineas_arbol, archivos_contenido

def generar_reporte(output_path: Path, nombre_proyecto: str, archivos: list, arbol: list, ruta_base: Path):
    """Escribe el archivo final de resumen."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            header = [
                "="*60,
                f"RESUMEN DE PROYECTO GODOT",
                f"FECHA: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"PROYECTO: {nombre_proyecto}",
                f"ARCHIVOS PROCESADOS: {len(archivos)}",
                "="*60,
                "\nESTRUCTURA DEL PROYECTO:",
                "\n".join(arbol),
                "\n" + "="*60,
                "CONTENIDO DE ARCHIVOS",
                "="*60
            ]
            f.write("\n".join(header) + "\n")

            for path in archivos:
                rel_p = path.relative_to(ruta_base)
                f.write(f"\n[ARCHIVO]: {rel_p}\n")
                f.write("-" * (len(str(rel_p)) + 12) + "\n")
                
                try:
                    content = path.read_text(encoding='utf-8', errors='replace')
                    f.write(content)
                except Exception as e:
                    f.write(f"<< Error al leer archivo: {e} >>\n")
                
                f.write(f"\n--- FIN DE: {rel_p} ---\n")
        return True
    except Exception as e:
        print(f"❌ Error crítico al escribir el reporte: {e}")
        return False

def mostrar_banner():
    print("\n" + "🚀 GODOT PROJECT SUMMARIZER ".center(60, "="))

def main():
    parser = argparse.ArgumentParser(description="Generador profesional de resúmenes para Godot 4.x")
    parser.add_argument("path", nargs="?", default=".", help="Ruta del proyecto")
    parser.add_argument("-o", "--output", help="Nombre personalizado para el archivo")
    parser.add_argument("-d", "--dir", help="Directorio de destino (ignora el .summary por defecto)")
    args = parser.parse_args()

    ruta_base = Path(args.path).resolve()
    nombre_proyecto = ruta_base.name if ruta_base.name else "proyecto_godot"
    
    mostrar_banner()

    if not es_proyecto_valido(ruta_base):
        print(f"❌ Error: No se encontró 'project.godot' en: {ruta_base}")
        print("Asegúrate de ejecutar el script en la raíz del proyecto.")
        input("\nPresiona Enter para cerrar...")
        sys.exit(1)

    # Lógica de Carpeta de Salida:
    # 1. Si el usuario provee un directorio con -d, se usa ese.
    # 2. Si no, se crea la carpeta .summary dentro de la ruta del proyecto.
    if args.dir:
        ruta_salida = Path(args.dir).resolve()
    else:
        ruta_salida = ruta_base / DEFAULT_OUTPUT_DIR
    
    ruta_salida.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"{args.output or nombre_proyecto}_{timestamp}.txt"
    output_path = ruta_salida / nombre_archivo

    print(f"🔍 Analizando: {nombre_proyecto}")
    
    lineas_arbol, archivos_lectura = obtener_estructura(ruta_base, nombre_archivo)
    
    print(f"📊 Archivos encontrados: {len(archivos_lectura)}")
    print(f"📝 Generando reporte en: {ruta_salida.name}/{nombre_archivo}...")

    if generar_reporte(output_path, nombre_proyecto, archivos_lectura, lineas_arbol, ruta_base):
        print("\n✅ ¡Reporte generado con éxito!")
        print(f"📂 Ubicación completa: {output_path}")
    
    print("="*60)
    input("Presiona Enter para finalizar...")

if __name__ == "__main__":
    main()