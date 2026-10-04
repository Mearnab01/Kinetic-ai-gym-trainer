const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore */
    }
    const err = new Error(detail);
    err.status = res.status;
    throw err;
  }

  return res.json();
}

export const api = {
  enroll: (username, imageBase64) =>
    request("/api/auth/enroll", {
      method: "POST",
      body: JSON.stringify({ username, image_base64: imageBase64 }),
    }),

  verify: (imageBase64) =>
    request("/api/auth/verify", {
      method: "POST",
      body: JSON.stringify({ image_base64: imageBase64 }),
    }),

  listExercises: () => request("/api/exercises"),

  startSession: (userId) =>
    request("/api/session/start", {
      method: "POST",
      body: JSON.stringify({ user_id: userId }),
    }),

  endSession: (sessionId) =>
    request(`/api/session/end?session_id=${encodeURIComponent(sessionId)}`, {
      method: "POST",
    }),

  resetExercise: (sessionId, exerciseType) =>
    request("/api/session/reset", {
      method: "POST",
      body: JSON.stringify({ session_id: sessionId, exercise_type: exerciseType }),
    }),

  sendFrame: (sessionId, exerciseType, imageBase64) =>
    request("/api/frame", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        exercise_type: exerciseType,
        image_base64: imageBase64,
      }),
    }),

  saveExercise: (userId, exerciseName, reps, sets, durationSec) =>
    request("/api/exercise/save", {
      method: "POST",
      body: JSON.stringify({
        user_id: userId,
        exercise_name: exerciseName,
        reps,
        sets,
        duration_sec: durationSec,
      }),
    }),

  getHistory: (userId) => request(`/api/exercise/history/${userId}`),
};

export async function fetchCachedCoachingAudio(username, event) {
  const res = await fetch(`${BASE_URL}/api/coach/cached`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, event }),
  });
  if (!res.ok) throw new Error("Cached coaching audio request failed");
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

export async function fetchCoachingAudio(event, exercise, metrics) {
  const res = await fetch(`${BASE_URL}/api/coach/speak`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ event, exercise, metrics }),
  });
  if (!res.ok) throw new Error("Coaching audio request failed");
  const blob = await res.blob();
  return URL.createObjectURL(blob);
}
