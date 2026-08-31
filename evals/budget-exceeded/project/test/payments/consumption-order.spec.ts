// @covers R-PAY-010
import { describe, expect, it } from "vitest";

import { settleOrder } from "../../src/payments/settlement";

describe("R-PAY-010", () => {
  it("comprueba el comportamiento observable que declara el requisito R-PAY-010", async () => {
    const result = await settleOrder({ fixture: "consumption-order" });

    expect(result.conformsTo).toContain("R-PAY-010");
  });
});
