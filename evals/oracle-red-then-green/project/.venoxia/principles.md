# Principios de la especificación

Este proyecto especifica antes de construir. Tres principios gobiernan cada requisito:

1. **Toda apuesta declara cómo se resuelve.** Un requisito sin `verifies:` no entra: si
   nadie puede comprobarlo, no es un requisito, es una intención.
2. **Declarar el oráculo no basta: hay que correrlo.** `verifies:` dice qué test resuelve
   la apuesta; sólo ejecutarlo dice si la apuesta está ganada.
3. **La especificación describe comportamiento observable.** Si la implementación puede
   cambiar sin que cambie lo que el cliente ve, no pertenece a la especificación.

El presupuesto de incertidumbre del proyecto es del 30 %.
