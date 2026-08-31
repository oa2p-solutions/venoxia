// @covers R-CHK-001
import { describe, expect, it } from "vitest";

import { recalculateCart } from "../../src/checkout/cart";

describe("total del carrito", () => {
  it("recalcula el total al subir la cantidad de una línea con stock", () => {
    const cart = recalculateCart({
      lines: [{ sku: "SKU-1", quantity: 3, unitPriceCents: 1000 }],
    });

    expect(cart.totalCents).toBe(3000);
  });
});
