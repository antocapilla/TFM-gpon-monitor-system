/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,jsx,ts,tsx}', // Include all JS/TS/JSX/TSX files
    './public/index.html', // Include the main HTML file
  ],
  theme: {
    extend: {
      colors: {
        'custom-blue': '#7EA1BC',
        'custom-blue-2': '#AECAE0',
        'custom-dark-blue': '#344973',
        'custom-dark-blue-2': '#5A6F99',
        'custom-grey': '#D9D9D9',
        'custom-grey-2': '#DDDDDD',
        //'custom-light-blue': '#80A7BF',
        //'custom-light-grey': '#D9DADB',
      },
    },
  },
  plugins: [],
}

