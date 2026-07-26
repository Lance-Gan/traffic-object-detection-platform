import { useMutation } from "@tanstack/react-query";
import { useState } from "react";

import { detectImage, type DetectImageInput } from "../../../api/detections";

type MutationInput = Omit<DetectImageInput, "onUploadProgress">;

export function useDetectImage() {
  const [uploadProgress, setUploadProgress] = useState(0);

  const mutation = useMutation({
    mutationFn: (input: MutationInput) =>
      detectImage({
        ...input,
        onUploadProgress: setUploadProgress,
      }),

    onMutate: () => {
      setUploadProgress(0);
    },
  });

  const reset = () => {
    mutation.reset();
    setUploadProgress(0);
  };

  return {
    mutation,
    uploadProgress,
    reset,
  };
}
