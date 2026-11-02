# JARVIS FUNCIONAL
## Proposito:
En este proyecto intentaremos hacer un jarvis funcional.
## Versión
v0.2.0
## Estado
En este momento, Jarvis esta en fase 1. Jarvis solo poseé un nucleo que administra tres comandos simples, y memoria persistente con SQLite 3, en una tabla. Jarvis es capaz de ejecutarse en varios sistemas operativos como Windows, Linux y MACos. Ya que poseé un sistema de directorios independiente de la carpeta en la que se encuentre el proyecto.
## Tabla de memoria de Jarvis
|Campo|Tipo|Uso|
|:---:|:---:|:---:|
|ID|Int Autoincrement|Regula el orden de la tabla|
|Key|Text Unique|Es una llave que guarda un dato|
|Value|Text|El dato, en forma de texto a guardar. se busca con la llave|

> La tabla es una forma provicional de guardado de datos. Con el desarrollo del proyecto se puede expandir y mejorar en un futuro.
## Organización de archivos
<div class="tree">
  <ul>JARVIS/<ul>
        <li>src/<ul>
            <li>jarvis/<ul>
            <li>__init__.py</li>
            <li>main.py</li>
            <li>config.py</li>
            <li>brain.py</li>
            <li>memory.py</li>
            <li>capabilities.py</li>
            <li>platform.py</li></ul></li></ul></li>
        <li>tests/<ul>
        <li>__init__.py</li>
        <li>test_core.py</li>
        <li>test_memory_migration.py</li>
        <li>test_config.py</li></ul></li>
        <li>README.md</li>
        <li>.gitignore</li>
        <li>pyproject.toml</li></ul></ul>
</div>

## Descipción de los directorios
- carpeta **src/**:
    contiene el codigo fuente del proyecto.
  - subcarpeta **jarvis/**:
      el nucleo de jarvis y sus capacidades.
    - archivo **config.py**:
        gestiona parametros generales, rutas y configuraciones del asistente.
    - archivo **main.py**: 
      inicia y coordina a Jarvis.
    - archivo **brain.py**:
      procesa instrucciones.
    - archivo **memory.py**:
      guarda y recupera información local.
    - archivo **capabilities.py**:
      administra las funciones que se pueden ejecutar.
    - archivo **platform.py**:
      adapta las funciones a otros entornos.
    - archivo **__init__.py**:
      permite organizar los modulos como paquetes de python.
- carpeta **tests/**:
    contiene pruebas que verifican el funcionamiento de jarvis.
    - archivo **__init__.py**:
      permite organizar los modulos como paquetes de python.
    - archivo **test_core.py**:
      ayuda a comprobar el funcionamiento del nucleo.
    - archivo **test_config.py**:
      comprueba el funcionamiento de los directorios independientemente de su posición.
    - archivo **test_memory_migration.py**:
    comprueba el funcionamiento de la base de datos, independientemente de la carpeta del proyecto.
  
- archivo **README.md**:
contiene la principal informacion para el usuario.
- archivo **.gitignore**:
se asegura de que GitHub no guarde archivos innecesarios.
- archivo **pyprojecy.py**:
contiene información acerca de la configuración del proyecto.

>El proyecto continua en una fase temprana de desarrollo. Su estructura y funcionalidades cambiarán conforme a su construcción.

## Plan de creación de Jarvis

## Hoja de ruta

- **Fase 1 — Núcleo inicial** <sub>Completada</sub>
  - Estructura del proyecto.
  - Detección del sistema y hardware.
  - Memoria persistente con SQLite.
  - Procesamiento básico de comandos.
  - Pruebas automatizadas.

- **Fase 2 — Portabilidad y configuración** <sub>Completada</sub> 
  - Almacenamiento adecuado para cada sistema operativo.
  - Configuración centralizada.
  - Rutas independientes de la ubicación del proyecto.
  - Preparación para Windows y Linux.

- **Fase 3 — Cerebro e inteligencia**
  - Integración de modelos de IA locales.
  - Selección automática según el hardware.
  - Sistema de razonamiento y comprensión de instrucciones.
  - Funcionamiento básico sin conexión.

  Por Simplicidad, esta fase estará dividida en varias más, dependiendo de la potencia esperada en la IA.

- **3.1. Arquitectura de inteligencia**
  - Diseñar la estructura interna del cerebro de JARVIS.
  - Definir los componentes y su comunicación.
  - Establecer una arquitectura modular, independiente y ampliable.

- **3.2. Procesamiento del lenguaje**
  - Implementar un sistema propio de procesamiento del lenguaje.
  - Desarrollar tokenización y normalización de texto.
  - Identificar palabras, estructuras y elementos relevantes de las instrucciones.

- **3.3. Comprensión de intenciones**
  - Reconocer las intenciones del usuario.
  - Identificar entidades, parámetros y contexto.
  - Relacionar instrucciones con las capacidades de JARVIS.

- **3.4. Motor neuronal propio**
  - Desarrollar las bases de una red neuronal desde cero.
  - Implementar operaciones, capas y funciones de activación.
  - Crear un sistema propio de inferencia.

- **3.5. Entrenamiento y aprendizaje**
  - Implementar algoritmos propios de entrenamiento.
  - Crear y entrenar modelos pequeños especializados.
  - Evaluar resultados y mejorar los modelos mediante entrenamiento controlado.

- **3.6. Memoria contextual**
  - Incorporar contexto a las conversaciones.
  - Relacionar información actual con recuerdos anteriores.
  - Mejorar la recuperación y utilización de información almacenada.

- **3.7. Razonamiento y planificación**
  - Desarrollar mecanismos para analizar instrucciones.
  - Dividir tareas complejas en pasos.
  - Evaluar alternativas y seleccionar acciones.
  - Gestionar errores y resultados inesperados.

- **3.8. Integración con las capacidades de JARVIS**
  - Conectar la inteligencia con los módulos internos.
  - Traducir decisiones en acciones.
  - Validar resultados y gestionar respuestas.

- **3.9. Integración opcional de modelos externos**
  - Permitir conexiones con modelos de inteligencia artificial externos.
  - Crear una interfaz independiente del proveedor o modelo.
  - Mantener el funcionamiento completo de JARVIS sin conexiones externas.
  - Permitir activar o desactivar estas integraciones.

- **3.10. Optimización y evaluación**
  - Optimizar el rendimiento y consumo de recursos.
  - Evaluar precisión, velocidad y calidad de respuestas.
  - Mejorar la compatibilidad con diferentes dispositivos.
  - Realizar pruebas de funcionamiento offline.

- **3.11. Consolidación del cerebro**
  - Integrar todos los componentes de inteligencia.
  - Verificar su funcionamiento conjunto.
  - Documentar la arquitectura y los mecanismos de aprendizaje.
  - Preparar el sistema para las siguientes fases del proyecto.

- **Fase 4 — Sistema de voz**
  - Reconocimiento de voz.
  - Síntesis de voz.
  - Activación por voz, si el hardware lo permite.
  - Conversación hablada.

- **Fase 5 — Memoria avanzada**
  - Memoria a corto y largo plazo.
  - Contexto de conversaciones.
  - Organización y recuperación inteligente de información.
  - Control del usuario sobre sus recuerdos.

- **Fase 6 — Herramientas y automatización**
  - Ejecutar tareas locales autorizadas.
  - Administrar archivos y carpetas.
  - Automatizar tareas repetitivas.
  - Sistema de permisos y confirmaciones.

- **Fase 7 — Internet y conocimiento**
  - Acceso opcional a Internet.
  - Búsqueda de información.
  - Consulta de fuentes y verificación.
  - Capacidad de funcionar sin Internet cuando no sea necesario.

- **Fase 8 — Interfaz y experiencia**
  - Interfaz gráfica.
  - Panel de configuración.
  - Historial de conversaciones.
  - Personalización de voz y comportamiento.

- **Fase 9 — Adaptabilidad y multiplataforma**
  - Detección de recursos disponibles.
  - Ajuste automático de capacidades.
  - Preparación para dispositivos de menor potencia.
  - Evaluación de compatibilidad con Android.

- **Fase 10 — Seguridad, optimización y distribución**
  - Protección de datos y permisos.
  - Optimización de rendimiento.
  - Pruebas de estabilidad.
  - Instaladores y distribución gratuita.
  - Documentación final.

## Principios del proyecto

- **Gratuito:** sin servicios de pago obligatorios.
- **Local primero:** las funciones esenciales deben trabajar sin Internet.
- **Python como lenguaje principal:** dependencias externas solo cuando aporten valor.
- **Adaptable:** ajustar las capacidades al hardware disponible.
- **Portable:** evitar depender de una computadora o sistema operativo específico.
- **Privacidad:** los datos personales permanecen bajo control del usuario.
- **Modular:** cada capacidad debe poder mantenerse, sustituirse o desactivarse independientemente.

> Este proyecto se inició con fines mayormente de aprendizaje.