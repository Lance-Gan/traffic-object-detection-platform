import { FileImage, UploadCloud, X } from "lucide-react";
import { useCallback, type MouseEvent } from "react";
import { useDropzone, type FileRejection } from "react-dropzone";

import { env } from "../../../lib/env";
import { formatBytes } from "../../../lib/format";
import { cn } from "../../../lib/cn";

interface ImageDropzoneProps {
  selectedFile: File | null;
  onFileSelect: (file: File | null) => void;
  onValidationError: (message: string | null) => void;
  disabled?: boolean;
}

const acceptedImageTypes = {
  "image/jpeg": [".jpg", ".jpeg"],
  "image/png": [".png"],
  "image/webp": [".webp"],
};

function getRejectionMessage(rejection: FileRejection): string {
  const firstError = rejection.errors[0];

  if (!firstError) {
    return "The selected file could not be accepted";
  }

  if (firstError.code === "file-too-large") {
    return `The image must not exceed ${formatBytes(env.VITE_MAX_IMAGE_UPLOAD_BYTES)}`;
  }

  if (firstError.code === "file-invalid-type") {
    return "Only JPEG, PNG, and WebP images are supported";
  }

  if (firstError.code === "too-many-files") {
    return "Select one image at a time";
  }

  return firstError.message;
}

export function ImageDropzone({
  selectedFile,
  onFileSelect,
  onValidationError,
  disabled = false,
}: ImageDropzoneProps) {
  const handleAcceptedFiles = useCallback(
    (files: File[]) => {
      const file = files[0] ?? null;

      onValidationError(null);
      onFileSelect(file);
    },
    [onFileSelect, onValidationError],
  );

  const handleRejectedFiles = useCallback(
    (rejections: FileRejection[]) => {
      const firstRejection = rejections[0];

      onFileSelect(null);

      onValidationError(
        firstRejection
          ? getRejectionMessage(firstRejection)
          : "The selected file could not be accepted",
      );
    },
    [onFileSelect, onValidationError],
  );

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    accept: acceptedImageTypes,
    maxFiles: 1,
    maxSize: env.VITE_MAX_IMAGE_UPLOAD_BYTES,
    disabled,
    noClick: true,
    onDropAccepted: handleAcceptedFiles,
    onDropRejected: handleRejectedFiles,
  });

  const removeSelectedFile = (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    onValidationError(null);
    onFileSelect(null);
  };

  return (
    <div
      {...getRootProps()}
      className={cn(
        "rounded-2xl border-2 border-dashed p-6 text-center transition sm:p-10",
        isDragActive ? "border-blue-500 bg-blue-50" : "border-slate-300 bg-slate-50",
        disabled && "cursor-not-allowed opacity-60",
      )}
    >
      <input {...getInputProps()} aria-label="Select an image for object detection" />

      {selectedFile ? (
        <div className="flex flex-col items-center">
          <span className="flex size-14 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-700">
            <FileImage aria-hidden="true" className="size-7" />
          </span>

          <p className="mt-4 max-w-full truncate text-sm font-semibold text-slate-900">
            {selectedFile.name}
          </p>

          <p className="mt-1 text-sm text-slate-500">{formatBytes(selectedFile.size)}</p>

          <div className="mt-5 flex flex-wrap justify-center gap-3">
            <button
              type="button"
              onClick={open}
              disabled={disabled}
              className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed"
            >
              Replace image
            </button>

            <button
              type="button"
              onClick={removeSelectedFile}
              disabled={disabled}
              className="inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold text-red-600 hover:bg-red-50 disabled:cursor-not-allowed"
            >
              <X aria-hidden="true" className="size-4" />
              Remove
            </button>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center">
          <span className="flex size-14 items-center justify-center rounded-2xl bg-blue-100 text-blue-700">
            <UploadCloud aria-hidden="true" className="size-7" />
          </span>

          <p className="mt-4 text-base font-semibold text-slate-900">
            {isDragActive ? "Drop the image here" : "Drag and drop an image"}
          </p>

          <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
            JPEG, PNG, or WebP. Maximum file size {formatBytes(env.VITE_MAX_IMAGE_UPLOAD_BYTES)}.
          </p>

          <button
            type="button"
            onClick={open}
            disabled={disabled}
            className="mt-5 rounded-lg bg-slate-900 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-700 disabled:cursor-not-allowed"
          >
            Browse files
          </button>
        </div>
      )}
    </div>
  );
}
