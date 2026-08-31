// @covers R-CHK-002
import { describe, expect, it } from "vitest";

import { confirmPayment } from "../../src/checkout/payment";

describe("confirmación de pago", () => {
  it("devuelve el resultado de la primera confirmación y no cobra dos veces", async () => {
    const first = await confirmPayment({ intentId: "pi_1" });
    const second = await confirmPayment({ intentId: "pi_1" });

    expect(second.status).toBe(200);
    expect(second.chargeId).toBe(first.chargeId);
  });
});
