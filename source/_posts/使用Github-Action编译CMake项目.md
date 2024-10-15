---
title: 使用Github Action编译CMake项目
date: 2024-10-15 15:34:04
tags:
    - cmake
    - Github Action
categories: 开发
---

因为Github Action提供了多平台的编译环境，可以用来编译CMake项目。下面是一个使用Github Action编译CMake项目的例子。
其中使用了`MarkusJx/install-boost`来安装boost库。
新建`.github/workflows/cmake.yml`文件，内容如下：

```yaml
# This starter workflow is for a CMake project running on multiple platforms. There is a different starter workflow if you just want a single platform.
# See: https://github.com/actions/starter-workflows/blob/main/ci/cmake-single-platform.yml
name: CMake on multiple platforms

on:
  # 手动触发
  workflow_dispatch
  # push:
  #   branches: ["main"]
  # pull_request:
  #   branches: ["main"]

jobs:
  build:
    runs-on: ${{ matrix.os }}

    strategy:
      # Set fail-fast to false to ensure that feedback is delivered for all matrix combinations. Consider changing this to true when your workflow is stable.
      fail-fast: false

      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        build_type: [Release]
        include:
          - os: windows-latest
            c_compiler: cl
            cpp_compiler: cl
            toolset: msvc
            arch: x86
          - os: ubuntu-latest
            c_compiler: gcc
            cpp_compiler: g++
            toolset: gcc
            arch: x86
          - os: macos-latest
            c_compiler: clang
            cpp_compiler: clang++
            toolset: clang
            arch: aarch64

    steps:
      - uses: actions/checkout@v4

      - name: Install boost
        id: install-boost
        uses: MarkusJx/install-boost@v2.4.5
        with:
          boost_version: 1.85.0
          toolset: ${{ matrix.toolset }}
          arch: ${{ matrix.arch }}

      - name: Set reusable strings
        # Turn repeated input strings (such as the build output directory) into step outputs. These step outputs can be used throughout the workflow file.
        id: strings
        shell: bash
        run: |
          echo "build-output-dir=${{ github.workspace }}/build" >> "$GITHUB_OUTPUT"

      - name: Configure CMake project
        run: >
          cmake -B ${{ steps.strings.outputs.build-output-dir }}
          -DCMAKE_CXX_COMPILER=${{ matrix.cpp_compiler }}
          -DCMAKE_C_COMPILER=${{ matrix.c_compiler }}
          -DCMAKE_BUILD_TYPE=${{ matrix.build_type }}
          -S ${{ github.workspace }}
        env:
          Boost_ROOT: ${{ steps.install-boost.outputs.BOOST_ROOT }}

      - name: Build the project
        run: cmake --build ${{ steps.strings.outputs.build-output-dir }} --config ${{ matrix.build_type }}

      - name: Test
        working-directory: ${{ steps.strings.outputs.build-output-dir }}
        # Execute tests defined by the CMake configuration. Note that --build-config is needed because the default Windows generator is a multi-config generator (Visual Studio generator).
        # See https://cmake.org/cmake/help/latest/manual/ctest.1.html for more detail
        run: ctest --build-config ${{ matrix.build_type }}

```
