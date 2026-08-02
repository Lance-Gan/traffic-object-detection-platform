import { Box, Clock3, Cpu, FileImage, ScanSearch } from "lucide-react";

import { Card, CardContent, CardHeader } from "../../../components/ui/card";
import { formatConfidence, formatDuration, formatMelbourneDate } from "../../../lib/format";
import type { DetectionJobDetail } from "../detection-schema";

interface DetectionResultsProps {
  result: DetectionJobDetail | undefined;
  localPreviewUrl: string | null;
}

interface MetricCardProps {
  label: string;
  value: string;
  icon: typeof Box;
}

function MetricCard({ label, value, icon: Icon }: MetricCardProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div className="flex items-center gap-2 text-slate-500">
        <Icon aria-hidden="true" className="size-4" />

        <span className="text-xs font-semibold tracking-wide uppercase">{label}</span>
      </div>

      <p className="mt-2 text-lg font-bold wrap-break-word text-slate-950">{value}</p>
    </div>
  );
}

export function DetectionResults({ result, localPreviewUrl }: DetectionResultsProps) {
  const displayedMediaUrl = result?.result_url ?? localPreviewUrl;

  const isVideoResult = result?.source_type === "video" && result.result_url !== null;

  if (!displayedMediaUrl) {
    return (
      <Card className="h-full">
        <CardContent className="flex min-h-96 flex-col items-center justify-center text-center">
          <span className="flex size-16 items-center justify-center rounded-2xl bg-slate-100 text-slate-500">
            <ScanSearch aria-hidden="true" className="size-8" />
          </span>

          <h2 className="mt-5 text-lg font-bold text-slate-950">Detection result</h2>

          <p className="mt-2 max-w-sm text-sm leading-6 text-slate-500">
            Select an image or video and start detection. The processed result and detected objects
            will appear here.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-bold text-slate-950">
                {result ? "Detection result" : "Image preview"}
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                {result
                  ? result.original_filename
                  : "The selected image has not been processed yet"}
              </p>
            </div>

            {result ? (
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold tracking-wide text-emerald-700 uppercase">
                {result.status}
              </span>
            ) : null}
          </div>
        </CardHeader>

        <CardContent>
          <div className="overflow-hidden rounded-xl border border-slate-200 bg-slate-950">
            {isVideoResult ? (
              <video
                src={displayedMediaUrl}
                controls
                preload="metadata"
                className="max-h-155 w-full rounded-xl bg-black"
              >
                Your browser does not support video playback.
              </video>
            ) : (
              <img
                src={displayedMediaUrl}
                alt={
                  result
                    ? `Detection result for ${result.original_filename}`
                    : "Selected image preview"
                }
                className="mx-auto max-h-155 w-full object-contain"
              />
            )}
          </div>
        </CardContent>
      </Card>

      {result ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <MetricCard label="Objects" value={String(result.detected_object_count)} icon={Box} />

            <MetricCard label="Duration" value={formatDuration(result.duration_ms)} icon={Clock3} />

            <MetricCard label="Model" value={result.model_name} icon={ScanSearch} />

            <MetricCard label="Device" value={result.device.toUpperCase()} icon={Cpu} />
          </div>

          <Card>
            <CardHeader>
              <h2 className="text-lg font-bold text-slate-950">Detection summary</h2>

              <p className="mt-1 text-sm text-slate-500">
                Completed at {formatMelbourneDate(result.completed_at)}
              </p>
            </CardHeader>

            <CardContent>
              {Object.keys(result.summary).length > 0 ? (
                <div className="flex flex-wrap gap-3">
                  {Object.entries(result.summary)
                    .sort(([firstName], [secondName]) => firstName.localeCompare(secondName))
                    .map(([className, count]) => (
                      <div
                        key={className}
                        className="rounded-xl border border-blue-200 bg-blue-50 px-4 py-3"
                      >
                        <p className="text-xs font-semibold tracking-wide text-blue-600 uppercase">
                          {className}
                        </p>

                        <p className="mt-1 text-2xl font-bold text-blue-950">{count}</p>
                      </div>
                    ))}
                </div>
              ) : (
                <div className="rounded-xl bg-slate-50 p-5 text-sm text-slate-600">
                  No supported traffic objects were detected at the selected confidence threshold.
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <FileImage aria-hidden="true" className="size-5 text-blue-600" />

                <div>
                  <h2 className="text-lg font-bold text-slate-950">Detected objects</h2>

                  <p className="mt-1 text-sm text-slate-500">
                    Frame numbers, tracking IDs, confidence scores and bounding-box coordinates
                  </p>
                </div>
              </div>
            </CardHeader>

            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-left">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-5 py-3 text-xs font-bold tracking-wide whitespace-nowrap text-slate-500 uppercase">
                      Frame
                    </th>

                    <th className="px-5 py-3 text-xs font-bold tracking-wide whitespace-nowrap text-slate-500 uppercase">
                      Track ID
                    </th>

                    <th className="px-5 py-3 text-xs font-bold tracking-wide whitespace-nowrap text-slate-500 uppercase">
                      Class
                    </th>

                    <th className="px-5 py-3 text-xs font-bold tracking-wide whitespace-nowrap text-slate-500 uppercase">
                      Confidence
                    </th>

                    <th className="px-5 py-3 text-xs font-bold tracking-wide whitespace-nowrap text-slate-500 uppercase">
                      Bounding box
                    </th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-100 bg-white">
                  {result.objects.map((detectedObject, index) => {
                    const box = detectedObject.bounding_box;

                    const rowKey = [
                      detectedObject.frame_index,
                      detectedObject.track_id ?? "untracked",
                      detectedObject.class_name,
                      index,
                    ].join("-");

                    return (
                      <tr key={rowKey}>
                        <td className="px-5 py-4 text-sm whitespace-nowrap text-slate-700">
                          {detectedObject.frame_index}
                        </td>

                        <td className="px-5 py-4 text-sm whitespace-nowrap text-slate-700">
                          {detectedObject.track_id ?? "Not tracked"}
                        </td>

                        <td className="px-5 py-4 text-sm font-semibold whitespace-nowrap text-slate-900">
                          {detectedObject.class_name}
                        </td>

                        <td className="px-5 py-4 text-sm whitespace-nowrap text-slate-700">
                          {formatConfidence(detectedObject.confidence)}
                        </td>

                        <td className="px-5 py-4 font-mono text-xs whitespace-nowrap text-slate-600">
                          [{box.x1.toFixed(1)}, {box.y1.toFixed(1)}, {box.x2.toFixed(1)},{" "}
                          {box.y2.toFixed(1)}]
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>

              {result.objects.length === 0 ? (
                <div className="p-6 text-center text-sm text-slate-500">
                  No object records are available.
                </div>
              ) : null}
            </div>
          </Card>
        </>
      ) : null}
    </div>
  );
}
