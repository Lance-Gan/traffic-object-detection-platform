import { Play, RotateCcw } from "lucide-react";
import { useEffect, useRef, useState } from "react";

import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader } from "../components/ui/card";
import { ConfidenceControl } from "../features/detections/components/confidence-control";
import { DetectionResults } from "../features/detections/components/detection-results";
import { ImageDropzone } from "../features/detections/components/image-dropzone";
import { UploadProgress } from "../features/detections/components/upload-progress";
import { useDetectImage } from "../features/detections/hooks/use-detect-image";
import { getErrorMessage } from "../lib/http-error";

export function DetectionWorkspacePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [confidenceThreshold, setConfidenceThreshold] = useState(0.25);

  const [validationError, setValidationError] = useState<string | null>(null);

  const [localPreviewUrl, setLocalPreviewUrl] = useState<string | null>(null);

  const previewUrlRef = useRef<string | null>(null);

  const { mutation, uploadProgress, reset } = useDetectImage();

  const updateLocalPreview = (file: File | null) => {
    if (previewUrlRef.current !== null) {
      URL.revokeObjectURL(previewUrlRef.current);
    }

    const nextPreviewUrl = file === null ? null : URL.createObjectURL(file);

    previewUrlRef.current = nextPreviewUrl;

    setLocalPreviewUrl(nextPreviewUrl);
  };

  useEffect(() => {
    return () => {
      if (previewUrlRef.current !== null) {
        URL.revokeObjectURL(previewUrlRef.current);
      }
    };
  }, []);

  const handleFileSelect = (file: File | null) => {
    reset();
    updateLocalPreview(file);
    setSelectedFile(file);
  };

  const handleDetect = () => {
    if (!selectedFile) {
      setValidationError("Select an image before starting detection");
      return;
    }

    setValidationError(null);

    mutation.mutate({
      file: selectedFile,
      confidenceThreshold,
    });
  };

  const handleReset = () => {
    reset();
    updateLocalPreview(null);
    setSelectedFile(null);
    setValidationError(null);
    setConfidenceThreshold(0.25);
  };

  const requestError = mutation.error ? getErrorMessage(mutation.error) : null;

  return (
    <div className="space-y-6">
      <header>
        <p className="text-sm font-semibold text-blue-700">Detection workspace</p>

        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
          Image object detection
        </h1>

        <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600 sm:text-base">
          Upload a traffic image, choose a confidence threshold, and run YOLO detection through the
          FastAPI backend.
        </p>
      </header>

      <div className="grid items-start gap-6 xl:grid-cols-[420px_minmax(0,1fr)]">
        <Card className="xl:sticky xl:top-6">
          <CardHeader>
            <h2 className="text-lg font-bold text-slate-950">Detection settings</h2>

            <p className="mt-1 text-sm text-slate-500">Configure and submit one image at a time.</p>
          </CardHeader>

          <CardContent className="space-y-6">
            <ImageDropzone
              selectedFile={selectedFile}
              onFileSelect={handleFileSelect}
              onValidationError={setValidationError}
              disabled={mutation.isPending}
            />

            <ConfidenceControl
              value={confidenceThreshold}
              onChange={setConfidenceThreshold}
              disabled={mutation.isPending}
            />

            {validationError ? (
              <div
                role="alert"
                className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-900"
              >
                {validationError}
              </div>
            ) : null}

            {requestError ? (
              <div
                role="alert"
                className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm leading-6 text-red-900"
              >
                {requestError}
              </div>
            ) : null}

            {mutation.isPending ? <UploadProgress percentage={uploadProgress} /> : null}

            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
              <Button
                onClick={handleDetect}
                disabled={!selectedFile}
                isLoading={mutation.isPending}
                icon={Play}
                className="w-full"
              >
                {mutation.isPending ? "Running detection" : "Start detection"}
              </Button>

              <Button
                onClick={handleReset}
                disabled={mutation.isPending || (!selectedFile && !mutation.data)}
                variant="secondary"
                icon={RotateCcw}
                className="w-full"
              >
                Reset workspace
              </Button>
            </div>
          </CardContent>
        </Card>

        <DetectionResults result={mutation.data} localPreviewUrl={localPreviewUrl} />
      </div>
    </div>
  );
}
