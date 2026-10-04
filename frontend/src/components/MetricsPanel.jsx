import { METRICS_FIELDS } from "../lib/exerciseConfig";

function Stat({ label, value }) {
  return (
    <div className="flex items-center justify-between py-2.5 border-b border-border last:border-0">
      <span className="text-sm text-text-dim">{label}</span>
      <span className="text-sm font-medium">{value}</span>
    </div>
  );
}

export default function MetricsPanel({ exercise, metrics, progress }) {
  const fields = METRICS_FIELDS[exercise] || [];

  return (
    <div className="rounded-lg border border-border bg-surface p-5">
      <h3 className="text-sm font-medium text-text-dim uppercase tracking-wide mb-3">
        Workout Progress
      </h3>
      <Stat label="Total Reps" value={progress.reps} />
      <Stat
        label="Current Set Reps"
        value={`${progress.currentSetReps} / ${progress.repsPerSet}`}
      />
      <Stat
        label="Sets Completed"
        value={`${progress.setsCompleted} / ${progress.targetSets}`}
      />

      <h3 className="text-sm font-medium text-text-dim uppercase tracking-wide mt-6 mb-3">
        {exercise} Metrics
      </h3>
      {fields.map((f) => (
        <Stat
          key={f.key}
          label={f.label}
          value={
            metrics[f.key] !== undefined && metrics[f.key] !== null
              ? `${metrics[f.key]}${f.suffix || ""}`
              : "N/A"
          }
        />
      ))}
    </div>
  );
}
