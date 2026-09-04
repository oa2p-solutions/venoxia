# Venoxia · Principios

## Convenciones técnicas

- Python 3 stdlib en scripts, tests y herramientas de desarrollo. Nada de pip
  ni de entornos virtuales; probado con 3.14.
- Tests con `unittest` de la biblioteca estándar, ejecutados con
  `python3 -m unittest discover -s tests -q`. `pytest` puede correr la misma
  suite, pero nunca es un requisito.
- Tags, claves e identificadores en inglés; prosa, valores y mensajes de
  error en español. Aplica a código, documentación, skills, plantillas y
  mensajes.
- Códigos de salida uniformes en `validate.py`, `charter_lint.py` y
  `diff_readings.py`: `0` cumple, `1` no cumple, `2` error de uso.
- Flags comunes a los tres scripts anteriores: `--json`, `--no-color` y
  `--strict`. El esquema JSON que producen es versión 1 y estable: se le
  pueden añadir claves, nunca renombrarlas ni quitarlas.

## Principios de dominio

- Ninguna regla de `validate.py`, `charter_lint.py` ni `diff_readings.py`
  consulta a un modelo: toda la aritmética de un veredicto está en código, y
  dos ejecuciones sobre el mismo árbol producen el mismo resultado.
- El fail-open es exclusivo del guardián. Un validador que no puede decidir
  se calla con un `Finding` y sigue con la regla siguiente; nunca convierte
  su propio fallo en un veredicto de aprobado.
- Un falso positivo pesa más que un falso negativo: entre avisar de más sobre
  una spec que en realidad cumple y dejar pasar una que no cumple, el
  sistema entero está diseñado para preferir el primer error.
- Las cifras nunca se diluyen en la comparación de lecturas: dos números
  distintos —«21 días» contra «14 días»— son una divergencia aunque
  compartan casi todas las demás palabras.
