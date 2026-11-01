import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate } from 'remotion';
import { COLORS } from '../constants';
import { Typography } from '../components/Typography';
import { Particles } from '../components/Particles';
import { DataLines } from '../components/DataLines';

export const Scene6: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const localFrame = frame - 29 * fps;

  const opacity = interpolate(localFrame, [0, 0.5 * fps], [0, 1], { extrapolateRight: 'clamp' });

  const orbScale = interpolate(localFrame, [0, 2 * fps], [0.6, 1], { extrapolateRight: 'clamp' });
  const orbOpacity = interpolate(localFrame, [0, 1 * fps], [0, 1], { extrapolateRight: 'clamp' });

  const text1Opacity = interpolate(localFrame, [0.5 * fps, 1.5 * fps], [0, 1], { extrapolateRight: 'clamp' });
  const text1Y = interpolate(localFrame, [0.5 * fps, 1.5 * fps], [30, 0], { extrapolateRight: 'clamp' });

  const text2Opacity = interpolate(localFrame, [1.5 * fps, 2.5 * fps], [0, 1], { extrapolateRight: 'clamp' });
  const text2Y = interpolate(localFrame, [1.5 * fps, 2.5 * fps], [30, 0], { extrapolateRight: 'clamp' });

  const text3Opacity = interpolate(localFrame, [3 * fps, 4 * fps], [0, 1], { extrapolateRight: 'clamp' });
  const text3Y = interpolate(localFrame, [3 * fps, 4 * fps], [30, 0], { extrapolateRight: 'clamp' });

  const particleScale = 1 + Math.sin(localFrame / fps * 0.5) * 0.02;

  return (
    <div style={{ position: 'absolute', inset: 0, background: `radial-gradient(ellipse at 50% 50%, ${COLORS.navy} 0%, ${COLORS.black} 100%)`, opacity }}>
      <Particles count={60} color={COLORS.cyan} speed={0.15} size={4} />
      <DataLines count={12} color={COLORS.gold} animated />

      {/* Central orb */}
      <div
        style={{
          position: 'absolute',
          top: '35%',
          left: '50%',
          width: 200,
          height: 200,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${COLORS.cyan}22, ${COLORS.gold}11, transparent 70%)`,
          border: `2px solid ${COLORS.gold}44`,
          opacity: orbOpacity,
          boxShadow: `0 0 60px ${COLORS.cyan}33, 0 0 120px ${COLORS.gold}22, inset 0 0 40px ${COLORS.cyan}11`,
          transform: `translate(-50%, -50%) scale(${orbScale * particleScale})`,
        }}
      />

      {/* Closing text 1 */}
      <div
        style={{
          position: 'absolute',
          top: '52%',
          left: '8%',
          right: '8%',
          opacity: text1Opacity,
          transform: `translateY(${text1Y}px)`,
          textAlign: 'center',
        }}
      >
        <Typography size="title" color={COLORS.white}>
          الأتمتة مش مجرد أداة…
        </Typography>
      </div>

      {/* Closing text 2 */}
      <div
        style={{
          position: 'absolute',
          top: '62%',
          left: '8%',
          right: '8%',
          opacity: text2Opacity,
          transform: `translateY(${text2Y}px)`,
          textAlign: 'center',
        }}
      >
        <Typography size="title" color={COLORS.gold}>
          دي طريقة أذكى لإدارة الشغل
        </Typography>
      </div>

      {/* Closing text 3 */}
      <div
        style={{
          position: 'absolute',
          bottom: '12%',
          left: '8%',
          right: '8%',
          opacity: text3Opacity,
          transform: `translateY(${text3Y}px)`,
          textAlign: 'center',
        }}
      >
        <Typography size="body" color={COLORS.muted}>
          ابدأ بالمشكلة، وابنِ النظام المناسب لها
        </Typography>
        <div
          style={{
            height: 2,
            width: '60%',
            margin: '20px auto 0',
            background: `linear-gradient(90deg, transparent, ${COLORS.gold}, ${COLORS.cyan}, transparent)`,
            borderRadius: 1,
            boxShadow: `0 0 10px ${COLORS.gold}66`,
          }}
        />
      </div>
    </div>
  );
};
