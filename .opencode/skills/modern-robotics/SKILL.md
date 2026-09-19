---
name: modern-robotics
description: "Reasons about robots: configuration space, rigid-body motion, kinematics, and planning. Use when the user says 'forward kinematics', 'inverse kinematics', 'configuration space', 'SE(3)', 'twists', 'Jacobian', 'motion planning', 'Modern Robotics', 'robot arm', or when bodies must move correctly in space."
---

# Modern Robotics

Distilled from Lynch & Park *Modern Robotics*: robots live in configuration
space, move via rigid-body transforms, and plan before they act. Geometry
first, dynamics second, control last.

## Purpose

Model any mechanism's motion exactly — where it is, where it can go, and how
to get it there without collision.

## The stack (geometry -> motion -> planning)

1. **Configuration space.** The robot IS a point in C-space (joint angles,
   pose parameters). Degrees of freedom counted honestly (Grübler formula
   for mechanisms). Topology matters: revolute joints wrap (S¹), prismatic
   slide (R) — planners that ignore topology collide with reality.
2. **Rigid-body motions.** Rotations (SO(3): roll-pitch-yaw vs axis-angle vs
   quaternions — quaternions for computation, Euler only for display),
   homogeneous transforms in SE(3), twists (screw motions unify rotation +
   translation). Compose transforms right-to-left; mind the frame (body vs
   space).
3. **Forward kinematics.** Product of Exponentials: T = e^[S1]θ1 ... e^[Sn]θn
   M. One formula, any serial chain — derive frames once (screw axes in the
   home position), evaluate forever.
4. **Inverse kinematics.** Analytic where the geometry allows (6-DOF with
   spherical wrist: decouple position/orientation); numeric elsewhere
   (Newton-Raphson on the end-effector error, damped least squares near
   singularities). Multiple/no solutions are normal — characterize, don't
   assume.
5. **Velocity and statics.** Spatial Jacobian maps joint rates to end-effector
   twist; singularities (Jacobian rank loss) identified in advance; force/
   torque duality (τ = J^T F) sizes actuators.
6. **Planning and control.** C-space obstacles (grown by robot geometry);
   sampling planners (RRT/PRM) for high DOF, grid/A* where discretization is
   honest. Trajectory: time-scaling with velocity/acceleration limits. Control
   closes the loop (feedforward + feedback; stability before performance).

## Verification

Every motion claim ships with: frames diagram, DOF accounting, singularity
check, and a simulated trajectory (collision-free in the planner) before any
hardware moves. Unsimulated motion commands are rejected.

## Pairs with

- `strang-linear-algebra` (transforms and Jacobians),
  `computational-geometry` (C-space obstacles),
  `thinking-model-router`/`thinking-systems` (planning under constraints),
  `operating-systems-three-easy-pieces` (real-time control loops).
