import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Dumbbell,
  LogOut,
  StopCircle,
  PlayCircle,
  AlertTriangle,
  CheckCircle2,
  Camera,
  CameraOff,
} from "lucide-react";
import { useAuth } from "../lib/AuthContext";
import { useCamera } from "../lib/useCamera";
import { api, fetchCachedCoachingAudio, fetchCoachingAudio } from "../lib/api";
import { EXERCISE_OPTIONS, BAD_FORM_CHECK } from "../lib/exerciseConfig";
import PoseOverlay from "../components/PoseOverlay";
import MetricsPanel from "../components/MetricsPanel";
import WorkoutHistory from "../components/WorkoutHistory";

const FRAME_INTERVAL_MS = 200;

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const {
    videoRef,
    active,
    error: camError,
    start,
    stop,
    captureFrame,
  } = useCamera();

  const [planExercise, setPlanExercise] = useState(EXERCISE_OPTIONS[0]);
  const [planSets, setPlanSets] = useState(3);
  const [planReps, setPlanReps] = useState(10);

  const [workoutStarted, setWorkoutStarted] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [metrics, setMetrics] = useState({});
  const [poseDetected, setPoseDetected] = useState(null);

  const [history, setHistory] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(true);

  const progressRef = useRef({
    reps: 0,
    repsPerSet: 0,
    targetSets: 0,
    setsCompleted: 0,
    currentSetReps: 0,
    lastSavedSets: 0,
    cycleStartedAt: 0,
  });
  const [progress, setProgress] = useState(progressRef.current);

  // ── Voice coaching ────────────────────────────────────────────────────
  const audioRef = useRef(null);
  const poseLostCooldownRef = useRef(0); // timestamp; avoids repeating every 200ms while out of frame
  const formCooldownRef = useRef(0); // same idea for form_correction, which checks every frame
  const voiceBusyRef = useRef(false); // avoids overlapping Groq calls piling up

  const playAudioUrl = (url) => {
    if (!audioRef.current) return;
    audioRef.current.pause();
    audioRef.current.src = url;
    audioRef.current.play().catch(() => {});
  };

  const playCachedCoachLine = useCallback(
    async (event) => {
      if (!user) return;
      try {
        const url = await fetchCachedCoachingAudio(user.username, event);
        playAudioUrl(url);
      } catch {
        /* non-fatal: voice is a nice-to-have, never block the workout on it */
      }
    },
    [user],
  );

  const playDynamicCoachLine = useCallback(async (event, exercise, metrics) => {
    if (voiceBusyRef.current) return; // a line is already being generated/played
    voiceBusyRef.current = true;
    try {
      const url = await fetchCoachingAudio(event, exercise, metrics);
      playAudioUrl(url);
    } catch {
      /* non-fatal: voice is a nice-to-have, never block the workout on it */
    } finally {
      voiceBusyRef.current = false;
    }
  }, []);

  useEffect(() => {
    if (!user) navigate("/auth");
  }, [user, navigate]);

  const loadHistory = useCallback(async () => {
    if (!user) return;
    setHistoryLoading(true);
    try {
      const { history: h } = await api.getHistory(user.id);
      setHistory(h);
    } catch {
      /* non-fatal */
    } finally {
      setHistoryLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  useEffect(() => () => stop(), [stop]);

  const handleOpenCamera = () => {
    start();
  };

  const handleCloseCamera = async () => {
    if (workoutStarted) {
      await handleEnd();
    }
    stop();
  };

  const handleStart = async () => {
    const { session_id } = await api.startSession(user.id);
    setSessionId(session_id);
    progressRef.current = {
      reps: 0,
      repsPerSet: planReps,
      targetSets: planSets,
      setsCompleted: 0,
      currentSetReps: 0,
      lastSavedSets: 0,
      cycleStartedAt: Date.now(),
    };
    setProgress(progressRef.current);
    setMetrics({});
    setPoseDetected(null);
    setWorkoutStarted(true);
  };

  const handleEnd = async () => {
    setWorkoutStarted(false);
    if (sessionId) await api.endSession(sessionId);
    setSessionId(null);
    loadHistory();
  };

  // ── Frame polling loop ──────────────────────────────────────────────────
  useEffect(() => {
    if (!workoutStarted || !sessionId || !active) return;

    const interval = setInterval(async () => {
      const frame = captureFrame();
      if (!frame) return;

      try {
        const result = await api.sendFrame(sessionId, planExercise, frame);
        setMetrics(result);
        setPoseDetected(result.pose_detected);

        const {
          landmarks: _landmarks,
          connections: _connections,
          ...coachMetrics
        } = result;

        if (result.pose_detected === false) {
          const now = Date.now();
          if (now - poseLostCooldownRef.current > 8000) {
            poseLostCooldownRef.current = now;
            playCachedCoachLine("pose_lost");
          }
        } else {
          const badForm = BAD_FORM_CHECK[planExercise];
          if (badForm && result[badForm.field] === badForm.badValue) {
            const now = Date.now();
            if (now - formCooldownRef.current > 10000) {
              formCooldownRef.current = now;
              playDynamicCoachLine(
                "form_correction",
                planExercise,
                coachMetrics,
              );
            }
          }
        }

        const reps = result.reps ?? progressRef.current.reps;
        const p = progressRef.current;
        p.reps = reps;

        if (p.repsPerSet > 0 && p.targetSets > 0) {
          p.setsCompleted = Math.floor(reps / p.repsPerSet);
          p.currentSetReps = reps % p.repsPerSet;

          if (p.setsCompleted > p.lastSavedSets) {
            const newlyCompleted = p.setsCompleted - p.lastSavedSets;
            const now = Date.now();
            const timeTaken = (now - p.cycleStartedAt) / 1000;

            api
              .saveExercise(
                user.id,
                planExercise,
                newlyCompleted * p.repsPerSet,
                newlyCompleted,
                timeTaken,
              )
              .then(loadHistory)
              .catch(() => {});

            playDynamicCoachLine(
              p.setsCompleted >= p.targetSets
                ? "workout_complete"
                : "set_complete",
              planExercise,
              coachMetrics,
            );

            p.cycleStartedAt = now;
            p.lastSavedSets = p.setsCompleted;
          }
        }

        setProgress({ ...p });
      } catch {
        /* transient frame errors are expected (e.g. no face in frame) */
      }
    }, FRAME_INTERVAL_MS);

    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    workoutStarted,
    sessionId,
    active,
    planExercise,
    playCachedCoachLine,
    playDynamicCoachLine,
  ]);

  const handleLogout = async () => {
    if (sessionId) await api.endSession(sessionId);
    logout();
    navigate("/");
  };

  if (!user) return null;

  const workoutComplete =
    progress.targetSets > 0 && progress.setsCompleted >= progress.targetSets;

  return (
    <div className="min-h-screen bg-bg text-text flex flex-col md:flex-row">
      <audio ref={audioRef} className="hidden" />
      {/* Sidebar */}
      <aside className="w-full md:w-72 border-b md:border-b-0 md:border-r border-border p-5 flex flex-col gap-5">
        <div className="flex items-center gap-2">
          <Dumbbell className="text-accent" size={20} />
          <span className="font-semibold tracking-tight">Kinetic</span>
        </div>

        {!workoutStarted ? (
          <div className="space-y-3">
            <h2 className="text-sm font-medium text-text-dim uppercase tracking-wide">
              Plan Your Workout
            </h2>
            <select
              value={planExercise}
              onChange={(e) => setPlanExercise(e.target.value)}
              className="w-full bg-surface border border-border rounded-md px-3 py-2 text-sm outline-none focus:border-accent/60"
            >
              {EXERCISE_OPTIONS.map((ex) => (
                <option key={ex} value={ex}>
                  {ex}
                </option>
              ))}
            </select>
            <div className="flex gap-2">
              <label className="flex-1 text-xs text-text-dim">
                Sets
                <input
                  type="number"
                  min={1}
                  max={50}
                  value={planSets}
                  onChange={(e) => setPlanSets(Number(e.target.value))}
                  className="mt-1 w-full bg-surface border border-border rounded-md px-3 py-2 text-sm outline-none focus:border-accent/60"
                />
              </label>
              <label className="flex-1 text-xs text-text-dim">
                Reps
                <input
                  type="number"
                  min={1}
                  max={100}
                  value={planReps}
                  onChange={(e) => setPlanReps(Number(e.target.value))}
                  className="mt-1 w-full bg-surface border border-border rounded-md px-3 py-2 text-sm outline-none focus:border-accent/60"
                />
              </label>
            </div>
            <button
              onClick={handleStart}
              disabled={!active}
              className="w-full flex items-center justify-center gap-2 bg-accent text-bg font-medium py-2.5 rounded-md hover:brightness-110 transition disabled:opacity-50"
            >
              <PlayCircle size={16} />
              Start Workout Session
            </button>
            {!active && (
              <p className="text-xs text-text-dim flex items-center gap-1">
                <AlertTriangle size={13} /> Open the camera first to start a
                session
              </p>
            )}
          </div>
        ) : (
          <div className="space-y-3">
            <div className="text-sm px-3 py-2 rounded-md border border-accent/30 bg-accent/5 text-accent">
              <span className="font-medium">{planExercise}</span> — {planSets}{" "}
              Sets / {planReps} Reps
            </div>
            <button
              onClick={handleEnd}
              className="w-full flex items-center justify-center gap-2 border border-border py-2.5 rounded-md hover:border-danger/50 hover:text-danger transition"
            >
              <StopCircle size={16} />
              End Workout Session
            </button>
          </div>
        )}

        <div className="mt-auto pt-4 border-t border-border">
          <p className="text-sm text-text-dim mb-3">
            Logged in as{" "}
            <span className="text-text font-medium">{user.username}</span>
          </p>
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center gap-2 text-sm text-text-dim hover:text-text border border-border py-2 rounded-md transition"
          >
            <LogOut size={15} />
            Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 p-5 md:p-8 grid lg:grid-cols-[1fr_320px] gap-6">
        <div className="space-y-6">
          <div>
            <h1 className="text-xl font-semibold">Welcome, {user.username}</h1>
            <p className="text-text-dim text-sm">
              {workoutStarted
                ? "Session active — stay in frame for accurate tracking."
                : "Plan a workout in the sidebar to begin."}
            </p>
          </div>

          {/* Coach feedback */}
          <div className="rounded-lg border border-border bg-surface p-4 flex items-center gap-2 text-sm">
            {!workoutStarted ? (
              <span className="text-text-dim">No active session.</span>
            ) : poseDetected === false ? (
              <>
                <AlertTriangle size={16} className="text-danger" />
                <span className="text-danger">
                  No pose detected — please face the camera.
                </span>
              </>
            ) : workoutComplete ? (
              <>
                <CheckCircle2 size={16} className="text-accent" />
                <span className="text-accent">
                  Workout complete! Great job.
                </span>
              </>
            ) : (
              <>
                <CheckCircle2 size={16} className="text-accent" />
                <span>Tracking your form...</span>
              </>
            )}
          </div>

          {/* Camera / stream */}
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-medium text-text-dim uppercase tracking-wide">
              Camera
            </h2>
            <button
              onClick={active ? handleCloseCamera : handleOpenCamera}
              className={`flex items-center gap-2 text-sm px-3 py-1.5 rounded-md border transition ${
                active
                  ? "border-border hover:border-danger/50 hover:text-danger"
                  : "border-accent/40 text-accent hover:brightness-110"
              }`}
            >
              {active ? <CameraOff size={15} /> : <Camera size={15} />}
              {active ? "Close Camera" : "Open Camera"}
            </button>
          </div>

          <div className="relative rounded-lg overflow-hidden border border-border bg-surface aspect-video">
            <video
              ref={videoRef}
              className="w-full h-full object-cover -scale-x-100"
              muted
              playsInline
            />
            {workoutStarted && active && (
              <PoseOverlay
                landmarks={metrics.landmarks}
                connections={metrics.connections}
                width={videoRef.current?.videoWidth || 640}
                height={videoRef.current?.videoHeight || 480}
              />
            )}
            {!active && (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-text-dim text-sm bg-bg/60">
                <CameraOff size={20} />
                {camError
                  ? camError
                  : "Camera is off — click Open Camera to begin"}
              </div>
            )}
            {active && !workoutStarted && (
              <div className="absolute inset-0 flex items-center justify-center text-text-dim text-sm bg-bg/40">
                Plan a workout in the sidebar to start tracking
              </div>
            )}
          </div>

          <WorkoutHistory history={history} loading={historyLoading} />
        </div>

        {workoutStarted && (
          <div>
            <MetricsPanel
              exercise={planExercise}
              metrics={metrics}
              progress={progress}
            />
          </div>
        )}
      </main>
    </div>
  );
}
