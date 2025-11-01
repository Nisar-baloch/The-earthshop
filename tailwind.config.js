
module.exports = {
  content: [
    "./templates/**/*.html",
    "./*/templates/**/*.html",
    "./static/**/*.js"
  ],
  theme: { extend: {} },
  plugins: [require("daisyui")],
  daisyui: { themes: ["light", "dark", "cupcake"] }
}