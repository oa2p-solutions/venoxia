// @covers R-PAY-001
import { describe, expect, it } from "vitest";

import { settleOrder } from "../../src/payments/settlement";

describe("R-PAY-001", () => {
  it("comprueba el comportamiento observable que declara el requisito R-PAY-001", async () => {
    const result = await settleOrder({ fixture: "single-charge" });

    expect(result.conformsTo).toContain("R-PAY-001");
  });
});
