# Startupilot 线索短片

把「为什么会发生这件事」做成一分钟的中文短片。导演规则负责组织证据、空间和节奏，两个 Python 工具负责生成机位轨迹、核对录音与字幕。配音、绘图和视频编码由运行 Skill 的代理调用所在环境完成。

## 安装到当前项目

在拍片项目的终端运行对应命令。首次使用需联网，建议 Node.js 22.20 或更高版本。

**Codex**

```sh
npx skills add startupilo-creat/startupilot-evidence-film --skill startupilot-evidence-film -a codex --copy -y
```

**Claude Code**

```sh
npx skills add startupilo-creat/startupilot-evidence-film --skill startupilot-evidence-film -a claude-code --copy -y
```

配套的两个脚本只需 Python 3.9 或更高版本。制作成片还需普通话配音、中文字体、绘图工具及视频编码器。

**安装自检**　向助手发送：“使用 startupilot-evidence-film，运行包内 camera_path.py，读取 references/clock-camera.json。报告读到的 SKILL.md 路径、帧数，再检查中文配音、字体和 FFmpeg。”示例为 12 秒 × 24 fps，CSV 应有 288 行数据及一行表头。

## 试拍

> 使用 Startupilot 线索短片，拍一部 60 秒的中文短片，题材是【主题】，给【观众】看。开场用一件能近看的东西提出问题，片尾回到它，让我看懂答案。挑两到三条真正共同造成结果的线索；每条用能拍出来的证据说明它解决了什么。按题材选地图、档案桌或结构剖面，先让我看懂全局，再让我跟进细节。镜头拉远时交代彼此的位置，推近时让我看清证据，关键动作给足停留。普通话口播按实际发声段落平均每秒约七个字，给环境声与动作留白。逐句实录校时，让关键词、画面变化与相关拟音落在同一拍。用代码渲染，交付含烧录中文字幕和音效的 MP4、可编辑 SRT 和工程。

试题可以只用一句：“用 Startupilot 线索短片讲莱特兄弟的首次飞行。开头请观众看照片里一人的脚仍踩在沙地上，片尾再回到这张照片。”导演规则会提供其他默认项。

## 使用许可

发布者为 **Startupilot**。你可以安装、内部修改并用它制作商业视频，也可以撰写自己的教程。分发或打包销售本 Skill 源文件或其改编版本须取得书面许可。完整条款见 [LICENSE.md](LICENSE.md)。

本项目使用 AI 辅助编写。制作影片所用的档案、配音、字体与音乐按各自许可使用。
