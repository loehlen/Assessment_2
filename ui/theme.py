"""
ui/theme.py - the visual design: the app's style sheet (colours, fonts, labels, tables), and the style of the
hover boxes in steps ③ and ④. Style only, no logic.
"""



# The theme (colours, fonts) is in .streamlit/config.toml. Here: the few things the theme cannot reach, in one place:
# the flat labels, the Commission line, the step tabs, the row rules and the hover boxes. Colours carry meaning only:
# red = potential horizontal overlap, yellow = potential vertical relationship; in step ④ the result of the
# Commission's view, as rounded chips (the labels of step ③ are square): the colour of the relationship it belongs to,
# filled only where the decisions back the overlap itself (Confirmed); red outline = possible / not excluded; yellow
# outline = a vertical row's markets (a definition identifies the markets, not the supply); green = not supported;
# grey outline = no precedent. Neutral bands (an unclear row, a rewritten line, a decision entry) are sand.
APP_CSS = """<style>
.lab{display:inline-block;font-size:.8rem;font-weight:600;padding:.08rem .45rem;border-radius:4px;line-height:1.45;
 margin:.05rem .25rem .05rem 0}
.lab-h{background:#FDECEA;color:#8A1C12}
.lab-v{background:#FFF3D1;color:#6E4B00}
.lab-q{background:#ECEAE5;color:#4A463F}
.lab-off{background:#ECEAE5;color:#7A756C;text-decoration:line-through}
.tag{font-size:.78rem;color:#55514A;font-style:italic;white-space:nowrap}
.sub2{color:#55514A}
.hov{cursor:help;border-bottom:1px dotted #8A857C}
.dots{cursor:help;border-bottom:1px dotted #8A857C;padding-bottom:.1rem}
.dts{display:inline-flex;gap:.13em;align-items:center;vertical-align:.1em}
.dts + .dts{margin-left:.45em}
.dts i{display:inline-block;width:.46em;height:.46em;border-radius:50%;border:1.2px solid currentColor;
 box-sizing:border-box}
.dts i.on{background:currentColor}
.src{text-decoration:none;font-size:.85em;color:#3A5A80}
.oc{display:inline-block;font-size:.75rem;font-weight:600;padding:0 .5rem;border-radius:10px;margin:0 .3rem;
 white-space:nowrap;border:1px solid transparent;line-height:1.5}
.oc.o-conf{background:#FDECEA;color:#8A1C12;border-color:#FDECEA}
.oc.o-open{background:transparent;color:#8A1C12;border-color:#E7A9A2}
.oc.o-vert{background:transparent;color:#6E4B00;border-color:#E6C66E}
.oc.o-nosup{background:#E3EDE4;color:#2F5D3A;border-color:#E3EDE4}
.oc.o-nopre{background:transparent;color:#55514A;border-color:#BDB7AC}
details.mkts{margin:.1rem 0 .4rem 0}
details.mkts>summary{cursor:pointer;color:#5B7089;font-size:.85rem;list-style:none}
details.mkts>summary::-webkit-details-marker{display:none}
details.mkts>summary:before{content:"▸ "}
details.mkts[open]>summary:before{content:"▾ "}
details.lfold{margin:.05rem 0 .2rem 0}
details.lfold>summary .oc{margin-left:0}
details.lfold ul{margin-top:.2rem}
[class*="st-key-note_"] [data-testid="stTextAreaRootElement"]:has(textarea:placeholder-shown:not(:focus)){
 background:transparent !important;border-color:transparent !important;border-bottom:1px dashed #C9C2B4 !important;
 border-radius:0 !important;min-height:0 !important;height:auto !important}
[class*="st-key-note_"] textarea:placeholder-shown:not(:focus){height:2.3rem !important;min-height:2.3rem !important;
 background:transparent !important}
[class*="st-key-note_"] textarea::placeholder{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.it{padding:.12rem 0 .12rem .6rem;border-left:2px solid #5B7089;margin:.1rem 0}
.it.one{border-left-color:#E2DDD2}
.or{color:#55514A;font-style:italic}
[data-testid="stSelectboxVirtualDropdown"]{min-width:11.5rem !important}
/* messages: slate blue = done or for information, sand = to check, ink frame = blocking (red, yellow and green
   stay reserved for the labels and results) */
[data-testid="stAlertContainer"]{background:#E9EEF4 !important}
[data-testid^="stAlertContent"],[data-testid^="stAlertContent"] p{color:#22313F !important}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]){background:#F2EFE8 !important;
 border:1px solid #C9C2B4}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]){background:#FBFAF7 !important;
 border:1.5px solid #22313F}
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) p{font-weight:600}
.st-key-stepnav{border-bottom:1px solid #E2DDD2;margin-bottom:.4rem}
.st-key-stepnav button{background:transparent !important;border:none !important;border-bottom:2px solid transparent !important;
 border-radius:0 !important;box-shadow:none !important;color:#1F1D1A !important;padding-left:0;padding-right:0}
.st-key-stepnav button p{font-size:.95rem}
.st-key-stepnav button[data-testid="stBaseButton-primary"]{border-bottom-color:#22313F !important;color:#22313F !important}
.st-key-stepnav button[data-testid="stBaseButton-primary"] p{font-weight:600}
.st-key-stepnav button:disabled{color:#A39E94 !important}
.st-key-stepnav button:hover:not(:disabled){color:#22313F !important}
[data-testid="stSidebar"]{min-width:20.5rem;max-width:20.5rem}
.lgg{font-size:.86rem;line-height:1.45;display:grid;grid-template-columns:fit-content(8.2rem) 1fr;column-gap:.5rem;
 row-gap:.3rem;align-items:baseline}
.lgg .oc,.lgg .lab{font-size:.72rem;padding:0 .4rem}
.lgl{display:contents}
.lgl>span{cursor:help}
.lgm .lab,.lgm .oc{margin:0;white-space:nowrap}
.lgm .lab.lab-q{white-space:normal}
.lgm .lab{border:1px solid transparent}
.lgm .lab-h,.lgm .oc.o-conf{border-color:#E7A9A2}
.lgm .lab-v{border-color:#E6C66E}
.lgm .lab-q{border-color:#BDB7AC}
.lgm .oc.o-nosup{border-color:#A9C4AE}
.lgm .tag,.lgm>.dts{padding-left:calc(.4rem + 1px)}
.lgh{grid-column:1/-1;font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:.92rem;
 margin:.45rem 0 0 0}
.lgh:first-child{margin-top:0}
.lp-title{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:2.45rem;line-height:1.15;color:#22313F;
 margin:0 0 .8rem 0}
.lp-lead{font-size:1.17rem;line-height:1.5;color:#3D3A35;margin:0 0 1.1rem 0}
.lp-lead,.lp-why p,.lp-item>div{text-align:justify;hyphens:auto;-webkit-hyphens:auto}
.lp-lead{hyphens:manual;-webkit-hyphens:manual}
.lp-split{display:flex;flex-wrap:wrap;gap:2.5rem;align-items:flex-start;margin:0 0 1.3rem 0}
.lp-main{flex:3 1 28rem;min-width:0}
.lp-h2{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:1.42rem;margin:0 0 .6rem 0;color:#22313F}
.lp-why p{margin:0 0 .55rem 0;color:#3D3A35;line-height:1.5;font-size:1rem}
.lp-why b{color:#1F1D1A}
.lp-panel{flex:2 1 22rem;min-width:0;background:#F2EFE8;border-radius:8px;padding:1.5rem 1.7rem .55rem 1.7rem}
.lp-item{display:flex;gap:.85rem;align-items:flex-start;margin:0 0 .85rem 0;line-height:1.5;font-size:1rem}
.lp-item svg{flex:none;margin-top:.15rem}
.lp-item span{color:#3D3A35}
.lp-steps-sec{border-top:1px solid #E2DDD2;padding-top:1rem;margin-bottom:1.5rem}
.lp-steps{list-style:none;margin:1.45rem 0 0 0;padding:0;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));
 gap:1.6rem 1.4rem}
@media (max-width:900px){.lp-steps{grid-template-columns:repeat(auto-fit,minmax(11rem,1fr))}}
.lp-steps li{border-top:2px solid #E2DDD2;display:flex;flex-direction:column;gap:.35rem;margin:0;padding:0}
.lp-num{display:inline-flex;align-items:center;justify-content:center;width:1.9rem;height:1.9rem;margin-top:-1rem;
 border-radius:50%;background:#22313F;color:#fff;font-size:.88rem;font-weight:600}
.lp-st{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:1.18rem}
.lp-sx{font-size:.96rem;line-height:1.45;color:#3D3A35}
.lp-foot{font-size:.82rem;line-height:1.4;color:#55514A;border-top:1px solid #E2DDD2;padding-top:.8rem;margin-top:1.3rem}
.st-key-ctaband{background:#22313F;border-radius:8px;padding:1.3rem 2.1rem}
.lp-cta-t{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:1.65rem;line-height:1.2;color:#fff;
 margin:0 0 .3rem 0}
.lp-cta-x{color:#D9DEE4;font-size:1.02rem}
.st-key-cta_start button{background:#fff !important;color:#22313F !important;border:1px solid #fff !important;
 min-height:3.1rem;padding:0 1.8rem}
.st-key-cta_start button p{font-weight:700;font-size:1.05rem;color:#22313F !important}
.st-key-ctaband [data-testid="stPopover"] button{background:transparent !important;border:1px solid #8C9AAA !important;
 min-height:3.1rem}
.st-key-ctaband [data-testid="stPopover"] button p,.st-key-ctaband [data-testid="stPopover"] button svg{color:#fff !important}
.chip{display:inline-block;font-size:.76rem;padding:.02rem .5rem;border-radius:10px;background:#ECEAE5;color:#4A463F;
 margin:0 .2rem;white-space:nowrap}
.k{display:inline-block;min-width:6.8rem;color:#55514A;font-size:.85rem}
.act>div{margin:.1rem 0;line-height:1.6}
.fld{display:flex;align-items:baseline}
.fld .k{flex:none;width:6.8rem;min-width:6.8rem;padding-right:.4rem}
.fld .v{flex:1;min-width:0}
.prof{background:#F2EFE8;border-radius:6px;padding:.55rem .8rem;margin:.2rem 0 .7rem 0;line-height:1.6}
.sec{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:1.65rem;line-height:1.25;color:#22313F;
 margin:.8rem 0 .1rem 0}
.sec.next{margin-top:2.2rem;border-top:2px solid #22313F;padding-top:.9rem}
.secsub{color:#55514A;font-size:.9rem;margin:0 0 .6rem 0}
.gate-space{height:16vh}
.gate-title{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:2.3rem;line-height:1.2;color:#22313F;
 text-align:center;margin-bottom:.3rem}
.gate-lead{font-size:1.05rem;text-align:center;color:#3D3A35;margin-bottom:1.4rem}
.gate-key{text-align:center;line-height:1.6;border:1px solid #E2DDD2;border-radius:6px;padding:.9rem 1.1rem}
.gate-key span{display:block;margin-top:.4rem;font-size:.88rem;color:#55514A}
.gate-note{text-align:center;font-size:.88rem;line-height:1.5;color:#55514A;margin-top:.9rem}
/* "Why?" and the other pop-overs: justified like the hover boxes */
[data-testid="stPopoverBody"] [data-testid="stMarkdownContainer"] p{text-align:justify;hyphens:auto;-webkit-hyphens:auto}
.basis{color:#6E6A63}
.sumt{border-collapse:collapse;width:100%;margin:.4rem 0 .3rem 0}
.sumt th{background:#22313F;color:#fff;text-align:left;padding:.45rem .7rem;font-weight:600}
.sumt th .lab{margin:0}
.sumt td{border-bottom:1px solid #C9C2B4;padding:.5rem .7rem;vertical-align:top}
.sumul{margin:0;padding-left:1.1rem}.sumul li{margin:.15rem 0}
.sless{font-size:.85rem;font-style:italic;margin:.25rem 0 0 0}
.sgrp{font-size:.85rem;font-weight:600;color:#3D3A35;margin:0 0 .2rem 0}
.sgrp.next{margin-top:.7rem}
.swrt{color:#6E6A63;font-size:.85rem;line-height:1.45;margin:.05rem 0 0 0}
.scnt{font-size:.85rem;color:#55514A;line-height:1.5;margin-top:.3rem}
.srel{margin-top:.45rem}.srel .lab{margin:0}
.sres{background:#F2EFE8;border-radius:6px;padding:.7rem 1rem;margin:.3rem 0 .7rem 0;line-height:1.6;
 display:flex;flex-direction:column;gap:.3rem}
.sres-t{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:1.1rem;color:#22313F}
.sres .lab{margin:0 .3rem 0 0}
[class*="st-key-thead"]{background:#22313F;border-radius:4px;padding:.5rem .7rem .05rem .7rem;margin-top:.3rem}
[class*="st-key-thead"] p{color:#FFFFFF !important;font-weight:600}
[class*="st-key-thead"] [data-testid="stTooltipIcon"],[class*="st-key-thead"] [data-testid="stTooltipIcon"] *{
 color:#FFFFFF !important;opacity:1 !important;filter:none !important}
[class*="st-key-thead"] [data-testid="stTooltipIcon"] svg,[class*="st-key-thead"] [data-testid="stTooltipIcon"] svg *{
 stroke:#FFFFFF !important}
[class*="st-key-pfrow"]{border-bottom:1px solid #E2DDD2;padding:.4rem 0 .45rem 0;gap:.4rem}
.st-key-thead_pf{margin-bottom:-.6rem;padding:.55rem 0 !important}
.st-key-thead_pf p{font-size:.875rem;font-weight:400;margin:0 !important;line-height:1.4}
.st-key-thead_pf [data-testid="stMarkdownContainer"],.st-key-thead_pf [data-testid="stMarkdown"]{margin:0 !important}
.st-key-thead_pf [data-testid="stMarkdownContainer"]>div{margin:0 !important}
.st-key-thead_pf strong{font-weight:600}
.st-key-thead_pf [data-testid="stColumn"]{padding-left:.75rem}
.st-key-thead_pf [data-testid="stColumn"]:nth-child(4){padding-left:.5rem}
.wr{display:block;margin:.05rem 0 0 0}
.aext{margin-top:.5rem}
.guide{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));margin:.1rem 0 .2rem 0}
.guide>div{padding:0 1.1rem;border-left:1px solid #E2DDD2}
.guide>div:first-child{padding-left:0;border-left:none}
.guide>div:last-child{padding-right:0}
.guide .gh{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:1.1rem;color:#22313F;margin:0 0 .35rem 0}
[data-testid="stMain"] h1,[data-testid="stMain"] h2,[data-testid="stMain"] h3,[data-testid="stMain"] h4{color:#22313F}
.guide ul{margin:0;padding-left:1.1rem}
.guide li{margin:.25rem 0;line-height:1.5;font-size:.93rem}
.guide .lab{margin:0 .15rem 0 0}
@media (max-width:900px){.guide{grid-template-columns:1fr;gap:.8rem}.guide>div{border-left:none;padding:0}}
.br{color:#6E6A63}
.rd-t{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:1.25rem;color:#22313F}
.rd-m{color:#55514A;font-size:.88rem;margin:.1rem 0 .4rem 0}
.rd-j{font-size:.88rem;margin:.1rem 0 .5rem 0}.rd-j a{margin-right:.35rem}
.rd{line-height:1.6}
.rd-h{font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:.95rem;color:#22313F;margin:.9rem 0 .3rem 0}
.rd-p{padding:.35rem .6rem;margin:.15rem 0;border-left:3px solid transparent;scroll-margin-top:1rem;
 text-align:justify;hyphens:auto;-webkit-hyphens:auto}
.rd-mk{font-size:.88rem;color:#3D3A35;margin:.1rem 0 .5rem 0;text-align:justify}
.rd-p.used{background:#EEF2F7;border-left-color:#2E5A88}
.rd-n{font-weight:600;color:#22313F;margin-right:.4rem;float:left}
.rd-u{font-size:.8rem;font-weight:600;color:#1F3F66;margin-bottom:.15rem}
.rd-fn{font-size:.8rem;color:#55514A;margin-top:.2rem;text-align:justify;hyphens:auto}
.rd-pdf{width:100%;height:72vh;border:1px solid #E2DDD2;border-radius:4px}
[class*="st-key-read_"] button{justify-content:flex-start;text-align:left;padding:.1rem 0;min-height:0}
[class*="st-key-read_"] button p{color:#3A5A80;font-size:.88rem;text-align:left}
[class*="st-key-read_"] button:hover p{text-decoration:underline}
</style>"""


# The Commission's markets: under each row, full width, after the facts and the preliminary assessment, one card per
# market says what the Commission defined (its own words, checked in code), what the market covers, why it was
# separated, and which products of each company it covers. Every paragraph is cited as [M.1234 (24)]; hovering shows the
# paragraph exactly as the AI saw it, a click opens the decision.
PREF_CSS = """<style>
[data-testid="stMarkdownContainer"]{position:relative}
.pref{position:static;cursor:help;color:#3A5A80;text-decoration:none !important;border-bottom:1px dotted #3A5A80;
 white-space:nowrap}
.pref .pbox{display:block;visibility:hidden;opacity:0;position:absolute;z-index:1000;left:0;right:0;margin-top:1.5em;
 width:auto;max-width:44em;max-height:26em;overscroll-behavior:contain;
 overflow:auto;background:#fff;color:#1f2328;border:1px solid #c8c8c8;border-radius:6px;padding:.6em .8em;
 box-shadow:0 4px 14px rgba(0,0,0,.18);font-size:.86rem;line-height:1.45;white-space:normal;text-align:justify;
 hyphens:auto;-webkit-hyphens:auto;
 font-weight:normal;font-style:normal;transition:visibility 0s linear .35s,opacity .12s linear .25s}
.pref .pbox::before{content:"";position:absolute;left:0;right:0;top:-1.6em;height:1.6em}
.pref:hover .pbox{visibility:visible;opacity:1;transition-delay:0s}
.pref.mk{white-space:normal}
.ccell{overflow-wrap:anywhere;padding:0 0 .2rem 0;margin:0 0 .4rem 0;line-height:1.5;font-size:.92rem}
.mkt{font-size:.9rem;table-layout:fixed}
.mkt td{border-bottom:1px solid #E2DDD2}
.mkt .mgrp td{background:#F2EFE8;font-family:"Times New Roman",Tinos,serif;font-weight:700;font-size:.98rem;
 padding:.35rem .7rem;border-bottom:none}
.mkt .mrow{margin:.1rem 0 .3rem 0;line-height:1.45}
.mkt .mact{font-weight:600}
.mkt .mco{font-style:italic}
.ccell .cph{font-weight:600;font-size:.82rem;color:#3D3A35;margin-left:.1rem}
.ccell .cpart + .cpart{border-top:1px solid rgba(0,0,0,.09);margin-top:.35rem;padding-top:.4rem}
.ccell .cpart .oc{margin:0 .35rem 0 0}
.ccell .ed{color:#55514A;font-style:italic;font-size:.8rem}
.ccell ul{margin:.2rem 0 0 0;padding-left:1.05rem}
.ccell li{margin:.12rem 0}
.cnote{opacity:.68;font-size:.92em}
</style>"""