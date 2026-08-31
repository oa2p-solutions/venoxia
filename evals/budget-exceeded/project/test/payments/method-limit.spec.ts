// @covers R-PAY-011
import { describe, expect, it } from "vitest";

import { settleOrder } from "../../src/payments/settlement";

describe("R-PAY-011", () => {
  it("comprueba el comportamiento observable que declara el requisito R-PAY-011", async () => {
    const result = await settleOrder({ fixture: "method-limit" });

    expect(result.conformsTo).toContain("R-PAY-011");
  });
});
