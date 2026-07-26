import { ArrowLeft } from "lucide-react";
import { Link } from "react-router";

export function NotFoundPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-6">
      <div className="max-w-lg text-center">
        <p className="text-sm font-bold tracking-[0.2em] text-blue-700 uppercase">404</p>

        <h1 className="mt-4 text-4xl font-bold tracking-tight text-slate-950">Page not found</h1>

        <p className="mt-4 text-base leading-7 text-slate-600">
          The requested page does not exist or has been moved.
        </p>

        <Link
          to="/detect"
          className="mt-7 inline-flex min-h-11 items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
        >
          <ArrowLeft aria-hidden="true" className="size-4" />
          Return to detection
        </Link>
      </div>
    </main>
  );
}
