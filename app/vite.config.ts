import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// Served at policyengine.org/scorecard (app-v2 vercel.json proxies the
// path to this app's deployment, which serves the same /scorecard/ base —
// see app/vercel.json). BASE_URL-absolute asset and data URLs make the
// bare /scorecard path work without a trailing slash.
export default defineConfig({
  base: "/scorecard/",
  plugins: [react(), tailwindcss()],
});
