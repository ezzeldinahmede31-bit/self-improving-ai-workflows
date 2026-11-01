import React from 'react';
import { AbsoluteFill } from 'remotion';

interface TypographyProps {
  children: React.ReactNode;
  size?: 'hook' | 'title' | 'body' | 'small';
  color?: string;
  opacity?: number;
  style?: React.CSSProperties;
}

export const Typography: React.FC<TypographyProps> = ({
  children,
  size = 'body',
  color = '#FFFFFF',
  opacity = 1,
  style = {},
}) => {
  const sizes = {
    hook: { fontSize: 72, fontWeight: 700, lineHeight: 1.3, letterSpacing: '-2px' },
    title: { fontSize: 64, fontWeight: 700, lineHeight: 1.4, letterSpacing: '-1.5px' },
    body: { fontSize: 44, fontWeight: 500, lineHeight: 1.6, letterSpacing: '-0.5px' },
    small: { fontSize: 32, fontWeight: 500, lineHeight: 1.5, letterSpacing: '0px' },
  };

  return (
    <div
      style={{
        fontFamily: '"Cairo", "Tajawal", "Noto Sans Arabic", Tahoma, Arial, sans-serif',
        direction: 'rtl',
        textAlign: 'right',
        color,
        opacity,
        ...sizes[size],
        ...style,
      }}
    >
      {children}
    </div>
  );
};
