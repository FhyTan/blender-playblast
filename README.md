# Blender Playblast Tool

A plugin similar to Maya's playblast functionality that allows you to create animation previews with one click and conveniently add custom information to videos.

<video controls src="images/demonstrate.mp4" title="Title"></video>

## System Requirements

- Blender 4.2.0 or higher
- FFmpeg (required for video processing)

Due to some limitations of the Blender Python API, this plugin requires FFmpeg to be installed on your computer for video processing and compositing.

If you are using Windows, we recommend using [UniGetUI](https://github.com/marticliment/UniGetUI) to quickly install FFmpeg.

## Location

3D Viewport ‣ N-panel ‣ Tool ‣ Playblast

![interface](images/interface.png)

## Usage Tutorial

Ensure there is an active camera in the scene, go to the playblast panel and click "Run" to start.

## Feature Overview

### Basic Playblast

- One-click generation of current scene preview videos
- Support for multiple video codec formats (H.264, H.265, MPEG-4, AV1)
- Adjustable resolution scaling (1-100%)
- Support for custom frame ranges

### Burn-in Subtitles

- Overlay custom information on videos
- Support for 6 positions: top-left, top-center, top-right, bottom-left, bottom-center, bottom-right
- Display scene information, timestamps, frame numbers and other metadata
- Support for custom fonts, colors, sizes and margins

### Audio Processing

- Automatically include audio tracks from the scene
- Synchronized output with video

### Settings Management

- Save current settings as default configuration
- Import/export settings files
- Team sharing of unified playblast formats

## Contributing

If you have additional video format or video metadata requirements, or other feature requests, feel free to submit Issues and Pull Requests!
