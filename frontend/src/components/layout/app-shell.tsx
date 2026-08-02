import { Activity, BarChart3, Camera, Clock3, ScanSearch, Film } from "lucide-react";
import { NavLink, Outlet } from "react-router";

import { cn } from "../../lib/cn";

const navigationItems = [
  {
    label: "Image Detection",
    to: "/detect",
    icon: ScanSearch,
  },
  {
    label: "Video Detection",
    to: "/video",
    icon: Film,
  },
  {
    label: "Live Camera",
    to: "/camera",
    icon: Camera,
  },
  {
    label: "History",
    to: "/history",
    icon: Clock3,
  },
  {
    label: "Analytics",
    to: "/analytics",
    icon: BarChart3,
  },
  {
    label: "System",
    to: "/system",
    icon: Activity,
  },
];

export function AppShell() {
  return (
    <div className="min-h-screen bg-slate-50">
      <aside className="border-b border-slate-200 bg-slate-950 text-white lg:fixed lg:inset-y-0 lg:left-0 lg:w-72 lg:border-r lg:border-b-0 lg:border-slate-800">
        <div className="flex h-full flex-col">
          <div className="flex items-center gap-3 px-5 py-5 lg:px-6 lg:py-7">
            <span className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-blue-600">
              <ScanSearch aria-hidden="true" className="size-6" />
            </span>

            <div className="min-w-0">
              <p className="truncate text-sm font-bold">Traffic Detection</p>

              <p className="truncate text-xs text-slate-400">Object analytics platform</p>
            </div>
          </div>

          <nav
            aria-label="Primary navigation"
            className="flex gap-2 overflow-x-auto px-4 pb-4 lg:flex-col lg:overflow-visible lg:px-4 lg:pb-0"
          >
            {navigationItems.map(({ label, to, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  cn(
                    "flex min-h-11 shrink-0 items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition",
                    isActive
                      ? "bg-blue-600 text-white"
                      : "text-slate-300 hover:bg-slate-800 hover:text-white",
                  )
                }
              >
                <Icon aria-hidden="true" className="size-5" />

                {label}
              </NavLink>
            ))}
          </nav>

          <div className="mt-auto hidden border-t border-slate-800 px-6 py-5 lg:block">
            <p className="text-xs font-semibold text-slate-400">Local development</p>

            <p className="mt-1 text-xs text-slate-500">FastAPI + YOLO + MySQL</p>
          </div>
        </div>
      </aside>

      <main className="lg:pl-72">
        <div className="mx-auto max-w-[1600px] px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
