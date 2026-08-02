import { useCallback, useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { createCameraSession } from "../../../api/camera";
import { getErrorMessage } from "../../../lib/http-error";
import { resolveWebSocketUrl } from "../../../lib/websocket-url";
import {
  cameraServerMessageSchema,
  type CameraCompletedMessage,
  type CameraFrameMessage,
  type CameraSession,
} from "../camera-schema";

interface ElementReference<T> {
  current: T | null;
}

interface UseCameraDetectionOptions {
  videoRef: ElementReference<HTMLVideoElement>;
  captureCanvasRef: ElementReference<HTMLCanvasElement>;
  overlayCanvasRef: ElementReference<HTMLCanvasElement>;
}

export type CameraFacingMode = "user" | "environment";

export type CameraClientStatus =
  | "idle"
  | "requesting_permission"
  | "creating_session"
  | "connecting"
  | "loading_model"
  | "streaming"
  | "stopping"
  | "completed"
  | "error";

interface StartCameraInput {
  confidenceThreshold: number;
  facingMode: CameraFacingMode;
}

function canvasToJpegBlob(canvas: HTMLCanvasElement, quality: number): Promise<Blob> {
  return new Promise((resolve, reject) => {
    canvas.toBlob(
      (blob) => {
        if (blob) {
          resolve(blob);
          return;
        }

        reject(new Error("The camera frame could not be encoded"));
      },
      "image/jpeg",
      quality,
    );
  });
}

function getCameraPermissionError(error: unknown): string {
  if (!(error instanceof DOMException)) {
    return getErrorMessage(error);
  }

  switch (error.name) {
    case "NotAllowedError":
      return (
        "Camera permission was denied. " +
        "Allow camera access in the browser " +
        "and macOS Privacy & Security settings."
      );

    case "NotFoundError":
      return "No camera was found on this device.";

    case "NotReadableError":
      return "The camera is already being used by another application.";

    case "OverconstrainedError":
      return "The selected camera cannot provide the requested video settings.";

    default:
      return error.message || "The camera could not be opened.";
  }
}

function getClassColour(className: string): string {
  let hash = 0;

  for (let index = 0; index < className.length; index += 1) {
    hash = className.charCodeAt(index) + ((hash << 5) - hash);
  }

  const hue = Math.abs(hash) % 360;

  return `hsl(${hue} 78% 48%)`;
}

function drawDetections(canvas: HTMLCanvasElement, message: CameraFrameMessage): void {
  canvas.width = message.frame_width;
  canvas.height = message.frame_height;

  const context = canvas.getContext("2d");

  if (!context) {
    return;
  }

  context.clearRect(0, 0, canvas.width, canvas.height);

  context.lineWidth = 3;
  context.font = "600 14px ui-sans-serif, system-ui";
  context.textBaseline = "top";

  for (const detectedObject of message.objects) {
    const { x1, y1, x2, y2 } = detectedObject.bounding_box;

    const width = Math.max(0, x2 - x1);
    const height = Math.max(0, y2 - y1);

    const colour = getClassColour(detectedObject.class_name);

    context.strokeStyle = colour;
    context.strokeRect(x1, y1, width, height);

    const trackText = detectedObject.track_id !== null ? ` #${detectedObject.track_id}` : "";

    const label =
      `${detectedObject.class_name}` +
      `${trackText} ` +
      `${(detectedObject.confidence * 100).toFixed(0)}%`;

    const labelWidth = context.measureText(label).width + 12;
    const labelHeight = 24;
    const labelY = Math.max(0, y1 - labelHeight);

    context.fillStyle = colour;
    context.fillRect(x1, labelY, labelWidth, labelHeight);

    context.fillStyle = "#ffffff";
    context.fillText(label, x1 + 6, labelY + 4);
  }
}

function clearCanvas(canvas: HTMLCanvasElement | null): void {
  if (!canvas) {
    return;
  }

  const context = canvas.getContext("2d");

  context?.clearRect(0, 0, canvas.width, canvas.height);
}

export function useCameraDetection({
  videoRef,
  captureCanvasRef,
  overlayCanvasRef,
}: UseCameraDetectionOptions) {
  const queryClient = useQueryClient();

  const [status, setStatus] = useState<CameraClientStatus>("idle");

  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [session, setSession] = useState<CameraSession | null>(null);

  const [latestFrame, setLatestFrame] = useState<CameraFrameMessage | null>(null);

  const [completedSession, setCompletedSession] = useState<CameraCompletedMessage | null>(null);

  const [frameAspectRatio, setFrameAspectRatio] = useState(16 / 9);

  const [sentFrameCount, setSentFrameCount] = useState(0);

  const mediaStreamRef = useRef<MediaStream | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const sessionRef = useRef<CameraSession | null>(null);
  const nextFrameTimerRef = useRef<number | null>(null);

  const streamingRef = useRef(false);
  const endedNormallyRef = useRef(false);

  const statusRef = useRef<CameraClientStatus>("idle");

  const updateStatus = useCallback((nextStatus: CameraClientStatus) => {
    statusRef.current = nextStatus;
    setStatus(nextStatus);
  }, []);

  const clearNextFrameTimer = useCallback(() => {
    if (nextFrameTimerRef.current !== null) {
      window.clearTimeout(nextFrameTimerRef.current);
      nextFrameTimerRef.current = null;
    }
  }, []);

  const stopMediaStream = useCallback(() => {
    const stream = mediaStreamRef.current;

    if (stream) {
      for (const track of stream.getTracks()) {
        track.stop();
      }
    }

    mediaStreamRef.current = null;

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
  }, [videoRef]);

  const cleanClientResources = useCallback(() => {
    clearNextFrameTimer();
    stopMediaStream();

    clearCanvas(overlayCanvasRef.current);
    clearCanvas(captureCanvasRef.current);
  }, [captureCanvasRef, clearNextFrameTimer, overlayCanvasRef, stopMediaStream]);

  const start = useCallback(
    async ({ confidenceThreshold, facingMode }: StartCameraInput): Promise<void> => {
      cleanClientResources();

      socketRef.current?.close(1000, "Starting a new session");

      socketRef.current = null;
      sessionRef.current = null;

      streamingRef.current = false;
      endedNormallyRef.current = false;

      setErrorMessage(null);
      setLatestFrame(null);
      setCompletedSession(null);
      setSentFrameCount(0);

      if (!navigator.mediaDevices) {
        setErrorMessage(
          "Camera access requires a secure " +
            "browser context. Use localhost " +
            "during development and HTTPS " +
            "when deployed.",
        );

        updateStatus("error");
        return;
      }

      try {
        updateStatus("requesting_permission");

        const mediaStream = await navigator.mediaDevices.getUserMedia({
          audio: false,

          video: {
            facingMode: {
              ideal: facingMode,
            },

            width: {
              ideal: 1280,
            },

            height: {
              ideal: 720,
            },
          },
        });

        mediaStreamRef.current = mediaStream;

        const video = videoRef.current;

        if (!video) {
          throw new Error("The camera video element is not available");
        }

        video.srcObject = mediaStream;

        await video.play();

        if (video.videoWidth > 0 && video.videoHeight > 0) {
          setFrameAspectRatio(video.videoWidth / video.videoHeight);
        }

        updateStatus("creating_session");

        const createdSession = await createCameraSession(confidenceThreshold);

        sessionRef.current = createdSession;
        setSession(createdSession);

        const socket = new WebSocket(resolveWebSocketUrl(createdSession.websocket_path));

        socket.binaryType = "arraybuffer";

        socketRef.current = socket;

        updateStatus("connecting");

        const scheduleNextFrame = (inferenceMilliseconds = 0): void => {
          clearNextFrameTimer();

          const interval = 1000 / createdSession.target_fps;

          const delay = Math.max(0, interval - inferenceMilliseconds);

          nextFrameTimerRef.current = window.setTimeout(() => {
            void sendFrame();
          }, delay);
        };

        async function sendFrame(): Promise<void> {
          if (!streamingRef.current) {
            return;
          }

          if (socket.readyState !== WebSocket.OPEN) {
            return;
          }

          const currentVideo = videoRef.current;
          const captureCanvas = captureCanvasRef.current;

          if (
            !currentVideo ||
            !captureCanvas ||
            currentVideo.videoWidth <= 0 ||
            currentVideo.videoHeight <= 0
          ) {
            scheduleNextFrame(0);
            return;
          }

          const scale = Math.min(1, createdSession.frame_width / currentVideo.videoWidth);

          const frameWidth = Math.max(1, Math.round(currentVideo.videoWidth * scale));

          const frameHeight = Math.max(1, Math.round(currentVideo.videoHeight * scale));

          captureCanvas.width = frameWidth;
          captureCanvas.height = frameHeight;

          const context = captureCanvas.getContext("2d", {
            alpha: false,
          });

          if (!context) {
            throw new Error("The capture canvas is not available");
          }

          context.drawImage(currentVideo, 0, 0, frameWidth, frameHeight);

          const frameBlob = await canvasToJpegBlob(captureCanvas, createdSession.jpeg_quality);

          if (frameBlob.size > createdSession.max_frame_bytes) {
            throw new Error("The encoded camera frame exceeds the server limit");
          }

          if (socket.bufferedAmount > createdSession.max_frame_bytes) {
            throw new Error("The camera connection cannot send frames fast enough");
          }

          socket.send(frameBlob);

          setSentFrameCount((currentValue) => currentValue + 1);
        }

        socket.addEventListener("message", (event) => {
          if (typeof event.data !== "string") {
            return;
          }

          let rawMessage: unknown;

          try {
            rawMessage = JSON.parse(event.data);
          } catch {
            setErrorMessage("The camera server returned an invalid message.");

            return;
          }

          const parsedMessage = cameraServerMessageSchema.safeParse(rawMessage);

          if (!parsedMessage.success) {
            setErrorMessage("The camera server response has an unexpected format.");

            return;
          }

          const message = parsedMessage.data;

          switch (message.type) {
            case "loading_model":
              updateStatus("loading_model");
              break;

            case "ready":
              streamingRef.current = true;

              updateStatus("streaming");

              void sendFrame();
              break;

            case "frame_result":
              setLatestFrame(message);

              if (overlayCanvasRef.current) {
                drawDetections(overlayCanvasRef.current, message);
              }

              scheduleNextFrame(message.inference_ms);
              break;

            case "session_completed":
              streamingRef.current = false;
              endedNormallyRef.current = true;

              setCompletedSession(message);
              updateStatus("completed");

              cleanClientResources();

              void queryClient.invalidateQueries();
              break;

            case "error":
              setErrorMessage(message.message);

              if (message.fatal) {
                streamingRef.current = false;

                updateStatus("error");
                cleanClientResources();
              }

              break;

            case "pong":
              break;
          }
        });

        socket.addEventListener("close", () => {
          streamingRef.current = false;
          cleanClientResources();

          if (!endedNormallyRef.current && statusRef.current !== "error") {
            setErrorMessage("The live camera connection closed unexpectedly.");

            updateStatus("error");
          }
        });

        socket.addEventListener("error", () => {
          setErrorMessage("The live camera WebSocket could not be connected.");

          streamingRef.current = false;

          updateStatus("error");
          cleanClientResources();
        });
      } catch (error) {
        setErrorMessage(getCameraPermissionError(error));

        updateStatus("error");
        cleanClientResources();
      }
    },
    [
      captureCanvasRef,
      cleanClientResources,
      clearNextFrameTimer,
      overlayCanvasRef,
      queryClient,
      updateStatus,
      videoRef,
    ],
  );

  const stop = useCallback(() => {
    streamingRef.current = false;
    clearNextFrameTimer();

    updateStatus("stopping");

    const socket = socketRef.current;

    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(
        JSON.stringify({
          type: "stop",
        }),
      );

      window.setTimeout(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.close(1000, "Client stop timeout");
        }
      }, 3000);

      return;
    }

    endedNormallyRef.current = true;

    cleanClientResources();
    updateStatus("completed");
  }, [cleanClientResources, clearNextFrameTimer, updateStatus]);

  useEffect(() => {
    const overlayCanvas = overlayCanvasRef.current;

    return () => {
      streamingRef.current = false;

      clearNextFrameTimer();

      socketRef.current?.close(1000, "Camera page unmounted");

      socketRef.current = null;

      stopMediaStream();

      clearCanvas(overlayCanvas);
    };
  }, [clearNextFrameTimer, overlayCanvasRef, stopMediaStream]);

  return {
    status,
    errorMessage,
    session,
    latestFrame,
    completedSession,
    frameAspectRatio,
    sentFrameCount,
    start,
    stop,
  };
}
