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