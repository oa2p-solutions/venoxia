// @covers R-CHK-012
import { describe, expect, it } from "vitest";

import { confirmPayment } from "../../src/checkout/payment";

describe("reserva con líneas sin stock", () => {
  it("responde 200 y comunica el resultado de la reserva con las tres líneas servibles", async () => {
    const response = await confirmPayment({ intentId: "pi_4" });

    expect(response.status).toBe(200);
    expect(response.reservation).not.toBeNull();
  });

  it("responde 200 y comunica el resultado cuando una línea se queda corta", async () => {
    const response = await confirmPayment({ intentId: "pi_5", shortLine: "SKU-9" });

    expect(response.status).toBe(200);
    expect(response.reservation).not.toBeNull();
  });
});
