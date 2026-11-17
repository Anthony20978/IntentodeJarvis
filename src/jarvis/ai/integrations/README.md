# Integraciones secundarias

## Calculadora

Fué una integracion con el proposito de probar el funcionamiento de las integraciones. Ya está integrada en Jarvis y utiliza las banderas -x, que toma la expresión a calcular -u que toma la unidad angular que usara la expresión.

## Montaje de una integracion
Se necesitan 4 archivos para hacer una integración:
### __init__.py
Es el archivo que monta la integracion, se deben seguir estos casos para programarlo.

#### Imports

Un init necesitará el import de la funcion que se va a implementar, y de las estructuras de IntegrationDefinition y IntegrationParameter

#### Definir los parametros

Se debe definir cada parametro como un IntegrationParameter

#### Definir las integraciones

Se deben definir las integraciones como un IntegrationDefinition
Se recomienda hacer un duplicado de cada IntegrationDefinition, con la modificacion para lograr que una devuelva el resultado en formato de texto, y una integracion que devuelve el formato directo para Jarvis.
Para esto se diseño la variable visible, que puede manejar cual comando se muestra al usuario, aunque ambos siguen siendo visibles para Jarvis, se planea que en un futuro con IA integrada pueda optar la versión directa. 
#### Definir la lista de Integraciones

Jarvis requiere una lista llamada INTEGRATIONS que debe tener todas las integraciones

### Integration

Este archivo tiene de proposito servir de puente, es donde deben estar las funciones a que se van a integrar, funcionan para organizar los parametros.

Unicamente requiere tener las funciones que se van a integrarse

### Dev

Este archivo opcional puede contener el resto de codigo que requiera el archivo integration para cumplir su función.

### archivos de tests

Siempre que no se encuentren en una carpeta independiente pueden ser detectados por los comandos test_jarvis, y python -m unittest discover -s . -v