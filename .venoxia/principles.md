# Venoxia · Principios

Este proyecto especifica antes de construir. Tres principios gobiernan cada
requisito, y son del plugin, no del proyecto: quien instala Venoxia los acepta
con él.

1. **Toda apuesta declara cómo se resuelve.** Un requisito sin `verifies:` no
   entra: si nadie puede comprobarlo, no es un requisito, es una intención.
2. **La confianza se declara, no se presume.** `confidence:` dice cuánto nos
   fiamos de la apuesta, y una apuesta con poca confianza nace con el hecho
   que la cierra en `revisit:`, nunca con una fecha.
3. **La especificación describe comportamiento observable.** Si la
   implementación puede cambiar sin que cambie lo que el cliente ve, no
   pertenece a la especificación.

El presupuesto de incertidumbre del proyecto es del 30 %: como mucho tres de
cada diez requisitos pueden nacer con `confidence: low`.

Las decisiones técnicas verificables de este repositorio —sólo biblioteca
estándar, ningún script toca la red ni consulta a un modelo, el guardián
importa sólo stdlib, la cobertura por fichero, los códigos de salida `0`/`1`/`2`
de los cinco CLI, el esquema de informe versión 1 que sólo crece— no viven
aquí: son requisitos con oráculo en la capability `technical-contract`
(`.venoxia/capabilities/technical-contract/`, prefijo `R-TEC-`). Lo que aquí
queda es lo que por naturaleza no se verifica con un test: cómo se desempata.

## Principios de dominio

- Ninguna regla de `validate.py`, `charter_lint.py` ni `diff_readings.py`
  consulta a un modelo: toda la aritmética de un veredicto está en código, y
  dos ejecuciones sobre el mismo árbol producen el mismo resultado. Que ningún
  script pueda hacerlo lo vigila `R-TEC-002`; que ninguna regla deba hacerlo
  es este principio.
- El fail-open es exclusivo del guardián. Un validador que no puede decidir
  se calla con un `Finding` y sigue con la regla siguiente; nunca convierte
  su propio fallo en un veredicto de aprobado.
- Un falso positivo pesa más que un falso negativo: entre avisar de más sobre
  una spec que en realidad cumple y dejar pasar una que no cumple, el
  sistema entero está diseñado para preferir el primer error.
- Las cifras nunca se diluyen en la comparación de lecturas: dos números
  distintos —«21 días» contra «14 días»— son una divergencia aunque
  compartan casi todas las demás palabras (`R-DIV-004` lo verifica; este
  principio dice por qué).
- Tags, claves e identificadores en inglés; prosa, valores y mensajes en
  español. Aplica a código, documentación, skills, plantillas y mensajes de
  error. Es una convención de lectura, no un comportamiento: se sostiene por
  revisión.
