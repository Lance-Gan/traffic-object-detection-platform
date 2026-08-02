import { describe, expect, it } from "vitest";

import { formatBytes, formatConfidence, formatDuration } from "./format";

describe("formatBytes", () => {
  it("formats bytes", () => {
    expect(formatBytes(0)).toBe("0 B");

    expect(formatBytes(1024)).toBe("1.00 KiB");
  });
});

describe("formatDuration", () => {
  it("formats milliseconds", () => {
    expect(formatDuration(500)).toBe("500 ms");

    expect(formatDuration(1500)).toBe("1.50 s");
  });
});

describe("formatConfidence", () => {
  it("formats a percentage", () => {
    expect(formatConfidence(0.912)).toBe("91.2%");
  });
});
