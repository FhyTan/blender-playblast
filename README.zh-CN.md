# Blender 拍屏工具

一个类似 Maya 拍屏功能的插件，让你一键拍屏预览动画，还能方便的添加自定义信息到视频上

![demonstrate](images/demonstrate.gif)

## 系统要求

- Blender 4.2.0 或更高版本
- FFmpeg（必需，用于视频处理）

由于 Blender Python API 的一些使用限制，使用此插件需要先在电脑上安装 FFmpeg，用于插件的视频处理合成

如果你使用的是 Windows 系统，推荐使用 [UniGetUI](https://github.com/marticliment/UniGetUI) 快速安装 FFmpeg

## 位置

3D Viewport ‣ N-panel ‣ Tool ‣ Playblast

![interface](images/interface.png)

## 使用教程

确保场景中有活动摄像机，进入拍屏面板点击“运行”即可

## 功能详解

### 基本拍屏

- 一键生成当前场景的预览视频
- 支持多种视频编码格式（H.264、H.265、MPEG-4、AV1）
- 可调节分辨率缩放比例（1-100%）
- 支持自定义帧范围

### 字幕叠加 (Burn-in)

- 在视频上叠加自定义信息
- 支持 6 个位置：上左，上中，上右，下左，下中，下右
- 可显示场景信息、时间戳、帧数等元数据
- 支持自定义字体、颜色、大小和边距

### 音频处理

- 自动包含场景中的音频轨道
- 与视频同步输出

### 设置管理

- 保存当前设置为默认配置
- 导入/导出设置文件
- 团队共享统一拍屏格式

## 贡献

如果有额外的视频格式或者视频元数据需求，或其他功能需求，欢迎提交 Issue 和 Pull Request！
