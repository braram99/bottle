# 🤖 Trading Risk Assistant

Un asistente inteligente que te ayuda a tomar decisiones de trading basadas en confluencias técnicas, psicología y condiciones de mercado. **NO opera automáticamente** - tú decides, él te guía.

## 🎯 ¿Qué hace este bot?

El Trading Risk Assistant evalúa si debes operar ese día y con cuánto riesgo (0%, 2% o 3%) basándose en:

- ✅ **Hard Stops**: Condiciones que te impiden operar (pérdidas consecutivas, mal estado mental, etc.)
- 📊 **Sistema de Scoring**: Evalúa psicología, condiciones de mercado y confluencias técnicas
- 💰 **Cálculo de Lote**: Calcula automáticamente el tamaño de posición según tu riesgo
- 📒 **Journal Automático**: Guarda todas tus decisiones para análisis posterior
- 🧠 **Coach Personal**: Te da insights y sugerencias basados en tus patrones

## 📁 Estructura del Proyecto

```
trading_risk_assistant/
│
├── main.py                 # CLI principal - ejecuta esto
├── risk_logic.py           # Lógica de scoring y evaluación
├── journal.py              # Sistema de registro de decisiones
├── brain.py                # Coach inteligente
├── config.yaml             # Configuración del sistema
├── journal.json            # Historial de decisiones (se crea automáticamente)
├── requirements.txt        # Dependencias
└── README.md              # Este archivo
```

## 🚀 Instalación

### 1. Clona o descarga el proyecto

```bash
git clone https://github.com/tu-usuario/trading_risk_assistant.git
cd trading_risk_assistant
```

### 2. Crea un entorno virtual (recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

## 💻 Uso Básico

### Ejecutar el bot en CLI

```bash
python main.py
```

El bot te hará preguntas interactivas sobre:

1. **Estadísticas actuales** (pérdidas consecutivas, pérdida diaria)
2. **Psicología** (estado mental, control emocional, horas de sueño)
3. **Condiciones de mercado** (noticias, correlación, bias, fase del mercado)
4. **Confluencias técnicas** (timeframes alineados, FVG, inducement, estructura)

Al final te dará:
- ✅ Si debes operar o no
- 📊 Tu score final y desglose por categoría
- 💰 Porcentaje de riesgo recomendado (2% o 3%)
- 📏 Tamaño de lote calculado (si lo solicitas)

### Ver estadísticas del journal

```python
from journal import JournalManager

journal = JournalManager()

# Ver resumen de los últimos 7 días
journal.print_summary(days=7)

# Obtener estadísticas programáticamente
stats = journal.get_stats(days=30)
print(stats)
```

### Obtener insights del coach

```python
from brain import TradingCoach
from journal import JournalManager
from risk_logic import ConfigLoader

journal = JournalManager()
config = ConfigLoader()
coach = TradingCoach(journal, config)

# Obtener mensaje de coaching
coach.print_coaching_message()

# Obtener reporte semanal
print(coach.get_weekly_report())
```

## ⚙️ Configuración

El archivo `config.yaml` controla todo el comportamiento del sistema. Puedes personalizar:

### Hard Stops

```yaml
hard_stops:
  max_consecutive_losses: 3
  max_daily_loss_percent: 6
  min_sleep_hours: 5
  psychology_min_score: 3
  require_clear_bias: true
```

### Sistema de Scoring

```yaml
scoring:
  weights:
    psychology: 25          # 25% del score total
    market_conditions: 30   # 30% del score total
    technical_confluence: 45 # 45% del score total
  
  thresholds:
    no_trade: 50      # Score < 50 = No operar
    risk_2_percent: 70 # Score 50-70 = 2% riesgo
    risk_3_percent: 100 # Score > 70 = 3% riesgo
```

### Preguntas y Pesos

Cada pregunta tiene un peso dentro de su categoría. Puedes ajustar los pesos según tu estrategia:

```yaml
questions:
  psychology:
    - id: "mental_state"
      question: "¿Cómo te sientes mentalmente?"
      weight: 0.4  # 40% de la categoría psicología
      type: "scale"
      min: 1
      max: 5
```

## 📊 Ejemplo de Uso Completo

```python
from risk_logic import RiskAssistant

# Crear instancia del asistente
assistant = RiskAssistant()

# Tus respuestas
answers = {
    # Psicología
    'mental_state': 4,
    'emotional_control': 5,
    'sleep_quality': 7,
    
    # Condiciones de mercado
    'red_news': False,
    'correlation_aligned': True,
    'clear_bias': True,
    'market_phase': 4,
    
    # Confluencias técnicas
    'timeframe_alignment': True,
    'fvg_present': True,
    'inducement': True,
    'structure_break': True,
    'liquidity_sweep': False,
    'confluence_count': 4
}

# Estadísticas
stats = {
    'consecutive_losses': 0,
    'daily_loss_percent': 0
}

# Evaluar
decision = assistant.evaluate(
    answers=answers,
    stats=stats,
    balance=1000,
    sl_pips=20,
    pair='EURUSD'
)

# Mostrar resultado
print(assistant.format_decision(decision))
```

## 🎓 Metodología del Sistema de Scoring

### Cómo se calcula el score:

1. **Por cada pregunta**: Se normaliza la respuesta a un valor 0-100
2. **Por categoría**: Se promedian las preguntas ponderadas por su peso
3. **Score final**: Se promedian las categorías ponderadas por su peso global

### Ejemplo de cálculo:

```
Psicología (25%):
  - mental_state (4/5) x 0.4 = 80 x 0.4 = 32
  - emotional_control (5/5) x 0.3 = 100 x 0.3 = 30
  - sleep_quality (7h) x 0.3 = 87.5 x 0.3 = 26.25
  = Score Psicología: 88.25

Market Conditions (30%): 85.0
Technical Confluence (45%): 75.0

Score Final = (88.25 × 0.25) + (85 × 0.30) + (75 × 0.45)
            = 22.06 + 25.5 + 33.75
            = 81.31/100 ✅ TRADEAR CON 3%
```

## 🔄 Flujo de Decisión

```
┌─────────────────────┐
│  Responder preguntas │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Evaluar Hard Stops  │
└──────────┬──────────┘
           │
     ¿Pasó? ──No──> ❌ NO TRADEAR
           │
          Sí
           │
           ▼
┌─────────────────────┐
│  Calcular Score     │
└──────────┬──────────┘
           │
           ▼
     Score < 50 ──────> ❌ NO TRADEAR
     Score 50-70 ─────> ✅ TRADEAR 2%
     Score > 70 ──────> ✅ TRADEAR 3%
           │
           ▼
┌─────────────────────┐
│  Calcular Lote      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Guardar en Journal │
└─────────────────────┘
```

## 🧠 Sistema de Coach

El coach analiza tus patrones y te da feedback:

- 📉 **Tendencia de scores**: ¿Están mejorando o empeorando?
- 🎯 **Patrones de riesgo**: ¿Eres muy agresivo o muy conservador?
- 😰 **Psicología**: ¿Tu estado mental ha sido consistente?
- ⏰ **Inactividad**: ¿Llevas mucho tiempo sin operar?
- 🛑 **Hard stops frecuentes**: ¿Qué te está deteniendo más?

## 🔮 Próximas Funcionalidades

- [ ] Bot de Telegram interactivo
- [ ] Integración con Google Sheets
- [ ] Exportar a Notion
- [ ] Dashboard web con gráficas
- [ ] Análisis de correlación con resultados reales
- [ ] Machine Learning para sugerencias personalizadas
- [ ] Notificaciones automáticas de inactividad

## 📝 Roadmap

### Fase 1: CLI (✅ Completado)
- Sistema de preguntas interactivo
- Evaluación de hard stops
- Cálculo de scoring
- Journal automático
- Coach básico

### Fase 2: Bot de Telegram (🚧 En progreso)
- Comandos básicos (/start, /evaluate, /stats)
- Guardado de preferencias por usuario
- Notificaciones programadas

### Fase 3: Integraciones
- Google Sheets export
- Notion integration
- CSV export con análisis

### Fase 4: Analytics
- Dashboard web
- Gráficas de desempeño
- Correlación score vs resultados

## 🤝 Contribuir

¿Tienes ideas para mejorar el bot? ¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## 📄 Licencia

MIT License - Siéntete libre de usar este proyecto para tu trading personal.

## ⚠️ Disclaimer

Este bot es una **herramienta de ayuda para la toma de decisiones**, NO es un sistema de trading automático ni asesoramiento financiero. 

- ❌ No garantiza ganancias
- ❌ No reemplaza tu análisis personal
- ❌ No opera automáticamente
- ✅ Te ayuda a ser más disciplinado
- ✅ Te obliga a seguir tu proceso
- ✅ Te protege de operar en malas condiciones

**El trading de divisas implica riesgos. Opera solo con capital que puedas permitirte perder.**

## 📧 Contacto

¿Preguntas o sugerencias? Abre un issue en GitHub.

---

**¡Buena suerte y trade seguro! 📈✨**
