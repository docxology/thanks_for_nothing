# Copyright (c) 2026 Daniel Ari Friedman
"""Accessible source-linked companion to the manuscript's qualitative traditions figure."""

from html import escape

from thanks_for_nothing.traditions import TraditionRow, TraditionsRecord

_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thanks for Nothing — textual traditions</title>
<style>
:root { color-scheme:only light; background:var(--background,white); }
body { margin:0; color:var(--foreground,#142e3a); background:transparent;
 font-family:var(--font-sans,system-ui,sans-serif); font-size:15px; line-height:1.5; }
* { box-sizing:border-box; }
h1 { font-size:26px; line-height:1.15; margin:0 0 12px; letter-spacing:-.5px; }
p { margin:0 0 12px; }
.intro { color:var(--muted-foreground,#596579); }
label { display:block; font-weight:650; }
input { margin:6px 0; width:100%; padding:10px 12px; border:1px solid var(--border,#bcc8ce);
 border-radius:var(--radius,8px); background:var(--background,#fff); color:inherit; font:inherit; }
input:focus-visible,summary:focus-visible,a:focus-visible {
 outline:3px solid var(--ring,#007c83); outline-offset:3px; }
.count { font-size:13px; color:var(--muted-foreground,#596579); }
.head,.summary { display:grid; grid-template-columns:1.05fr 1.35fr 1.5fr; gap:16px; }
.head { font-size:12px; text-transform:uppercase; letter-spacing:.65px; padding:12px 0 8px;
 border-bottom:2px solid var(--border,#bcc8ce); }
.head span:nth-child(2) { color:var(--chart-2,#92510c); }
.head span:nth-child(3) { color:var(--chart-1,#007c83); }
article { border-bottom:1px solid var(--border,#bcc8ce); padding:14px 0; }
article[hidden] { display:none; }
.tradition { font-weight:700; }
.witness { display:block; font-size:13px; color:var(--muted-foreground,#596579); }
.cell-label { display:none; }
details { margin-top:10px; }
summary { cursor:pointer; font-size:13px; color:var(--foreground,#142e3a); }
.detail { padding:16px; margin-top:10px; border-radius:var(--radius,8px);
 background:var(--muted,#edf2f4); }
.detail p:last-child { margin-bottom:0; }
.detail strong { font-weight:650; }
a { color:var(--foreground,#142e3a); text-underline-offset:3px; overflow-wrap:anywhere; }
ul { padding-left:20px; margin:6px 0 0; }
.empty { padding:16px 0; }
footer { margin-top:16px; font-size:13px; color:var(--muted-foreground,#596579); }
@media(max-width:540px) {
 h1 { font-size:23px; } .head { display:none; }
 .summary { grid-template-columns:1fr; gap:9px; }
 .cell-label { display:block; font-size:11px; text-transform:uppercase; letter-spacing:.5px;
 color:var(--muted-foreground,#596579); }
}
</style></head><body><main>
<h1>What could “Thanks for Nothing” mean?</h1>
<p class="intro">Selected textual witnesses answer different questions. Read across for the
interpretive comparison; expand a row for its textual basis, response, sources and limits.</p>
<label for="search">Find a tradition, passage or idea</label>
<input id="search" type="search" placeholder="Try nonattachment, gifts, adversity or ego"
 autocomplete="off">
<p id="count" class="count" role="status" aria-live="polite">__COUNT__ textual comparisons</p>
<div class="head" aria-hidden="true"><span>Textual witness</span>
<span>Absence / relinquishment</span><span>Appreciation / response</span></div>
<section aria-label="Selected textual comparisons">__ROWS__</section>
<p class="empty" id="empty" hidden>No matching passage. Clear the search to see all comparisons.</p>
<footer>__SCOPE__ Each source link identifies a named witness. An unspecified addressee in a passage
does not imply that its tradition lacks gratitude.
The computational model implements none of these traditions.</footer>
</main><script>
const input=document.getElementById('search');
const rows=Array.from(document.querySelectorAll('article'));
input.addEventListener('input',()=>{
 const query=input.value.trim().toLocaleLowerCase();
 let visible=0;
 for(const row of rows){
  row.hidden=!row.textContent.toLocaleLowerCase().includes(query);
  if(!row.hidden)visible++;
 }
 document.getElementById('count').textContent=visible+' of '+rows.length+' textual comparisons';
 document.getElementById('empty').hidden=visible!==0;
});
</script></body></html>
"""


def _row(row: TraditionRow, record: TraditionsRecord) -> str:
    sources = {source.key: source for source in record.sources}
    links = "".join(
        (
            f'<li><a href="{escape(str(sources[key].url), quote=True)}">'
            f"{escape(sources[key].title)}</a> <small>({escape(key)})</small></li>"
        )
        for key in row.source_keys
    )
    paragraphs = "".join(
        f"<p><strong>{label}.</strong> {escape(text)}</p>"
        for label, text in (
            ("Textual basis / appreciation", row.appreciation),
            ("Practice / response", row.practice),
            ("Our comparison", row.comparison),
            ("Interpretive limit", row.limit),
        )
    )
    return (
        f'<article id="{row.id}"><div class="summary">'
        f'<div><span class="tradition">{escape(row.tradition)}</span>'
        f'<span class="witness">{escape(row.witness)}</span></div>'
        f'<div><span class="cell-label">Absence / relinquishment</span>{escape(row.absence)}</div>'
        f'<div><span class="cell-label">Appreciation / response</span>{escape(row.response)}</div>'
        "</div><details><summary>Text, practice, sources &amp; limits</summary>"
        f'<div class="detail">{paragraphs}<strong>Named witnesses</strong><ul>{links}</ul>'
        "</div></details></article>"
    )


def render_traditions_html(record: TraditionsRecord) -> str:
    """Render admitted authored content with escaped text and no remote scripts or assets."""
    return (
        _PAGE.replace("__COUNT__", str(len(record.selection.rows)))
        .replace("__ROWS__", "".join(_row(row, record) for row in record.selection.rows))
        .replace("__SCOPE__", escape(record.selection.scope))
    )
