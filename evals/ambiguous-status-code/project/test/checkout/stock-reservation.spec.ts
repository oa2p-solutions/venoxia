// @covers R-CHK-010
import { describe, expect, it } from "vitest";

import { confirmPayment } from "../../src/checkout/payment";

describe("reserva de stock al confirmar el pago", () => {
  it("responde 201 y crea una única reserva con TTL de 15 minutos", async () => {
    const response = await confirmPayment({ intentId: "pi_2" });

    expect(response.status).toBe(201);
    expect(response.reservation.ttlSeconds).toBe(900);
  });

  it("responde 409 y no crea reserva si falta stock en una línea", async () => {
    const response = await confirmPayment({ intentId: "pi_3", shortLine: "SKU-9" });

    expect(response.status).toBe(409);
    expect(response.reservation).toBeNull();
  });
});
