import { keepPreviousData, useQuery } from "@tanstack/react-query";

import { getDetectionJob, listDetectionJobs, type DetectionJobFilters } from "../../../api/jobs";

export function useDetectionJobs(filters: DetectionJobFilters) {
  return useQuery({
    queryKey: ["detection-jobs", filters],
    queryFn: () => listDetectionJobs(filters),
    placeholderData: keepPreviousData,
  });
}

export function useDetectionJob(publicId: string | null) {
  return useQuery({
    queryKey: ["detection-job", publicId],
    queryFn: () => getDetectionJob(publicId as string),
    enabled: publicId !== null,
  });
}
