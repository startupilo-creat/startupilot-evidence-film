"""Sample a continuous 2-D camera path. Dimensions use artwork coordinates."""

import argparse
from bisect import bisect_right
import csv
import json
import math
from pathlib import Path
import sys


def numeric(value):
    return type(value) in (int, float) and math.isfinite(value)


class Camera:
    def __init__(self, plan):
        self.keys = plan["keys"]
        self.fps = plan["fps"]
        if type(self.fps) is not int or self.fps <= 0 or len(self.keys) < 2:
            raise ValueError("使用正整数 fps 和至少两个机位")
        self.times = []
        for key in self.keys:
            if not all(numeric(key[field]) for field in ("t", "x", "y", "width")):
                raise ValueError("机位的 t、x、y、width 必须是有限数字")
            if key["width"] <= 0 or (self.times and key["t"] <= self.times[-1]):
                raise ValueError("机位时间必须递增，取景宽度必须为正数")
            bend = key.get("bend", [0, 0])
            if len(bend) != 2 or not all(numeric(n) for n in bend):
                raise ValueError("bend 应为两个有限的偏移值")
            self.times.append(key["t"])
        if self.times[0] != 0 or abs(self.times[-1]*self.fps - round(self.times[-1]*self.fps)) > 1e-6:
            raise ValueError("首机位在零秒，末机位在片尾帧边界")

    def sample(self, t):
        index = max(0, min(len(self.keys)-2, bisect_right(self.times, t)-1))
        left, right = self.keys[index:index+2]
        u = min(1.0, max(0.0, (t-left["t"]) / (right["t"]-left["t"])))
        # Arrive with zero velocity so a diagram or a number can be read.
        p = (1-math.cos(math.pi*u))/2
        bend_x, bend_y = left.get("bend", [0, 0])
        arc = 4*p*(1-p)
        x = (1-p)*left["x"] + p*right["x"] + arc*bend_x
        y = (1-p)*left["y"] + p*right["y"] + arc*bend_y
        width = math.exp((1-p)*math.log(left["width"]) + p*math.log(right["width"]))
        return x, y, width


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()
    try:
        camera = Camera(json.loads(args.plan.read_text(encoding="utf-8")))
        writer = csv.writer(sys.stdout)
        writer.writerow(["frame", "time_s", "center_x", "center_y", "view_width"])
        for frame in range(round(camera.times[-1]*camera.fps)):
            t = frame / camera.fps
            writer.writerow([frame, f"{t:.6f}", *(f"{value:.4f}" for value in camera.sample(t))])
    except (KeyError, ValueError, OSError, TypeError) as error:
        parser.exit(1, f"机位表有误：{error}\n")


if __name__ == "__main__":
    main()
