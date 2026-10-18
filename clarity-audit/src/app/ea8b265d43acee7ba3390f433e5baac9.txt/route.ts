// IndexNow ownership key (see https://www.indexnow.org/documentation)
export async function GET() {
  return new Response("ea8b265d43acee7ba3390f433e5baac9", { headers: { "Content-Type": "text/plain; charset=utf-8" } });
}
