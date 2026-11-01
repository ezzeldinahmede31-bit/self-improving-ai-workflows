import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate } from 'remotion';
import { COLORS } from '../constants';
import { Typography } from '../components/Typography';
import { Particles } from '../components/Particles';

export const Scene3: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const localFrame = frame - 10 * fps;

  const chaosOpacity = interpolate(localFrame, [0, 1.5 * fps], [1, 0], { extrapolateRight: 'clamp' });
  const flowOpacity = interpolate(localFrame, [1 * fps, 2.5 * fps], [0, 1], { extrapolateRight: 'clamp' });
  const textOpacity = interpolate(localFrame, [2 * fps, 3 * fps], [0, 1], { extrapolateRight: 'clamp' });
  const textY = interpolate(localFrame, [2 * fps, 3 * fps], [40, 0], { extrapolateRight: 'clamp' });

  // Data path animation
  const pathProgress = interpolate(localFrame, [1 * fps, 3 * fps], [0, 1], { extrapolateRight: 'clamp' });

  return (
    <div style={{ position: 'absolute', inset: 0, background: `radial-gradient(ellipse at 50% 50%, ${COLORS.navy} 0%, ${COLORS.black} 100%)` }}>
      <Particles count={20} color={COLORS.gold} speed={0.2} />

      {/* Chaos fading out */}
      <div style={{ position: 'absolute', inset: 0, opacity: chaosOpacity }}>
        {[0, 1, 2, 3, 4, 5].map((i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${10 + i * 16}%`,
              top: `${15 + (i % 3) * 25}%`,
              width: 120,
              height: 80,
              background: `${COLORS.navy}88`,
              border: `1px solid ${COLORS.cyan}22`,
              borderRadius: 8,
              transform: `rotate(${i * 15 - 30}deg) translateX(${Math.sin(localFrame / 10 + i) * 20}px)`,
              opacity: 0.6,
            }}
          />
        ))}
      </div>

      {/* Glowing data path */}
      <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: flowOpacity }}>
        <defs>
          <linearGradient id="flowGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor={COLORS.cyan} stopOpacity="0.8" />
            <stop offset="50%" stopColor={COLORS.gold} stopOpacity="1" />
            <stop offset="100%" stopColor={COLORS.cyan} stopOpacity="0.8" />
          </linearGradient>
        </defs>
        <path
          d={`M 540 400 Q 300 700 540 1000 Q 780 1300 540 1600`}
          stroke="url(#flowGrad)"
          strokeWidth={4}
          fill="none"
          strokeDasharray={1000}
          strokeDashoffset={1000 * (1 - pathProgress)}
          style={{ filter: `drop-shadow(0 0 12px ${COLORS.cyan})` }}
        />
        {/* Nodes along the path */}
        {[0, 0.25, 0.5, 0.75, 1].map((p, i) => {
          const cx = 540 + Math.sin(p * Math.PI * 2) * 240;
          const cy = 400 + p * 1200;
          const nodeOpacity = interpolate(pathProgress, [p - 0.1, p], [0, 1], { extrapolateRight: 'clamp' });
          return (
            <circle
              key={i}
              cx={cx}
              cy={cy}
              r={12}
              fill={COLORS.gold}
              opacity={nodeOpacity}
              style={{ filter: `drop-shadow(0 0 20px ${COLORS.gold})` }}
            />
          );
        })}
      </svg>

      {/* Turning point text */}
      <div
        style={{
          position: 'absolute',
          bottom: '18%',
          left: '8%',
          right: '8%',
          opacity: textOpacity,
          transform: `translateY(${textY}px)`,
          textAlign: 'center',
        }}
      >
        <Typography size="title" color={COLORS.white}>
          ماذا لو النظام تولى المهام المتكررة؟
        </Typography>
      </div>
    </div>
  );
};
