import React from 'react';
import { useCurrentFrame, useVideoConfig } from 'remotion';

interface DataLinesProps {
  count?: number;
  color?: string;
  animated?: boolean;
}

export const DataLines: React.FC<DataLinesProps> = ({
  count = 8,
  color = '#00CFE8',
  animated = true,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const lines = Array.from({ length: count }, (_, i) => {
    const y = 200 + i * 180;
    const width = 400 + Math.sin(i * 0.7 + t * 0.5) * 100;
    const opacity = animated ? 0.3 + Math.sin(t * 0.8 + i) * 0.15 : 0.4;
    const glow = animated ? 4 + Math.sin(t * 1.2 + i) * 2 : 4;

    return { y, width, opacity, glow, index: i };
  });

  return (
    <svg
      viewBox="0 0 1080 1920"
      style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}
    >
      {lines.map((line, i) => (
        <g key={i}>
          <line
            x1={100}
            y1={line.y}
            x2={100 + line.width}
            y2={line.y}
            stroke={color}
            strokeWidth={2}
            opacity={line.opacity}
            style={{ filter: `drop-shadow(0 0 ${line.glow}px ${color})` }}
          />
          <circle
            cx={100 + line.width}
            cy={line.y}
            r={4}
            fill={color}
            opacity={line.opacity + 0.2}
            style={{ filter: `drop-shadow(0 0 ${line.glow * 2}px ${color})` }}
          />
        </g>
      ))}
    </svg>
  );
};
