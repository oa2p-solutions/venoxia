# cotizador

Herramienta de línea de comandos que usa el equipo de compras de una cadena de
restaurantes para elegir proveedor. Cada semana llegan por correo entre tres y
seis presupuestos en Excel, uno por proveedor, con los mismos productos y precios
distintos. `cotizador` los importa, los pone en una tabla común y dice, línea a
línea, qué proveedor sale más barato.

## Uso

```bash
cotizador importar presupuestos/*.xlsx      # lee los Excel y los deja en cotizaciones.json
cotizador comparar cotizaciones.json        # imprime el ganador por producto
cotizador exportar cotizaciones.json pedido.csv
```

## Estado

Funciona con los formatos de los cuatro proveedores actuales. Lo que aún se hace a
mano: mandar el pedido a cada proveedor (se copia del CSV a un correo) y comprobar
al recibir la mercancía que el precio facturado es el del presupuesto.

## Desarrollo

```bash
pip install -e ".[dev]"
pytest
```
