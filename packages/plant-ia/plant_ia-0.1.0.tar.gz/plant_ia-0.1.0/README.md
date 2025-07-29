# Plant-IA

Librería en español para estructurar prompts con variables dinámicas, ideal para proyectos de inteligencia artificial, asistentes conversacionales o generación de texto.

## Ejemplo de uso

```python
from plant_ia import Plantilla

p = Plantilla("Hola {nombre}, ¿cómo estás?")
print(p.rellenar(nombre="Luis"))  # Hola Luis, ¿cómo estás?
