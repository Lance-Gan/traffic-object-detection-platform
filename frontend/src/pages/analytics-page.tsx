import {
  Activity,
  Box,
  CheckCircle2,
  Clock3,
  LoaderCircle,
  Percent,
  ScanSearch,
  XCircle,
} from "lucide-react";
import { useState } from "react";

import { Card, CardContent, CardHeader } from "../components/ui/card";

import {
  ClassDistributionChart,
  DailyTrendChart,
  SourceDistributionChart,
} from "../features/analytics/components/analytics-charts";

import { useDashboardStatistics } from "../features/analytics/hooks/use-dashboard-statistics";

import { formatConfidence, formatDuration } from "../lib/format";

import { getErrorMessage } from "../lib/http-error";

interface MetricCardProps {
  label: string;
  value: string;
  icon: typeof Activity;
}

function MetricCard({ label, value, icon: Icon }: MetricCardProps) {
  return (
    <Card>
      <CardContent>
        <div className="flex items-center gap-3">
          <span className="flex size-11 items-center justify-center rounded-xl bg-blue-100 text-blue-700">
            <Icon aria-hidden="true" className="size-5" />
          </span>

          <div className="min-w-0">
            <p className="text-xs font-bold tracking-wide text-slate-500 uppercase">{label}</p>

            <p className="mt-1 truncate text-2xl font-bold text-slate-950">{value}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function AnalyticsPage() {
  const [days, setDays] = useState(30);

  const query = useDashboardStatistics(days);

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-blue-700">Business intelligence</p>

          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
            Detection analytics
          </h1>

          <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600 sm:text-base">
            Review detection activity, performance, confidence, and traffic-object distribution.
          </p>
        </div>

        <label>
          <span className="text-sm font-semibold text-slate-700">Reporting period</span>

          <select
            value={days}
            onChange={(event) => {
              setDays(Number(event.target.value));
            }}
            className="mt-2 min-h-11 rounded-lg border border-slate-300 bg-white px-3 text-sm outline-none focus:border-blue-500"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={365}>Last 365 days</option>
          </select>
        </label>
      </header>

      {query.isPending ? (
        <Card>
          <CardContent className="flex min-h-80 items-center justify-center">
            <LoaderCircle className="size-9 animate-spin text-blue-600" />
          </CardContent>
        </Card>
      ) : null}

      {query.isError ? (
        <Card>
          <CardContent>
            <div
              role="alert"
              className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-900"
            >
              {getErrorMessage(query.error)}
            </div>
          </CardContent>
        </Card>
      ) : null}

      {query.data ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <MetricCard
              label="Total jobs"
              value={String(query.data.metrics.total_jobs)}
              icon={Activity}
            />

            <MetricCard
              label="Completed"
              value={String(query.data.metrics.completed_jobs)}
              icon={CheckCircle2}
            />

            <MetricCard
              label="Failed"
              value={String(query.data.metrics.failed_jobs)}
              icon={XCircle}
            />

            <MetricCard
              label="Success rate"
              value={`${query.data.metrics.success_rate.toFixed(1)}%`}
              icon={Percent}
            />

            <MetricCard
              label="Detected objects"
              value={String(query.data.metrics.total_detected_objects)}
              icon={Box}
            />

            <MetricCard
              label="Average confidence"
              value={
                query.data.metrics.average_confidence !== null
                  ? formatConfidence(query.data.metrics.average_confidence)
                  : "Not available"
              }
              icon={ScanSearch}
            />

            <MetricCard
              label="Average duration"
              value={formatDuration(
                query.data.metrics.average_duration_ms !== null
                  ? Math.round(query.data.metrics.average_duration_ms)
                  : null,
              )}
              icon={Clock3}
            />

            <MetricCard
              label="Processing now"
              value={String(query.data.metrics.processing_jobs)}
              icon={LoaderCircle}
            />
          </div>

          <div className="grid gap-6 xl:grid-cols-2">
            <Card>
              <CardHeader>
                <h2 className="text-lg font-bold text-slate-950">Daily activity</h2>

                <p className="mt-1 text-sm text-slate-500">
                  Job and object totals grouped by UTC date.
                </p>
              </CardHeader>

              <CardContent>
                <DailyTrendChart statistics={query.data} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <h2 className="text-lg font-bold text-slate-950">Object classes</h2>

                <p className="mt-1 text-sm text-slate-500">Total detected objects by class.</p>
              </CardHeader>

              <CardContent>
                <ClassDistributionChart statistics={query.data} />
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <h2 className="text-lg font-bold text-slate-950">Detection sources</h2>

              <p className="mt-1 text-sm text-slate-500">
                Image, video, and camera job distribution.
              </p>
            </CardHeader>

            <CardContent>
              <SourceDistributionChart statistics={query.data} />
            </CardContent>
          </Card>
        </>
      ) : null}
    </div>
  );
}
