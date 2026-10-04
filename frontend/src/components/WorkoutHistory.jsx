import { History } from "lucide-react";

export default function WorkoutHistory({ history, loading }) {
  return (
    <div className="rounded-lg border border-border bg-surface p-5">
      <div className="flex items-center gap-2 mb-4">
        <History size={16} className="text-accent" />
        <h3 className="text-sm font-medium text-text-dim uppercase tracking-wide">
          Recent History
        </h3>
      </div>

      {loading ? (
        <p className="text-sm text-text-dim">Loading...</p>
      ) : history.length === 0 ? (
        <p className="text-sm text-text-dim">
          No workouts logged yet. Complete a set to see it here.
        </p>
      ) : (
        <div className="space-y-2 max-h-64 overflow-y-auto scrollbar-thin pr-1">
          {history.map((h) => (
            <div
              key={h.id}
              className="flex items-center justify-between text-sm py-2 border-b border-border last:border-0"
            >
              <div>
                <p className="font-medium">{h.exercise_name}</p>
                <p className="text-xs text-text-dim">{h.log_date}</p>
              </div>
              <div className="text-right text-xs text-text-dim">
                <p>{h.reps} reps</p>
                <p>{h.sets} sets</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
