---
title: 在VScode中使用lldb调试CMake项目
date: 2024-10-15 15:28:18
tags:
    - Vscode
    - lldb
    - cmake
categories: 开发
---

配置好CMake项目后在.vscode文件夹下生成`launch.json`和`task.json`文件，配置好后可以直接在VScode中使用lldb调试cmake项目。

`launch.json`文件

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "server release lldb",
      "type": "cppdbg",
      "request": "launch",
      "program": "${workspaceFolder}/cmake-build-release/RenderEngineServer",
      "stopAtEntry": false,
      "cwd": "${workspaceFolder}/cmake-build-release",
      "environment": [],
      "externalConsole": false,
      "MIMode": "lldb",
      "preLaunchTask": "CMake: build"
    },
    {
      "name": "server debug lldb",
      "type": "cppdbg",
      "request": "launch",
      "program": "${workspaceFolder}/cmake-build-debug/RenderEngineServer",
      "stopAtEntry": false,
      "cwd": "${workspaceFolder}/cmake-build-debug",
      "environment": [],
      "externalConsole": false,
      "MIMode": "lldb",
      "preLaunchTask": "CMake: build"
    }
  ]
}

```

`task.json`文件

```json
{
  "tasks": [
    {
      "type": "cmake",
      "label": "CMake: configure",
      "command": "configure",
      "preset": "${command:cmake.activeConfigurePresetName}",
      "problemMatcher": [],
      "detail": "CMake configure task"
    },
    {
      "type": "cmake",
      "label": "CMake: build",
      "command": "build",
      "targets": ["all"],
      "preset": "${command:cmake.activeBuildPresetName}",
      "group": "build",
      "problemMatcher": [],
      "detail": "CMake configure and build task",
      "dependsOn": "CMake: configure"
    }
  ],
  "version": "2.0.0"
}
```


