import { Activity, Cpu, Database, FileImage, LoaderCircle, ScanSearch, Server } from "lucide-react";

import { Card, CardContent, CardHeader } from "../components/ui/card";

import { useSystemStatus } from "../features/system/hooks/use-system-status";
import { formatBytes } from "../lib/format";
import { getErrorMessage } from "../lib/http-error";

interface StatusItemProps {
  label: string;
  value: string;
  icon: typeof Activity;
}

function StatusItem({ label, value, icon: Icon }: StatusItemProps) {
  return (
    <div className="flex items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4">
      <span className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-blue-100 text-blue-700">
        <Icon aria-hidden="true" className="size-5" />
      </span>

      <div className="min-w-0">
        <p className="text-xs font-bold tracking-wide text-slate-500 uppercase">{label}</p>

        <p className="mt-1 text-sm font-semibold wrap-break-word text-slate-950">{value}</p>
      </div>
    </div>
  );
}

export function SystemStatusPage() {
  const query = useSystemStatus();

  return (
    <div className="space-y-6">
      <header>
        <p className="text-sm font-semibold text-blue-700">Infrastructure</p>

        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">System status</h1>

        <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600 sm:text-base">
          Monitor the API runtime, database connection, model configuration, and upload limits.
        </p>
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
          <div className="grid gap-4 sm:grid-cols-2">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <h2 className="text-lg font-bold text-slate-950">API service</h2>

                    <p className="mt-1 text-sm text-slate-500">FastAPI runtime status</p>
                  </div>

                  <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold tracking-wide text-emerald-700 uppercase">
                    Online
                  </span>
                </div>
              </CardHeader>

              <CardContent className="grid gap-4 sm:grid-cols-2">
                <StatusItem label="Service" value={query.data.system.service} icon={Server} />

                <StatusItem label="Version" value={query.data.system.version} icon={Activity} />

                <StatusItem
                  label="Environment"
                  value={query.data.system.environment}
                  icon={Activity}
                />

                <StatusItem label="Python" value={query.data.system.python_version} icon={Cpu} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <h2 className="text-lg font-bold text-slate-950">Database</h2>

                    <p className="mt-1 text-sm text-slate-500">MySQL connection status</p>
                  </div>

                  <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-bold tracking-wide text-emerald-700 uppercase">
                    Connected
                  </span>
                </div>
              </CardHeader>

              <CardContent>
                <StatusItem
                  label="Selected database"
                  value={query.data.database.database}
                  icon={Database}
                />
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <h2 className="text-lg font-bold text-slate-950">Detection runtime</h2>
            </CardHeader>

            <CardContent className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <StatusItem label="Model" value={query.data.system.model_name} icon={ScanSearch} />

              <StatusItem
                label="Configured device"
                value={query.data.system.configured_device.toUpperCase()}
                icon={Cpu}
              />

              <StatusItem
                label="MPS available"
                value={query.data.system.mps_available ? "Yes" : "No"}
                icon={Cpu}
              />

              <StatusItem
                label="Image limit"
                value={formatBytes(query.data.system.max_image_upload_bytes)}
                icon={FileImage}
              />
            </CardContent>
          </Card>
        </>
      ) : null}
    </div>
  );
}
