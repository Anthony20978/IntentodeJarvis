# JARVIS FUNCIONAL
## Proposito:
En este proyecto intentaremos hacer un jarvis funcional.
## Versión
v0.1.1
## Estado
En este momento, Jarvis esta en fase 1. Jarvis solo poseé un nucleo que administra tres comandos simples, y memoria persistente con SQLite 3, en una tabla.
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
        <li>test_core.py</li></ul></li>
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
      ayuda a comprobar el funcionamiento del nucleo
  
- archivo **README.md**:
contiene la principal informacion para el usuario.
- archivo **.gitignore**:
se asegura de que GitHub no guarde archivos innecesarios.
- archivo **pyprojecy.py**:
contiene información acerca de la configuración del proyecto.

>El proyecto continua en una fase temprana de desarrollo. Su estructura y funcionalidades cambiarán conforme a su construcción.