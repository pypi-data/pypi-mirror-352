# Medallion ETL

Una librería modular para construir data pipelines con arquitectura medallion (Bronze-Silver-Gold).

## 🚀 Características

- **Arquitectura Medallion**: Implementación completa del patrón Bronze-Silver-Gold
- **CLI Integrado**: Comandos para inicializar proyectos y crear pipelines
- **Modular y Extensible**: Componentes reutilizables para cada capa del proceso
- **Validación de Datos**: Esquemas con Pydantic para garantizar calidad de datos
- **Procesamiento Eficiente**: Powered by Polars para manejo de grandes volúmenes
- **Orquestación**: Integración nativa con Prefect para workflows complejos
- **Conectores**: Soporte para múltiples fuentes de datos (CSV, JSON, SQL, APIs)
- **Logging Avanzado**: Sistema de logging estructurado con Rich

## 📋 Requisitos

- Python 3.11+
- polars >= 1.30
- pydantic >= 2.7
- sqlalchemy >= 2.0
- prefect >= 3.0
- requests >= 2.25.0
- rich >= 14.0.0

## 📦 Instalación

```bash
pip install medallion-etl
```

O desde el código fuente:

```bash
git clone https://github.com/JuanManiglia/medallion-etl.git
cd medallion-etl
pip install -e .
```

## 🛠️ Comandos CLI

### Inicializar un nuevo proyecto

```bash
medallion-etl init
```

O especificar un directorio:

```bash
medallion-etl init --project-dir mi_proyecto
```

Esto creará la siguiente estructura:

```
mi_proyecto/
├── config.py              # Configuración del proyecto
├── main.py                 # Script principal
├── README.md              # Documentación del proyecto
├── data/                  # Directorio para datos
│   ├── bronze/           # Datos crudos (raw)
│   ├── silver/           # Datos validados y limpios
│   └── gold/             # Datos transformados y agregados
├── logs/                  # Logs del proyecto
├── pipelines/             # Definiciones de pipelines
└── schemas/               # Esquemas de datos (Pydantic)
```

### Crear un nuevo pipeline

```bash
medallion-etl create-pipeline MiPipeline
```

Esto generará:
- `pipelines/mipipeline_pipeline.py` - Definición del pipeline
- `schemas/mipipeline_schema.py` - Esquema de datos con Pydantic

## 🏗️ Arquitectura Medallion

### 🥉 Bronze Layer (Datos Crudos)
- **Propósito**: Ingesta de datos en su formato original
- **Extractores disponibles**:
  - `CSVExtractor` - Archivos CSV
  - `JSONExtractor` - Archivos JSON
  - `SQLExtractor` - Bases de datos SQL
  - `APIExtractor` - APIs REST

### 🥈 Silver Layer (Datos Validados)
- **Propósito**: Validación, limpieza y normalización
- **Componentes**:
  - `SchemaValidator` - Validación con esquemas Pydantic
  - `DataCleaner` - Limpieza de datos (duplicados, nulos)
  - `DataNormalizer` - Normalización de formatos

### 🥇 Gold Layer (Datos Transformados)
- **Propósito**: Agregaciones y transformaciones para análisis
- **Transformadores**:
  - `Aggregator` - Agregaciones (sum, mean, count, etc.)
  - `DataJoiner` - Unión de datasets
  - `FeatureEngineer` - Creación de nuevas características

## 🔧 Uso Básico

### 1. Crear un proyecto

```bash
medallion-etl init --project-dir mi_etl_project
cd mi_etl_project
```

### 2. Crear un pipeline personalizado

```bash
medallion-etl create-pipeline Ventas
```

### 3. Configurar el esquema de datos

Edita `schemas/ventas_schema.py`:

```python
from datetime import datetime
from typing import Optional
from medallion_etl.schemas import BaseSchema

class VentasSchema(BaseSchema):
    id: int
    producto: str
    cantidad: int
    precio: float
    fecha: datetime
    cliente: Optional[str] = None
```

### 4. Personalizar el pipeline

Edita `pipelines/ventas_pipeline.py` según tus necesidades.

### 5. Ejecutar el pipeline

```bash
python main.py --pipeline ventas --input data/ventas.csv
```

## 📊 Ejemplo de Pipeline Completo

```python
from medallion_etl.core import Pipeline
from medallion_etl.bronze import CSVExtractor
from medallion_etl.silver import SchemaValidator, DataCleaner
from medallion_etl.gold import Aggregator
from schemas.ventas_schema import VentasSchema

def create_sales_pipeline():
    pipeline = Pipeline(name="SalesPipeline")
    
    # Bronze: Extraer datos
    extractor = CSVExtractor(
        name="SalesExtractor",
        output_path=config.bronze_dir / "sales"
    )
    pipeline.add_task(extractor)
    
    # Silver: Validar y limpiar
    validator = SchemaValidator(
        schema_model=VentasSchema,
        name="SalesValidator"
    )
    pipeline.add_task(validator)
    
    cleaner = DataCleaner(
        name="SalesCleaner",
        drop_na=True,
        drop_duplicates=True
    )
    pipeline.add_task(cleaner)
    
    # Gold: Agregar datos
    aggregator = Aggregator(
        group_by=["producto"],
        aggregations={
            "cantidad": "sum",
            "precio": "mean"
        },
        name="SalesAggregator"
    )
    pipeline.add_task(aggregator)
    
    return pipeline

# Ejecutar pipeline
pipeline = create_sales_pipeline()
result = pipeline.run("data/ventas.csv")
```

## 🔌 Conectores Disponibles

### Extractores (Bronze)
- **CSVExtractor**: Archivos CSV con configuración flexible
- **JSONExtractor**: Archivos JSON y JSONL
- **SQLExtractor**: Bases de datos relacionales
- **APIExtractor**: APIs REST con autenticación
- **FileExtractor**: Extractor base para otros formatos

### Validadores (Silver)
- **SchemaValidator**: Validación con esquemas Pydantic
- **DataCleaner**: Limpieza automática de datos
- **DataNormalizer**: Normalización de tipos y formatos

### Transformadores (Gold)
- **Aggregator**: Agregaciones grupales
- **DataJoiner**: Unión de múltiples datasets
- **FeatureEngineer**: Creación de características derivadas

## 🔧 Configuración

La configuración se maneja a través de la clase `MedallionConfig`:

```python
from medallion_etl.config import MedallionConfig

config = MedallionConfig(
    bronze_dir="data/bronze",
    silver_dir="data/silver", 
    gold_dir="data/gold",
    log_dir="logs",
    log_level="INFO"
)
```

## 🚀 Integración con Prefect

Convierte cualquier pipeline en un flow de Prefect:

```python
from prefect import serve

pipeline = create_sales_pipeline()
flow = pipeline.as_prefect_flow(name="sales-etl")

# Desplegar como servicio
serve(flow)
```

## 📝 Logging

Sistema de logging estructurado con Rich:

```python
from medallion_etl.utils import logger

logger.info("Pipeline iniciado", extra={"pipeline": "sales"})
logger.error("Error en validación", extra={"records_failed": 10})
```

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🔗 Enlaces

- **Repositorio**: [https://github.com/JuanManiglia/medallion-etl](https://github.com/JuanManiglia/medallion-etl)
- **Documentación**: [En desarrollo]
- **Issues**: [https://github.com/JuanManiglia/medallion-etl/issues](https://github.com/JuanManiglia/medallion-etl/issues)

---

**Medallion ETL** - Construye pipelines de datos robustos y escalables con arquitectura medallion 🏅