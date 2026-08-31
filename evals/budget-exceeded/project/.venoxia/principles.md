# Principios de la especificación

Este proyecto especifica antes de construir. Tres principios gobiernan cada requisito:

1. **Toda apuesta declara cómo se resuelve.** Un requisito sin `verifies:` no entra: si
   nadie puede comprobarlo, no es un requisito, es una intención.
2. **La confianza se declara, no se presume.** `confidence:` dice cuánto nos fiamos de la
   apuesta, y una apuesta con poca confianza nace con fecha de caducidad.
3. **La especificación describe comportamiento observable.** Si la implementación puede
   cambiar sin que cambie lo que el cliente ve, no pertenece a la especificación.

El presupuesto de incertidumbre del proyecto es del 30 %: como mucho tres de cada diez
requisitos pueden nacer con `confidence: low`. Pasado ese límite el cambio no se valida:
no es una especificación, es una lista de deseos.
