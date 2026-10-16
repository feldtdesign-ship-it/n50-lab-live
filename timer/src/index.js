// N50 lab timer. Every 15 minutes, asks GitHub to run the "Lab data from SiteView"
// workflow in feldtdesign-ship-it/n50-lab-live. GitHub does the reading and upload.
// Cloudflare can't reach SiteView directly (port 8998), so this only starts the run.
// GH_TOKEN is a Cloudflare secret: a fine-grained GitHub token limited to this repo, Actions write.

const URL = "https://api.github.com/repos/feldtdesign-ship-it/n50-lab-live/actions/workflows/lab-data.yml/dispatches";

async function poke(env) {
  const r = await fetch(URL, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.GH_TOKEN}`,
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "n50-lab-timer",
    },
    body: JSON.stringify({ ref: "main" }),
  });
  if (r.status !== 204) throw new Error(`GitHub said ${r.status}: ${(await r.text()).slice(0, 200)}`);
  return r.status;
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(poke(env));
  },
  // A visit to the worker's address just says it's alive. It never starts a run.
  async fetch() {
    return new Response("N50 lab timer: runs every 15 minutes.\n", { headers: { "content-type": "text/plain" } });
  },
};
