class InterpolatingMap:
    def __init__(self):
        self._points = {}

    def insert(self, x: float, y: float):
        self._points[x] = y

    def get(self, x: float) -> float:
        if not self._points:
            return 0.0

        keys = sorted(self._points.keys())

        # Clamp
        if x <= keys[0]:
            return self._points[keys[0]]
        if x >= keys[-1]:
            return self._points[keys[-1]]

        # Linear interpolation
        for i in range(len(keys) - 1):
            x0, x1 = keys[i], keys[i + 1]
            if x0 <= x <= x1:
                y0, y1 = self._points[x0], self._points[x1]
                t = (x - x0) / (x1 - x0)
                return y0 + t * (y1 - y0)

        return 0.0