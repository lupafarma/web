import { describe, it, expect } from "vitest";
import { SAMPLE_LINES } from "./sample";

describe("SAMPLE_LINES (Cargar ejemplo)", () => {
  it("loads 8 sample invoice lines", () => {
    expect(SAMPLE_LINES).toHaveLength(8);
  });

  it("every line has the InvoiceLine shape (cn string, qty/unit/total numbers)", () => {
    for (const l of SAMPLE_LINES) {
      expect(typeof l.cn).toBe("string");
      expect(l.cn).toMatch(/^\d{6}$/);
      expect(typeof l.qty).toBe("number");
      expect(typeof l.unit).toBe("number");
      expect(typeof l.total).toBe("number");
      expect(l.qty).toBeGreaterThan(0);
    }
  });
});
