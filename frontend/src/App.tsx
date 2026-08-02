import { Navigate, Route, Routes } from "react-router";

import { AppShell } from "./components/layout/app-shell";
import { AnalyticsPage } from "./pages/analytics-page";
import { DetectionWorkspacePage } from "./pages/detection-workspace-page";
import { HistoryPage } from "./pages/history-page";
import { NotFoundPage } from "./pages/not-found-page";
import { SystemStatusPage } from "./pages/system-status-page";
import { CameraDetectionPage } from "./pages/camera-detection-page";
import { VideoDetectionPage } from "./pages/video-detection-page";

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<Navigate to="/detect" replace />} />

        <Route path="/detect" element={<DetectionWorkspacePage />} />

        <Route path="/history" element={<HistoryPage />} />

        <Route path="/analytics" element={<AnalyticsPage />} />

        <Route path="/system" element={<SystemStatusPage />} />

        <Route path="/video" element={<VideoDetectionPage />} />

        <Route path="/camera" element={<CameraDetectionPage />} />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
