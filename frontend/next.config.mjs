const API_TARGET = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const isLocalApi = /^https?:\/\/(localhost|127\.0\.0\.1)(:|\/|$)/.test(API_TARGET);

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Hospedado, o navegador chama /backend/... no próprio site e o Vercel repassa à API.
  // Assim bloqueadores de anúncios não veem uma chamada para outro domínio.
  async rewrites() {
    return isLocalApi ? [] : [{ source: "/backend/:path*", destination: `${API_TARGET}/:path*` }];
  },
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;