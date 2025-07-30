#!/usr/bin/env -S uv run --script

import math

import numpy as np

from nccapy import Vec3

np.random.seed(0)


def random_vector_on_sphere(radius: float) -> Vec3:
    theta = np.random.uniform(0, 2 * math.pi)
    phi = np.random.uniform(0, math.pi)
    x = radius * math.sin(phi) * math.cos(theta)
    y = radius * math.sin(phi) * math.sin(theta)
    z = radius * math.cos(phi)
    return Vec3(x, y, z)


pos = Vec3(0.0, 0.0, 0.0)
emit_dir = Vec3(0.0, 10.0, 0.0)
spread = 5.5
dir = emit_dir * np.random.rand() + random_vector_on_sphere(1.0) * spread
dir.y = abs(dir.y)


def update(dt=0.01):
    global dir, pos
    gravity = Vec3(0.0, -9.81, 0.0)
    g_update = gravity * dt
    print(f"g_update = {g_update}")
    dir += g_update
    print(f"dir = {dir}")
    pos += dir * dt * 0.5
    print(f"pos = {pos}")


def debug(v, p):
    print(f"dir {v.x: 0.2f} {v.y: 0.2f} {v.z: 0.2f} pos {p.x: 0.2f} {p.y: 0.2f} {p.z: 0.2f}")


print(f"dir = {dir}")
print(f"pos = {pos}")
for i in range(50):
    update()
    debug(dir, pos)
