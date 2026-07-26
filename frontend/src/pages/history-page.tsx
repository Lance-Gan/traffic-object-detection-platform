import {
  ChevronLeft,
  ChevronRight,
  Eye,
  Filter,
  LoaderCircle,
  RotateCcw,
  Search,
} from "lucide-react";
import { useState, type FormEvent } from "react";

import { type DetectionJobFilters } from "../api/jobs";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader } from "../components/ui/card";
import {
  type DetectionJobStatus,
  type DetectionSourceType,
} from "../features/detections/detection-schema";
import { JobDetailDialog } from "../features/history/components/job-detail-dialog";
import { StatusBadge } from "../features/history/components/status-badge";
import { useDetectionJobs } from "../features/history/hooks/use-detection-jobs";
import { formatDuration, formatMelbourneDate } from "../lib/format";
import { getErrorMessage } from "../lib/http-error";

interface DraftFilters {
  search: string;
  status: "" | DetectionJobStatus;
  sourceType: "" | DetectionSourceType;
  dateFrom: string;
  dateTo: string;
}

const initialDraftFilters: DraftFilters = {
  search: "",
  status: "",
  sourceType: "",
  dateFrom: "",
  dateTo: "",
};

function startOfLocalDay(value: string): string | undefined {
  if (!value) {
    return undefined;
  }

  return new Date(`${value}T00:00:00`).toISOString();
}

function endOfLocalDay(value: string): string | undefined {
  if (!value) {
    return undefined;
  }

  return new Date(`${value}T23:59:59.999`).toISOString();
}

export function HistoryPage() {
  const [draftFilters, setDraftFilters] = useState<DraftFilters>(initialDraftFilters);

  const [filters, setFilters] = useState<DetectionJobFilters>({
    page: 1,
    pageSize: 10,
  });

  const [selectedPublicId, setSelectedPublicId] = useState<string | null>(null);

  const query = useDetectionJobs(filters);

  const applyFilters = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setFilters({
      page: 1,
      pageSize: filters.pageSize,

      search: draftFilters.search.trim() || undefined,

      status: draftFilters.status || undefined,

      sourceType: draftFilters.sourceType || undefined,

      createdFrom: startOfLocalDay(draftFilters.dateFrom),

      createdTo: endOfLocalDay(draftFilters.dateTo),
    });
  };

  const resetFilters = () => {
    setDraftFilters(initialDraftFilters);

    setFilters({
      page: 1,
      pageSize: 10,
    });
  };

  const changePage = (nextPage: number) => {
    setFilters((currentFilters) => ({
      ...currentFilters,
      page: nextPage,
    }));
  };

  return (
    <div className="space-y-6">
      <header>
        <p className="text-sm font-semibold text-blue-700">Job management</p>

        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">Detection history</h1>

        <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600 sm:text-base">
          Search, filter, and review previously completed detection jobs.
        </p>
      </header>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <Filter aria-hidden="true" className="size-5 text-blue-600" />

            <div>
              <h2 className="font-bold text-slate-950">Filters</h2>

              <p className="mt-1 text-sm text-slate-500">
                Date inputs use your browser&apos;s local timezone and are sent to the API as UTC.
              </p>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          <form onSubmit={applyFilters} className="grid gap-4 lg:grid-cols-6">
            <label className="lg:col-span-2">
              <span className="text-sm font-semibold text-slate-700">Search</span>

              <div className="relative mt-2">
                <Search
                  aria-hidden="true"
                  className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-slate-400"
                />

                <input
                  value={draftFilters.search}
                  onChange={(event) => {
                    setDraftFilters((current) => ({
                      ...current,
                      search: event.target.value,
                    }));
                  }}
                  placeholder="Filename or public ID"
                  className="min-h-11 w-full rounded-lg border border-slate-300 bg-white py-2 pr-3 pl-10 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />
              </div>
            </label>

            <label>
              <span className="text-sm font-semibold text-slate-700">Status</span>

              <select
                value={draftFilters.status}
                onChange={(event) => {
                  const status = event.target.value as DraftFilters["status"];

                  setDraftFilters((current) => ({
                    ...current,
                    status,
                  }));
                }}
                className="mt-2 min-h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm outline-none focus:border-blue-500"
              >
                <option value="">All statuses</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
                <option value="processing">Processing</option>
                <option value="pending">Pending</option>
              </select>
            </label>

            <label>
              <span className="text-sm font-semibold text-slate-700">Source</span>

              <select
                value={draftFilters.sourceType}
                onChange={(event) => {
                  const sourceType = event.target.value as DraftFilters["sourceType"];

                  setDraftFilters((current) => ({
                    ...current,
                    sourceType,
                  }));
                }}
                className="mt-2 min-h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm outline-none focus:border-blue-500"
              >
                <option value="">All sources</option>
                <option value="image">Image</option>
                <option value="video">Video</option>
                <option value="camera">Camera</option>
              </select>
            </label>

            <label>
              <span className="text-sm font-semibold text-slate-700">From date</span>

              <input
                type="date"
                value={draftFilters.dateFrom}
                onChange={(event) => {
                  setDraftFilters((current) => ({
                    ...current,
                    dateFrom: event.target.value,
                  }));
                }}
                className="mt-2 min-h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm outline-none focus:border-blue-500"
              />
            </label>

            <label>
              <span className="text-sm font-semibold text-slate-700">To date</span>

              <input
                type="date"
                value={draftFilters.dateTo}
                onChange={(event) => {
                  setDraftFilters((current) => ({
                    ...current,
                    dateTo: event.target.value,
                  }));
                }}
                className="mt-2 min-h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm outline-none focus:border-blue-500"
              />
            </label>

            <div className="flex flex-wrap gap-3 lg:col-span-6">
              <Button type="submit" icon={Search}>
                Apply filters
              </Button>

              <Button type="button" variant="secondary" icon={RotateCcw} onClick={resetFilters}>
                Reset
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <h2 className="font-bold text-slate-950">Detection jobs</h2>

              <p className="mt-1 text-sm text-slate-500">
                {query.data ? `${query.data.total} matching jobs` : "Loading detection jobs"}
              </p>
            </div>

            {query.isFetching ? (
              <LoaderCircle
                aria-label="Refreshing detection jobs"
                className="size-5 animate-spin text-blue-600"
              />
            ) : null}
          </div>
        </CardHeader>

        {query.isError ? (
          <CardContent>
            <div
              role="alert"
              className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-900"
            >
              {getErrorMessage(query.error)}
            </div>
          </CardContent>
        ) : null}

        {query.isPending ? (
          <CardContent className="flex min-h-64 items-center justify-center">
            <LoaderCircle className="size-8 animate-spin text-blue-600" />
          </CardContent>
        ) : null}

        {query.data ? (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200 text-left">
                <thead className="bg-slate-50">
                  <tr>
                    {["File", "Status", "Source", "Objects", "Duration", "Created", "Action"].map(
                      (heading) => (
                        <th
                          key={heading}
                          className="px-5 py-3 text-xs font-bold tracking-wide whitespace-nowrap text-slate-500 uppercase"
                        >
                          {heading}
                        </th>
                      ),
                    )}
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-100 bg-white">
                  {query.data.items.map((job) => (
                    <tr key={job.public_id}>
                      <td className="max-w-xs px-5 py-4">
                        <p className="truncate text-sm font-semibold text-slate-900">
                          {job.original_filename}
                        </p>

                        <p className="mt-1 truncate font-mono text-xs text-slate-500">
                          {job.public_id}
                        </p>
                      </td>

                      <td className="px-5 py-4">
                        <StatusBadge status={job.status} />
                      </td>

                      <td className="px-5 py-4 text-sm whitespace-nowrap text-slate-700 capitalize">
                        {job.source_type}
                      </td>

                      <td className="px-5 py-4 text-sm font-semibold whitespace-nowrap text-slate-900">
                        {job.detected_object_count}
                      </td>

                      <td className="px-5 py-4 text-sm whitespace-nowrap text-slate-700">
                        {formatDuration(job.duration_ms)}
                      </td>

                      <td className="px-5 py-4 text-sm whitespace-nowrap text-slate-700">
                        {formatMelbourneDate(job.created_at)}
                      </td>

                      <td className="px-5 py-4">
                        <button
                          type="button"
                          onClick={() => {
                            setSelectedPublicId(job.public_id);
                          }}
                          className="inline-flex min-h-10 items-center gap-2 rounded-lg px-3 text-sm font-semibold text-blue-700 hover:bg-blue-50"
                        >
                          <Eye aria-hidden="true" className="size-4" />
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {query.data.items.length === 0 ? (
                <div className="p-10 text-center text-sm text-slate-500">
                  No detection jobs match the selected filters.
                </div>
              ) : null}
            </div>

            <div className="flex flex-wrap items-center justify-between gap-4 border-t border-slate-200 px-5 py-4">
              <p className="text-sm text-slate-600">
                Page {query.data.page}
                {query.data.total_pages > 0 ? ` of ${query.data.total_pages}` : ""}
              </p>

              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  icon={ChevronLeft}
                  disabled={!query.data.has_previous}
                  onClick={() => {
                    changePage(query.data.page - 1);
                  }}
                >
                  Previous
                </Button>

                <Button
                  variant="secondary"
                  icon={ChevronRight}
                  disabled={!query.data.has_next}
                  onClick={() => {
                    changePage(query.data.page + 1);
                  }}
                >
                  Next
                </Button>
              </div>
            </div>
          </>
        ) : null}
      </Card>

      <JobDetailDialog
        publicId={selectedPublicId}
        onOpenChange={(open) => {
          if (!open) {
            setSelectedPublicId(null);
          }
        }}
      />
    </div>
  );
}
