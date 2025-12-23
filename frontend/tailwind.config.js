/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'navy-dark': '#001f3f',
                'navy-light': '#003366',
                'navy-accent': '#0b1f3b',
            }
        },
    },
    plugins: [],
}
