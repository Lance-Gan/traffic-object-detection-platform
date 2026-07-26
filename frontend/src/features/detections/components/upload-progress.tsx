interface UploadProgressProps {
  percentage: number;
}

export function UploadProgress({ percentage }: UploadProgressProps) {
  const normalizedPercentage = Math.min(100, Math.max(0, percentage));

  return (
    <div
      aria-label="Image upload progress"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={normalizedPercentage}
      role="progressbar"
    >
      <div className="mb-2 flex items-center justify-between text-sm">
        <span className="font-medium text-slate-700">Uploading image</span>

        <span className="font-semibold text-blue-700">{normalizedPercentage}%</span>
      </div>

      <div className="h-2 overflow-hidden rounded-full bg-slate-200">
        <div
          className="h-full rounded-full bg-blue-600 transition-[width] duration-200"
          style={{
            width: `${normalizedPercentage}%`,
          }}
        />
      </div>

      {normalizedPercentage === 100 ? (
        <p className="mt-2 text-xs text-slate-500">
          Upload completed. The server is running object detection.
        </p>
      ) : null}
    </div>
  );
}
