// @covers R-PAY-012
import { describe, expect, it } from "vitest";

import { settleOrder } from "../../src/payments/settlement";

describe("R-PAY-012", () => {
  it("comprueba el comportamiento observable que declara el requisito R-PAY-012", async () => {
    const result = await settleOrder({ fixture: "split-amounts" });

    expect(result.conformsTo).toContain("R-PAY-012");
  });
});
