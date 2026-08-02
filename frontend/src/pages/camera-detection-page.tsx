import {
  Camera,
  CircleStop,
  Cpu,
  Frame,
  LoaderCircle,
  Radio,
  ScanSearch,
  Timer,
} from "lucide-react";
import { useRef, useState } from "react";

import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader } from "../components/ui/card";
import {
  type CameraFacingMode,
  useCameraDetection,
} from "../features/camera/hooks/use-camera-detection";
import { formatDuration } from "../lib/format";

const statusLabels = {
  idle: "Idle",
  requesting_permission: "Requesting permission",
  creating_session: "Creating session",
  connecting: "Connecting",
  loading_model: "Loading model",
  streaming: "Live",
  stopping: "Stopping",
  completed: "Completed",
  error: "Error",
} as const;

interface MetricProps {
  label: string;
  value: string;
  icon: typeof Camera;
}

function Metric({ label, value, icon: Icon }: MetricProps) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div className="flex items-center gap-2 text-slate-500">
        <Icon aria-hidden="true" className="size-4" />

        <span className="text-xs font-semibold tracking-wide uppercase">{label}</span>
      </div>

      <p className="mt-2 text-xl font-bold text-slate-950">{value}</p>
    </div>
  );
}

export function CameraDetectionPage() {
  const videoRef = useRef<HTMLVideoElement>(null);

  const captureCanvasRef = useRef<HTMLCanvasElement>(null);

  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);

  const [confidenceThreshold, setConfidenceThreshold] = useState(0.25);

  const [facingMode, setFacingMode] = useState<CameraFacingMode>("user");

  const cameraDetection = useCameraDetection({
    videoRef,
    captureCanvasRef,
    overlayCanvasRef,
  });

  const isActive = [
    "requesting_permission",
    "creating_session",
    "connecting",
    "loading_model",
    "streaming",
    "stopping",
  ].includes(cameraDetection.status);

  const isLoading = [
    "requesting_permission",
    "creating_session",
    "connecting",
    "loading_model",
  ].includes(cameraDetection.status);

  const currentMetrics = cameraDetection.latestFrame?.session;

  return (
    <div className="space-y-6">
      <header>
        <p className="text-sm font-semibold text-blue-700">Stage 10</p>

        <h1 className="mt-1 text-3xl font-black tracking-tight text-slate-950">
          Live camera detection
        </h1>

        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          Capture frames in the browser, send them through WebSocket, and display YOLO tracking
          results in real time.
        </p>
      </header>

      {cameraDetection.errorMessage ? (
        <div
          role="alert"
          className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-900"
        >
          {cameraDetection.errorMessage}
        </div>
      ) : null}

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-bold text-slate-950">Camera preview</h2>

                <p className="mt-1 text-sm text-slate-500">
                  Frames are processed temporarily and are not saved as a recording.
                </p>
              </div>

              <span
                aria-live="polite"
                className={[
                  "inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-bold tracking-wide uppercase",
                  cameraDetection.status === "streaming"
                    ? "bg-emerald-100 text-emerald-700"
                    : cameraDetection.status === "error"
                      ? "bg-red-100 text-red-700"
                      : "bg-slate-100 text-slate-700",
                ].join(" ")}
              >
                {cameraDetection.status === "streaming" ? (
                  <Radio aria-hidden="true" className="size-3 animate-pulse" />
                ) : isLoading ? (
                  <LoaderCircle aria-hidden="true" className="size-3 animate-spin" />
                ) : null}

                {statusLabels[cameraDetection.status]}
              </span>
            </div>
          </CardHeader>

          <CardContent>
            <div
              className="relative overflow-hidden rounded-2xl bg-slate-950"
              style={{
                aspectRatio: cameraDetection.frameAspectRatio,
              }}
            >
              <video
                ref={videoRef}
                muted
                playsInline
                className="absolute inset-0 size-full object-fill"
              />

              <canvas
                ref={overlayCanvasRef}
                className="pointer-events-none absolute inset-0 size-full"
              />

              <canvas ref={captureCanvasRef} className="hidden" />

              {!isActive && !cameraDetection.completedSession ? (
                <div className="absolute inset-0 flex flex-col items-center justify-center px-6 text-center text-white">
                  <span className="flex size-16 items-center justify-center rounded-2xl bg-white/10">
                    <Camera aria-hidden="true" className="size-8" />
                  </span>

                  <p className="mt-4 font-bold">Camera is not active</p>

                  <p className="mt-2 max-w-sm text-sm text-slate-300">
                    Select the settings and start a live detection session.
                  </p>
                </div>
              ) : null}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-lg font-bold text-slate-950">Session controls</h2>
          </CardHeader>

          <CardContent className="space-y-6">
            <label className="block">
              <span className="text-sm font-semibold text-slate-800">Camera direction</span>

              <select
                value={facingMode}
                disabled={isActive}
                onChange={(event) => {
                  const nextFacingMode: CameraFacingMode =
                    event.target.value === "environment" ? "environment" : "user";

                  setFacingMode(nextFacingMode);
                }}
                className="mt-2 min-h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-100"
              >
                <option value="user">Front camera</option>

                <option value="environment">Rear camera</option>
              </select>
            </label>

            <label className="block">
              <span className="flex items-center justify-between gap-4 text-sm font-semibold text-slate-800">
                <span>Confidence threshold</span>

                <span className="text-blue-700">{(confidenceThreshold * 100).toFixed(0)}%</span>
              </span>

              <input
                type="range"
                min="0.1"
                max="0.9"
                step="0.05"
                value={confidenceThreshold}
                disabled={isActive}
                onChange={(event) => {
                  setConfidenceThreshold(Number(event.target.value));
                }}
                className="mt-3 w-full accent-blue-600"
              />
            </label>

            {!isActive ? (
              <Button
                icon={Camera}
                className="w-full"
                onClick={() => {
                  void cameraDetection.start({
                    confidenceThreshold,
                    facingMode,
                  });
                }}
              >
                Start live detection
              </Button>
            ) : (
              <Button
                icon={CircleStop}
                variant="danger"
                className="w-full"
                disabled={cameraDetection.status === "stopping"}
                onClick={cameraDetection.stop}
              >
                Stop live detection
              </Button>
            )}

            <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 text-sm leading-6 text-blue-950">
              <strong>Privacy:</strong> audio is never requested. Raw camera frames are not stored
              as files or videos.
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <Metric
          label="Current objects"
          value={String(cameraDetection.latestFrame?.objects.length ?? 0)}
          icon={ScanSearch}
        />

        <Metric
          label="Processed frames"
          value={String(currentMetrics?.processed_frames ?? 0)}
          icon={Frame}
        />

        <Metric
          label="Total detections"
          value={String(currentMetrics?.total_detections ?? 0)}
          icon={Camera}
        />

        <Metric
          label="Unique tracks"
          value={String(currentMetrics?.unique_objects ?? 0)}
          icon={Radio}
        />

        <Metric
          label="Inference"
          value={
            cameraDetection.latestFrame
              ? `${cameraDetection.latestFrame.inference_ms} ms`
              : "Not available"
          }
          icon={Cpu}
        />
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <h2 className="text-lg font-bold text-slate-950">Current-frame summary</h2>
          </CardHeader>

          <CardContent>
            {cameraDetection.latestFrame &&
            Object.keys(cameraDetection.latestFrame.summary).length > 0 ? (
              <div className="grid gap-3 sm:grid-cols-2">
                {Object.entries(cameraDetection.latestFrame.summary).map(([className, count]) => (
                  <div
                    key={className}
                    className="flex items-center justify-between rounded-xl border border-slate-200 p-4"
                  >
                    <span className="font-semibold text-slate-800 capitalize">{className}</span>

                    <span className="rounded-full bg-blue-100 px-3 py-1 text-sm font-bold text-blue-700">
                      {count}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">
                No supported objects are visible in the current frame.
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-lg font-bold text-slate-950">Runtime</h2>
          </CardHeader>

          <CardContent className="grid gap-4 sm:grid-cols-2">
            <Metric
              label="Server FPS"
              value={
                cameraDetection.latestFrame
                  ? cameraDetection.latestFrame.server_fps.toFixed(2)
                  : "0.00"
              }
              icon={Radio}
            />

            <Metric
              label="Elapsed"
              value={formatDuration(currentMetrics?.elapsed_ms ?? null)}
              icon={Timer}
            />

            <Metric
              label="Frames sent"
              value={String(cameraDetection.sentFrameCount)}
              icon={Frame}
            />

            <Metric
              label="Target FPS"
              value={String(cameraDetection.session?.target_fps ?? 0)}
              icon={Cpu}
            />
          </CardContent>
        </Card>
      </div>

      {cameraDetection.completedSession ? (
        <Card>
          <CardHeader>
            <h2 className="text-lg font-bold text-slate-950">Completed session</h2>
          </CardHeader>

          <CardContent className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <Metric
              label="Processed frames"
              value={String(cameraDetection.completedSession.processed_frames)}
              icon={Frame}
            />

            <Metric
              label="Detections"
              value={String(cameraDetection.completedSession.total_detections)}
              icon={ScanSearch}
            />

            <Metric
              label="Unique tracks"
              value={String(cameraDetection.completedSession.unique_objects)}
              icon={Radio}
            />

            <Metric
              label="Duration"
              value={formatDuration(cameraDetection.completedSession.duration_ms)}
              icon={Timer}
            />
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
