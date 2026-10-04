import { useNavigate } from "react-router-dom";
import {
  Activity,
  ArrowRight,
  Camera,
  Dumbbell,
  ScanFace,
  CheckCircle2,
  Gauge,
} from "lucide-react";

const EXERCISES = [
  "Squats",
  "Push-ups",
  "Biceps Curls",
  "Shoulder Press",
  "Lunges",
];

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-bg text-text">
      <nav className="flex items-center justify-between px-6 md:px-12 py-5 border-b border-border">
        <div className="flex items-center gap-2">
          <Dumbbell className="text-accent" size={22} />
          <span className="font-semibold tracking-tight text-lg">Kinetic</span>
        </div>
        <button
          onClick={() => navigate("/auth")}
          className="text-sm px-4 py-2 rounded-md border border-border hover:border-accent/50 transition-colors"
        >
          Sign in
        </button>
      </nav>

      {/* Hero */}
      <section className="px-6 md:px-12 pt-20 pb-24 max-w-5xl mx-auto text-center animate-[fadeIn_0.6s_ease-out]">
        <div className="inline-flex items-center gap-2 text-xs px-3 py-1 rounded-full border border-border text-text-dim mb-6">
          <Activity size={14} className="text-accent" />
          Computer-vision workout tracking, in your browser
        </div>
        <h1 className="text-4xl md:text-6xl font-semibold tracking-tight leading-tight mb-6">
          AI-Powered Personal Gym Trainer
        </h1>
        <p className="text-text-dim text-lg max-w-2xl mx-auto mb-10 leading-relaxed">
          Kinetic watches your form through pose analysis, counts reps
          automatically, and gives real-time feedback on your technique — no
          wearables required.
        </p>
        <div className="flex items-center justify-center gap-4">
          <button
            onClick={() => navigate("/auth")}
            className="inline-flex items-center gap-2 bg-accent text-bg font-medium px-6 py-3 rounded-md hover:brightness-110 transition"
          >
            Start Training <ArrowRight size={18} />
          </button>
          <button
            onClick={() => navigate("/auth")}
            className="px-6 py-3 rounded-md border border-border hover:border-accent/50 transition-colors text-sm"
          >
            Face sign-in
          </button>
        </div>
      </section>

      {/* How it works */}
      <section className="px-6 md:px-12 py-16 border-t border-border">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-semibold mb-10 text-center">
            How it works
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            <FeatureCard
              icon={<ScanFace className="text-accent" size={22} />}
              title="Face sign-in"
              text="Verify your identity with a quick face scan — the same biometric pipeline used in our attendance system."
            />
            <FeatureCard
              icon={<Camera className="text-accent" size={22} />}
              title="Real-time pose tracking"
              text="MediaPipe pose estimation runs on every frame to track 33 body landmarks as you train."
            />
            <FeatureCard
              icon={<Gauge className="text-accent" size={22} />}
              title="Live form feedback"
              text="Per-exercise detectors count reps and flag form issues like depth, alignment, and posture instantly."
            />
          </div>
        </div>
      </section>

      {/* Supported exercises */}
      <section className="px-6 md:px-12 py-16 border-t border-border">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-semibold mb-8 text-center">
            Supported exercises
          </h2>
          <div className="flex flex-wrap justify-center gap-3">
            {EXERCISES.map((ex) => (
              <div
                key={ex}
                className="flex items-center gap-2 px-4 py-2 rounded-md border border-border text-sm text-text-dim"
              >
                <CheckCircle2 size={15} className="text-accent" />
                {ex}
              </div>
            ))}
          </div>
        </div>
      </section>

      <footer className="px-6 md:px-12 py-8 border-t border-border text-center text-xs text-text-dim">
        Kinetic — AI Gym Trainer. Pose estimation via MediaPipe, face auth via
        MTCNN + FaceNet.
      </footer>
    </div>
  );
}

function FeatureCard({ icon, title, text }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-6">
      <div className="mb-4">{icon}</div>
      <h3 className="font-medium mb-2">{title}</h3>
      <p className="text-sm text-text-dim leading-relaxed">{text}</p>
    </div>
  );
}
