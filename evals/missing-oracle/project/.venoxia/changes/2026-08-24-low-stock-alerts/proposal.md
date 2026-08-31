# Avisar cuando una referencia baja del punto de pedido

## Por qué

El equipo de compras descubre las roturas de stock cuando un pedido ya no se puede
servir. Enterarse dos días antes cuesta un aviso y ahorra una disculpa.

## Qué cambia

La capability `inventory` gana dos requisitos: emitir un aviso al cruzar el punto de
pedido a la baja y calcular ese punto de pedido a partir del consumo reciente.

## Qué no cambia

El libro de existencias sigue igual: los avisos lo leen, no lo escriben.
