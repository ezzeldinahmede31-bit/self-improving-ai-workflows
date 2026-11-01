import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate } from 'remotion';
import { COLORS } from '../constants';
import { Typography } from '../components/Typography';
import { Particles } from '../components/Particles';
import { DataLines } from '../components/DataLines';

export const Scene2: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const localFrame = frame - 5 * fps;
  const sceneDuration = 5 * fps;

  const opacity = interpolate(localFrame, [0, 0.5 * fps], [0, 1], { extrapolateRight: 'clamp' });

  const messages = [
    { x: 8, y: 20, delay: 0 },
    { x: 60, y: 35, delay: 0.3 },
    { x: 25, y: 50, delay: 0.6 },
    { x: 75, y: 65, delay: 0.9 },
    { x: 15, y: 80, delay: 1.2 },
    { x: 50, y: 70, delay: 1.5 },
  ];

  const textOpacity = interpolate(localFrame, [1 * fps, 2 * fps], [0, 1], { extrapolateRight: 'clamp' });
  const textY = interpolate(localFrame, [1 * fps, 2 * fps], [40, 0], { extrapolateRight: 'clamp' });

  return (
    <div style={{ position: 'absolute', inset: 0, background: `radial-gradient(ellipse at 30% 30%, ${COLORS.darkSurface} 0%, ${COLORS.navy} 40%, ${COLORS.black} 100%)`, opacity }}>
      <Particles count={50} color={COLORS.cyan} speed={0.8} />
      <DataLines count={10} color={COLORS.cyan} animated />

      {/* Accumulating message cards */}
      {messages.map((msg, i) => {
        const delay = msg.delay * fps;
        const cardOpacity = interpolate(localFrame, [delay, delay + 0.5 * fps], [0, 0.85], { extrapolateRight: 'clamp' });
        const cardScale = interpolate(localFrame, [delay, delay + 0.5 * fps], [0.8, 1], { extrapolateRight: 'clamp' });
        const cardX = interpolate(localFrame, [delay, delay + 0.8 * fps], [msg.x + 20, msg.x], { extrapolateRight: 'clamp' });

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: `${cardX}%`,
              top: `${msg.y}%`,
              width: 280,
              padding: 16,
              background: `linear-gradient(135deg, ${COLORS.navy}ee, ${COLORS.darkSurface}dd)`,
              border: `1px solid ${COLORS.cyan}33`,
              borderRadius: 12,
              opacity: cardOpacity,
              transform: `scale(${cardScale})`,
              boxShadow: `0 8px 32px ${COLORS.black}88, 0 0 15px ${COLORS.cyan}22`,
              backdropFilter: 'blur(8px)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
              <div style={{ width: 32, height: 32, borderRadius: 8, background: i % 2 === 0 ? COLORS.gold : COLORS.cyan, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 700, color: COLORS.black }}>
                {['م', 'ع', 'س', 'ي', 'أ', 'ب'][i]}
              </div>
              <div style={{ fontSize: 14, color: COLORS.muted, fontWeight: 500 }}>
                {'منذ ' + (i + 1) + ' دقيقة'}
              </div>
            </div>
            <div style={{ fontSize: 16, color: COLORS.white, lineHeight: 1.5 }}>
              {['مساء الخير، عايزة أحجز كشف', 'فيه ميعاد بكرة؟', 'ممكن أعرف مواعيد العيادة؟', 'كنت سألت عن الحجز', 'متى يمكنني الحضور؟', 'أحتاج تأكيد موعد'][i]}
            </div>
          </div>
        );
      })}

      {/* Overlapping work paths - chaotic lines */}
      <svg style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', opacity: 0.3 }}>
        {[0, 1, 2, 3, 4].map((i) => (
          <path
            key={i}
            d={`M ${100 + i * 200} ${200 + i * 300} Q ${500 + i * 100} ${600 + i * 200} ${900 - i * 100} ${1200 + i * 100}`}
            stroke={i % 2 === 0 ? COLORS.gold : COLORS.cyan}
            strokeWidth={1.5}
            fill="none"
            opacity={0.4 + Math.sin(frame / 30 + i) * 0.2}
          />
        ))}
      </svg>

      {/* Problem text */}
      <div
        style={{
          position: 'absolute',
          bottom: '15%',
          left: '8%',
          right: '8%',
          opacity: textOpacity,
          transform: `translateY(${textY}px)`,
          textAlign: 'center',
        }}
      >
        <Typography size="title" color={COLORS.white}>
          رسائل. متابعة. إدخال بيانات. أخطاء.
        </Typography>
      </div>
    </div>
  );
};
