// noinspection ES6UnusedImports
import { Config } from "tailwindcss"

export default {
  content: ["./app/applets/**/templates/*.{html,js,ts}"],
  theme: {
    fontSize: {
      xs: ["0.75rem", { lineHeight: "1rem" }],
      sm: ["0.875rem", { lineHeight: "1.5rem" }],
      base: ["1rem", { lineHeight: "1.5rem" }],
      lg: ["1.125rem", { lineHeight: "2rem" }],
      xl: ["1.25rem", { lineHeight: "2rem" }],
      "2xl": ["1.5rem", { lineHeight: "2.5rem" }],
      "3xl": ["2rem", { lineHeight: "2.5rem" }],
      "4xl": ["2.5rem", { lineHeight: "3rem" }],
      "5xl": ["3rem", { lineHeight: "3.5rem" }],
      "6xl": ["4rem", { lineHeight: "1" }],
      "7xl": ["5rem", { lineHeight: "1" }],
      "8xl": ["6rem", { lineHeight: "1" }],
      "9xl": ["8rem", { lineHeight: "1" }],
    },
    extend: {
      colors: {
        "primary": "#4584b6",
        "secondary": "#ffde57",
        "tertiary": "#646464",
      },
      borderRadius: {
        "4xl": "2rem",
        "5xl": "2.5rem",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        display: ["DM Sans", "sans-serif"],
      },
      maxWidth: {
        "2xl": "40rem",
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
