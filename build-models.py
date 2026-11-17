"""Render models.html from the live catalog. Run after catalog.json changes."""
import json, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
CAT = json.loads((ROOT.parent / "gateway" / "catalog.json").read_text(encoding="utf-8"))
MARKUP = CAT.get("markup_default", 0.2)
MODELS = CAT["models"]

def elo(m):
    return 1000 + (m["quality_prior"] - 60) * 8

def value(m):
    blend = (m["in_per_m"] + m["out_per_m"]) * (1 + MARKUP)
    return (elo(m) - 800) / max(0.05, blend)

rows = sorted(MODELS, key=lambda m: -elo(m))
body = []
for i, m in enumerate(rows, 1):
    blend = (m["in_per_m"] + m["out_per_m"]) * (1 + MARKUP)
    tags = " ".join(t for t in m["tags"] if t in ("uncensored", "reasoning", "code", "tools"))
    body.append(f"""      <tr>
        <td class="rank">{i:02d}</td>
        <td><div class="mname">{html.escape(m['name'])}</div><div class="mid">{html.escape(m['id'])}<span class="tier">{m['tier']}</span>{f'<span class="tagx">{tags}</span>' if tags else ''}</div></td>
        <td class="num">${m['in_per_m']*(1+MARKUP):.3f} / ${m['out_per_m']*(1+MARKUP):.3f}</td>
        <td class="num">${blend:.2f}</td>
        <td class="num">{(m['context'] or 0)//1000}k</td>
        <td class="num strong">{int(elo(m))}</td>
        <td class="num">{value(m):.0f}</td>
      </tr>""")

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Models and credits — Devcaster</title>
<meta name="description" content="Every model on one key. Prepaid credits, a router that picks the model per task, and a leaderboard that starts guessed and becomes real." />
<meta name="theme-color" content="#08090B" />
<link rel="icon" href="/favicon.svg" type="image/svg+xml" />
<style>
  :root{{
    --bg:#08090B; --panel:#0D0F12; --panel-2:#111418; --line:#1B1F24; --line-2:#252A31;
    --text:#EEF0F3; --muted:#8B919B; --dim:#5C636D;
    --acc:#D8FF3E; --acc-dim:#9CB82C; --ok:#57D9A3; --run:#F0B429;
    --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,"Liberation Mono",monospace;
    --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif;
    --w:1180px;
  }}
  *{{box-sizing:border-box}}
  body{{margin:0;background:var(--bg);color:var(--text);font-family:var(--sans);line-height:1.5;-webkit-font-smoothing:antialiased}}
  a{{color:inherit;text-decoration:none}}
  ::selection{{background:var(--acc);color:#0A0B0D}}
  .wrap{{max-width:var(--w);margin:0 auto;padding:0 24px}}
  header{{position:sticky;top:0;z-index:50;background:rgba(8,9,11,.86);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}}
  nav{{display:flex;align-items:center;gap:28px;height:62px}}
  .brand{{display:flex;align-items:center;gap:10px;font-weight:650;letter-spacing:-.02em;font-size:17px}}
  nav .links{{display:flex;gap:24px;margin-left:auto;font-size:14px;color:var(--muted)}}
  nav .links a:hover,nav .links a[aria-current]:hover{{color:var(--text)}}
  nav .links a[aria-current]{{color:var(--text)}}
  .btn{{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--acc);background:var(--acc);color:#0A0B0D;font-weight:650;font-size:14px;padding:9px 16px;border-radius:6px}}
  .btn.ghost{{background:transparent;color:var(--text);border-color:var(--line-2);font-weight:550}}
  nav .btn{{margin-left:8px;padding:7px 14px}}
  .hero{{padding:72px 0 40px}}
  .eyebrow{{font-family:var(--mono);font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;color:var(--acc);display:flex;align-items:center;gap:10px}}
  .eyebrow i{{width:6px;height:6px;background:var(--acc);border-radius:50%;display:inline-block;box-shadow:0 0 12px var(--acc)}}
  h1{{font-size:clamp(34px,5vw,62px);line-height:1;letter-spacing:-.035em;margin:20px 0 0;font-weight:680;max-width:16ch}}
  h1 .thin{{color:var(--muted)}}
  .sub{{margin:22px 0 0;color:var(--muted);font-size:17px;max-width:60ch}}
  .sub b{{color:var(--text);font-weight:600}}
  h2{{font-size:clamp(24px,3vw,34px);letter-spacing:-.03em;margin:0 0 8px;font-weight:660}}
  section{{padding:64px 0;border-top:1px solid var(--line)}}
  .kick{{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--acc-dim);margin-bottom:14px}}
  p.lead{{color:var(--muted);max-width:64ch;margin:0 0 28px}}

  .grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--line);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin-top:28px}}
  .cell{{background:var(--bg);padding:24px}}
  .cell .n{{font-family:var(--mono);font-size:11px;color:var(--acc);letter-spacing:.1em}}
  .cell h3{{margin:12px 0 6px;font-size:17px;font-weight:620;letter-spacing:-.015em}}
  .cell p{{margin:0;color:var(--muted);font-size:14px}}

  table{{width:100%;border-collapse:collapse;border:1px solid var(--line);border-radius:10px;overflow:hidden;font-size:14px}}
  thead th{{background:var(--panel-2);text-align:left;font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);font-weight:500;padding:12px 14px;border-bottom:1px solid var(--line)}}
  tbody td{{padding:13px 14px;border-bottom:1px solid var(--line);vertical-align:middle}}
  tbody tr:last-child td{{border-bottom:0}}
  tbody tr:hover td{{background:rgba(255,255,255,.015)}}
  .rank{{font-family:var(--mono);color:var(--dim);font-size:12px;width:38px}}
  .mname{{font-weight:560;letter-spacing:-.01em}}
  .mid{{font-family:var(--mono);font-size:11px;color:var(--dim);margin-top:3px;display:flex;gap:8px;align-items:center;flex-wrap:wrap}}
  .tier{{border:1px solid var(--line-2);border-radius:3px;padding:1px 5px;font-size:9.5px;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}}
  .tagx{{border:1px solid rgba(216,255,62,.3);color:var(--acc);border-radius:3px;padding:1px 5px;font-size:9.5px;text-transform:uppercase;letter-spacing:.08em}}
  .num{{font-family:var(--mono);font-size:12.5px;color:var(--muted);text-align:right;white-space:nowrap}}
  .num.strong{{color:var(--text);font-weight:600}}
  .prov{{display:inline-flex;align-items:center;gap:7px;border:1px solid rgba(240,180,41,.35);color:var(--run);border-radius:4px;padding:4px 9px;font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase}}
  .tablehead{{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:16px}}
  .note{{color:var(--dim);font-size:12.5px;font-family:var(--mono);margin-top:12px}}

  .price{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:24px}}
  .plan{{border:1px solid var(--line);border-radius:10px;padding:24px;background:var(--panel)}}
  .plan.hot{{background:linear-gradient(180deg,rgba(216,255,62,.05),transparent 60%),var(--panel);border-color:var(--line-2)}}
  .plan .name{{font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--dim)}}
  .plan .amt{{font-size:34px;letter-spacing:-.035em;font-weight:660;margin:10px 0 0}}
  .plan .amt small{{font-size:13px;color:var(--muted);font-weight:500;letter-spacing:0}}
  .plan ul{{list-style:none;padding:0;margin:16px 0 0;display:grid;gap:8px;font-size:13.5px;color:var(--muted)}}
  .plan li:before{{content:"—";color:var(--acc-dim);margin-right:8px}}

  .band{{border:1px solid var(--line);border-radius:12px;padding:40px;background:radial-gradient(600px 200px at 15% 0%,rgba(216,255,62,.08),transparent 70%),var(--panel);display:flex;justify-content:space-between;align-items:center;gap:24px;flex-wrap:wrap}}
  footer{{border-top:1px solid var(--line);padding:32px 0 48px;color:var(--dim);font-size:13px}}
  .foot{{display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}}
  .fine{{margin-top:18px;font-size:11.5px;color:#4E545D;max-width:72ch;line-height:1.7}}
  @media (max-width:900px){{
    nav .links{{display:none}}
    .grid3,.price{{grid-template-columns:1fr}}
    table{{font-size:13px}}
    thead th:nth-child(4),tbody td:nth-child(4),thead th:nth-child(5),tbody td:nth-child(5){{display:none}}
    .band{{padding:28px}}
  }}
</style>
</head>
<body>
<header>
  <div class="wrap">
    <nav>
      <a class="brand" href="/">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <rect x="1.5" y="1.5" width="21" height="21" rx="5" stroke="#D8FF3E" stroke-width="1.4"/>
          <path d="M6 15.5 9 8l3 7.5L15 8l3 7.5" stroke="#EEF0F3" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Devcaster
      </a>
      <div class="links">
        <a href="/#how">How it works</a>
        <a href="/models" aria-current="page">Models</a>
        <a href="/models#board">Leaderboard</a>
        <a href="/#pricing">Pricing</a>
      </div>
      <a class="btn" href="mailto:hello@devcaster.com?subject=Devcaster%20credits">Get credits</a>
    </nav>
  </div>
</header>

<main>
  <div class="wrap">
    <section class="hero" style="border-top:0">
      <div class="eyebrow"><i></i> Model rail · {len(MODELS)} models</div>
      <h1>Every model. One key. <span class="thin">One bill.</span></h1>
      <p class="sub">Prepaid credits that work on any model, a router that picks the model per task, and a leaderboard fed by real usage instead of launch-day vibes. <b>Markup {int(MARKUP*100)}%. No per-seat model tax.</b></p>
    </section>

    <section>
      <div class="kick">How the rail works</div>
      <h2>Buy credits once. Route per request.</h2>
      <div class="grid3">
        <div class="cell"><div class="n">01</div><h3>Top up</h3><p>Prepaid balance in dollars. Every call settles on real tokens at the end of the response, not an estimate.</p></div>
        <div class="cell"><div class="n">02</div><h3>Route</h3><p><code>devrouter/auto</code> reads the task, sets a quality bar, and buys the cheapest model that clears it. Or pin a model.</p></div>
        <div class="cell"><div class="n">03</div><h3>See the split</h3><p>Each response returns provider cost, what you were charged and the margin, so the invoice is never a surprise.</p></div>
      </div>
    </section>

    <section>
      <div class="kick">Credits</div>
      <h2>The ladder</h2>
      <p class="lead">Tokens included, then overage at cost plus {int(MARKUP*100)}%. Bring your own provider keys and the spread drops to 10%.</p>
      <div class="price">
        <div class="plan"><div class="name">Starter</div><div class="amt">$49<small> / month</small></div>
          <ul><li>5M tokens included</li><li>All {len(MODELS)} models</li><li>devrouter auto-routing</li><li>{int(MARKUP*100)}% on overage</li></ul></div>
        <div class="plan hot"><div class="name">Pro</div><div class="amt">$199<small> / month</small></div>
          <ul><li>30M tokens included</li><li>Uncensored tier enabled</li><li>Budget ceilings per key</li><li>Usage export</li></ul></div>
        <div class="plan"><div class="name">BYOK</div><div class="amt">10%<small> routing fee</small></div>
          <ul><li>Your keys, your provider bill</li><li>We only charge for routing</li><li>Same ledger and board</li><li>Best for heavy volume</li></ul></div>
      </div>
    </section>

    <section id="board">
      <div class="tablehead">
        <div>
          <div class="kick">Decision board</div>
          <h2 style="margin-bottom:4px">Ranked by outcome, not by launch post.</h2>
        </div>
        <span class="prov">Provisional · priors guessed</span>
      </div>
      <p class="lead" style="margin-bottom:18px">Elo starts from a guessed prior and moves only when a real head-to-head vote lands. Under 30 votes a row is still a guess. Value is Elo above baseline per dollar per million, the column a price list cannot fake.</p>
      <table>
        <thead><tr><th></th><th>Model</th><th style="text-align:right">In / Out per M</th><th style="text-align:right">Blended</th><th style="text-align:right">Context</th><th style="text-align:right">Elo</th><th style="text-align:right">Value</th></tr></thead>
        <tbody>
{chr(10).join(body)}
        </tbody>
      </table>
      <div class="note">Prices include the {int(MARKUP*100)}% markup, pulled from provider list prices on {CAT['fetched']}. Elo priors are guesses until live votes replace them.</div>
    </section>

    <section>
      <div class="kick">devrouter</div>
      <h2>Pick by task, not by habit.</h2>
      <p class="lead">Complexity score in, quality bar out, cheapest model that clears it. Every response carries the decision and the reasons, so a wrong route is a config change, not a mystery.</p>
      <table>
        <thead><tr><th>Prompt</th><th style="text-align:right">Complexity</th><th>Balanced pick</th><th>Best pick</th></tr></thead>
        <tbody>
          <tr><td>"say hi"</td><td class="num">0.05</td><td class="num" style="text-align:left">llama-3.1-8b</td><td class="num" style="text-align:left">llama-3.1-8b</td></tr>
          <tr><td>"summarize this email"</td><td class="num">0.08</td><td class="num" style="text-align:left">glm-5.3-flash</td><td class="num" style="text-align:left">llama-3.1-8b</td></tr>
          <tr><td>"write a python function to dedupe a csv"</td><td class="num">0.26</td><td class="num" style="text-align:left">deepseek-v4-flash</td><td class="num" style="text-align:left">qwen3-coder-next</td></tr>
          <tr><td>"prove the optimal stopping rule, compare 3 designs, 2000 word report"</td><td class="num">0.52</td><td class="num" style="text-align:left">claude-haiku-5.5</td><td class="num" style="text-align:left">claude-opus-5.5</td></tr>
        </tbody>
      </table>
    </section>

    <section style="border-top:0;padding-top:0">
      <div class="band">
        <div>
          <div class="kick">Start</div>
          <h2>Put $25 in. See where it goes.</h2>
          <p style="color:var(--muted);margin:10px 0 0">Every call itemised: model, tokens, cost, charge, margin.</p>
        </div>
        <a class="btn" href="mailto:hello@devcaster.com?subject=Devcaster%20credits" style="padding:13px 22px;font-size:15px">Get credits</a>
      </div>
    </section>
  </div>
</main>

<footer>
  <div class="wrap">
    <div class="foot">
      <span class="brand" style="font-size:15px">Devcaster</span>
      <div style="display:flex;gap:20px;flex-wrap:wrap">
        <a href="/">Home</a><a href="/#pricing">Pricing</a><a href="mailto:hello@devcaster.com">hello@devcaster.com</a>
      </div>
    </div>
    <div class="fine">Model names and prices belong to their providers and are passed through at list price plus the stated markup. Leaderboard priors are Devcaster estimates, not provider claims. Devcaster is built on the MIT-licensed Paperclip harness.</div>
  </div>
</footer>
</body>
</html>
"""
(ROOT / "models.html").write_text(page, encoding="utf-8")
print("wrote models.html", len(page), "bytes,", len(rows), "models")
