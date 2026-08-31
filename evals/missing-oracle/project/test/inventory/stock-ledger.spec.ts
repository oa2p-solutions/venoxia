// @covers R-INV-001
import { describe, expect, it } from "vitest";

import { recordMovement, readLedger } from "../../src/inventory/ledger";

describe("libro de existencias", () => {
  it("anota una salida de tres unidades con su motivo e instante", async () => {
    await recordMovement({ sku: "SKU-1", quantity: -3, reason: "sale" });

    const entries = await readLedger("SKU-1");

    expect(entries.at(-1)).toMatchObject({ quantity: -3, reason: "sale" });
  });
});
