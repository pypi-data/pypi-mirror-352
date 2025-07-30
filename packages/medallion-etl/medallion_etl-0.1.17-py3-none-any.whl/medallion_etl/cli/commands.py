"""Comandos CLI para Medallion ETL."""

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel

console = Console()
app = typer.Typer(
    name="medallion-etl",
    help="🏅 CLI para Medallion ETL - Construye pipelines de datos con arquitectura medallion",
    add_completion=True
)


@app.command()
def init(
    project_dir: str = typer.Option(
        ".", 
        "--project-dir", 
        "-d",
        help="📁 Directorio donde inicializar el proyecto"
    )
):
    """🚀 Inicializa un nuevo proyecto con la estructura de carpetas necesaria."""
    project_dir = Path(project_dir)
    
    # Crear directorios principales
    project_dir.mkdir(exist_ok=True)
    
    # Crear estructura de carpetas para datos
    data_dir = project_dir / "data"
    (data_dir / "bronze").mkdir(parents=True, exist_ok=True)
    (data_dir / "silver").mkdir(parents=True, exist_ok=True)
    (data_dir / "gold").mkdir(parents=True, exist_ok=True)
    
    # Crear directorio de logs
    (project_dir / "logs").mkdir(exist_ok=True)
    
    # Crear directorio de pipelines
    pipelines_dir = project_dir / "pipelines"
    pipelines_dir.mkdir(exist_ok=True)
    
    # Crear directorio de schemas
    schemas_dir = project_dir / "schemas"
    schemas_dir.mkdir(exist_ok=True)
    
    # Crear archivo de configuración
    config_path = project_dir / "config.py"
    with open(config_path, "w", encoding="utf-8") as f:
        f.write("# Configuración para el proyecto Medallion ETL.\n\n")
        f.write("import os\n")
        f.write("from pathlib import Path\n")
        f.write("from medallion_etl.config import MedallionConfig\n\n")
        f.write("# Directorio base del proyecto\n")
        f.write("BASE_DIR = Path(__file__).parent\n\n")
        f.write("# Configuración personalizada\n")
        f.write("config = MedallionConfig(\n")
        f.write("    bronze_dir=BASE_DIR / \"data\" / \"bronze\",\n")
        f.write("    silver_dir=BASE_DIR / \"data\" / \"silver\",\n")
        f.write("    gold_dir=BASE_DIR / \"data\" / \"gold\",\n")
        f.write("    log_dir=BASE_DIR / \"logs\",\n")
        f.write(")\n\n")
        f.write("# Asegurar que los directorios existan\n")
        f.write("config.ensure_directories()\n")
    
    # Crear archivo principal
    main_path = project_dir / "main.py"
    with open(main_path, "w", encoding="utf-8") as f:
        f.write("# Script principal para ejecutar pipelines.\n\n")
        f.write("import argparse\n")
        f.write("from pathlib import Path\n\n")
        f.write("# Importar configuración local\n")
        f.write("from config import config\n\n")
        f.write("# Importar pipelines\n")
        f.write("from pipelines.sample_pipeline import run_sample_pipeline\n\n\n")
        f.write("def main():\n")
        f.write("    parser = argparse.ArgumentParser(description=\"Ejecutar pipelines de Medallion ETL\")\n")
        f.write("    parser.add_argument(\n")
        f.write("        \"--pipeline\", \n")
        f.write("        choices=[\"sample\"], \n")
        f.write("        default=\"sample\",\n")
        f.write("        help=\"Pipeline a ejecutar\"\n")
        f.write("    )\n")
        f.write("    parser.add_argument(\n")
        f.write("        \"--input\", \n")
        f.write("        type=str, \n")
        f.write("        required=True,\n")
        f.write("        help=\"Ruta al archivo de entrada\"\n")
        f.write("    )\n\n")
        f.write("    args = parser.parse_args()\n\n")
        f.write("    if args.pipeline == \"sample\":\n")
        f.write("        metadata = run_sample_pipeline(args.input)\n")
        f.write("        print(f\"Pipeline ejecutado con éxito. Metadatos: {metadata}\")\n")
        f.write("    else:\n")
        f.write("        print(f\"Pipeline {args.pipeline} no encontrado\")\n\n\n")
        f.write("if __name__ == \"__main__\":\n")
        f.write("    main()\n")
    
    # Crear archivo README.md
    readme_path = project_dir / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("# Proyecto Medallion ETL\n\n")
        f.write("Este proyecto utiliza la librería Medallion ETL para construir pipelines de datos con arquitectura medallion.\n\n")
        f.write("## Estructura del proyecto\n\n")
        f.write("```\n")
        f.write(".\n")
        f.write("|- config.py           # Configuración del proyecto\n")
        f.write("|- data/               # Directorio para almacenar datos\n")
        f.write("|   |- bronze/         # Datos crudos (raw)\n")
        f.write("|   |- silver/         # Datos validados y limpios\n")
        f.write(r"|   \- gold/           # Datos transformados y listos para análisis\n")
        f.write("|- logs/               # Logs del proyecto\n")
        f.write("|- main.py             # Script principal\n")
        f.write("|- pipelines/          # Definiciones de pipelines\n")
        f.write(r"\- schemas/            # Esquemas de datos (Pydantic)\n")
        f.write("```\n\n")
        f.write("## Uso\n\n")
        f.write("### Ejecutar un pipeline\n\n")
        f.write("```bash\n")
        f.write("python main.py --pipeline sample --input data/input.csv\n")
        f.write("```\n")
    
    console.print(Panel.fit(
        f"✅ [bold green]Proyecto inicializado en {project_dir}[/bold green]",
        title="🎉 ¡Éxito!"
    ))
    
    console.print("\n📁 [bold blue]Estructura de carpetas creada:[/bold blue]")
    console.print("  📦 data/bronze/   - Datos crudos (raw)")
    console.print("  🥈 data/silver/   - Datos validados y limpios") 
    console.print("  🥇 data/gold/     - Datos transformados y agregados")
    console.print("  📋 logs/          - Logs del proyecto")
    console.print("  🔧 pipelines/     - Definiciones de pipelines")
    console.print("  📝 schemas/       - Esquemas de datos (Pydantic)")
    
    console.print("\n📄 [bold blue]Archivos creados:[/bold blue]")
    console.print("  ⚙️  config.py")
    console.print("  🚀 main.py")
    console.print("  📖 README.md")
    
    console.print("\n💡 [bold yellow]Para comenzar:[/bold yellow]")
    console.print(f"  cd {project_dir}")
    console.print("  medallion-etl create-pipeline MiPipeline")
    console.print("  python main.py --pipeline mipipeline --input <ruta-a-tus-datos>")


@app.command("create-pipeline")
def create_pipeline_cmd(
    name: str = typer.Argument(..., help="📝 Nombre del pipeline a crear"),
    project_dir: Optional[str] = typer.Option(
        None, 
        "--project-dir", 
        "-d",
        help="📁 Directorio del proyecto (por defecto: directorio actual)"
    )
):
    """🔧 Crea un nuevo pipeline a partir de la plantilla."""
    project_dir = Path(project_dir) if project_dir else Path.cwd()
    
    # Verificar que estamos en un proyecto Medallion ETL
    if not (project_dir / "pipelines").exists() or not (project_dir / "schemas").exists():
        console.print("❌ [bold red]Error:[/bold red] El directorio actual no parece ser un proyecto Medallion ETL.")
        console.print("💡 Ejecuta [bold cyan]'medallion-etl init'[/bold cyan] primero para crear la estructura del proyecto.")
        raise typer.Exit(1)
    
    # Crear archivo de pipeline
    pipeline_path = project_dir / "pipelines" / f"{name.lower()}_pipeline.py"
    
    # Crear archivo de esquema
    schema_path = project_dir / "schemas" / f"{name.lower()}_schema.py"
    
    # Escribir el archivo de pipeline
    with open(pipeline_path, "w", encoding="utf-8") as f:
        f.write(f"# Pipeline {name}\n\n")
        f.write("from medallion_etl.core import MedallionPipeline\n")
        f.write("from medallion_etl.bronze import CSVExtractor\n")
        f.write("from medallion_etl.silver import SchemaValidator, DataCleaner\n")
        f.write("from medallion_etl.gold import Aggregator\n")
        f.write(f"from schemas.{name.lower()}_schema import {name}Schema\n")
        f.write("from config import config\n\n\n")
        f.write(f"def create_{name.lower()}_pipeline(pipeline_name=\"{name}Pipeline\"):\n")
        f.write(f"    \"\"\"Crea y configura el pipeline {name}.\"\"\"\n")
        f.write(f"    pipeline = MedallionPipeline(name=pipeline_name, description=\"{name} pipeline\")\n\n")
        f.write("    # Capa Bronze - Extracción\n")
        f.write("    extractor = CSVExtractor(\n")
        f.write(f"        name=\"{name}Extractor\",\n")
        f.write("        description=\"Extrae datos de un archivo CSV\",\n")
        f.write(f"        output_path=config.bronze_dir / \"{name.lower()}\",\n")
        f.write("        save_raw=True\n")
        f.write("    )\n")
        f.write("    pipeline.add_bronze_task(extractor)\n\n")
        f.write("    # Capa Silver - Validación\n")
        f.write("    validator = SchemaValidator(\n")
        f.write(f"        schema_model={name}Schema,\n")
        f.write(f"        name=\"{name}Validator\",\n")
        f.write("        description=\"Valida datos contra el esquema definido\",\n")
        f.write(f"        output_path=config.silver_dir / \"{name.lower()}\",\n")
        f.write("        save_validated=True\n")
        f.write("    )\n")
        f.write("    pipeline.add_silver_task(validator)\n\n")
        f.write("    cleaner = DataCleaner(\n")
        f.write(f"        name=\"{name}Cleaner\",\n")
        f.write("        description=\"Limpia los datos\",\n")
        f.write(f"        output_path=config.silver_dir / \"{name.lower()}\",\n")
        f.write("        drop_na=True,\n")
        f.write("        drop_duplicates=True\n")
        f.write("    )\n")
        f.write("    pipeline.add_silver_task(cleaner)\n\n")
        f.write("    # Capa Gold - Transformación\n")
        f.write("    # TODO: Personalizar las columnas y agregaciones según tus datos\n")
        f.write("    aggregator = Aggregator(\n")
        f.write("        group_by=[\"column1\"],  # Reemplazar con columnas reales\n")
        f.write("        aggregations={\n")
        f.write("            \"column2\": \"sum\",  # Reemplazar con columnas y agregaciones reales\n")
        f.write("            \"column3\": \"mean\"\n")
        f.write("        },\n")
        f.write(f"        name=\"{name}Aggregator\",\n")
        f.write("        description=\"Agrega los datos\",\n")
        f.write(f"        output_path=config.gold_dir / \"{name.lower()}\"\n")
        f.write("    )\n")
        f.write("    pipeline.add_gold_task(aggregator)\n\n")
        f.write("    return pipeline\n\n\n")
        f.write(f"def run_{name.lower()}_pipeline(input_path):\n")
        f.write(f"    \"\"\"Ejecuta el pipeline {name} con los datos de entrada.\"\"\"\n")
        f.write(f"    pipeline = create_{name.lower()}_pipeline()\n")
        f.write("    result = pipeline.run(input_path)\n")
        f.write("    return result.metadata\n")
    
    # Escribir el archivo de esquema
    with open(schema_path, "w", encoding="utf-8") as f:
        f.write(f"# Esquema para el pipeline {name}\n\n")
        f.write("from datetime import datetime\n")
        f.write("from typing import Optional\n")
        f.write("from medallion_etl.schemas import BaseSchema\n\n\n")
        f.write(f"class {name}Schema(BaseSchema):\n")
        f.write(f"    \"\"\"Esquema de datos para el pipeline {name}.\n")
        f.write("    \n")
        f.write("    Define aquí los campos que esperas en tus datos de entrada.\n")
        f.write("    Esto permitirá validar automáticamente la estructura y tipos de datos.\n")
        f.write("    \n")
        f.write("    Ejemplos de campos comunes:\n")
        f.write("    - id: int                           # Campo obligatorio entero\n")
        f.write("    - name: str                         # Campo obligatorio texto\n")
        f.write("    - value: float                      # Campo obligatorio decimal\n")
        f.write("    - date: datetime                    # Campo obligatorio fecha\n")
        f.write("    - optional_field: Optional[str] = None  # Campo opcional\n")
        f.write("    \"\"\"\n")
        f.write("    \n")
        f.write("    # TODO: Define aquí los campos de tu esquema\n")
        f.write("    # Ejemplo:\n")
        f.write("    # id: int\n")
        f.write("    # name: str\n")
        f.write("    # created_at: datetime\n")
        f.write("    \n")
        f.write("    pass  # Elimina esta línea cuando agregues campos reales\n")
    
    console.print(Panel.fit(
        f"✅ [bold green]Pipeline '{name}' creado exitosamente![/bold green]",
        title="🎉 ¡Pipeline Creado!"
    ))
    
    console.print("\n📁 [bold blue]Archivos creados:[/bold blue]")
    console.print(f"  🔧 {pipeline_path}")
    console.print(f"  📝 {schema_path}")
    
    console.print("\n🚀 [bold yellow]Próximos pasos:[/bold yellow]")
    console.print("1. 📝 Edita el esquema en el archivo de schema para definir tus campos")
    console.print("2. ⚙️  Personaliza el pipeline según tus necesidades (columnas, agregaciones)")
    console.print("3. 🔧 Actualiza main.py para incluir tu nuevo pipeline")
    
    console.print("\n💡 [bold cyan]Para probar tu pipeline:[/bold cyan]")
    console.print(f"   python main.py --pipeline {name.lower()} --input <ruta-a-tus-datos>")


def main():
    """Función principal para el CLI de Medallion ETL."""
    app()


if __name__ == "__main__":
    main()