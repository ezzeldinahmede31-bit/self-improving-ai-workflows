import { COLORS } from '../constants';

export const theme = {
  colors: COLORS,
  fontFamily: '"Cairo", "Tajawal", "Noto Sans Arabic", Tahoma, Arial, sans-serif',
  rtl: true,
} as const;

export const typography = {
  hook: { fontSize: 72, fontWeight: 700, lineHeight: 1.3, letterSpacing: '-2px' },
  title: { fontSize: 64, fontWeight: 700, lineHeight: 1.4, letterSpacing: '-1.5px' },
  body: { fontSize: 44, fontWeight: 500, lineHeight: 1.6, letterSpacing: '-0.5px' },
  small: { fontSize: 32, fontWeight: 500, lineHeight: 1.5, letterSpacing: '0px' },
} as const;

export const spacing = {
  xs: 8,
  sm: 16,
  md: 24,
  lg: 40,
  xl: 64,
  xxl: 96,
} as const;
