# Etapa 5: Selector de Modelos Agrupados por Uso/Tipo

## Objetivo
Transformar el selector de modelos de Cognitia de una lista plana con filtros básicos a un selector inteligente que agrupe modelos por categorías de uso, facilitando la selección para usuarios no técnicos y power users.

## Investigación de Mercado (Benchmark)

### 1. OpenRouter - Líder en Categorización
**URL:** [openrouter.ai/models](https://openrouter.ai/models)

**Categorías de Uso:**
| Categoría | Descripción |
|-----------|-------------|
| Programming/Coding | Modelos optimizados para código y desarrollo |
| Creative/Roleplay | Escritura creativa, storytelling, interacción |
| Reasoning | Modelos con capacidades de pensamiento paso a paso |
| Technology | Consultas técnicas generales |
| Science | Investigación y análisis científico |
| Finance | Análisis financiero y negocios |
| Translation | Traducciones y multilingüe |

**Atributos por Modelo:**
- Token usage (popularidad)
- Context window size (262K, 128K, etc.)
- Pricing (input/output tokens)
- Ranking por categoría (#1 en Programming, #3 en Science)
- Provider/Author (Anthropic, OpenAI, Google, etc.)

**Filtros y Ordenamiento:**
- Newest, Most Popular, Top Weekly
- Pricing: Low to High / High to Low
- Context: High to Low
- Throughput: High to Low
- Latency: Low to High

**UX Destacada:**
- Auto Router: Selección automática del mejor modelo basada en el prompt
- Collections: Agrupaciones curadas (Free Models, Best for Coding, Roleplay)

### 2. TypingMind - Organización por Agentes
**URL:** [typingmind.com](https://www.typingmind.com/)

**Características:**
- **Tags en prompts y chats** para búsqueda/filtrado rápido
- **Categorías para AI Agents** organizados por tareas específicas
- **Project Folders** con modelo pre-asignado por contexto
- **Prompt Library** con tags de la comunidad

**UX Destacada:**
- Cambio fluido entre providers sin salir de la interfaz
- Chat con múltiples modelos simultáneamente para comparación
- Asignación de modelos específicos a agentes/proyectos

### 3. Poe (Quora) - Agregador Multi-Modelo
**URL:** [poe.com](https://poe.com)

**Características:**
- Iconos por proveedor (GPT logo, Claude logo, etc.)
- Bots personalizados como "GPTs" con casos de uso específicos
- Comparación de respuestas entre modelos
- Descubrimiento de bots por comunidad

**UX Destacada:**
- Sidebar para cambio rápido de modelo
- Vista colorida con identidad visual por modelo
- Playground para experimentación

### 4. ChatGPT 5.2 - Auto-Routing
**Innovación:**
- Detección automática si el prompt requiere "Thinking Mode"
- Usuario no necesita elegir modelo manualmente
- Ajuste dinámico de compute allocation

### 5. MultipleChat - Modo Colaborativo
**URL:** [multiple.chat](https://multiple.chat)

**Características:**
- Smart Mode: Procesamiento colaborativo entre modelos
- Modo Individual: Interacción con modelo específico
- Selector contextual basado en necesidad

---

## Estado Actual (AS-IS) - Open WebUI

### Componentes Existentes
- `src/lib/components/chat/ModelSelector.svelte` - Wrapper principal
- `src/lib/components/chat/ModelSelector/Selector.svelte` - Dropdown con lógica

### Funcionalidades Actuales
| Feature | Estado | Notas |
|---------|--------|-------|
| Búsqueda fuzzy (Fuse.js) | ✅ | Por nombre, tags, descripción |
| Filtro por tags | ✅ | Tags personalizados del admin |
| Filtro por conexión | ✅ | Local / External / Direct |
| Modelos pineados | ✅ | Guardados en settings |
| Descarga Ollama inline | ✅ | Solo admin |
| Agrupación por categoría | ❌ | No existe |
| Badges de capacidades | ❌ | No existe |
| Métricas de performance | ❌ | No existe |
| Auto-selección inteligente | ❌ | No existe |

### Limitaciones Actuales
1. Lista plana sin jerarquía visual
2. Tags genéricos definidos por admin, no semánticos
3. Sin indicadores de capacidades (coding, reasoning, etc.)
4. Sin información de context window o pricing
5. Difícil para usuarios no técnicos elegir el modelo correcto

---

## Propuesta (TO-BE)

### Agrupación por Categoría de Uso

```
┌─────────────────────────────────────────────┐
│ 🔍 Buscar modelo...                         │
├─────────────────────────────────────────────┤
│ [Todos] [Coding] [Creativo] [Análisis] ... │
├─────────────────────────────────────────────┤
│ ⭐ FAVORITOS                                │
│   └─ Claude Sonnet 4.5          🧠 128K    │
│   └─ GPT-4o                     🧠 128K    │
├─────────────────────────────────────────────┤
│ 💻 CODING & DESARROLLO                      │
│   └─ Claude Sonnet 4.5    #1    🧠 128K ⚡ │
│   └─ GPT-4o              #2    🧠 128K    │
│   └─ DeepSeek Coder      #3    🧠 32K  💰 │
├─────────────────────────────────────────────┤
│ 🎨 CREATIVO & ESCRITURA                     │
│   └─ Claude Opus 4.5     #1    🧠 200K    │
│   └─ GPT-4o              #2    🧠 128K    │
├─────────────────────────────────────────────┤
│ 📊 ANÁLISIS & RAZONAMIENTO                  │
│   └─ o1                  #1    🧠 128K 🤔 │
│   └─ Claude Opus 4.5     #2    🧠 200K    │
├─────────────────────────────────────────────┤
│ ⚡ RÁPIDOS & ECONÓMICOS                     │
│   └─ Claude Haiku        ⚡⚡   🧠 200K 💰💰│
│   └─ GPT-4o-mini         ⚡⚡   🧠 128K 💰💰│
│   └─ Gemini Flash        ⚡⚡⚡  🧠 1M   💰💰│
├─────────────────────────────────────────────┤
│ 🏠 LOCALES (Ollama)                         │
│   └─ llama3.2:latest           🧠 8K      │
│   └─ mistral:7b                🧠 8K      │
└─────────────────────────────────────────────┘

Leyenda:
🧠 = Context Window    ⚡ = Velocidad    💰 = Económico
🤔 = Reasoning Mode    #N = Ranking
```

### Categorías Propuestas para Cognitia (Enterprise Colombia)

| ID | Categoría | Emoji | Descripción | Modelos Típicos |
|----|-----------|-------|-------------|-----------------|
| `coding` | Coding & Desarrollo | 💻 | Generación de código, debugging, reviews | Claude Sonnet, GPT-4o, DeepSeek |
| `creative` | Creativo & Escritura | 🎨 | Contenido, copywriting, storytelling | Claude Opus, GPT-4 |
| `analysis` | Análisis & Razonamiento | 📊 | Datos, investigación, decisiones | o1, Claude Opus |
| `fast` | Rápidos & Económicos | ⚡ | Tareas simples, alto volumen | Haiku, GPT-4o-mini, Flash |
| `local` | Locales | 🏠 | Modelos Ollama, privacidad total | Llama, Mistral, Phi |
| `vision` | Visión & Multimodal | 👁️ | Análisis de imágenes, OCR | GPT-4o, Claude, Gemini |
| `documents` | Documentos Largos | 📄 | RAG, análisis de PDFs extensos | Gemini 1M, Claude 200K |

### Badges de Capacidades

| Badge | Significado |
|-------|-------------|
| 🧠 128K | Context window |
| ⚡ | Alta velocidad (latencia <500ms) |
| ⚡⚡ | Muy rápido (latencia <200ms) |
| 💰 | Económico (< $1/1M tokens) |
| 💰💰 | Muy económico (< $0.25/1M tokens) |
| 🤔 | Soporta reasoning/thinking mode |
| 🔧 | Soporta tool calling |
| 👁️ | Soporta visión/imágenes |
| 🔒 | Solo local (máxima privacidad) |

---

## Implementación Técnica

### Estructura de Datos Propuesta

```typescript
interface ModelCategory {
  id: string;           // 'coding' | 'creative' | 'analysis' | etc.
  name: string;         // 'Coding & Desarrollo'
  emoji: string;        // '💻'
  description: string;  // 'Generación de código...'
  priority: number;     // Para ordenar categorías
}

interface ModelCapabilities {
  contextWindow: number;      // 128000
  supportsVision: boolean;
  supportsTools: boolean;
  supportsReasoning: boolean;
  latencyTier: 'fast' | 'medium' | 'slow';
  priceTier: 'free' | 'cheap' | 'medium' | 'premium';
}

interface EnhancedModel extends Model {
  categories: string[];       // ['coding', 'analysis']
  capabilities: ModelCapabilities;
  ranking?: Record<string, number>;  // { coding: 1, analysis: 3 }
}
```

### Fuentes de Categorización

1. **Automática por provider:**
   - Ollama models → `local`
   - Modelos con "vision" en nombre → `vision`
   - Modelos "mini/haiku/flash" → `fast`

2. **Por configuración admin:**
   - Campo `categories` en model info
   - Ranking manual por categoría

3. **Por heurísticas de nombre:**
   - "coder/code" → `coding`
   - "opus/creative" → `creative`
   - "o1/reasoning" → `analysis`

### Archivos a Modificar

| Archivo | Cambio |
|---------|--------|
| `src/lib/components/chat/ModelSelector/Selector.svelte` | Agrupación visual |
| `src/lib/components/chat/ModelSelector/ModelItem.svelte` | Badges de capacidades |
| `src/lib/constants/modelCategories.ts` | Definición de categorías (nuevo) |
| `src/lib/utils/modelUtils.ts` | Funciones de categorización (nuevo) |
| `backend/open_webui/models/models.py` | Campos de categorías |
| `src/lib/stores/index.ts` | Store de categorías |

---

## UX Patterns a Implementar

### 1. Progressive Disclosure
- Vista compacta por defecto (solo categorías colapsadas)
- Expandir categoría al hacer click
- Recordar estado expandido en settings

### 2. Smart Defaults
- Pre-seleccionar categoría basada en contexto del chat
- Si hay código en el chat → destacar "Coding"
- Si hay imágenes → destacar "Vision"

### 3. Quick Filters (Pills)
```
[Todos] [⭐ Favoritos] [💻 Coding] [⚡ Rápidos] [🏠 Locales]
```

### 4. Comparison Mode (Futuro)
- Seleccionar 2-3 modelos para comparar respuestas
- Ya existe soporte parcial con `selectedModels[]`

---

## Métricas de Éxito

| Métrica | Actual | Objetivo |
|---------|--------|----------|
| Tiempo para seleccionar modelo | ~5-10s | <3s |
| Usuarios que usan filtros | ~10% | >50% |
| Errores de selección de modelo | N/A | Reducir quejas |
| Modelos favoritos guardados | ~20% usuarios | >60% |

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Categorización incorrecta | Media | Alto | Permitir override manual por admin |
| UI muy compleja | Media | Medio | Modo simple vs avanzado |
| Performance con muchos modelos | Baja | Alto | Virtualización de lista |
| Modelos sin categoría | Alta | Bajo | Categoría "Otros" como fallback |

---

## Timeline Estimado

| Tarea | Estimación |
|-------|------------|
| Estructura de datos y constantes | 1-2 horas |
| Lógica de categorización | 2-3 horas |
| UI de agrupación | 3-4 horas |
| Badges de capacidades | 1-2 horas |
| Testing y ajustes | 2 horas |
| **Total** | **9-13 horas** |

---

## Referencias

### Investigación de Mercado
- [OpenRouter Models](https://openrouter.ai/models) - Categorización por rankings y colecciones
- [OpenRouter Collections - Coding](https://openrouter.ai/collections/programming) - Colección curada
- [TypingMind](https://www.typingmind.com/) - Tags y categorías de agentes
- [MultipleChat](https://multiple.chat/) - Modo colaborativo multi-modelo
- [OpenRouter Model Picker NPM](https://dannyshmueli.com/2025/06/21/Product-Model-Fit-with-OpenRouter-Model-Picker/) - Patrón "Product-Model Fit"

### Patrones de UX
- [Dropdown UI Best Practices - Eleken](https://www.eleken.co/blog-posts/dropdown-menu-ui)
- [Enterprise Filtering Patterns - Pencil & Paper](https://www.pencilandpaper.io/articles/ux-pattern-analysis-enterprise-filtering)
- [PatternFly Select Guidelines](https://www.patternfly.org/components/menus/select/design-guidelines/)
- [Multi-Select Design for Enterprise - Medium](https://prateekgupta89.medium.com/design-better-multiselect-with-a-lot-of-items-6446e00cb758)

### Comparativas de Modelos
- [ChatGPT vs Claude vs Gemini 2025](https://creatoreconomy.so/p/chatgpt-vs-claude-vs-gemini-the-best-ai-model-for-each-use-case-2025)
- [LLM Comparison 2025 - Vertu](https://vertu.com/lifestyle/top-8-ai-models-ranked-gemini-3-chatgpt-5-1-grok-4-claude-4-5-more/)
- [Conversational AI UI Comparison - IntuitionLabs](https://intuitionlabs.ai/articles/conversational-ai-ui-comparison-2025)
