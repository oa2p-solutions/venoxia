// @covers R-PAY-013
import { describe, expect, it } from "vitest";

import { settleOrder } from "../../src/payments/settlement";

describe("R-PAY-013", () => {
  it("comprueba el comportamiento observable que declara el requisito R-PAY-013", async () => {
    const result = await settleOrder({ fixture: "rollback" });

    expect(result.conformsTo).toContain("R-PAY-013");
  });
});
