import type { DetectionJobStatus } from "../../detections/detection-schema";
import { cn } from "../../../lib/cn";

interface StatusBadgeProps {
  status: DetectionJobStatus;
}

const statusClasses: Record<DetectionJobStatus, string> = {
  completed: "bg-emerald-100 text-emerald-700",
  failed: "bg-red-100 text-red-700",
  processing: "bg-blue-100 text-blue-700",
  pending: "bg-amber-100 text-amber-700",
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex rounded-full px-2.5 py-1 text-xs font-bold tracking-wide uppercase",
        statusClasses[status],
      )}
    >
      {status}
    </span>
  );
}
