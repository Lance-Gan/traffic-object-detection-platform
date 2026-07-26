import type { LucideIcon } from "lucide-react";

import { Card, CardContent } from "../components/ui/card";

interface PlaceholderPageProps {
  title: string;
  description: string;
  icon: LucideIcon;
  plannedStage: string;
}

export function PlaceholderPage({
  title,
  description,
  icon: Icon,
  plannedStage,
}: PlaceholderPageProps) {
  return (
    <div className="space-y-6">
      <header>
        <p className="text-sm font-semibold text-blue-700">{plannedStage}</p>

        <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">{title}</h1>

        <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-600 sm:text-base">
          {description}
        </p>
      </header>

      <Card>
        <CardContent className="flex min-h-80 flex-col items-center justify-center text-center">
          <span className="flex size-16 items-center justify-center rounded-2xl bg-blue-100 text-blue-700">
            <Icon aria-hidden="true" className="size-8" />
          </span>

          <h2 className="mt-5 text-lg font-bold text-slate-950">Page foundation ready</h2>

          <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">
            Routing and application layout are complete. Business functionality will be added in{" "}
            {plannedStage.toLowerCase()}.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
