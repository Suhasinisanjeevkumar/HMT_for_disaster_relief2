import { useEffect, useState } from "react";

// Recharts renders raw SVG fill/stroke attributes, which cannot reliably
// resolve CSS custom properties across browsers the way plain CSS/HTML
// can -- so chart color constants are picked in JS against this, rather
// than referencing var(--...) directly in chart props. Everything outside
// charts (badges, cards, nav, etc.) uses the CSS variables in index.css
// directly and needs no JS at all.
export function usePrefersDark(): boolean {
  const [prefersDark, setPrefersDark] = useState(
    () => typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches
  );

  useEffect(() => {
    const mql = window.matchMedia("(prefers-color-scheme: dark)");
    const listener = (e: MediaQueryListEvent) => setPrefersDark(e.matches);
    mql.addEventListener("change", listener);
    return () => mql.removeEventListener("change", listener);
  }, []);

  return prefersDark;
}
