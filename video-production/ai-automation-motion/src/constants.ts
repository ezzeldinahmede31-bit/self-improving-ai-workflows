export const WIDTH = 1080;
export const HEIGHT = 1920;
export const FPS = 30;
export const DURATION_IN_SECONDS = 36;

export const COLORS = {
  navy: '#0A1128',
  black: '#050505',
  gold: '#D4AF37',
  cyan: '#00CFE8',
  white: '#FFFFFF',
  muted: '#9BA8C3',
  darkSurface: '#111D38',
} as const;

export const SCENES = [
  { start: 0, end: 5, name: 'hook' },
  { start: 5, end: 10, name: 'problem' },
  { start: 10, end: 15, name: 'turning' },
  { start: 15, end: 22, name: 'process' },
  { start: 22, end: 29, name: 'comparison' },
  { start: 29, end: 36, name: 'closing' },
] as const;

export const COPY = {
  hook: 'كل يوم… شغل بيتكرر ووقت بيضيع',
  problem: 'رسائل. متابعة. إدخال بيانات. أخطاء.',
  turning: 'ماذا لو النظام تولى المهام المتكررة؟',
  processSteps: [
    'رسالة عميل',
    'فهم الطلب',
    'تسجيل البيانات',
    'تحديد الخطوة التالية',
    'متابعة تلقائية',
  ],
  closing1: 'الأتمتة مش مجرد أداة…',
  closing2: 'دي طريقة أذكى لإدارة الشغل',
  closing3: 'ابدأ بالمشكلة، وابنِ النظام المناسب لها',
} as const;
