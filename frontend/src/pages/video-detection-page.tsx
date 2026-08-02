import { CheckCircle2, Film, Gauge, RefreshCw, ScanSearch, Timer, UploadCloud } from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";
import { useDropzone } from "react-dropzone";

import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader } from "../components/ui/card";
import { useVideoDetection } from "../features/videos/hooks/use-video-detection";
import { env } from "../lib/env";
import { formatBytes, formatDuration } from "../lib/format";

const VIDEO_ACCEPT = {
  "video/mp4": [".mp4"],

  "video/quicktime": [".mov"],

  "video/webm": [".webm"],
};

function inspectVideoDuration(file: File): Promise<number | null> {
  return new Promise((resolve) => {
    const objectUrl = URL.createObjectURL(file);

    const video = document.createElement("video");

    const cleanup = () => {
      URL.revokeObjectURL(objectUrl);

      video.removeAttribute("src");
    };

    video.preload = "metadata";

    video.onloadedmetadata = () => {
      const duration = Number.isFinite(video.duration) ? video.duration : null;

      cleanup();
      resolve(duration);
    };

    video.onerror = () => {
      cleanup();
      resolve(null);
    };

    video.src = objectUrl;
  });
}

interface MetricProps {
  label: string;
  value: string;
  icon: typeof Film;
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

function ProgressBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="flex items-center justify-between text-sm font-semibold text-slate-700">
        <span>{label}</span>
        <span>{value}%</span>
      </div>

      <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-200">
        <div
          className="h-full rounded-full bg-blue-600 transition-[width] duration-300"
          style={{
            width: `${value}%`,
          }}
        />
      </div>
    </div>
  );
}

function Alert({ children }: { children: ReactNode }) {
  return (
    <div
      role="alert"
      className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-900"
    >
      {children}
    </div>
  );
}

export function VideoDetectionPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const [videoDuration, setVideoDuration] = useState<number | null>(null);

  const [confidenceThreshold, setConfidenceThreshold] = useState(0.25);

  const [localError, setLocalError] = useState<string | null>(null);

  const videoDetection = useVideoDetection();

  useEffect(() => {
    return () => {
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const selectVideo = async (file: File) => {
    setLocalError(null);

    const duration = await inspectVideoDuration(file);

    if (duration !== null && duration > env.VITE_MAX_VIDEO_DURATION_SECONDS) {
      setSelectedFile(null);
      setVideoDuration(null);

      setLocalError(
        "The video must not exceed " + `${env.VITE_MAX_VIDEO_DURATION_SECONDS} seconds.`,
      );

      return;
    }

    setSelectedFile(file);
    setVideoDuration(duration);

    setPreviewUrl(URL.createObjectURL(file));

    videoDetection.reset();
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: VIDEO_ACCEPT,

    maxFiles: 1,

    maxSize: env.VITE_MAX_VIDEO_UPLOAD_BYTES,

    disabled: videoDetection.isProcessing,

    onDropAccepted: (files) => {
      const file = files[0];

      if (file) {
        void selectVideo(file);
      }
    },

    onDropRejected: (rejections) => {
      const errorCode = rejections[0]?.errors[0]?.code;

      if (errorCode === "file-too-large") {
        setLocalError(
          "The video must not exceed " + formatBytes(env.VITE_MAX_VIDEO_UPLOAD_BYTES) + ".",
        );

        return;
      }

      setLocalError("Only MP4, MOV, and WebM " + "videos are supported.");
    },
  });

  const job = videoDetection.job;

  const resetPage = () => {
    setSelectedFile(null);
    setVideoDuration(null);
    setLocalError(null);
    setPreviewUrl(null);

    videoDetection.reset();
  };

  const submitVideo = () => {
    if (!selectedFile) {
      setLocalError("Select a video first.");

      return;
    }

    setLocalError(null);

    videoDetection.submit({
      file: selectedFile,
      confidenceThreshold,
    });
  };

  return (
    <div className="space-y-6">
      <header>
        <p className="text-sm font-semibold text-blue-700">Stage 9</p>

        <h1 className="mt-1 text-3xl font-black tracking-tight text-slate-950">Video detection</h1>

        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          Upload a video, process it asynchronously with YOLO Tracking, and review the annotated
          H.264 result.
        </p>
      </header>

      {localError ? <Alert>{localError}</Alert> : null}

      {videoDetection.errorMessage ? <Alert>{videoDetection.errorMessage}</Alert> : null}

      <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_360px]">
        <Card>
          <CardHeader>
            <h2 className="text-lg font-bold text-slate-950">Source video</h2>
          </CardHeader>

          <CardContent className="space-y-5">
            <div
              {...getRootProps()}
              className={[
                "flex min-h-48 cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-10 text-center transition",
                isDragActive
                  ? "border-blue-500 bg-blue-50"
                  : "border-slate-300 bg-slate-50 hover:border-blue-400 hover:bg-blue-50/50",
                videoDetection.isProcessing ? "cursor-not-allowed opacity-60" : "",
              ].join(" ")}
            >
              <input {...getInputProps()} />

              <span className="flex size-14 items-center justify-center rounded-2xl bg-blue-100 text-blue-700">
                <UploadCloud aria-hidden="true" className="size-7" />
              </span>

              <p className="mt-4 font-bold text-slate-900">
                {isDragActive ? "Drop the video here" : "Drag a video here or browse"}
              </p>

              <p className="mt-2 text-sm text-slate-500">
                MP4, MOV, or WebM · up to {formatBytes(env.VITE_MAX_VIDEO_UPLOAD_BYTES)}
              </p>
            </div>

            {selectedFile ? (
              <div className="rounded-xl border border-slate-200 p-4">
                <p className="font-semibold text-slate-900">{selectedFile.name}</p>

                <p className="mt-1 text-sm text-slate-500">
                  {formatBytes(selectedFile.size)}

                  {videoDuration !== null ? ` · ${videoDuration.toFixed(1)} seconds` : ""}
                </p>
              </div>
            ) : null}

            {previewUrl ? (
              <video
                src={previewUrl}
                controls
                preload="metadata"
                className="max-h-130 w-full rounded-xl bg-black"
              />
            ) : null}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <h2 className="text-lg font-bold text-slate-950">Detection settings</h2>
          </CardHeader>

          <CardContent className="space-y-6">
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
                disabled={videoDetection.isProcessing}
                onChange={(event) => {
                  setConfidenceThreshold(Number(event.target.value));
                }}
                className="mt-3 w-full accent-blue-600"
              />
            </label>

            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm leading-6 text-slate-700">
              <p>Target processing rate: approximately 10 FPS.</p>

              <p>Maximum duration: {env.VITE_MAX_VIDEO_DURATION_SECONDS} seconds.</p>
            </div>

            <Button
              icon={ScanSearch}
              isLoading={videoDetection.isProcessing}
              disabled={!selectedFile || videoDetection.isProcessing}
              className="w-full"
              onClick={submitVideo}
            >
              Start video detection
            </Button>

            <Button
              icon={RefreshCw}
              variant="secondary"
              disabled={videoDetection.isProcessing}
              className="w-full"
              onClick={resetPage}
            >
              Reset
            </Button>
          </CardContent>
        </Card>
      </div>

      {videoDetection.isProcessing || job ? (
        <Card>
          <CardHeader>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <h2 className="text-lg font-bold text-slate-950">Processing status</h2>

              <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-bold tracking-wide text-blue-700 uppercase">
                {job?.status ?? "uploading"}
              </span>
            </div>
          </CardHeader>

          <CardContent className="space-y-5">
            {videoDetection.uploadProgress < 100 ? (
              <ProgressBar label="Upload progress" value={videoDetection.uploadProgress} />
            ) : null}

            {job ? <ProgressBar label="Processing progress" value={job.progress_percent} /> : null}
          </CardContent>
        </Card>
      ) : null}

      {job ? (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <Metric label="Processed frames" value={String(job.processed_frames ?? 0)} icon={Film} />

          <Metric
            label="Total detections"
            value={String(job.detected_object_count)}
            icon={ScanSearch}
          />

          <Metric label="Unique tracks" value={String(job.unique_object_count)} icon={Gauge} />

          <Metric label="Processing time" value={formatDuration(job.duration_ms)} icon={Timer} />
        </div>
      ) : null}

      {job?.status === "completed" && job.result_url ? (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <CheckCircle2 aria-hidden="true" className="size-5 text-emerald-600" />

              <h2 className="text-lg font-bold text-slate-950">Annotated result</h2>
            </div>
          </CardHeader>

          <CardContent>
            <video
              src={job.result_url}
              controls
              preload="metadata"
              className="max-h-170 w-full rounded-xl bg-black"
            />
          </CardContent>
        </Card>
      ) : null}

      {job && Object.keys(job.summary).length > 0 ? (
        <Card>
          <CardHeader>
            <h2 className="text-lg font-bold text-slate-950">Unique objects by class</h2>
          </CardHeader>

          <CardContent>
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
              {Object.entries(job.summary).map(([className, count]) => (
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
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
