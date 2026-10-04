import { useCallback, useEffect, useRef, useState } from "react";

export function useCamera() {
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  const startingRef = useRef(false);
  const generationRef = useRef(0);

  const [error, setError] = useState(null);
  const [active, setActive] = useState(false);

  const start = useCallback(async () => {
    // Already active or a start() is already in flight — don't kick off a
    // second getUserMedia/play() race against ourselves.
    if (startingRef.current || streamRef.current) return;

    startingRef.current = true;
    setError(null);
    const myGeneration = ++generationRef.current;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: "user" },
        audio: false,
      });

      if (myGeneration !== generationRef.current) {
        stream.getTracks().forEach((t) => t.stop());
        return;
      }

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        try {
          await videoRef.current.play();
        } catch (playErr) {
          const supersededWhilePlaying = myGeneration !== generationRef.current;
          if (playErr.name === "AbortError" || supersededWhilePlaying) {
            if (supersededWhilePlaying) return;
          } else {
            throw playErr;
          }
        }
      }

      if (myGeneration === generationRef.current) {
        setActive(true);
      }
    } catch (err) {
      if (myGeneration === generationRef.current) {
        setError(err.message || "Camera access was denied.");
        setActive(false);
      }
    } finally {
      if (myGeneration === generationRef.current) {
        startingRef.current = false;
      }
    }
  }, []);

  const stop = useCallback(() => {
    generationRef.current += 1; 
    startingRef.current = false;

    const video = videoRef.current;
    if (video) {
      video.pause();
      video.srcObject = null;
    }

    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
    setActive(false);
  }, []);

  useEffect(() => () => stop(), [stop]);

  const captureFrame = useCallback((quality = 0.7) => {
    const video = videoRef.current;
    if (!video || video.readyState < 2) return null;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1); // mirror, matches the flip in the original video processor
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg", quality);
  }, []);

  return { videoRef, active, error, start, stop, captureFrame };
}