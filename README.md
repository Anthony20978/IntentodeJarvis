# JARVIS FUNCIONAL

## Propósito

JARVIS es un proyecto de asistente personal desarrollado principalmente en Python. Su objetivo es construir progresivamente una inteligencia artificial propia, capaz de comprender instrucciones, analizar información, aprender y ejecutar tareas mediante sus capacidades internas.

Uno de los objetivos del proyecto es permitir que el usuario pueda crear, entrenar, administrar y ejecutar redes neuronales sencillas mediante instrucciones de diálogo.

## Versión

`v0.3.0`

## Estado del proyecto

JARVIS se encuentra actualmente en la **Fase 3: Cerebro e inteligencia**.

El sistema cuenta con un núcleo inicial, memoria persistente mediante SQLite y procesamiento básico de comandos. Actualmente dispone de tres comandos principales para interactuar con sus funciones iniciales.

El proyecto incluye una arquitectura modular para el desarrollo de su inteligencia, así como componentes propios para el procesamiento del lenguaje, la comprensión de instrucciones, el razonamiento básico y las redes neuronales.

El motor neuronal implementa una red multicapa básica con inferencia y entrenamiento. Sin embargo, estos componentes todavía no constituyen una inteligencia artificial conversacional completa.

La estructura de almacenamiento permite mantener los datos independientes de la ubicación del proyecto. Se contempla compatibilidad con Windows, Linux y macOS.

## Memoria persistente

La memoria inicial utiliza SQLite para almacenar información mediante una tabla con la siguiente estructura:

| Campo | Tipo | Uso |
|---|---|---|
| ID | INTEGER AUTOINCREMENT | Identificador único y orden de los registros. |
| Key | TEXT UNIQUE | Clave utilizada para identificar un dato. |
| Value | TEXT | Información almacenada como texto. |

Esta estructura constituye una implementación inicial. Podrá ampliarse conforme evolucionen las necesidades de memoria de JARVIS.

## Estructuras de comunicación

Se utilizan `dataclasses` de Python para establecer formatos estandarizados de comunicación entre los componentes.

### `InputData` — Entrada

- `text`: instrucción recibida (`str`).
- `timestamp`: momento de recepción (`datetime`).
- `source`: origen de la instrucción (`str`).

### `AnalysisResult` — Análisis

- `intent`: intención identificada (`str`).
- `entities`: elementos relevantes extraídos (`dict`).
- `confidence`: nivel de confianza estimado (`float`).
- `understood`: indica si la instrucción fue comprendida (`bool`).

### `ActionPlan` — Plan de acción

- `actions`: acciones propuestas (`list`).
- `parameters`: parámetros necesarios para las acciones (`dict`).
- `requires_confirmation`: indica si se necesita autorización (`bool`).
- `reason`: justificación del plan (`str`).

### `ExecutionResult` — Resultado de ejecución

- `success`: indica si la ejecución fue exitosa (`bool`).
- `output`: resultado obtenido (`str`).
- `error`: información del error, si existe (`str | None`).

Estas estructuras permiten mantener una comunicación consistente, facilitar las pruebas y reducir las dependencias entre componentes.

## Organización de archivos

<p align="center">
  <img src="estructura.svg" alt="Árbol de archivos de JARVIS" width="100%">
</p>

> El proyecto continúa en una fase temprana de desarrollo. Su estructura y funcionalidades evolucionarán conforme avance su construcción.

## Hoja de ruta

### Fase 1 — Núcleo inicial
<sub>Completada</sub>

- Estructura inicial del proyecto.
- Detección del sistema y hardware.
- Memoria persistente con SQLite.
- Procesamiento básico de comandos.
- Pruebas automatizadas.

### Fase 2 — Portabilidad y configuración
<sub>Completada</sub>

- Almacenamiento adecuado para cada sistema operativo.
- Configuración centralizada.
- Rutas independientes de la ubicación del proyecto.
- Preparación para Windows y Linux.

### Fase 3 — Cerebro e inteligencia
<sub>En desarrollo</sub>

- Desarrollo de una inteligencia artificial propia.
- Selección de capacidades según el hardware disponible.
- Comprensión de instrucciones y razonamiento.
- Funcionamiento local y sin conexión siempre que sea posible.

Esta fase se divide en subfases para desarrollar y evaluar cada componente de manera independiente.

#### 3.1. Arquitectura de inteligencia
<sub>Completada</sub>

- Diseñar la estructura interna del cerebro de JARVIS.
- Definir los componentes y su comunicación.
- Establecer una arquitectura modular, independiente y ampliable.

#### 3.2. Procesamiento del lenguaje

- Implementar un sistema propio de procesamiento del lenguaje.
- Desarrollar tokenización y normalización de texto.
- Identificar palabras, estructuras y elementos relevantes de las instrucciones.

#### 3.3. Comprensión de intenciones

- Reconocer las intenciones del usuario.
- Identificar entidades, parámetros y contexto.
- Relacionar instrucciones con las capacidades de JARVIS.

#### 3.4. Motor neuronal propio

- Desarrollar las bases de una red neuronal desde cero.
- Implementar operaciones, capas y funciones de activación.
- Crear un sistema propio de inferencia.

#### 3.5. Entrenamiento y aprendizaje

- Implementar algoritmos propios de entrenamiento.
- Crear y entrenar modelos pequeños especializados.
- Evaluar resultados y mejorar los modelos mediante entrenamiento controlado.

#### 3.6. Memoria contextual

- Incorporar contexto a las conversaciones.
- Relacionar información actual con recuerdos anteriores.
- Mejorar la recuperación y utilización de información almacenada.

#### 3.7. Razonamiento y planificación

- Desarrollar mecanismos para analizar instrucciones.
- Dividir tareas complejas en pasos.
- Evaluar alternativas y seleccionar acciones.
- Gestionar errores y resultados inesperados.

#### 3.8. Integración con las capacidades de JARVIS

- Conectar la inteligencia con los módulos internos.
- Traducir decisiones en acciones.
- Validar resultados y gestionar respuestas.

#### 3.9. Integración opcional de modelos externos

- Permitir conexiones con modelos de inteligencia artificial externos.
- Crear una interfaz independiente del proveedor o modelo.
- Mantener el funcionamiento de las capacidades propias sin conexiones externas.
- Permitir activar o desactivar estas integraciones.

#### 3.10. Optimización y evaluación

- Optimizar el rendimiento y consumo de recursos.
- Evaluar precisión, velocidad y calidad de respuestas.
- Mejorar la compatibilidad con diferentes dispositivos.
- Realizar pruebas de funcionamiento sin conexión.

#### 3.11. Consolidación del cerebro

- Integrar todos los componentes de inteligencia.
- Verificar su funcionamiento conjunto.
- Documentar la arquitectura y los mecanismos de aprendizaje.
- Preparar el sistema para las siguientes fases del proyecto.

### Fase 4 — Sistema de voz

- Reconocimiento de voz.
- Síntesis de voz.
- Activación por voz, si el hardware lo permite.
- Conversación hablada.

### Fase 5 — Memoria avanzada

- Memoria a corto y largo plazo.
- Contexto de conversaciones.
- Organización y recuperación inteligente de información.
- Control del usuario sobre sus recuerdos.

### Fase 6 — Herramientas y automatización

- Ejecutar tareas locales autorizadas.
- Administrar archivos y carpetas.
- Automatizar tareas repetitivas.
- Sistema de permisos y confirmaciones.

### Fase 7 — Internet y conocimiento

- Acceso opcional a Internet.
- Búsqueda de información.
- Consulta de fuentes y verificación.
- Funcionamiento sin Internet cuando no sea necesario.

### Fase 8 — Interfaz y experiencia

- Interfaz gráfica.
- Panel de configuración.
- Historial de conversaciones.
- Personalización de voz y comportamiento.

### Fase 9 — Adaptabilidad y multiplataforma

- Detección de recursos disponibles.
- Ajuste automático de capacidades.
- Preparación para dispositivos de menor potencia.
- Evaluación de compatibilidad con Android.

### Fase 10 — Seguridad, optimización y distribución

- Protección de datos y permisos.
- Optimización de rendimiento.
- Pruebas de estabilidad.
- Instaladores y distribución gratuita.
- Documentación final.

## Principios del proyecto

- **Gratuito:** sin servicios de pago obligatorios ni suscripciones necesarias.
- **Local primero:** las funciones esenciales deben trabajar sin Internet siempre que sea posible.
- **Python como lenguaje principal:** dependencias externas únicamente cuando aporten un beneficio justificado.
- **Adaptable:** ajustar las capacidades al hardware disponible.
- **Portable:** evitar depender de una computadora o sistema operativo específico.
- **Privacidad:** los datos personales permanecen bajo el control del usuario.
- **Modular:** cada capacidad debe poder mantenerse, sustituirse o desactivarse independientemente.
- **Código limpio:** priorizar soluciones sencillas, eficientes y fáciles de mantener.

## Diseño de inteligencia artificial

### Objetivo

Desarrollar una inteligencia artificial propia desde cero, capaz de comprender instrucciones, analizar información, aprender y ejecutar tareas mediante las capacidades de JARVIS.

El sistema será independiente de modelos y servicios externos, aunque permitirá utilizarlos opcionalmente para ampliar sus capacidades.

### 1. Procesamiento y comprensión

- Procesamiento y normalización del lenguaje.
- Tokenización y análisis de texto.
- Identificación de intenciones del usuario.
- Reconocimiento de entidades, parámetros y contexto.
- Interpretación progresiva de instrucciones ambiguas o incompletas.

### 2. Inteligencia y razonamiento

- Desarrollo de mecanismos propios de razonamiento.
- Análisis de información y evaluación de alternativas.
- Planificación y división de tareas complejas.
- Selección de acciones según la intención y el contexto.
- Gestión de errores y situaciones inesperadas.

### 3. Redes neuronales propias

- Desarrollo de redes neuronales desde cero.
- Implementación de operaciones, capas y funciones de activación.
- Creación de modelos pequeños especializados.
- Implementación de mecanismos propios de inferencia.
- Optimización para diferentes capacidades de hardware.

### 4. Aprendizaje y entrenamiento

- Desarrollo de algoritmos propios de entrenamiento.
- Creación y preparación de conjuntos de datos.
- Entrenamiento de modelos especializados.
- Evaluación de precisión y rendimiento.
- Mejora de modelos mediante entrenamiento controlado.

### 5. Memoria y contexto

- Utilización de información almacenada para comprender instrucciones.
- Gestión del contexto de las conversaciones.
- Relación entre información actual y recuerdos anteriores.
- Recuperación de información relevante.
- Adaptación de las respuestas según el contexto disponible.

### 6. Ejecución de acciones

- Transformación de instrucciones en acciones.
- Validación de las acciones antes de ejecutarlas.
- Comunicación con las capacidades internas de JARVIS.
- Verificación de resultados.
- Gestión de permisos y confirmaciones cuando sean necesarias.

### 7. Integraciones externas opcionales

- Posibilidad de utilizar modelos de IA existentes.
- Compatibilidad con diferentes modelos y proveedores.
- Integración independiente del motor principal.
- Activación y desactivación de conexiones externas.
- Funcionamiento de las capacidades propias sin depender de estas integraciones.

### 8. Independencia y optimización

- Funcionamiento local y sin conexión a Internet.
- Ausencia de dependencias obligatorias de motores externos.
- Optimización del consumo de memoria y procesamiento.
- Adaptación a los recursos disponibles.
- Evaluación continua de precisión, velocidad y estabilidad.

### Principios de desarrollo

La inteligencia de JARVIS se desarrollará progresivamente, priorizando la comprensión de sus mecanismos internos y la creación de tecnología propia.

Se evitará depender de soluciones externas cuando sea posible, sin descartar su utilización opcional cuando aporten mejoras significativas.

El aprendizaje de los modelos será controlado y evaluado. La memoria de JARVIS y el entrenamiento de sus redes neuronales serán mecanismos independientes.

## Pruebas

El proyecto utiliza la biblioteca `unittest` de Python para realizar pruebas automatizadas de sus componentes.

Para ejecutar todas las pruebas desde la raíz del proyecto, utiliza el siguiente comando en PowerShell:

```powershell
python -m unittest discover -s tests -v
```

### Listado de pruebas

#### `test_core.py` — 11 pruebas

| Nombre de la prueba | Qué verifica |
|---|---|
| `test_save_and_get_memory` | Guardar y recuperar información de la memoria. |
| `test_update_memory` | Actualizar información previamente almacenada. |
| `test_missing_memory` | Manejar la búsqueda de una clave inexistente. |
| `test_delete_memory` | Eliminar información de la memoria. |
| `test_empty_memory_values` | Rechazar valores vacíos al guardar información. |
| `test_remember_command` | Procesar el comando para recordar. |
| `test_retrieve_command` | Procesar el comando para recuperar información. |
| `test_empty_command` | Manejar instrucciones vacías. |
| `test_help_command` | Mostrar la ayuda de JARVIS. |
| `test_system_detection` | Detectar el sistema operativo. |
| `test_capabilities` | Verificar las capacidades detectadas del sistema. |

#### `test_neural.py` — 8 pruebas

| Nombre de la prueba | Qué verifica |
|---|---|
| `test_network_creation` | Creación correcta de una red neuronal. |
| `test_prediction_output_size` | Cantidad correcta de valores de salida. |
| `test_default_sigmoid_range` | Que las salidas de la función sigmoid estén entre 0 y 1. |
| `test_reproducible_with_seed` | Que una misma semilla produzca resultados reproducibles. |
| `test_invalid_layer_sizes` | Rechazo de arquitecturas con dimensiones inválidas. |
| `test_invalid_activation` | Rechazo de funciones de activación no admitidas. |
| `test_invalid_input_size` | Rechazo de entradas con dimensiones incorrectas. |
| `test_invalid_input_values` | Rechazo de entradas no numéricas o no finitas. |

#### `test_executor.py` — 8 pruebas

| Nombre de la prueba | Qué verifica |
|---|---|
| `test_execute_confirmed_action` | Ejecución de una acción después de recibir confirmación. |
| `test_confirmation_required` | Bloqueo de acciones que no han sido confirmadas. |
| `test_execute_with_parameters` | Entrega correcta de parámetros a la acción ejecutada. |
| `test_unknown_action` | Rechazo de acciones que no están registradas. |
| `test_empty_plan` | Manejo de planes sin acciones. |
| `test_execution_error` | Manejo de errores durante la ejecución. |
| `test_invalid_plan` | Rechazo de planes que no sean objetos `ActionPlan`. |
| `test_invalid_confirmation` | Rechazo de valores de confirmación incorrectos. |

#### `test_reasoning.py` — 5 pruebas

| Nombre de la prueba | Qué verifica |
|---|---|
| `test_help_plan` | Generación de un plan para mostrar ayuda. |
| `test_remember_plan` | Generación de un plan para guardar información. |
| `test_unknown_plan` | Manejo de intenciones desconocidas. |
| `test_default_confirmation` | Verifica que las acciones requieran confirmación por defecto. |
| `test_invalid_input` | Rechazo de entradas que no sean objetos `AnalysisResult`. |

#### `test_config.py` — 5 pruebas

| Nombre de la prueba | Qué verifica |
|---|---|
| `test_windows_data_directory` | Obtener el directorio de datos en Windows. |
| `test_windows_fallback_directory` | Utilizar una ruta alternativa en Windows cuando sea necesario. |
| `test_macos_data_directory` | Obtener el directorio de datos en macOS. |
| `test_linux_data_directory` | Obtener el directorio de datos en Linux. |
| `test_linux_fallback_directory` | Utilizar una ruta alternativa en Linux cuando sea necesario. |

#### `test_memory_migration.py` — 3 pruebas

| Nombre de la prueba | Qué verifica |
|---|---|
| `test_migration_preserves_memory` | Comprobar que los datos se conservan durante la migración. |
| `test_legacy_database_is_preserved` | Verificar que la base de datos anterior no se elimina. |
| `test_existing_database_is_not_overwritten` | Evitar sobrescribir una base de datos existente. |

#### `test_language.py` — 4 pruebas

| Nombre de la prueba | Qué verifica |
|---|---|
| `test_normalize_text` | Normalizar espacios y convertir el texto a minúsculas. |
| `test_tokenize` | Dividir el texto en palabras y signos de puntuación. |
| `test_prepare_text` | Preparar correctamente el texto normalizado. |
| `test_invalid_input` | Rechazar entradas que no sean cadenas de texto. |

#### `test_understanding.py` — 7 pruebas

| Nombre de la prueba | Qué verifica |
|---|---|
| `test_help_intent` | Reconocer la intención de solicitar ayuda. |
| `test_exit_intent` | Reconocer la intención de salir. |
| `test_remember_intent` | Reconocer el comando para recordar y extraer clave y valor. |
| `test_recall_intent` | Reconocer el comando para recuperar información y extraer la clave. |
| `test_unknown_intent` | Identificar intenciones desconocidas. |
| `test_empty_input` | Manejar entradas vacías. |
| `test_invalid_input` | Rechazar entradas de tipos incorrectos. |

#### `test_learning.py` — 8 pruebas

| Nombre de la prueba | Qué verifica |
|---|---|
| `test_training_reduces_loss` | Que el entrenamiento reduzca el error de la red. |
| `test_training_returns_history` | Que se registre el error de cada época. |
| `test_invalid_network` | Rechazo de objetos que no sean redes neuronales. |
| `test_invalid_epochs` | Rechazo de cantidades de épocas inválidas. |
| `test_invalid_learning_rate` | Rechazo de tasas de aprendizaje inválidas. |
| `test_mismatched_dataset_size` | Rechazo de conjuntos con distinta cantidad de entradas y objetivos. |
| `test_invalid_dimensions` | Rechazo de entradas y objetivos con dimensiones incorrectas. |
| `test_non_finite_values` | Rechazo de datos con valores infinitos. |

#### `test_context.py` — 6 pruebas

| Nombre de la prueba | Qué verifica |
|---|---|
| `test_add_input` | Añadir entradas al historial de conversación. |
| `test_get_recent` | Recuperar las entradas más recientes. |
| `test_max_history` | Respetar el límite máximo del historial. |
| `test_clear` | Limpiar el historial de conversación. |
| `test_invalid_input` | Rechazar entradas que no sean objetos `InputData`. |
| `test_invalid_history_limit` | Rechazar límites de historial inválidos. |

**Total: 65 pruebas automatizadas documentadas.**

Las pruebas permiten verificar el funcionamiento de los componentes, detectar errores y comprobar que las modificaciones no afecten funcionalidades existentes. Se incorporarán nuevas pruebas conforme avance el desarrollo.

> La cantidad indicada corresponde a las pruebas documentadas; su estado de ejecución debe verificarse mediante el comando anterior.

---

Proyecto iniciado con fines principalmente educativos, de investigación y desarrollo.