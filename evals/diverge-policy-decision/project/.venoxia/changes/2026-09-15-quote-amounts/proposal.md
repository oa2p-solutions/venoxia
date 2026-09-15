# 2026-09-15-quote-amounts Proposal

## Why

Los presupuestos llegan en PDF con el importe escrito como cada proveedor quiere:
«1.468.135,00», «1.468.135.00» o «$ 1.500.000.-». El comprador tiene que poder
compararlos sin corregir a mano la notación.

## What Changes

- El importe de un presupuesto en pesos chilenos se registra como entero, sea cual
  sea la notación con la que venga escrito.

## Capabilities

### Modified Capabilities

- `checkout`: la carga de presupuestos acepta las tres notaciones habituales.

## Impact

- Sólo la lectura del importe cambia; la comparación posterior no.
