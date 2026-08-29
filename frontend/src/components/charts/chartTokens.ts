// JS-side mirror of the CSS custom properties in index.css -- see
// useColorScheme.ts for why chart color props can't just reference
// var(--...) the way the rest of the UI does.
export function chartTokens(dark: boolean) {
  return {
    seriesBlue: dark ? "#3987e5" : "#2a78d6",
    good: dark ? "#0ca30c" : "#0ca30c",
    warning: dark ? "#fab219" : "#fab219",
    critical: dark ? "#d03b3b" : "#d03b3b",
    grid: dark ? "#2c2c2a" : "#e1e0d9",
    axis: "#898781",
    tooltipBg: dark ? "#232322" : "#ffffff",
    tooltipBorder: dark ? "rgba(255,255,255,0.10)" : "rgba(11,11,11,0.10)",
    tooltipText: dark ? "#ffffff" : "#0b0b0b",
  };
}
