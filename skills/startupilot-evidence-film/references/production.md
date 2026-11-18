# 把导演决定写进可复核的时间线

## 运镜

示例 clock-camera.json 是 12 秒虚构钟楼剖面习作。世界画布建议 2200 × 1400。右上方的报时人偶先不动，镜头拉远显露传动关系，再向左下方追踪连杆，经过中心的销钉，最后回到人偶。定住机位的时间用来观察主体。示例仅含机位，使用者按题材另画美术与动作。

在 Skill 目录运行以下命令，得到 288 行逐帧坐标及表头。

```sh
python3 scripts/camera_path.py references/clock-camera.json > camera.csv
```

t 使用秒，x 和 y 为画布坐标，width 为取景窗口在画布中的宽度。bend 为从本机位出发时，在路径中点相对直线中点的偏移。重复同一坐标和宽度、取零偏移即可停机位。绘图器逐帧把世界点投到屏幕。横坐标为「输出宽度的一半 +（世界横坐标 − 机位中心横坐标）× 输出宽度 / 取景宽度」，纵坐标使用屏幕高度的一半加同一比例的纵坐标差。文字字幕最后按屏幕坐标绘制。

## 配音与动作锚点

在剪辑工程旁建立 cut.json。以下只是字段示例。先准备自己的 PCM WAV，再填写从该文件中听得的关键词起点，及剪辑工程中画面、拟音的实际时间。offset 相对句首，picture 和 sound 相对片首，单位为秒。多个角色分别编号，默认逐句轮流说。连续重叠对白需另行分轨审校。

```json
{
  "seconds": 12,
  "fps": 24,
  "target_cps": 7,
  "cps_tolerance": 0.3,
  "sync_frames": 2,
  "cues": [
    {"id": "pin", "start": 2.0, "spoken": "看这枚销钉落下。", "subtitle": "看，这枚销钉落下。", "wav": "voice/pin.wav"}
  ],
  "anchors": [
    {"cue": "pin", "word": "落下", "offset": 0.64, "picture": 2.65, "sound": 2.67}
  ]
}
```

```sh
python3 scripts/cue_sheet.py /path/to/cut.json --srt film.srt --report timing.json
```

语速分母是裁边后各 WAV 时长之和，含句内停连。whole_film_cps 使用整片时长。字幕可将“一九零三年”写为“1903 年”。脚本读取音频长度并交叉检查登记的事件，关键词位置需从录音取得，动作位置需从实际渲染时间线或画面取得。报告列出每句语速，允许强调词和短促感叹有快慢。遇到错配先回到该句及事件修正，再重新导出。

## 成片复核

以一条观众能指出来的证据验收每个段落。例如“手指松开了哪根线，哪个零件开始动”，或“地图上两处标记怎样帮助理解接下来的行动”。在开头和结尾截图上让主体占同一位置，检查观众是否能在看第二张图时回答最初的问题。

用下列命令检查媒体容器。配音是否自然、字幕是否挡住主体、画面是否够亮、强调词有没有击中真正的动作，都要在导出画面和声音上另行核对。

```sh
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,avg_frame_rate -of json film.mp4
```
