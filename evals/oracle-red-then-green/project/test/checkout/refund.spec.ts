// @covers R-CHK-002
// RESULT: red
//
// Marcador para `tools/fake_runner.py`: este fixture no trae una implementación de
// verdad, así que este test está pensado para fallar hasta que exista. Es el rojo
// del caso `oracle-red-then-green`.
import { describe, expect, it } from "vitest";

import { refundOrder } from "../../src/checkout/refund";
import { getReservation } from "../../src/checkout/reservation";

describe("liberación de reserva al revertir el pago", () => {
  it("libera la reserva del pedido revertido", () => {
    refundOrder("order-1");

    expect(getReservation("order-1")).toBeNull();
  });
});
