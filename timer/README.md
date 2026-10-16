# N50 lab timer (Cloudflare)

GitHub's own timer is best effort and skips runs. This Cloudflare Worker (free plan) asks GitHub to run
`.github/workflows/lab-data.yml` at 2, 17, 32 and 47 past every hour. GitHub then reads SiteView and uploads.

Setup, once:
1. `npx wrangler login` (Michael signs in to Cloudflare in the browser).
2. Make a fine-grained GitHub token: repository access "Only select repositories" = n50-lab-live,
   permission "Actions: Read and write". Nothing else.
3. `npx wrangler secret put GH_TOKEN` and paste the token. It is stored only in Cloudflare.
4. `npx wrangler deploy`.

The token expires on the date chosen when it was made. Renew it before then and repeat step 3.
