class AngleSmoother:
    ALPHA = 0.35
    ANGLE_KEYS = {
        "knee_angle", "back_angle", "elbow_angle",
        "front_knee_angle", "torso_angle"
    }
 
    def __init__(self):
        self._state: dict[str, float] = {}
 
    def smooth(self, metrics: dict) -> dict:
        result = dict(metrics)
        for key in self.ANGLE_KEYS:
            if key not in metrics:
                continue
            raw = metrics[key]
            if not isinstance(raw, (int, float)):
                continue
            if key in self._state:
                smoothed = self.ALPHA * raw + (1 - self.ALPHA) * self._state[key]
            else:
                smoothed = float(raw)
            self._state[key] = smoothed
            result[key] = round(smoothed)
        return result
 
    def reset(self):
        self._state.clear()