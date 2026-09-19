---
name: foley-computer-graphics
description: "Builds correct rendering: transforms, viewing, rasterization, and shading. Use when the user says 'render this', 'projection matrix', 'homogeneous coordinates', 'clipping', 'rasterization', 'z-buffer', 'shading model', 'ray tracing', 'texture mapping', 'Bézier', 'Foley', 'graphics pipeline', or when pixels must come out of geometry."
---

# Foley Computer Graphics

Distilled from Foley/van Dam et al.'s *Computer Graphics: Principles and
Practice*: the pipeline every renderer implements, and the math that makes
each stage correct.

## Purpose

Assemble or debug a rendering path stage by stage — model, view, project,
clip, rasterize, shade — knowing exactly which matrix and which space each
step lives in.

## The pipeline (in order, each with its contract)

1. **Modeling transforms.** Objects live in local space; compose
   scale-rotate-translate into a model matrix. Use homogeneous 4x4 matrices so
   translation composes with rotation. Order matters: M = T·R·S applies S first.
2. **Viewing.** World -> camera space via the view matrix (eye, look-at, up).
   Keep the camera orthonormal; a skewed basis leaks into every later stage.
3. **Projection.** Perspective (foreshortening, vanishing points) vs
   orthographic. The projection matrix maps the view frustum to the canonical
   cube; near/far plane choice controls depth precision (z-fighting comes from
   a too-wide ratio).
4. **Clipping.** Clip in homogeneous space BEFORE the perspective divide
   (Sutherland-Hodgman for polygons); never divide by w<=0.
5. **Rasterization.** Convert primitives to fragments: edge functions +
   barycentric interpolation of attributes (color, depth, UVs — perspective-
   correct interpolation divides by w). Z-buffer resolves visibility per
   fragment; clear it every frame.
6. **Shading.** Local illumination = ambient + diffuse (Lambert: n·l) +
   specular (Phong/Blinn-Phong: halfway vector). Normals must be re-
   normalized after interpolation. Textures sample in UV space with
   mipmapping to kill aliasing.
7. **Global effects (when local is not enough).** Ray tracing for true
   reflection/refraction/shadows; path tracing for full global illumination.
   Cost rule: rays multiply — bound bounces and use spatial acceleration.

## Curves and color (the two perennial traps)

- Bézier/B-spline: control points shape, convex-hull property bounds;
  evaluate with de Casteljau, never by expanding polynomials.
- Color: do lighting math in LINEAR space, gamma-encode only for display;
  sRGB La La Land (lighting in gamma space) washes everything out.

## Verification

Render a test scene with a known answer (single triangle at known depth +
one light): pixel color and depth must match hand computation. Then scale up.

## Pairs with

- `strang-linear-algebra` (every matrix in the pipeline),
  `impeccable`/`frontend-design` (visual output quality),
  `systems-performance-profiling` (frame-time budgets).
