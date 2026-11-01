import React from 'react';
import { useCurrentFrame, useVideoConfig } from 'remotion';

interface ParticleProps {
  count?: number;
  color?: string;
  speed?: number;
  size?: number;
}

export const Particles: React.FC<ParticleProps> = ({
  count = 40,
  color = '#00CFE8',
  speed = 0.5,
  size = 3,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const particles = Array.from({ length: count }, (_, i) => {
    const seed = i * 137.508;
    const x = (Math.sin(seed) * 0.5 + 0.5) * 1080;
    const y = (Math.cos(seed * 2) * 0.5 + 0.5) * 1920;
    const phase = (frame / fps) * speed + seed;
    const dx = Math.sin(phase * 0.7) * 15;
    const dy = Math.cos(phase * 0.5) * 12;
    const opacity = 0.3 + Math.sin(phase) * 0.2;
    const scale = 0.5 + Math.sin(phase * 1.3) * 0.3;

    return { x: x + dx, y: y + dy, opacity, scale, size };
  });

  return (
    <div style={{ position: 'absolute', inset: 0, overflow: 'hidden' }}>
      {particles.map((p, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            left: p.x,
            top: p.y,
            width: p.size,
            height: p.size,
            borderRadius: '50%',
            backgroundColor: color,
            opacity: p.opacity,
            transform: `scale(${p.scale})`,
            boxShadow: `0 0 ${p.size * 4}px ${color}`,
          }}
        />
      ))}
    </div>
  );
};
