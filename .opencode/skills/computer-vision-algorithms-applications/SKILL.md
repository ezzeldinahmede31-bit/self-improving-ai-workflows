---
name: computer-vision-algorithms-applications
description: Applies Richard Szeliski's Computer Vision: Algorithms and Applications to build vision systems: image formation and filtering, feature detection and matching, segmentation, stereo and multi-view geometry, motion and optical flow, recognition and classification with modern deep learning, and practical applications such as 3D reconstruction, image stitching, and object detection. Use when the user says 'computer vision', 'image processing', 'feature detection', 'SIFT', 'object detection', 'optical flow', '3D reconstruction', 'segmentation', 'Szeliski', 'build a vision system', or when a vision problem needs both classical algorithms and modern deep-learning solutions. Pairs with: deep-learning-vision-systems, hands-on-ml-sklearn-keras-tensorflow, generative-deep-learning, persistent-browser-automation.
---
# Computer Vision: Algorithms and Applications

Transfers Szeliski's comprehensive method: vision is a pipeline from pixels to structure to semantics, and the classical algorithms still underlie the modern deep-learning systems.

## When to use
- Building any vision feature, from filtering to recognition.
- Choosing between a classical algorithm and a deep model for a vision step.
- Understanding the geometry and math behind cameras, stereo, and reconstruction.

## Core pipeline
1. Image formation and filtering: sensors, color, convolution, pyramids, and denoising as the foundation.
2. Features and matching: SIFT-like local features and descriptors for correspondence, stitching, and tracking.
3. Geometry: camera models, epipolar geometry, stereo disparity, and multi-view 3D reconstruction.
4. Semantics: segmentation, detection, and recognition, dominated today by deep CNNs.

## Practice rules
- Match the technique to the problem: classical geometry for reconstruction, deep learning for recognition.
- Validate vision pipelines on real captured images, not only synthetic ones.
- Understand the coordinate and calibration assumptions before trusting any geometry output.

## Verification discipline
- Check calibration and undistortion before multi-view math.
- Measure detection/matching accuracy on labeled data with precision-recall.
- Reproduce the same result across runs (fix seeds and nondeterminism in deep models).

## Pairs with
deep-learning-vision-systems, hands-on-ml-sklearn-keras-tensorflow, generative-deep-learning, persistent-browser-automation.
