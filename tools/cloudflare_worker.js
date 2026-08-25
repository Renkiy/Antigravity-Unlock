/**
 * Antigravity Cloudflare Worker L7 Relay
 * 
 * Назначение:
 * 1. Проксирование запросов к Gemini Code Assist / Antigravity из зарубежных датацентров Cloudflare.
 * 2. Полное удаление геолокационных заголовков (CF-Connecting-IP, X-Forwarded-For).
 * 3. Перехват и подмена ответа эндпоинта :loadCodeAssist для российских Google-аккаунтов:
 *    автоматическая замена статусов 'ineligible' / 'UNSUPPORTED' на 'eligible' / 'ALLOWED'.
 */

const TARGET_HOST = "cloudcode-pa.googleapis.com";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Перенаправляем запрос на официальный хост Google Cloud Code
    url.hostname = TARGET_HOST;
    url.protocol = "https:";

    // Формируем чистые заголовки без гео-меток
    const newHeaders = new Headers(request.headers);
    newHeaders.set("Host", TARGET_HOST);
    newHeaders.delete("cf-connecting-ip");
    newHeaders.delete("cf-ipcountry");
    newHeaders.delete("x-forwarded-for");
    newHeaders.delete("x-real-ip");

    // Клонируем запрос
    const newRequest = new Request(url.toString(), {
      method: request.method,
      headers: newHeaders,
      body: request.body,
      redirect: "follow"
    });

    try {
      const response = await fetch(newRequest);

      // Проверяем, является ли запрос проверкой статуса аккаунта (:loadCodeAssist)
      if (url.pathname.includes("loadCodeAssist")) {
        const contentType = response.headers.get("content-type") || "";
        
        if (contentType.includes("application/json") || contentType.includes("text/")) {
          let text = await response.text();
          
          // Подменяем блокирующие статусы аккаунта на разрешающие
          text = text
            .replaceAll('"ineligible"', '"eligible"')
            .replaceAll('"INELIGIBLE"', '"ALLOWED"')
            .replaceAll('"UNSUPPORTED"', '"ALLOWED"');

          const patchedHeaders = new Headers(response.headers);
          patchedHeaders.delete("content-length");

          return new Response(text, {
            status: 200,
            statusText: "OK",
            headers: patchedHeaders
          });
        }
      }

      // Для потокового стриминга токенов (gRPC-Web / Chunked Transfer) возвращаем сквозной ответ
      return response;

    } catch (err) {
      return new Response(JSON.stringify({ error: "Worker Relay Error", details: err.message }), {
        status: 502,
        headers: { "Content-Type": "application/json" }
      });
    }
  }
};
