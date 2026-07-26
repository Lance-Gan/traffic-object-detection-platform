import * as Dialog from "@radix-ui/react-dialog";
import { LoaderCircle, X } from "lucide-react";

import { DetectionResults } from "../../detections/components/detection-results";
import { getErrorMessage } from "../../../lib/http-error";
import { useDetectionJob } from "../hooks/use-detection-jobs";

interface JobDetailDialogProps {
  publicId: string | null;

  onOpenChange: (open: boolean) => void;
}

export function JobDetailDialog({ publicId, onOpenChange }: JobDetailDialogProps) {
  const query = useDetectionJob(publicId);

  return (
    <Dialog.Root open={publicId !== null} onOpenChange={onOpenChange}>
      <Dialog.Portal>
        <Dialog.Overlay className="fixed inset-0 z-40 bg-slate-950/60 backdrop-blur-sm" />

        <Dialog.Content className="fixed inset-x-4 top-4 z-50 max-h-[calc(100vh-2rem)] overflow-y-auto rounded-2xl bg-slate-50 p-4 shadow-2xl outline-none sm:inset-x-8 sm:p-6 lg:right-auto lg:left-1/2 lg:w-[min(1100px,calc(100vw-4rem))] lg:-translate-x-1/2">
          <div className="mb-6 flex items-start justify-between gap-4">
            <div>
              <Dialog.Title className="text-xl font-bold text-slate-950">
                Detection job details
              </Dialog.Title>

              <Dialog.Description className="mt-1 text-sm text-slate-500">
                Review the annotated result, metrics, and detected objects.
              </Dialog.Description>
            </div>

            <Dialog.Close
              aria-label="Close job details"
              className="flex size-10 shrink-0 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-200 hover:text-slate-900"
            >
              <X aria-hidden="true" className="size-5" />
            </Dialog.Close>
          </div>

          {query.isPending ? (
            <div className="flex min-h-80 items-center justify-center">
              <LoaderCircle
                aria-label="Loading job details"
                className="size-8 animate-spin text-blue-600"
              />
            </div>
          ) : null}

          {query.isError ? (
            <div
              role="alert"
              className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-900"
            >
              {getErrorMessage(query.error)}
            </div>
          ) : null}

          {query.data ? <DetectionResults result={query.data} localPreviewUrl={null} /> : null}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
