# devcaster.com

Static site. One file, no build step, no dependencies. Open `index.html` or serve the folder.

```bash
python -m http.server 8080 --bind 127.0.0.1   # local preview
```

## Files

| File | Purpose |
| --- | --- |
| `index.html` | Whole site, inline CSS, dark theme, responsive |
| `favicon.svg` | Wordmark square |
| `404.html` | Host-level not found |
| `robots.txt` | Allow all |
| `CNAME` | `devcaster.com` for GitHub Pages |
| `preview-desktop.png` / `preview-mobile.png` | Renders for review |

## Live status, 2026-11-17

`devcaster.com` resolves to `76.76.21.21` (Vercel) and returns **402 DEPLOYMENT_DISABLED**.
The Vercel account (`enerzy`) is suspended, so every `*.vercel.app` project on it is down too,
including the old `devcaster-site`, `devcaster-website` and `devcaster` projects.

DNS is not on Vercel. Nameservers are Namecheap (`dns1/dns2.registrar-servers.com`), so the Vercel
target is a single A record that can be repointed without touching the registrar.

## Two ways to make it live

**A. Fix Vercel (costs money).** Un-suspend the account, then `vercel deploy --prod` this folder
with the `devcaster` project. Zero code changes.

**B. Free host, repoint DNS (no money).** Publish on Cloudflare Pages or GitHub Pages, then change
the A record for the apex at Namecheap to the host's target. GitHub Pages needs a public repo;
`enerzy17/devcaster-website` is private and archived, so it must be unarchived and made public
(or a new public repo created) for free Pages.

Both routes need the owner's account access. The site itself is done and verified.
