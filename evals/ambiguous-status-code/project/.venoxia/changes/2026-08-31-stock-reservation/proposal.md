# Reservar el stock al confirmar el pago

## Por qué

Entre la confirmación del pago y su liquidación pasan hasta doce minutos. En ese hueco
dos clientes pueden comprar la misma unidad y uno de los dos recibe una disculpa.

## Qué cambia

La capability `checkout` gana un requisito: reservar el stock de las líneas del pedido
al confirmar el pago, con un TTL de 15 minutos.

## Apuestas

El TTL de 15 minutos sale del percentil 99 del tiempo de liquidación actual. Lo que el
sistema responde cuando falta stock no está decidido: el PR/FAQ solo dice que la petición
«se rechaza».
