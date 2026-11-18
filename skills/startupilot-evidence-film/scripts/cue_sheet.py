"""Check a Mandarin cut against its trimmed WAV takes and export timed subtitles."""

import argparse
import json
import math
from pathlib import Path
import re
import sys
import wave


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} 应是有限数字")
    return value


def timecode(seconds):
    minutes, ms = divmod(round(seconds * 1000), 60000)
    hour, minute = divmod(minutes, 60)
    second, fraction = divmod(ms, 1000)
    return f"{hour:02}:{minute:02}:{second:02},{fraction:03}"


def read_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} 需要填写文本")
    return value.strip()


def count_spoken(text):
    if re.search(r"[A-Za-z0-9０-９Ａ-Ｚａ-ｚ%％°℃￥¥$=+×÷]", text):
        raise ValueError(f"请把 spoken 的数字、单位、缩写写成实际中文读音：{text}")
    count = len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff\U00020000-\U0002ebef]", text))
    if not count:
        raise ValueError("spoken 需要中文读音")
    return count


def prepare(project, directory):
    runtime = number(project["seconds"], "seconds")
    fps = number(project["fps"], "fps")
    target = number(project.get("target_cps", 7), "target_cps")
    tolerance = number(project.get("cps_tolerance", 0.3), "cps_tolerance")
    allowance = number(project.get("sync_frames", 2), "sync_frames")
    if min(runtime, fps, target) <= 0 or min(tolerance, allowance) < 0:
        raise ValueError("片长、帧率和目标语速应为正数，容差应为非负数")
    if not isinstance(project["cues"], list) or not project["cues"]:
        raise ValueError("cues 至少需要一段配音")
    last_end = voiced = 0.0
    total = 0
    takes, srt, metrics, issues = {}, [], [], []
    for index, cue in enumerate(project["cues"], 1):
        name = read_text(cue["id"], "id")
        if name in takes:
            raise ValueError(f"配音编号重复：{name}")
        wav = directory / cue["wav"]
        with wave.open(str(wav), "rb") as audio:
            duration = audio.getnframes() / audio.getframerate()
        if duration <= 0:
            raise ValueError(f"{name} WAV 为空")
        spoken = read_text(cue["spoken"], "spoken")
        caption = read_text(cue.get("subtitle", spoken), "subtitle")
        if any(not line.strip() for line in caption.splitlines()):
            raise ValueError(f"{name} 字幕中不能包含空段")
        count = count_spoken(spoken)
        start = number(cue["start"], "start")
        end = start + duration
        if start < 0 or start < last_end - 0.0005 or end > runtime + 0.0005:
            raise ValueError(f"{name} 越过片界、顺序有误或与前一句重叠")
        srt.append(f"{index}\n{timecode(start)} --> {timecode(end)}\n{caption}\n")
        metrics.append(dict(id=name, chars=count, start=start, end=round(end, 4), cps=round(count/duration, 3)))
        takes[name] = (spoken, start, duration)
        last_end = end
        total += count
        voiced += duration
    rate = total / voiced
    if abs(rate - target) > tolerance + 1e-9:
        issues.append(f"配音整体语速 {rate:.2f}，目标 {target:g} ± {tolerance:g}")
    anchors = project.get("anchors")
    if not isinstance(anchors, list) or not anchors:
        raise ValueError("anchors 至少需要一个有视听依据的关键词")
    checks = []
    for mark in anchors:
        name = read_text(mark["cue"], "anchor.cue")
        word = read_text(mark["word"], "anchor.word")
        spoken, start, duration = takes[name]
        offset = number(mark["offset"], "offset")
        if word not in spoken or not 0 <= offset < duration:
            raise ValueError(f"{name}/{word} 的词或音频内起点无效")
        when = start + offset
        for kind in ("picture", "sound"):
            if kind == "sound" and kind not in mark:
                continue
            event = number(mark[kind], kind)
            if not 0 <= event < runtime:
                raise ValueError(f"{name}/{word} 的 {kind} 在片外")
            frames = (event - when) * fps
            checks.append(dict(cue=name, word=word, track=kind, frames=round(frames, 3)))
            if abs(frames) > allowance + 1e-9:
                issues.append(f"{name}/{word} 的 {kind} 相差 {frames:+.1f} 帧")
    report = dict(chars=total, voice_seconds=round(voiced, 4), gap_seconds=round(runtime-voiced, 4),
                  voice_cps=round(rate, 3), whole_film_cps=round(total/runtime, 3),
                  cues=metrics, anchors=checks, issues=issues)
    return "\n".join(srt), report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--srt", type=Path, help="成功时输出 UTF-8 SRT")
    parser.add_argument("--report", type=Path, help="保存各句语速及音画误差")
    args = parser.parse_args()
    try:
        project = json.loads(args.project.read_text(encoding="utf-8"))
        srt, report = prepare(project, args.project.parent)
        data = json.dumps(report, ensure_ascii=False, indent=2)
        if args.report:
            args.report.write_text(data + "\n", encoding="utf-8")
        print(f"{report['chars']} 字 / {report['voice_seconds']:.2f} 秒 = {report['voice_cps']:.2f} 字/秒")
        if report["issues"]:
            raise ValueError("\n".join(report["issues"]))
        if args.srt:
            args.srt.write_text(srt, encoding="utf-8")
    except (KeyError, ValueError, TypeError, OSError, EOFError, wave.Error) as error:
        parser.exit(1, f"校验失败：{error}\n")


if __name__ == "__main__":
    main()
