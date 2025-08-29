// Color Scheme Utility
// Based on the provided color palette: #272757, #8686AC, #505081, #0F0E47

export const colors = {
  // Primary Color Scheme
  primary: {
    dark: '#0F0E47',
    main: '#272757', 
    medium: '#505081',
    light: '#8686AC',
  },
  
  // Semantic Colors
  background: {
    primary: '#0F0E47',
    secondary: '#272757',
    surface: 'rgba(134, 134, 172, 0.1)',
    surfaceSecondary: 'rgba(80, 80, 129, 0.2)',
  },
  
  // Text Colors
  text: {
    primary: '#ffffff',
    secondary: 'rgba(255, 255, 255, 0.8)',
    muted: 'rgba(255, 255, 255, 0.6)',
  },
  
  // Border Colors
  border: {
    primary: 'rgba(134, 134, 172, 0.3)',
    secondary: 'rgba(255, 255, 255, 0.2)',
  },
  
  // Shadow Colors
  shadow: {
    primary: 'rgba(15, 14, 71, 0.3)',
    secondary: 'rgba(39, 39, 87, 0.2)',
  },
  
  // Gradients
  gradient: {
    primary: 'linear-gradient(135deg, #272757 0%, #8686AC 25%, #505081 75%, #0F0E47 100%)',
    button: 'linear-gradient(135deg, #505081, #0F0E47)',
    surface: 'linear-gradient(135deg, rgba(39, 39, 87, 0.8), rgba(134, 134, 172, 0.1))',
  }
};

// CSS Variables mapping for use in styled-components
export const cssVars = {
  '--primary-dark': colors.primary.dark,
  '--primary-main': colors.primary.main,
  '--primary-medium': colors.primary.medium,
  '--primary-light': colors.primary.light,
  '--background-primary': colors.background.primary,
  '--background-secondary': colors.background.secondary,
  '--text-primary': colors.text.primary,
  '--text-secondary': colors.text.secondary,
  '--text-muted': colors.text.muted,
  '--border-primary': colors.border.primary,
  '--border-secondary': colors.border.secondary,
  '--shadow-primary': colors.shadow.primary,
  '--shadow-secondary': colors.shadow.secondary,
};

// Helper function to get CSS variable with fallback
export const getColor = (path: string): string => {
  const keys = path.split('.');
  let current: any = colors;
  
  for (const key of keys) {
    current = current[key];
    if (!current) return '#000000'; // fallback
  }
  
  return current;
};

export default colors;
