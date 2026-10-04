import { useEffect, useRef } from "react";

const ACCENT = "#4ade80";
const KEY_JOINTS = new Set([11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]);

export default function PoseOverlay({ landmarks, connections, width, height }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, width, height);

    if (!landmarks || landmarks.length === 0) return;

    ctx.strokeStyle = ACCENT;
    ctx.lineWidth = 2;
    (connections || []).forEach(([s, e]) => {
      const p1 = landmarks[s];
      const p2 = landmarks[e];
      if (!p1 || !p2) return;
      if (p1.visibility > 0.65 && p2.visibility > 0.65) {
        ctx.beginPath();
        ctx.moveTo(p1.x * width, p1.y * height);
        ctx.lineTo(p2.x * width, p2.y * height);
        ctx.stroke();
      }
    });

    landmarks.forEach((lm, i) => {
      if (lm.visibility <= 0.65) return;
      const cx = lm.x * width;
      const cy = lm.y * height;
      if (KEY_JOINTS.has(i)) {
        ctx.beginPath();
        ctx.arc(cx, cy, 5, 0, Math.PI * 2);
        ctx.fillStyle = "white";
        ctx.fill();
        ctx.lineWidth = 1;
        ctx.strokeStyle = ACCENT;
        ctx.stroke();
      } else {
        ctx.beginPath();
        ctx.arc(cx, cy, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = "#c8c8c8";
        ctx.fill();
      }
    });
  }, [landmarks, connections, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="absolute inset-0 h-full w-full pointer-events-none"
    />
  );
}
