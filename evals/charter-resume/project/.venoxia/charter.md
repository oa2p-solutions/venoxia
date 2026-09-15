# Reservas Bistró · Acta del proyecto

## Purpose

Que un restaurante pequeño deje de perder mesas por reservas apuntadas en un
cuaderno que sólo entiende quien lo escribió.

## Users

### owner · Dueño del restaurante
- **hoy:** apunta las reservas en un cuaderno y las repasa cada mañana.
- **con esto:** ve la ocupación de la noche desde el móvil sin llamar a nadie.

### diner · Cliente que reserva
- **hoy:** llama por teléfono y espera a que alguien coja.
- **con esto:** reserva desde el enlace del perfil, a cualquier hora.

## Capabilities

| # | Capability | Qué podrá hacer | Done when | Risk |
|---|---|---|---|---|
| 1 | `booking` | reservar una mesa para una fecha y hora | un cliente reserva y recibe la confirmación con su hora | high |
| 2 | `availability` | ver qué queda libre esta noche | el dueño abre el móvil y ve las mesas libres de hoy | medium |

## Out of scope

- **Pagos y señales.** No se cobra nada en la v1; el riesgo regulatorio no compensa
  hasta que haya reservas de verdad.
- **App nativa.** La web basta para lo que promete el propósito.

## Bets

### B-001 · Nadie anula por WhatsApp

Damos por hecho que un cliente que quiere anular usará el enlace y no el
teléfono del restaurante.

confidence: low
  why:      no lo hemos comprobado con ningún restaurante real
  revisit:  cuando hayamos servido las cincuenta primeras reservas
  fatal:    no

### B-002 · Diez reservas por noche bastan

Damos por hecho que un restaurante de veinte mesas no pasa de diez reservas
por noche, así que la disponibilidad se puede calcular al vuelo.

confidence: medium
  why:      es lo que cuenta el dueño del bistró piloto, sin registro que lo respalde
  revisit:  cuando el bistró piloto lleve un mes completo de reservas registradas
  fatal:    no
