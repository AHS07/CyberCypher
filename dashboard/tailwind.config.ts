import type { Config } from "tailwindcss";

export default {
    darkMode: ["class"],
    content: [
        "./pages/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "hsl(222, 47%, 11%)",
                foreground: "hsl(213, 31%, 91%)",
                card: "hsl(222, 47%, 15%)",
                "card-foreground": "hsl(213, 31%, 91%)",
                primary: {
                    DEFAULT: "hsl(217, 91%, 60%)",
                    foreground: "hsl(213, 31%, 91%)",
                },
                secondary: {
                    DEFAULT: "hsl(270, 70%, 65%)",
                    foreground: "hsl(213, 31%, 91%)",
                },
                success: {
                    DEFAULT: "hsl(142, 71%, 45%)",
                    foreground: "hsl(213, 31%, 91%)",
                },
                warning: {
                    DEFAULT: "hsl(38, 92%, 50%)",
                    foreground: "hsl(222, 47%, 11%)",
                },
                danger: {
                    DEFAULT: "hsl(0, 72%, 51%)",
                    foreground: "hsl(213, 31%, 91%)",
                },
                muted: {
                    DEFAULT: "hsl(223, 23%, 23%)",
                    foreground: "hsl(213, 20%, 70%)",
                },
                accent: {
                    DEFAULT: "hsl(217, 91%, 60%)",
                    foreground: "hsl(213, 31%, 91%)",
                },
                border: "hsl(223, 23%, 23%)",
            },
            fontFamily: {
                sans: ["var(--font-inter)", "system-ui", "sans-serif"],
                mono: ["var(--font-jetbrains-mono)", "monospace"],
            },
            borderRadius: {
                lg: "0.75rem",
                md: "0.5rem",
                sm: "0.375rem",
            },
            boxShadow: {
                glow: "0 0 20px rgba(96, 165, 250, 0.3)",
                "glow-purple": "0 0 20px rgba(168, 85, 247, 0.3)",
                "glow-green": "0 0 20px rgba(34, 197, 94, 0.3)",
            },
            animation: {
                pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                "pulse-fast": "pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite",
                shimmer: "shimmer 2s linear infinite",
            },
            keyframes: {
                shimmer: {
                    from: { backgroundPosition: "0 0" },
                    to: { backgroundPosition: "-200% 0" },
                },
            },
        },
    },
    plugins: [],
} satisfies Config;
