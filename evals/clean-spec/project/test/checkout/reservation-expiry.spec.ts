// @covers R-CHK-011
import { describe, expect, it } from "vitest";

import { advanceClock, readReservation } from "../../src/checkout/reservation";

describe("caducidad de la reserva", () => {
  it("libera el stock y marca la reserva como caducada al cumplirse el TTL", async () => {
    const reservation = await readReservation("res_1");
    await advanceClock({ minutes: 15 });

    const expired = await readReservation(reservation.id);

    expect(expired.state).toBe("expired");
    expect(expired.stockReleased).toBe(true);
  });
});
