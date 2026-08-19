---
name: computer-vision-multiview-stereo
description: Applies the camera-geometry and stereo chapters of Richard Szeliski's Computer Vision: Algorithms and Applications: camera models and calibration, epipolar geometry and the fundamental matrix, stereo disparity estimation, and multi-view 3D reconstruction and structure from motion. Use when the user says 'camera calibration', 'epipolar geometry', 'stereo vision', 'disparity', 'fundamental matrix', '3D reconstruction', 'structure from motion', 'multi-view geometry', or when recovering 3D structure from two or more camera views. Pairs with: computer-vision-algorithms-applications, computer-systems-programmers-perspective, algorithmic-math-reasoner, generative-deep-learning.
---
# Multi-View Geometry and Stereo (Szeliski)

Transfers Szeliski's geometry for recovering 3D from images: calibrate the cameras, relate the views, match pixels, and triangulate structure.

## When to use
- Reconstructing 3D from multiple photos or video frames.
- Computing depth from a stereo pair.
- Understanding camera calibration and how pixels relate to rays in the world.

## Core pipeline
1. Camera model and calibration: intrinsics (focal length, principal point) and extrinsics (pose) map 3D points to pixels; calibrate before geometry work.
2. Epipolar geometry: the fundamental matrix relates corresponding points across two views, constraining the search from 2D to a line.
3. Stereo matching: find corresponding pixels along epipolar lines and convert disparity to depth.
4. Multi-view reconstruction: triangulate matches, refine poses (structure from motion), and fuse depth into dense geometry.

## Practice rules
- Calibrate and undistort before any epipolar math; garbage calibration makes garbage geometry.
- Normalize coordinates before estimating the fundamental matrix to keep it well-conditioned.
- Validate reprojection error; low error is the honest signal the geometry is correct.

## Verification discipline
- Check reprojection errors on known calibration targets.
- Verify epipolar constraints hold on matched pairs.
- Test reconstruction on data with known ground-truth 3D where possible.

## Pairs with
computer-vision-algorithms-applications, computer-systems-programmers-perspective, algorithmic-math-reasoner, generative-deep-learning.
