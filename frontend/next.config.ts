import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: process.env.NEXT_OUTPUT === "export" ? "export" : "standalone",
  images: {
    // Allow the Next.js <Image> component to load from the bundled
    // FastAPI static server during local Electron runs.
    unoptimized: true,
  },
};

export default nextConfig;
