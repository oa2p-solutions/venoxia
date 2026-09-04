// @covers R-CHK-001
import { describe, expect, it } from "vitest";

import { buildReceipt } from "../../src/checkout/receipt";

describe("recibo al confirmar el pago", () => {
  it("muestra la línea única con su importe exacto", () => {
    const receipt = buildReceipt({ lines: [{ sku: "ABC", amountCents: 1999 }] });

    expect(receipt.lines).toEqual([{ sku: "ABC", amountCents: 1999 }]);
  });
});
