import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, spring } from 'remotion';
import { COLORS } from '../constants';
import { Typography } from '../components/Typography';
import { Particles } from '../components/Particles';
import { DataLines } from '../components/DataLines';

export const Scene1: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const localFrame = frame;
  const sceneDuration = 5 * fps;

  const hookOpacity = interpolate(localFrame, [0, 0.5 * fps, 1.5 * fps], [0, 1, 1], { extrapolateRight: 'clamp' });
  const hookY = interpolate(localFrame, [0, 1.5 * fps], [60, 0], { extrapolateRight: 'clamp' });
  const ruleWidth = interpolate(localFrame, [1 * fps, 2.5 * fps], [0, 40], { extrapolateRight: 'clamp' });
  const subOpacity = interpolate(localFrame, [2 * fps, 3 * fps], [0, 1], { extrapolateRight: 'clamp' });

  const clockScale = 1 + Math.sin(localFrame / fps * 2) * 0.02;
  const notifScale = 1 + Math.sin((localFrame / fps) * 3 + 1) * 0.05;

  return (
    <div style={{ position: 'absolute', inset: 0, background: `radial-gradient(ellipse at 50% 40%, ${COLORS.darkSurface} 0%, ${COLORS.navy} 50%, ${COLORS.black} 100%)` }}>
      <Particles count={30} color={COLORS.cyan} speed={0.3} />
      <DataLines count={6} color={COLORS.cyan} animated />

      {/* Busy desk / notification chaos */}
      <div style={{ position: 'absolute', top: '25%', left: '50%', transform: 'translateX(-50%)', width: '80%' }}>
        {/* Notification badges */}
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${20 + i * 15}%`,
              top: `${-5 + i * 8}%`,
              width: 60,
              height: 60,
              borderRadius: 16,
              background: i % 2 === 0 ? COLORS.gold : COLORS.cyan,
              opacity: interpolate(localFrame, [0.5 * fps + i * 0.3 * fps, 1 * fps + i * 0.3 * fps], [0, 0.9], { extrapolateRight: 'clamp' }),
              transform: `scale(${notifScale})`,
              boxShadow: `0 0 20px ${i % 2 === 0 ? COLORS.gold : COLORS.cyan}88`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 24,
              fontWeight: 700,
              color: COLORS.black,
            }}
          >
            {i + 1}
          </div>
        ))}

        {/* Clock */}
        <div
          style={{
            position: 'absolute',
            right: '10%',
            top: '10%',
            width: 80,
            height: 80,
            borderRadius: '50%',
            border: `3px solid ${COLORS.gold}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            opacity: interpolate(localFrame, [0, 0.5 * fps], [0, 0.8], { extrapolateRight: 'clamp' }),
            transform: `scale(${clockScale})`,
            boxShadow: `0 0 25px ${COLORS.gold}66`,
          }}
        >
          <div
            style={{
              width: 2,
              height: 28,
              background: COLORS.gold,
              transformOrigin: 'bottom center',
              transform: `rotate(${localFrame * 6}deg)`,
              position: 'absolute',
              bottom: '50%',
            }}
          />
          <div
            style={{
              width: 2,
              height: 20,
              background: COLORS.cyan,
              transformOrigin: 'bottom center',
              transform: `rotate(${localFrame * 0.5}deg)`,
              position: 'absolute',
              bottom: '50%',
            }}
          />
        </div>
      </div>

      {/* Hook text */}
      <div
        style={{
          position: 'absolute',
          bottom: '20%',
          left: '8%',
          right: '8%',
          opacity: hookOpacity,
          transform: `translateY(${hookY}px)`,
        }}
      >
        <Typography size="hook" color={COLORS.white} style={{ textAlign: 'center' }}>
          كل يوم… شغل بيتكرر ووقت بيضيع
        </Typography>
        <div
          style={{
            height: 3,
            width: `${ruleWidth}%`,
            margin: '24px auto 0',
            background: `linear-gradient(90deg, transparent, ${COLORS.gold}, ${COLORS.cyan})`,
            borderRadius: 2,
          }}
        />
        <div style={{ opacity: subOpacity, marginTop: 20, textAlign: 'center' }}>
          <Typography size="small" color={COLORS.muted}>
            رسائل. متابعة. إدخال بيانات. أخطاء.
          </Typography>
        </div>
      </div>
    </div>
  );
};
