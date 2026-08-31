// @covers R-INV-003
import { describe, expect, it } from "vitest";

import { reorderPoint } from "../../src/inventory/reorder";

describe("punto de pedido", () => {
  it("es el consumo medio diario por el plazo de entrega", () => {
    const point = reorderPoint({ dailyAverage: 12, leadTimeDays: 5 });

    expect(point).toBe(60);
  });
});
