import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate } from 'remotion';
import { COLORS } from '../constants';
import { Typography } from '../components/Typography';
import { Particles } from '../components/Particles';

export const Scene5: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const localFrame = frame - 22 * fps;

  const opacity = interpolate(localFrame, [0, 0.5 * fps], [0, 1], { extrapolateRight: 'clamp' });

  const dividerPos = interpolate(localFrame, [0.5 * fps, 2 * fps], [50, 50], { extrapolateRight: 'clamp' });
  const leftOpacity = interpolate(localFrame, [0, 1 * fps], [0, 1], { extrapolateRight: 'clamp' });
  const rightOpacity = interpolate(localFrame, [1 * fps, 2 * fps], [0, 1], { extrapolateRight: 'clamp' });

  // Metrics bars (no fake numbers, just visual bars)
  const workTimeBar = interpolate(localFrame, [2 * fps, 3.5 * fps], [0.8, 0.3], { extrapolateRight: 'clamp' });
  const errorBar = interpolate(localFrame, [2 * fps, 3.5 * fps], [0.7, 0.15], { extrapolateRight: 'clamp' });
  const followBar = interpolate(localFrame, [2 * fps, 3.5 * fps], [0.2, 0.9], { extrapolateRight: 'clamp' });

  return (
    <div style={{ position: 'absolute', inset: 0, background: COLORS.black, opacity }}>
      {/* Left side - chaotic/dark */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          width: '50%',
          height: '100%',
          background: `linear-gradient(135deg, ${COLORS.navy} 0%, ${COLORS.black} 100%)`,
          opacity: leftOpacity,
          borderRight: `2px solid ${COLORS.cyan}22`,
        }}
      >
        <div style={{ position: 'absolute', top: '15%', left: '10%', right: '10%', textAlign: 'center' }}>
          <Typography size="body" color={COLORS.muted}>
            قبل
          </Typography>
        </div>
        {/* Chaotic elements */}
        {[0, 1, 2, 3, 4].map((i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${15 + i * 12}%`,
              top: `${30 + (i % 3) * 15}%`,
              width: 60 + i * 10,
              height: 40 + i * 8,
              background: `${COLORS.navy}66`,
              border: `1px solid ${COLORS.cyan}22`,
              borderRadius: 6,
              transform: `rotate(${i * 12 - 20}deg)`,
              opacity: 0.5,
            }}
          />
        ))}
      </div>

      {/* Right side - organized/bright */}
      <div
        style={{
          position: 'absolute',
          right: 0,
          top: 0,
          width: '50%',
          height: '100%',
          background: `linear-gradient(135deg, ${COLORS.darkSurface} 0%, ${COLORS.navy} 100%)`,
          opacity: rightOpacity,
        }}
      >
        <div style={{ position: 'absolute', top: '15%', left: '10%', right: '10%', textAlign: 'center' }}>
          <Typography size="body" color={COLORS.gold}>
            بعد
          </Typography>
        </div>
        {/* Organized elements */}
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: '15%',
              top: `${35 + i * 15}%`,
              width: '70%',
              height: 30,
              background: `linear-gradient(90deg, ${COLORS.cyan}22, ${COLORS.cyan}44)`,
              border: `1px solid ${COLORS.cyan}44`,
              borderRadius: 6,
              opacity: 0.8,
              boxShadow: `0 0 10px ${COLORS.cyan}22`,
            }}
          />
        ))}
      </div>

      {/* Divider line */}
      <div
        style={{
          position: 'absolute',
          left: '50%',
          top: 0,
          width: 2,
          height: '100%',
          background: `linear-gradient(180deg, transparent, ${COLORS.gold}, transparent)`,
          transform: 'translateX(-50%)',
          opacity: 0.6,
          boxShadow: `0 0 15px ${COLORS.gold}66`,
        }}
      />

      {/* Metrics bars */}
      <div
        style={{
          position: 'absolute',
          bottom: '18%',
          left: '8%',
          right: '8%',
          display: 'flex',
          justifyContent: 'space-around',
          gap: 20,
        }}
      >
        {[
          { label: 'وقت العمل', value: workTimeBar, color: COLORS.cyan },
          { label: 'الأخطاء', value: errorBar, color: COLORS.gold },
          { label: 'المتابعة', value: followBar, color: COLORS.cyan },
        ].map((metric, i) => (
          <div key={i} style={{ flex: 1, textAlign: 'center' }}>
            <div
              style={{
                width: '100%',
                height: 8,
                background: `${COLORS.navy}88`,
                borderRadius: 4,
                overflow: 'hidden',
                marginBottom: 8,
              }}
            >
              <div
                style={{
                  width: `${metric.value * 100}%`,
                  height: '100%',
                  background: `linear-gradient(90deg, ${metric.color}, ${metric.color}88)`,
                  borderRadius: 4,
                  boxShadow: `0 0 10px ${metric.color}66`,
                  transition: 'width 0.3s ease',
                }}
              />
            </div>
            <Typography size="small" color={COLORS.muted}>
              {metric.label}
            </Typography>
          </div>
        ))}
      </div>
    </div>
  );
};
