import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Disable Turbopack to avoid lockfile permission issues
  experimental: {},
};

export default nextConfig;
