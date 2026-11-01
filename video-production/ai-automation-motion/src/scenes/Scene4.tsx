import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate } from 'remotion';
import { COLORS } from '../constants';
import { Typography } from '../components/Typography';
import { Particles } from '../components/Particles';

export const Scene4: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const localFrame = frame - 15 * fps;

  const opacity = interpolate(localFrame, [0, 0.5 * fps], [0, 1], { extrapolateRight: 'clamp' });

  const steps = [
    { label: 'رسالة عميل', delay: 0, color: COLORS.cyan },
    { label: 'فهم الطلب', delay: 0.8, color: COLORS.gold },
    { label: 'تسجيل البيانات', delay: 1.6, color: COLORS.cyan },
    { label: 'تحديد الخطوة التالية', delay: 2.4, color: COLORS.gold },
    { label: 'متابعة تلقائية', delay: 3.2, color: COLORS.cyan },
  ];

  return (
    <div style={{ position: 'absolute', inset: 0, background: `radial-gradient(ellipse at 50% 40%, ${COLORS.darkSurface} 0%, ${COLORS.navy} 50%, ${COLORS.black} 100%)`, opacity }}>
      <Particles count={25} color={COLORS.gold} speed={0.4} />

      {/* Process flow */}
      <div style={{ position: 'absolute', top: '15%', left: '8%', right: '8%', bottom: '25%' }}>
        {steps.map((step, i) => {
          const delay = step.delay * fps;
          const stepOpacity = interpolate(localFrame, [delay, delay + 0.5 * fps], [0, 1], { extrapolateRight: 'clamp' });
          const stepX = interpolate(localFrame, [delay, delay + 0.6 * fps], [i % 2 === 0 ? -80 : 80, 0], { extrapolateRight: 'clamp' });
          const connectorOpacity = interpolate(localFrame, [delay + 0.4 * fps, delay + 0.7 * fps], [0, 0.6], { extrapolateRight: 'clamp' });

          return (
            <React.Fragment key={i}>
              {/* Connector line */}
              {i > 0 && (
                <div
                  style={{
                    position: 'absolute',
                    left: '50%',
                    top: `${10 + (i - 1) * 16 + 8}%`,
                    width: 2,
                    height: '8%',
                    background: `linear-gradient(180deg, ${step.color}88, ${step.color}44)`,
                    opacity: connectorOpacity,
                    transform: 'translateX(-50%)',
                    boxShadow: `0 0 8px ${step.color}66`,
                  }}
                />
              )}
              {/* Step card */}
              <div
                style={{
                  position: 'absolute',
                  left: '50%',
                  top: `${10 + i * 16}%`,
                  transform: `translateX(-50%) translateX(${stepX}px)`,
                  opacity: stepOpacity,
                  width: '70%',
                  padding: 20,
                  background: `linear-gradient(135deg, ${COLORS.navy}dd, ${COLORS.darkSurface}cc)`,
                  border: `1px solid ${step.color}44`,
                  borderRadius: 14,
                  boxShadow: `0 8px 32px ${COLORS.black}66, 0 0 20px ${step.color}22`,
                  backdropFilter: 'blur(8px)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 16,
                }}
              >
                <div
                  style={{
                    width: 40,
                    height: 40,
                    borderRadius: 10,
                    background: `linear-gradient(135deg, ${step.color}, ${step.color}88)`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 20,
                    fontWeight: 700,
                    color: COLORS.black,
                    boxShadow: `0 0 15px ${step.color}66`,
                  }}
                >
                  {i + 1}
                </div>
                <div style={{ fontSize: 28, fontWeight: 600, color: COLORS.white }}>
                  {step.label}
                </div>
              </div>
            </React.Fragment>
          );
        })}
      </div>

      {/* Subtitle */}
      <div
        style={{
          position: 'absolute',
          bottom: '12%',
          left: '8%',
          right: '8%',
          textAlign: 'center',
        }}
      >
        <Typography size="small" color={COLORS.muted}>
          عناصر تتحرك وتتصل — واجهات تجريدية أنيقة
        </Typography>
      </div>
    </div>
  );
};
