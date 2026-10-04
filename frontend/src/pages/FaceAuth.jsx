import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ScanFace,
  Loader2,
  AlertCircle,
  ArrowLeft,
  UserPlus,
} from "lucide-react";
import { useCamera } from "../lib/useCamera";
import { useAuth } from "../lib/AuthContext";
import { api } from "../lib/api";

export default function FaceAuth() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const {
    videoRef,
    active,
    error: camError,
    start,
    stop,
    captureFrame,
  } = useCamera();

  const [mode, setMode] = useState("verify"); // "verify" | "enroll"
  const [username, setUsername] = useState("");
  const [status, setStatus] = useState("idle"); // idle | working | error | success
  const [message, setMessage] = useState("");

  useEffect(() => {
    start();
    return () => stop();
  }, [start, stop]);

  const handleVerify = async () => {
    const frame = captureFrame();
    if (!frame) {
      setMessage("Camera isn't ready yet.");
      setStatus("error");
      return;
    }
    setStatus("working");
    setMessage("Scanning face...");
    try {
      const user = await api.verify(frame);
      setStatus("success");
      setMessage(`Welcome back, ${user.username}!`);
      login(user);
      setTimeout(() => navigate("/dashboard"), 600);
    } catch (err) {
      setStatus("error");
      setMessage(
        err.status === 401
          ? err.message
          : `Verification failed: ${err.message}`,
      );
    }
  };

  const handleEnroll = async () => {
    const trimmed = username.trim();
    if (trimmed.length < 2) {
      setMessage("Enter a username with at least 2 characters.");
      setStatus("error");
      return;
    }
    const frame = captureFrame();
    if (!frame) {
      setMessage("Camera isn't ready yet.");
      setStatus("error");
      return;
    }
    setStatus("working");
    setMessage("Capturing your face...");
    try {
      const user = await api.enroll(trimmed, frame);
      setStatus("success");
      setMessage(`Enrolled! Welcome, ${user.username}.`);
      login(user);
      setTimeout(() => navigate("/dashboard"), 600);
    } catch (err) {
      setStatus("error");
      setMessage(`Enrollment failed: ${err.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-bg text-text flex flex-col items-center justify-center px-4 py-10">
      <button
        onClick={() => navigate("/")}
        className="absolute top-6 left-6 flex items-center gap-1 text-sm text-text-dim hover:text-text transition-colors"
      >
        <ArrowLeft size={16} /> Back
      </button>

      <div className="w-full max-w-md">
        <div className="text-center mb-6">
          <ScanFace className="mx-auto text-accent mb-3" size={32} />
          <h1 className="text-2xl font-semibold">Face Authentication</h1>
          <p className="text-text-dim text-sm mt-1">
            {mode === "verify"
              ? "Look at the camera to sign in."
              : "First time here? Enroll your face to create an account."}
          </p>
        </div>

        <div className="relative rounded-lg overflow-hidden border border-border bg-surface aspect-4/3">
          <video
            ref={videoRef}
            className="w-full h-full object-cover -scale-x-100"
            muted
            playsInline
          />
          {!active && (
            <div className="absolute inset-0 flex items-center justify-center text-text-dim text-sm">
              {camError ? camError : "Starting camera..."}
            </div>
          )}
        </div>

        {mode === "enroll" && (
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Choose a username, e.g. arnab_1028"
            className="mt-4 w-full bg-surface border border-border rounded-md px-4 py-2.5 text-sm outline-none focus:border-accent/60 transition-colors"
          />
        )}

        {message && (
          <div
            className={`mt-4 flex items-center gap-2 text-sm px-3 py-2 rounded-md border ${
              status === "error"
                ? "border-danger/40 text-danger"
                : "border-accent/40 text-accent"
            }`}
          >
            {status === "working" ? (
              <Loader2 size={15} className="animate-spin" />
            ) : (
              <AlertCircle size={15} />
            )}
            {message}
          </div>
        )}

        <button
          onClick={mode === "verify" ? handleVerify : handleEnroll}
          disabled={status === "working" || !active}
          className="mt-5 w-full bg-accent text-bg font-medium py-2.5 rounded-md hover:brightness-110 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          {status === "working" ? (
            <Loader2 size={16} className="animate-spin" />
          ) : mode === "verify" ? (
            <ScanFace size={16} />
          ) : (
            <UserPlus size={16} />
          )}
          {mode === "verify" ? "Verify & Sign In" : "Enroll Face"}
        </button>

        <button
          onClick={() => {
            setMode(mode === "verify" ? "enroll" : "verify");
            setMessage("");
            setStatus("idle");
          }}
          className="mt-3 w-full text-center text-xs text-text-dim hover:text-text transition-colors"
        >
          {mode === "verify"
            ? "New here? Enroll your face instead"
            : "Already enrolled? Sign in instead"}
        </button>
      </div>
    </div>
  );
}
