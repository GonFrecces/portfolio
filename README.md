# 📊 Portfolio Analysis - Challenge Técnico Python

Sistema de análisis de portafolios de inversión desarrollado en Django que permite modelar, gestionar y visualizar la evolución de portafolios financieros a través del tiempo.

## 🎯 Descripción del Challenge

Este proyecto implementa un sistema para analizar portafolios de inversión compuestos por N activos, donde:

- **$x_{i,t}$**: Monto en dólares del activo i en el tiempo t
- **$V_t = \sum_{i=1}^{N} x_{i,t}$**: Valor total del portafolio en el tiempo t
- **$p_{i,t}$**: Precio del activo i en el tiempo t
- **$c_{i,t}$**: Cantidad del activo i en el tiempo t
- **$x_{i,t} = p_{i,t} \times c_{i,t}$**
- **$w_{i,t} = \frac{x_{i,t}}{V_t}$**: Weight (peso) del activo i en el tiempo t

### Características del Modelo

- Portafolio inicial con valor $V_0 = $1,000,000,000$ al 15/02/2022
- 17 activos invertibles
- Cantidades invariantes: $c_{i,t} = c_{i,0}$ (las cantidades se mantienen constantes después del inicio)
- Los valores de $x_{i,t}$, $w_{i,t}$ y $V_t$ evolucionan por la variación de precios $p_{i,t}$

## 🛠️ Tecnologías Utilizadas

### Backend
- **Python 3.13**
- **Django 6.0** - Framework web principal
- **Django REST Framework 3.16.1** - APIs RESTful
- **SQLite** - Base de datos (desarrollo)

### Frontend
- **Tailwind CSS** - Framework CSS para diseño responsivo
- **Chart.js 4.4.0** - Biblioteca de gráficos interactivos
- **JavaScript (Vanilla)** - Interactividad del dashboard

### Librerías de Análisis de Datos
- **Pandas 2.3.3** - Procesamiento y análisis de datos
- **NumPy 2.4.0** - Operaciones numéricas
- **OpenPyXL 3.1.5** - Lectura de archivos Excel

### Otras Dependencias
- **python-decouple 3.8** - Gestión de configuración
- **python-dateutil 2.9.0** - Manejo de fechas

## 📋 Requisitos Previos

- Python 3.13 o superior
- pip (gestor de paquetes de Python)
- Entorno virtual (recomendado)

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd portfolio
```

### 2. Crear y activar entorno virtual
```bash
python -m venv .venv
source .venv/bin/activate  # En Linux/Mac
# o
.venv\Scripts\activate  # En Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos
```bash
python manage.py migrate
```

### 5. Cargar datos iniciales
```bash
# Cargar activos, portafolios, precios y weights desde datos.xlsx
python manage.py load_portfolio_data

# Calcular cantidades iniciales (c_i,0) para cada portafolio
python manage.py calculate_initial_quantities
```

### 6. Ejecutar el servidor de desarrollo
```bash
python manage.py runserver
```

El servidor estará disponible en: **http://127.0.0.1:8000/**

## 🌐 URLs Disponibles

### 🎨 Frontend - Dashboard

#### `GET /` o `GET /dashboard/`
**Descripción:** Dashboard interactivo con gráficos para visualizar la evolución del portafolio.

**Características:**
- Selector de portafolio
- Rango de fechas configurable
- Gráfico de línea para $V_t$ (valor del portafolio)
- Gráfico stacked area para $w_{i,t}$ (distribución de pesos)
- Gráfico multi-línea para $x_{i,t}$ (valores absolutos de activos)
- Tarjetas informativas con métricas clave

---

### 📡 APIs REST

#### 1. `GET /api/portfolios/`
**Descripción:** Lista todos los portafolios disponibles.

**Respuesta de Ejemplo:**
```json
{
    "count": 2,
    "portfolios": [
        {
            "id": 1,
            "name": "Portafolio 1",
            "initial_value": "1000000000.00",
            "start_date": "2022-02-15",
            "weights": [
                {
                    "asset": {
                        "id": 1,
                        "symbol": "EEUU",
                        "name": "Estados Unidos"
                    },
                    "weight": "0.280000"
                },
                {
                    "asset": {
                        "id": 2,
                        "symbol": "Europa",
                        "name": "Europa"
                    },
                    "weight": "0.087000"
                }
                // ... más activos
            ]
        },
        {
            "id": 2,
            "name": "Portafolio 2",
            "initial_value": "1000000000.00",
            "start_date": "2022-02-15",
            "weights": [
                // ... activos y weights
            ]
        }
    ]
}
```

---

#### 2. `GET /api/portfolios/{portfolio_id}/`
**Descripción:** Obtiene detalles de un portafolio específico.

**Parámetros de URL:**
- `portfolio_id` (int): ID del portafolio

**Ejemplo de Petición:**
```bash
curl http://127.0.0.1:8000/api/portfolios/1/
```

**Respuesta de Ejemplo:**
```json
{
    "id": 1,
    "name": "Portafolio 1",
    "initial_value": "1000000000.00",
    "start_date": "2022-02-15",
    "weights": [
        {
            "asset": {
                "id": 1,
                "symbol": "EEUU",
                "name": "Estados Unidos"
            },
            "weight": "0.280000"
        }
        // ... más activos
    ]
}
```

---

#### 3. `GET /api/metrics/` ⭐ (Pregunta 4 del Challenge)
**Descripción:** Calcula y retorna $w_{i,t}$ y $V_t$ para un portafolio en un rango de fechas.

**Parámetros de Query:**
- `portfolio_id` (int, requerido): ID del portafolio
- `fecha_inicio` (date, requerido): Fecha de inicio (formato: YYYY-MM-DD)
- `fecha_fin` (date, requerido): Fecha de fin (formato: YYYY-MM-DD)

**Ejemplo de Petición:**
```bash
curl "http://127.0.0.1:8000/api/metrics/?portfolio_id=1&fecha_inicio=2022-02-15&fecha_fin=2022-03-15"
```

**Respuesta de Ejemplo:**
```json
{
    "portfolio": {
        "id": 1,
        "name": "Portafolio 1",
        "initial_value": "1000000000.00",
        "start_date": "2022-02-15"
    },
    "query": {
        "fecha_inicio": "2022-02-15",
        "fecha_fin": "2022-03-15",
        "total_days": 29
    },
    "metrics": [
        {
            "date": "2022-02-15",
            "portfolio_value": 1000000000.00,
            "weights": {
                "EEUU": 0.28,
                "Europa": 0.087,
                "UK": 0.073,
                "Japón": 0.056,
                "China": 0.032,
                "EM": 0.082,
                "Gov Bonds": 0.11,
                "IG Corp": 0.085,
                "HY Corp": 0.03,
                "EM Debt": 0.015,
                "Oro": 0.01,
                "Infra": 0.025,
                "RE": 0.03,
                "Hedge Funds": 0.035,
                "PE": 0.025,
                "VC": 0.02,
                "Commodities": 0.045
            },
            "asset_values": {
                "EEUU": 280000000.00,
                "Europa": 87000000.00,
                "UK": 73000000.00,
                "Japón": 56000000.00,
                "China": 32000000.00,
                "EM": 82000000.00,
                "Gov Bonds": 110000000.00,
                "IG Corp": 85000000.00,
                "HY Corp": 30000000.00,
                "EM Debt": 15000000.00,
                "Oro": 10000000.00,
                "Infra": 25000000.00,
                "RE": 30000000.00,
                "Hedge Funds": 35000000.00,
                "PE": 25000000.00,
                "VC": 20000000.00,
                "Commodities": 45000000.00
            }
        },
        {
            "date": "2022-02-16",
            "portfolio_value": 1005234567.89,
            "weights": {
                "EEUU": 0.281234,
                "Europa": 0.086543,
                // ... valores actualizados según variación de precios
            },
            "asset_values": {
                "EEUU": 282456789.12,
                "Europa": 86987654.32,
                // ... valores actualizados
            }
        }
        // ... más días hasta fecha_fin
    ]
}
```

**Notas:**
- Los valores de `weights` suman 1.0 (100%)
- Los valores de `asset_values` suman el `portfolio_value`
- Las cantidades $c_{i,t}$ permanecen constantes, solo varían los precios

---

### 🔒 Admin Panel

#### `GET /admin/`
Panel de administración de Django para gestión manual de datos.

**Modelos disponibles:**
- Assets (Activos)
- Portfolios (Portafolios)
- Prices (Precios)
- Portfolio Weights (Pesos iniciales)
- Holdings (Cantidades)

## 🧮 Lógica de Resolución del Challenge

### 1️⃣ Modelado de Datos (Pregunta 1)

Se crearon los siguientes modelos en Django:

```python
# Activo invertible
class Asset(models.Model):
    symbol = CharField(max_length=50, unique=True)  # EEUU, Europa, etc.
    name = CharField(max_length=200)

# Portafolio
class Portfolio(models.Model):
    name = CharField(max_length=100)
    initial_value = DecimalField(max_digits=15, decimal_places=2)  # V_0
    start_date = DateField()  # t=0

# Precio de un activo en una fecha (p_i,t)
class Price(models.Model):
    asset = ForeignKey(Asset)
    date = DateField()
    price = DecimalField(max_digits=15, decimal_places=6)  # p_i,t

# Peso inicial de un activo en el portafolio (w_i,0)
class PortfolioWeight(models.Model):
    portfolio = ForeignKey(Portfolio)
    asset = ForeignKey(Asset)
    weight = DecimalField(max_digits=10, decimal_places=6)  # w_i,0

# Cantidad de un activo en el portafolio (c_i,t)
class Holding(models.Model):
    portfolio = ForeignKey(Portfolio)
    asset = ForeignKey(Asset)
    quantity = DecimalField(max_digits=15, decimal_places=6)  # c_i,t
    date = DateField()
```

**Relaciones:**
- Un Portfolio tiene múltiples PortfolioWeights (uno por activo)
- Un Portfolio tiene múltiples Holdings (cantidades por activo y fecha)
- Un Asset tiene múltiples Prices (uno por fecha)

---

### 2️⃣ ETL - Carga de Datos (Pregunta 2)

Comando Django: `python manage.py load_portfolio_data`

**Proceso:**
1. **Leer datos.xlsx** con pandas
2. **Hoja "Weights"**:
   - Crear Assets si no existen
   - Crear Portfolios 1 y 2
   - Crear PortfolioWeights para cada activo
3. **Hoja "Precios"**:
   - Crear Prices para cada activo y fecha
4. **Validaciones**:
   - Evitar duplicados
   - Verificar que weights suman 1.0

```python
def handle(self):
    df_weights = pd.read_excel('datos.xlsx', sheet_name='Weights')
    df_prices = pd.read_excel('datos.xlsx', sheet_name='Precios')
    
    # Crear activos, portafolios y cargar datos
    # ...
```

---

### 3️⃣ Cálculo de Cantidades Iniciales (Pregunta 3)

Comando Django: `python manage.py calculate_initial_quantities`

**Fórmula aplicada:**
$$C_{i,0} = \frac{w_{i,0} \times V_0}{P_{i,0}}$$

**Proceso:**
1. Para cada Portfolio (V_0 = $1,000,000,000)
2. Para cada Asset del portafolio:
   - Obtener $w_{i,0}$ (PortfolioWeight)
   - Obtener $p_{i,0}$ (Price en fecha de inicio)
   - Calcular $c_{i,0}$ con la fórmula
   - Crear Holding con la cantidad calculada

```python
for weight in portfolio.weights.all():
    price_at_start = Price.objects.get(
        asset=weight.asset,
        date=portfolio.start_date
    )
    
    # c_i,0 = (w_i,0 * V_0) / p_i,0
    quantity = (weight.weight * portfolio.initial_value) / price_at_start.price
    
    Holding.objects.create(
        portfolio=portfolio,
        asset=weight.asset,
        quantity=quantity,
        date=portfolio.start_date
    )
```

---

### 4️⃣ API de Métricas (Pregunta 4)

Endpoint: `GET /api/metrics/`

**Lógica en PortfolioAnalysisService:**

```python
def calculate_portfolio_metrics(portfolio, fecha_inicio, fecha_fin):
    # 1. Obtener cantidades iniciales (c_i,0 = constantes)
    quantities = {holding.asset_id: holding.quantity 
                  for holding in portfolio.holdings}
    
    # 2. Obtener precios en el rango de fechas (p_i,t)
    prices = Price.objects.filter(
        asset__in=quantities.keys(),
        date__gte=fecha_inicio,
        date__lte=fecha_fin
    )
    
    # 3. Para cada fecha t:
    for date in unique_dates:
        asset_values = {}
        
        for asset_id, price in prices_at_date:
            # x_i,t = p_i,t * c_i,0
            asset_values[asset_id] = price * quantities[asset_id]
        
        # V_t = Σ x_i,t
        portfolio_value = sum(asset_values.values())
        
        # w_i,t = x_i,t / V_t
        weights = {asset: value / portfolio_value 
                   for asset, value in asset_values.items()}
        
        # Retornar métricas del día
        yield {
            'date': date,
            'portfolio_value': portfolio_value,
            'weights': weights,
            'asset_values': asset_values
        }
```

**Optimizaciones:**
- Uso del ORM de Django con `select_related` para reducir queries
- Cálculos en memoria con Decimal para precisión financiera
- Índices en base de datos para búsquedas rápidas por fecha

---

### 5️⃣ Bonus 1: Dashboard con Gráficos

URL: `GET /` o `GET /dashboard/`

**Implementación:**
- **Backend**: Vista Django que renderiza template HTML
- **Frontend**: 
  - Tailwind CSS para diseño responsivo
  - Chart.js para gráficos interactivos
  - JavaScript vanilla para consumir API `/api/metrics/`

**Tipos de Gráficos:**
1. **Line Chart** para $V_t$: Muestra evolución del valor total
2. **Stacked Area Chart** para $w_{i,t}$: Muestra distribución porcentual de activos
3. **Multi-line Chart** para $x_{i,t}$: Muestra valores absolutos por activo

**Flujo:**
1. Usuario selecciona portafolio y rango de fechas
2. JavaScript hace fetch a `/api/metrics/`
3. Datos JSON se transforman a formato Chart.js
4. Gráficos se renderizan dinámicamente

---
