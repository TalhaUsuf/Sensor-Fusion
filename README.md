# ADAS2019
Advanced Driver Assistance Systems (ADAS), Carleton University, Canada, 2018-2019
Undergraduate 4th year Student Project

**Developers:**
- Shamoon Irshad
- Adam Fillion
- Mujaheed Khan
- Youssef Al-Sabbagh
- Junwen Fu

**About**

This project is a sensor fusion implementation on the NVIDIA Jetson TX2 development board. The sensory data from a camera, RADAR, and LIDAR are combined using a novel sensor-fusion algorithm to produce a high reliability pedestrian detector.

**Demo**

Simple Demonstration of pedestrian detection.

[![Not Found](https://img.youtube.com/vi/swne_90ZV08/0.jpg)](https://www.youtube.com/watch?v=swne_90ZV08)

Blind detection - despite a false-negative from the camera sensor, RADAR and LIDAR provide enough information to make a reasonable estimate of pedestrian position.

<img src="/media/blind.PNG">

**System Diagram**

<img src="/media/system_diagram.PNG">

**Dependancies**

Hardware: 

Platform: Nvidia Jetson TX2 (Nvidia Pascal GPU, ARM Cortex-A57 CPU, 8GB RAM)
Camera: Intel D435 (depth sensing, 30fps, 1280x720)
RADAR: TI AWR1642 (1cm resolution)
LIDAR: RPLidar A1M8 (2mm resolution)

Software:

TensorFlow
TensorRT
NVIDIA Jetpack
