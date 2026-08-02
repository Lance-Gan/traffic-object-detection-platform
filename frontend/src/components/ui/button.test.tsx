import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { Button } from "./button";

describe("Button", () => {
  it("renders its label", () => {
    render(<Button>Start detection</Button>);

    expect(
      screen.getByRole("button", {
        name: "Start detection",
      }),
    ).toBeInTheDocument();
  });

  it("calls the click handler", async () => {
    const user = userEvent.setup();

    const onClick = vi.fn();

    render(<Button onClick={onClick}>Run</Button>);

    await user.click(
      screen.getByRole("button", {
        name: "Run",
      }),
    );

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("prevents clicks when disabled", async () => {
    const user = userEvent.setup();

    const onClick = vi.fn();

    render(
      <Button disabled onClick={onClick}>
        Disabled
      </Button>,
    );

    await user.click(
      screen.getByRole("button", {
        name: "Disabled",
      }),
    );

    expect(onClick).not.toHaveBeenCalled();
  });
});
