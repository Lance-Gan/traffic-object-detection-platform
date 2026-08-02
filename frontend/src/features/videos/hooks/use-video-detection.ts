import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getDetectionJob } from "../../../api/jobs";
import { detectVideo, type DetectVideoInput } from "../../../api/videos";
import { getErrorMessage } from "../../../lib/http-error";

export function useVideoDetection() {
  const queryClient = useQueryClient();

  const [publicId, setPublicId] = useState<string | null>(null);

  const [uploadProgress, setUploadProgress] = useState(0);

  const mutation = useMutation({
    mutationFn: (input: Omit<DetectVideoInput, "onUploadProgress">) => {
      setUploadProgress(0);

      return detectVideo({
        ...input,

        onUploadProgress: (percentage) => {
          setUploadProgress(percentage);
        },
      });
    },

    onSuccess: (job) => {
      setUploadProgress(100);
      setPublicId(job.public_id);
    },
  });

  const jobQuery = useQuery({
    queryKey: ["detection-job", publicId],

    queryFn: () => {
      if (!publicId) {
        throw new Error("The video job ID is missing");
      }

      return getDetectionJob(publicId);
    },

    enabled: publicId !== null,

    refetchInterval: (query) => {
      const job = query.state.data;

      if (!job) {
        return 1500;
      }

      if (job.status === "pending" || job.status === "processing") {
        return 1500;
      }

      return false;
    },
  });

  const job = jobQuery.data ?? mutation.data ?? null;

  useEffect(() => {
    if (job?.status !== "completed" && job?.status !== "failed") {
      return;
    }

    void queryClient.invalidateQueries({
      queryKey: ["detection-jobs"],
    });

    void queryClient.invalidateQueries({
      queryKey: ["dashboard-statistics"],
    });
  }, [job?.status, queryClient]);

  const reset = () => {
    if (publicId) {
      queryClient.removeQueries({
        queryKey: ["detection-job", publicId],
      });
    }

    mutation.reset();

    setPublicId(null);
    setUploadProgress(0);
  };

  const error = mutation.error ?? jobQuery.error;

  const isProcessing =
    mutation.isPending || job?.status === "pending" || job?.status === "processing";

  return {
    job,
    uploadProgress,
    isProcessing,

    errorMessage: error ? getErrorMessage(error) : null,

    submit: mutation.mutate,
    reset,
  };
}
