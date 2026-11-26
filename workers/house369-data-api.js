/**
 * House369 Data API - Cloudflare Worker
 * Serves verified HK property datasets with high-speed Edge Caching, CORS, and filtering.
 */

const GITHUB_RAW_BASE = "https://raw.githubusercontent.com/sleepingarhat/directhk-property-data/main/data";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, HEAD, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  "Content-Type": "application/json; charset=utf-8"
};

async function fetchFromGithub(filename, cacheTtlSeconds = 300) {
  const url = `${GITHUB_RAW_BASE}/${filename}`;
  const resp = await fetch(url, {
    cf: {
      cacheTtl: cacheTtlSeconds,
      cacheEverything: true
    },
    headers: {
      "User-Agent": "House369-Cloudflare-Worker"
    }
  });
  if (!resp.ok) {
    throw new Error(`Failed to fetch ${filename} from upstream: ${resp.status}`);
  }
  return resp.json();
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS_HEADERS });
    }

    try {
      if (url.pathname === "/api/transactions") {
        const data = await fetchFromGithub("latest_transactions.json", 180);
        const limit = parseInt(url.searchParams.get("limit") || "100", 10);
        const district = url.searchParams.get("district");
        const type = url.searchParams.get("type"); // 買賣 / 出租

        let records = data.records || [];
        if (district) {
          records = records.filter(r => r.district && r.district.includes(district));
        }
        if (type) {
          records = records.filter(r => r.transaction_type === type);
        }
        if (limit > 0) {
          records = records.slice(0, limit);
        }

        return new Response(JSON.stringify({
          metadata: {
            ...data.metadata,
            returned_records: records.length,
            edge_cache: "HIT"
          },
          records
        }), {
          headers: {
            ...CORS_HEADERS,
            "Cache-Control": "public, max-age=180, s-maxage=300"
          }
        });
      }

      if (url.pathname === "/api/estates") {
        const data = await fetchFromGithub("centaline_estates_master.json", 3600);
        const q = url.searchParams.get("q")?.toLowerCase();
        const region = url.searchParams.get("region"); // HK / KLN / NT

        let estates = data.estates || [];
        if (region) {
          estates = estates.filter(e => e.district_region === region);
        }
        if (q) {
          estates = estates.filter(e =>
            (e.estate_name_tc && e.estate_name_tc.toLowerCase().includes(q)) ||
            (e.estate_name_en && e.estate_name_en.toLowerCase().includes(q)) ||
            (e.address_tc && e.address_tc.toLowerCase().includes(q))
          );
        }

        return new Response(JSON.stringify({
          metadata: {
            ...data.metadata,
            returned_estates: estates.length,
            edge_cache: "HIT"
          },
          estates
        }), {
          headers: {
            ...CORS_HEADERS,
            "Cache-Control": "public, max-age=3600, s-maxage=7200"
          }
        });
      }

      if (url.pathname === "/api/landreg") {
        const data = await fetchFromGithub("landreg_monthly_stats.json", 86400);
        return new Response(JSON.stringify({
          metadata: {
            ...data.metadata,
            edge_cache: "HIT"
          },
          data: data.data || []
        }), {
          headers: {
            ...CORS_HEADERS,
            "Cache-Control": "public, max-age=86400, s-maxage=86400"
          }
        });
      }

      if (url.pathname === "/api/health" || url.pathname === "/") {
        return new Response(JSON.stringify({
          service: "House369 Data Gateway API",
          status: "healthy",
          timestamp: new Date().toISOString(),
          endpoints: [
            "/api/transactions",
            "/api/estates",
            "/api/landreg",
            "/api/health"
          ]
        }, null, 2), {
          headers: CORS_HEADERS
        });
      }

      return new Response(JSON.stringify({ error: "Endpoint not found" }), {
        status: 404,
        headers: CORS_HEADERS
      });

    } catch (err) {
      return new Response(JSON.stringify({
        error: "Internal Server Error",
        detail: err.message
      }), {
        status: 500,
        headers: CORS_HEADERS
      });
    }
  }
};
