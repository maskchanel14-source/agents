/** @type {import('next').NextConfig} */
const API = process.env.INTERNAL_API_URL || "http://127.0.0.1:8000";

const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  // All browser traffic stays same-origin; Next proxies to the FastAPI service.
  // This keeps the HttpOnly auth cookie on this origin and avoids CORS entirely.
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${API}/api/:path*` },
      { source: "/media/:path*", destination: `${API}/media/:path*` },
    ];
  },
  async headers() {
    const headers = [
      { key: "X-Content-Type-Options", value: "nosniff" },
      { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
      // Preview hosts embed the app in a frame on another origin. Production
      // keeps SAMEORIGIN; DEMO_MODE is never set on a real deployment.
      ...(process.env.DEMO_MODE === "1"
        ? []
        : [{ key: "X-Frame-Options", value: "SAMEORIGIN" }]),
    ];
    return [{ source: "/(.*)", headers }];
  },
};

export default nextConfig;
