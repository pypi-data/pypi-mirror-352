var We = Object.defineProperty;
var we = (r) => {
  throw TypeError(r);
};
var Je = (r, e, t) => e in r ? We(r, e, { enumerable: !0, configurable: !0, writable: !0, value: t }) : r[e] = t;
var _ = (r, e, t) => Je(r, typeof e != "symbol" ? e + "" : e, t), Xe = (r, e, t) => e.has(r) || we("Cannot " + t);
var xe = (r, e, t) => e.has(r) ? we("Cannot add the same private member more than once") : e instanceof WeakSet ? e.add(r) : e.set(r, t);
var X = (r, e, t) => (Xe(r, e, "access private method"), t);
function ce() {
  return {
    async: !1,
    breaks: !1,
    extensions: null,
    gfm: !0,
    hooks: null,
    pedantic: !1,
    renderer: null,
    silent: !1,
    tokenizer: null,
    walkTokens: null
  };
}
let D = ce();
function $e(r) {
  D = r;
}
const Le = /[&<>"']/, Ye = new RegExp(Le.source, "g"), Me = /[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/, Ke = new RegExp(Me.source, "g"), et = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;"
}, _e = (r) => et[r];
function R(r, e) {
  if (e) {
    if (Le.test(r))
      return r.replace(Ye, _e);
  } else if (Me.test(r))
    return r.replace(Ke, _e);
  return r;
}
const tt = /&(#(?:\d+)|(?:#x[0-9A-Fa-f]+)|(?:\w+));?/ig;
function nt(r) {
  return r.replace(tt, (e, t) => (t = t.toLowerCase(), t === "colon" ? ":" : t.charAt(0) === "#" ? t.charAt(1) === "x" ? String.fromCharCode(parseInt(t.substring(2), 16)) : String.fromCharCode(+t.substring(1)) : ""));
}
const st = /(^|[^\[])\^/g;
function w(r, e) {
  let t = typeof r == "string" ? r : r.source;
  e = e || "";
  const n = {
    replace: (i, l) => {
      let s = typeof l == "string" ? l : l.source;
      return s = s.replace(st, "$1"), t = t.replace(i, s), n;
    },
    getRegex: () => new RegExp(t, e)
  };
  return n;
}
function ye(r) {
  try {
    r = encodeURI(r).replace(/%25/g, "%");
  } catch {
    return null;
  }
  return r;
}
const H = { exec: () => null };
function ve(r, e) {
  const t = r.replace(/\|/g, (l, s, o) => {
    let a = !1, p = s;
    for (; --p >= 0 && o[p] === "\\"; )
      a = !a;
    return a ? "|" : " |";
  }), n = t.split(/ \|/);
  let i = 0;
  if (n[0].trim() || n.shift(), n.length > 0 && !n[n.length - 1].trim() && n.pop(), e)
    if (n.length > e)
      n.splice(e);
    else
      for (; n.length < e; )
        n.push("");
  for (; i < n.length; i++)
    n[i] = n[i].trim().replace(/\\\|/g, "|");
  return n;
}
function Y(r, e, t) {
  const n = r.length;
  if (n === 0)
    return "";
  let i = 0;
  for (; i < n && r.charAt(n - i - 1) === e; )
    i++;
  return r.slice(0, n - i);
}
function it(r, e) {
  if (r.indexOf(e[1]) === -1)
    return -1;
  let t = 0;
  for (let n = 0; n < r.length; n++)
    if (r[n] === "\\")
      n++;
    else if (r[n] === e[0])
      t++;
    else if (r[n] === e[1] && (t--, t < 0))
      return n;
  return -1;
}
function Te(r, e, t, n) {
  const i = e.href, l = e.title ? R(e.title) : null, s = r[1].replace(/\\([\[\]])/g, "$1");
  if (r[0].charAt(0) !== "!") {
    n.state.inLink = !0;
    const o = {
      type: "link",
      raw: t,
      href: i,
      title: l,
      text: s,
      tokens: n.inlineTokens(s)
    };
    return n.state.inLink = !1, o;
  }
  return {
    type: "image",
    raw: t,
    href: i,
    title: l,
    text: R(s)
  };
}
function lt(r, e) {
  const t = r.match(/^(\s+)(?:```)/);
  if (t === null)
    return e;
  const n = t[1];
  return e.split(`
`).map((i) => {
    const l = i.match(/^\s+/);
    if (l === null)
      return i;
    const [s] = l;
    return s.length >= n.length ? i.slice(n.length) : i;
  }).join(`
`);
}
class ee {
  // set by the lexer
  constructor(e) {
    _(this, "options");
    _(this, "rules");
    // set by the lexer
    _(this, "lexer");
    this.options = e || D;
  }
  space(e) {
    const t = this.rules.block.newline.exec(e);
    if (t && t[0].length > 0)
      return {
        type: "space",
        raw: t[0]
      };
  }
  code(e) {
    const t = this.rules.block.code.exec(e);
    if (t) {
      const n = t[0].replace(/^ {1,4}/gm, "");
      return {
        type: "code",
        raw: t[0],
        codeBlockStyle: "indented",
        text: this.options.pedantic ? n : Y(n, `
`)
      };
    }
  }
  fences(e) {
    const t = this.rules.block.fences.exec(e);
    if (t) {
      const n = t[0], i = lt(n, t[3] || "");
      return {
        type: "code",
        raw: n,
        lang: t[2] ? t[2].trim().replace(this.rules.inline.anyPunctuation, "$1") : t[2],
        text: i
      };
    }
  }
  heading(e) {
    const t = this.rules.block.heading.exec(e);
    if (t) {
      let n = t[2].trim();
      if (/#$/.test(n)) {
        const i = Y(n, "#");
        (this.options.pedantic || !i || / $/.test(i)) && (n = i.trim());
      }
      return {
        type: "heading",
        raw: t[0],
        depth: t[1].length,
        text: n,
        tokens: this.lexer.inline(n)
      };
    }
  }
  hr(e) {
    const t = this.rules.block.hr.exec(e);
    if (t)
      return {
        type: "hr",
        raw: t[0]
      };
  }
  blockquote(e) {
    const t = this.rules.block.blockquote.exec(e);
    if (t) {
      let n = t[0].replace(/\n {0,3}((?:=+|-+) *)(?=\n|$)/g, `
    $1`);
      n = Y(n.replace(/^ *>[ \t]?/gm, ""), `
`);
      const i = this.lexer.state.top;
      this.lexer.state.top = !0;
      const l = this.lexer.blockTokens(n);
      return this.lexer.state.top = i, {
        type: "blockquote",
        raw: t[0],
        tokens: l,
        text: n
      };
    }
  }
  list(e) {
    let t = this.rules.block.list.exec(e);
    if (t) {
      let n = t[1].trim();
      const i = n.length > 1, l = {
        type: "list",
        raw: "",
        ordered: i,
        start: i ? +n.slice(0, -1) : "",
        loose: !1,
        items: []
      };
      n = i ? `\\d{1,9}\\${n.slice(-1)}` : `\\${n}`, this.options.pedantic && (n = i ? n : "[*+-]");
      const s = new RegExp(`^( {0,3}${n})((?:[	 ][^\\n]*)?(?:\\n|$))`);
      let o = "", a = "", p = !1;
      for (; e; ) {
        let c = !1;
        if (!(t = s.exec(e)) || this.rules.block.hr.test(e))
          break;
        o = t[0], e = e.substring(o.length);
        let g = t[2].split(`
`, 1)[0].replace(/^\t+/, (k) => " ".repeat(3 * k.length)), u = e.split(`
`, 1)[0], h = 0;
        this.options.pedantic ? (h = 2, a = g.trimStart()) : (h = t[2].search(/[^ ]/), h = h > 4 ? 1 : h, a = g.slice(h), h += t[1].length);
        let m = !1;
        if (!g && /^ *$/.test(u) && (o += u + `
`, e = e.substring(u.length + 1), c = !0), !c) {
          const k = new RegExp(`^ {0,${Math.min(3, h - 1)}}(?:[*+-]|\\d{1,9}[.)])((?:[ 	][^\\n]*)?(?:\\n|$))`), x = new RegExp(`^ {0,${Math.min(3, h - 1)}}((?:- *){3,}|(?:_ *){3,}|(?:\\* *){3,})(?:\\n+|$)`), z = new RegExp(`^ {0,${Math.min(3, h - 1)}}(?:\`\`\`|~~~)`), I = new RegExp(`^ {0,${Math.min(3, h - 1)}}#`);
          for (; e; ) {
            const C = e.split(`
`, 1)[0];
            if (u = C, this.options.pedantic && (u = u.replace(/^ {1,4}(?=( {4})*[^ ])/g, "  ")), z.test(u) || I.test(u) || k.test(u) || x.test(e))
              break;
            if (u.search(/[^ ]/) >= h || !u.trim())
              a += `
` + u.slice(h);
            else {
              if (m || g.search(/[^ ]/) >= 4 || z.test(g) || I.test(g) || x.test(g))
                break;
              a += `
` + u;
            }
            !m && !u.trim() && (m = !0), o += C + `
`, e = e.substring(C.length + 1), g = u.slice(h);
          }
        }
        l.loose || (p ? l.loose = !0 : /\n *\n *$/.test(o) && (p = !0));
        let d = null, y;
        this.options.gfm && (d = /^\[[ xX]\] /.exec(a), d && (y = d[0] !== "[ ] ", a = a.replace(/^\[[ xX]\] +/, ""))), l.items.push({
          type: "list_item",
          raw: o,
          task: !!d,
          checked: y,
          loose: !1,
          text: a,
          tokens: []
        }), l.raw += o;
      }
      l.items[l.items.length - 1].raw = o.trimEnd(), l.items[l.items.length - 1].text = a.trimEnd(), l.raw = l.raw.trimEnd();
      for (let c = 0; c < l.items.length; c++)
        if (this.lexer.state.top = !1, l.items[c].tokens = this.lexer.blockTokens(l.items[c].text, []), !l.loose) {
          const g = l.items[c].tokens.filter((h) => h.type === "space"), u = g.length > 0 && g.some((h) => /\n.*\n/.test(h.raw));
          l.loose = u;
        }
      if (l.loose)
        for (let c = 0; c < l.items.length; c++)
          l.items[c].loose = !0;
      return l;
    }
  }
  html(e) {
    const t = this.rules.block.html.exec(e);
    if (t)
      return {
        type: "html",
        block: !0,
        raw: t[0],
        pre: t[1] === "pre" || t[1] === "script" || t[1] === "style",
        text: t[0]
      };
  }
  def(e) {
    const t = this.rules.block.def.exec(e);
    if (t) {
      const n = t[1].toLowerCase().replace(/\s+/g, " "), i = t[2] ? t[2].replace(/^<(.*)>$/, "$1").replace(this.rules.inline.anyPunctuation, "$1") : "", l = t[3] ? t[3].substring(1, t[3].length - 1).replace(this.rules.inline.anyPunctuation, "$1") : t[3];
      return {
        type: "def",
        tag: n,
        raw: t[0],
        href: i,
        title: l
      };
    }
  }
  table(e) {
    const t = this.rules.block.table.exec(e);
    if (!t || !/[:|]/.test(t[2]))
      return;
    const n = ve(t[1]), i = t[2].replace(/^\||\| *$/g, "").split("|"), l = t[3] && t[3].trim() ? t[3].replace(/\n[ \t]*$/, "").split(`
`) : [], s = {
      type: "table",
      raw: t[0],
      header: [],
      align: [],
      rows: []
    };
    if (n.length === i.length) {
      for (const o of i)
        /^ *-+: *$/.test(o) ? s.align.push("right") : /^ *:-+: *$/.test(o) ? s.align.push("center") : /^ *:-+ *$/.test(o) ? s.align.push("left") : s.align.push(null);
      for (const o of n)
        s.header.push({
          text: o,
          tokens: this.lexer.inline(o)
        });
      for (const o of l)
        s.rows.push(ve(o, s.header.length).map((a) => ({
          text: a,
          tokens: this.lexer.inline(a)
        })));
      return s;
    }
  }
  lheading(e) {
    const t = this.rules.block.lheading.exec(e);
    if (t)
      return {
        type: "heading",
        raw: t[0],
        depth: t[2].charAt(0) === "=" ? 1 : 2,
        text: t[1],
        tokens: this.lexer.inline(t[1])
      };
  }
  paragraph(e) {
    const t = this.rules.block.paragraph.exec(e);
    if (t) {
      const n = t[1].charAt(t[1].length - 1) === `
` ? t[1].slice(0, -1) : t[1];
      return {
        type: "paragraph",
        raw: t[0],
        text: n,
        tokens: this.lexer.inline(n)
      };
    }
  }
  text(e) {
    const t = this.rules.block.text.exec(e);
    if (t)
      return {
        type: "text",
        raw: t[0],
        text: t[0],
        tokens: this.lexer.inline(t[0])
      };
  }
  escape(e) {
    const t = this.rules.inline.escape.exec(e);
    if (t)
      return {
        type: "escape",
        raw: t[0],
        text: R(t[1])
      };
  }
  tag(e) {
    const t = this.rules.inline.tag.exec(e);
    if (t)
      return !this.lexer.state.inLink && /^<a /i.test(t[0]) ? this.lexer.state.inLink = !0 : this.lexer.state.inLink && /^<\/a>/i.test(t[0]) && (this.lexer.state.inLink = !1), !this.lexer.state.inRawBlock && /^<(pre|code|kbd|script)(\s|>)/i.test(t[0]) ? this.lexer.state.inRawBlock = !0 : this.lexer.state.inRawBlock && /^<\/(pre|code|kbd|script)(\s|>)/i.test(t[0]) && (this.lexer.state.inRawBlock = !1), {
        type: "html",
        raw: t[0],
        inLink: this.lexer.state.inLink,
        inRawBlock: this.lexer.state.inRawBlock,
        block: !1,
        text: t[0]
      };
  }
  link(e) {
    const t = this.rules.inline.link.exec(e);
    if (t) {
      const n = t[2].trim();
      if (!this.options.pedantic && /^</.test(n)) {
        if (!/>$/.test(n))
          return;
        const s = Y(n.slice(0, -1), "\\");
        if ((n.length - s.length) % 2 === 0)
          return;
      } else {
        const s = it(t[2], "()");
        if (s > -1) {
          const a = (t[0].indexOf("!") === 0 ? 5 : 4) + t[1].length + s;
          t[2] = t[2].substring(0, s), t[0] = t[0].substring(0, a).trim(), t[3] = "";
        }
      }
      let i = t[2], l = "";
      if (this.options.pedantic) {
        const s = /^([^'"]*[^\s])\s+(['"])(.*)\2/.exec(i);
        s && (i = s[1], l = s[3]);
      } else
        l = t[3] ? t[3].slice(1, -1) : "";
      return i = i.trim(), /^</.test(i) && (this.options.pedantic && !/>$/.test(n) ? i = i.slice(1) : i = i.slice(1, -1)), Te(t, {
        href: i && i.replace(this.rules.inline.anyPunctuation, "$1"),
        title: l && l.replace(this.rules.inline.anyPunctuation, "$1")
      }, t[0], this.lexer);
    }
  }
  reflink(e, t) {
    let n;
    if ((n = this.rules.inline.reflink.exec(e)) || (n = this.rules.inline.nolink.exec(e))) {
      const i = (n[2] || n[1]).replace(/\s+/g, " "), l = t[i.toLowerCase()];
      if (!l) {
        const s = n[0].charAt(0);
        return {
          type: "text",
          raw: s,
          text: s
        };
      }
      return Te(n, l, n[0], this.lexer);
    }
  }
  emStrong(e, t, n = "") {
    let i = this.rules.inline.emStrongLDelim.exec(e);
    if (!i || i[3] && n.match(/[\p{L}\p{N}]/u))
      return;
    if (!(i[1] || i[2] || "") || !n || this.rules.inline.punctuation.exec(n)) {
      const s = [...i[0]].length - 1;
      let o, a, p = s, c = 0;
      const g = i[0][0] === "*" ? this.rules.inline.emStrongRDelimAst : this.rules.inline.emStrongRDelimUnd;
      for (g.lastIndex = 0, t = t.slice(-1 * e.length + s); (i = g.exec(t)) != null; ) {
        if (o = i[1] || i[2] || i[3] || i[4] || i[5] || i[6], !o)
          continue;
        if (a = [...o].length, i[3] || i[4]) {
          p += a;
          continue;
        } else if ((i[5] || i[6]) && s % 3 && !((s + a) % 3)) {
          c += a;
          continue;
        }
        if (p -= a, p > 0)
          continue;
        a = Math.min(a, a + p + c);
        const u = [...i[0]][0].length, h = e.slice(0, s + i.index + u + a);
        if (Math.min(s, a) % 2) {
          const d = h.slice(1, -1);
          return {
            type: "em",
            raw: h,
            text: d,
            tokens: this.lexer.inlineTokens(d)
          };
        }
        const m = h.slice(2, -2);
        return {
          type: "strong",
          raw: h,
          text: m,
          tokens: this.lexer.inlineTokens(m)
        };
      }
    }
  }
  codespan(e) {
    const t = this.rules.inline.code.exec(e);
    if (t) {
      let n = t[2].replace(/\n/g, " ");
      const i = /[^ ]/.test(n), l = /^ /.test(n) && / $/.test(n);
      return i && l && (n = n.substring(1, n.length - 1)), n = R(n, !0), {
        type: "codespan",
        raw: t[0],
        text: n
      };
    }
  }
  br(e) {
    const t = this.rules.inline.br.exec(e);
    if (t)
      return {
        type: "br",
        raw: t[0]
      };
  }
  del(e) {
    const t = this.rules.inline.del.exec(e);
    if (t)
      return {
        type: "del",
        raw: t[0],
        text: t[2],
        tokens: this.lexer.inlineTokens(t[2])
      };
  }
  autolink(e) {
    const t = this.rules.inline.autolink.exec(e);
    if (t) {
      let n, i;
      return t[2] === "@" ? (n = R(t[1]), i = "mailto:" + n) : (n = R(t[1]), i = n), {
        type: "link",
        raw: t[0],
        text: n,
        href: i,
        tokens: [
          {
            type: "text",
            raw: n,
            text: n
          }
        ]
      };
    }
  }
  url(e) {
    var n;
    let t;
    if (t = this.rules.inline.url.exec(e)) {
      let i, l;
      if (t[2] === "@")
        i = R(t[0]), l = "mailto:" + i;
      else {
        let s;
        do
          s = t[0], t[0] = ((n = this.rules.inline._backpedal.exec(t[0])) == null ? void 0 : n[0]) ?? "";
        while (s !== t[0]);
        i = R(t[0]), t[1] === "www." ? l = "http://" + t[0] : l = t[0];
      }
      return {
        type: "link",
        raw: t[0],
        text: i,
        href: l,
        tokens: [
          {
            type: "text",
            raw: i,
            text: i
          }
        ]
      };
    }
  }
  inlineText(e) {
    const t = this.rules.inline.text.exec(e);
    if (t) {
      let n;
      return this.lexer.state.inRawBlock ? n = t[0] : n = R(t[0]), {
        type: "text",
        raw: t[0],
        text: n
      };
    }
  }
}
const rt = /^(?: *(?:\n|$))+/, ot = /^( {4}[^\n]+(?:\n(?: *(?:\n|$))*)?)+/, at = /^ {0,3}(`{3,}(?=[^`\n]*(?:\n|$))|~{3,})([^\n]*)(?:\n|$)(?:|([\s\S]*?)(?:\n|$))(?: {0,3}\1[~`]* *(?=\n|$)|$)/, G = /^ {0,3}((?:-[\t ]*){3,}|(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})(?:\n+|$)/, ct = /^ {0,3}(#{1,6})(?=\s|$)(.*)(?:\n+|$)/, Be = /(?:[*+-]|\d{1,9}[.)])/, qe = w(/^(?!bull |blockCode|fences|blockquote|heading|html)((?:.|\n(?!\s*?\n|bull |blockCode|fences|blockquote|heading|html))+?)\n {0,3}(=+|-+) *(?:\n+|$)/).replace(/bull/g, Be).replace(/blockCode/g, / {4}/).replace(/fences/g, / {0,3}(?:`{3,}|~{3,})/).replace(/blockquote/g, / {0,3}>/).replace(/heading/g, / {0,3}#{1,6}/).replace(/html/g, / {0,3}<[^\n>]+>\n/).getRegex(), ue = /^([^\n]+(?:\n(?!hr|heading|lheading|blockquote|fences|list|html|table| +\n)[^\n]+)*)/, ut = /^[^\n]+/, he = /(?!\s*\])(?:\\.|[^\[\]\\])+/, ht = w(/^ {0,3}\[(label)\]: *(?:\n *)?([^<\s][^\s]*|<.*?>)(?:(?: +(?:\n *)?| *\n *)(title))? *(?:\n+|$)/).replace("label", he).replace("title", /(?:"(?:\\"?|[^"\\])*"|'[^'\n]*(?:\n[^'\n]+)*\n?'|\([^()]*\))/).getRegex(), pt = w(/^( {0,3}bull)([ \t][^\n]+?)?(?:\n|$)/).replace(/bull/g, Be).getRegex(), se = "address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|meta|nav|noframes|ol|optgroup|option|p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul", pe = /<!--(?:-?>|[\s\S]*?(?:-->|$))/, ft = w("^ {0,3}(?:<(script|pre|style|textarea)[\\s>][\\s\\S]*?(?:</\\1>[^\\n]*\\n+|$)|comment[^\\n]*(\\n+|$)|<\\?[\\s\\S]*?(?:\\?>\\n*|$)|<![A-Z][\\s\\S]*?(?:>\\n*|$)|<!\\[CDATA\\[[\\s\\S]*?(?:\\]\\]>\\n*|$)|</?(tag)(?: +|\\n|/?>)[\\s\\S]*?(?:(?:\\n *)+\\n|$)|<(?!script|pre|style|textarea)([a-z][\\w-]*)(?:attribute)*? */?>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n *)+\\n|$)|</(?!script|pre|style|textarea)[a-z][\\w-]*\\s*>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n *)+\\n|$))", "i").replace("comment", pe).replace("tag", se).replace("attribute", / +[a-zA-Z:_][\w.:-]*(?: *= *"[^"\n]*"| *= *'[^'\n]*'| *= *[^\s"'=<>`]+)?/).getRegex(), Pe = w(ue).replace("hr", G).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("|lheading", "").replace("|table", "").replace("blockquote", " {0,3}>").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", se).getRegex(), gt = w(/^( {0,3}> ?(paragraph|[^\n]*)(?:\n|$))+/).replace("paragraph", Pe).getRegex(), fe = {
  blockquote: gt,
  code: ot,
  def: ht,
  fences: at,
  heading: ct,
  hr: G,
  html: ft,
  lheading: qe,
  list: pt,
  newline: rt,
  paragraph: Pe,
  table: H,
  text: ut
}, ze = w("^ *([^\\n ].*)\\n {0,3}((?:\\| *)?:?-+:? *(?:\\| *:?-+:? *)*(?:\\| *)?)(?:\\n((?:(?! *\\n|hr|heading|blockquote|code|fences|list|html).*(?:\\n|$))*)\\n*|$)").replace("hr", G).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("blockquote", " {0,3}>").replace("code", " {4}[^\\n]").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", se).getRegex(), dt = {
  ...fe,
  table: ze,
  paragraph: w(ue).replace("hr", G).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("|lheading", "").replace("table", ze).replace("blockquote", " {0,3}>").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", se).getRegex()
}, kt = {
  ...fe,
  html: w(`^ *(?:comment *(?:\\n|\\s*$)|<(tag)[\\s\\S]+?</\\1> *(?:\\n{2,}|\\s*$)|<tag(?:"[^"]*"|'[^']*'|\\s[^'"/>\\s]*)*?/?> *(?:\\n{2,}|\\s*$))`).replace("comment", pe).replace(/tag/g, "(?!(?:a|em|strong|small|s|cite|q|dfn|abbr|data|time|code|var|samp|kbd|sub|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo|span|br|wbr|ins|del|img)\\b)\\w+(?!:|[^\\w\\s@]*@)\\b").getRegex(),
  def: /^ *\[([^\]]+)\]: *<?([^\s>]+)>?(?: +(["(][^\n]+[")]))? *(?:\n+|$)/,
  heading: /^(#{1,6})(.*)(?:\n+|$)/,
  fences: H,
  // fences not supported
  lheading: /^(.+?)\n {0,3}(=+|-+) *(?:\n+|$)/,
  paragraph: w(ue).replace("hr", G).replace("heading", ` *#{1,6} *[^
]`).replace("lheading", qe).replace("|table", "").replace("blockquote", " {0,3}>").replace("|fences", "").replace("|list", "").replace("|html", "").replace("|tag", "").getRegex()
}, Ze = /^\\([!"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])/, mt = /^(`+)([^`]|[^`][\s\S]*?[^`])\1(?!`)/, De = /^( {2,}|\\)\n(?!\s*$)/, bt = /^(`+|[^`])(?:(?= {2,}\n)|[\s\S]*?(?:(?=[\\<!\[`*_]|\b_|$)|[^ ](?= {2,}\n)))/, U = "\\p{P}\\p{S}", wt = w(/^((?![*_])[\spunctuation])/, "u").replace(/punctuation/g, U).getRegex(), xt = /\[[^[\]]*?\]\([^\(\)]*?\)|`[^`]*?`|<[^<>]*?>/g, _t = w(/^(?:\*+(?:((?!\*)[punct])|[^\s*]))|^_+(?:((?!_)[punct])|([^\s_]))/, "u").replace(/punct/g, U).getRegex(), yt = w("^[^_*]*?__[^_*]*?\\*[^_*]*?(?=__)|[^*]+(?=[^*])|(?!\\*)[punct](\\*+)(?=[\\s]|$)|[^punct\\s](\\*+)(?!\\*)(?=[punct\\s]|$)|(?!\\*)[punct\\s](\\*+)(?=[^punct\\s])|[\\s](\\*+)(?!\\*)(?=[punct])|(?!\\*)[punct](\\*+)(?!\\*)(?=[punct])|[^punct\\s](\\*+)(?=[^punct\\s])", "gu").replace(/punct/g, U).getRegex(), vt = w("^[^_*]*?\\*\\*[^_*]*?_[^_*]*?(?=\\*\\*)|[^_]+(?=[^_])|(?!_)[punct](_+)(?=[\\s]|$)|[^punct\\s](_+)(?!_)(?=[punct\\s]|$)|(?!_)[punct\\s](_+)(?=[^punct\\s])|[\\s](_+)(?!_)(?=[punct])|(?!_)[punct](_+)(?!_)(?=[punct])", "gu").replace(/punct/g, U).getRegex(), Tt = w(/\\([punct])/, "gu").replace(/punct/g, U).getRegex(), zt = w(/^<(scheme:[^\s\x00-\x1f<>]*|email)>/).replace("scheme", /[a-zA-Z][a-zA-Z0-9+.-]{1,31}/).replace("email", /[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+(@)[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+(?![-_])/).getRegex(), Rt = w(pe).replace("(?:-->|$)", "-->").getRegex(), St = w("^comment|^</[a-zA-Z][\\w:-]*\\s*>|^<[a-zA-Z][\\w-]*(?:attribute)*?\\s*/?>|^<\\?[\\s\\S]*?\\?>|^<![a-zA-Z]+\\s[\\s\\S]*?>|^<!\\[CDATA\\[[\\s\\S]*?\\]\\]>").replace("comment", Rt).replace("attribute", /\s+[a-zA-Z:_][\w.:-]*(?:\s*=\s*"[^"]*"|\s*=\s*'[^']*'|\s*=\s*[^\s"'=<>`]+)?/).getRegex(), te = /(?:\[(?:\\.|[^\[\]\\])*\]|\\.|`[^`]*`|[^\[\]\\`])*?/, It = w(/^!?\[(label)\]\(\s*(href)(?:\s+(title))?\s*\)/).replace("label", te).replace("href", /<(?:\\.|[^\n<>\\])+>|[^\s\x00-\x1f]*/).replace("title", /"(?:\\"?|[^"\\])*"|'(?:\\'?|[^'\\])*'|\((?:\\\)?|[^)\\])*\)/).getRegex(), Oe = w(/^!?\[(label)\]\[(ref)\]/).replace("label", te).replace("ref", he).getRegex(), Qe = w(/^!?\[(ref)\](?:\[\])?/).replace("ref", he).getRegex(), At = w("reflink|nolink(?!\\()", "g").replace("reflink", Oe).replace("nolink", Qe).getRegex(), ge = {
  _backpedal: H,
  // only used for GFM url
  anyPunctuation: Tt,
  autolink: zt,
  blockSkip: xt,
  br: De,
  code: mt,
  del: H,
  emStrongLDelim: _t,
  emStrongRDelimAst: yt,
  emStrongRDelimUnd: vt,
  escape: Ze,
  link: It,
  nolink: Qe,
  punctuation: wt,
  reflink: Oe,
  reflinkSearch: At,
  tag: St,
  text: bt,
  url: H
}, Et = {
  ...ge,
  link: w(/^!?\[(label)\]\((.*?)\)/).replace("label", te).getRegex(),
  reflink: w(/^!?\[(label)\]\s*\[([^\]]*)\]/).replace("label", te).getRegex()
}, ie = {
  ...ge,
  escape: w(Ze).replace("])", "~|])").getRegex(),
  url: w(/^((?:ftp|https?):\/\/|www\.)(?:[a-zA-Z0-9\-]+\.?)+[^\s<]*|^email/, "i").replace("email", /[A-Za-z0-9._+-]+(@)[a-zA-Z0-9-_]+(?:\.[a-zA-Z0-9-_]*[a-zA-Z0-9])+(?![-_])/).getRegex(),
  _backpedal: /(?:[^?!.,:;*_'"~()&]+|\([^)]*\)|&(?![a-zA-Z0-9]+;$)|[?!.,:;*_'"~)]+(?!$))+/,
  del: /^(~~?)(?=[^\s~])([\s\S]*?[^\s~])\1(?=[^~]|$)/,
  text: /^([`~]+|[^`~])(?:(?= {2,}\n)|(?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)|[\s\S]*?(?:(?=[\\<!\[`*~_]|\b_|https?:\/\/|ftp:\/\/|www\.|$)|[^ ](?= {2,}\n)|[^a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-](?=[a-zA-Z0-9.!#$%&'*+\/=?_`{\|}~-]+@)))/
}, Ct = {
  ...ie,
  br: w(De).replace("{2,}", "*").getRegex(),
  text: w(ie.text).replace("\\b_", "\\b_| {2,}\\n").replace(/\{2,\}/g, "*").getRegex()
}, K = {
  normal: fe,
  gfm: dt,
  pedantic: kt
}, V = {
  normal: ge,
  gfm: ie,
  breaks: Ct,
  pedantic: Et
};
class M {
  constructor(e) {
    _(this, "tokens");
    _(this, "options");
    _(this, "state");
    _(this, "tokenizer");
    _(this, "inlineQueue");
    this.tokens = [], this.tokens.links = /* @__PURE__ */ Object.create(null), this.options = e || D, this.options.tokenizer = this.options.tokenizer || new ee(), this.tokenizer = this.options.tokenizer, this.tokenizer.options = this.options, this.tokenizer.lexer = this, this.inlineQueue = [], this.state = {
      inLink: !1,
      inRawBlock: !1,
      top: !0
    };
    const t = {
      block: K.normal,
      inline: V.normal
    };
    this.options.pedantic ? (t.block = K.pedantic, t.inline = V.pedantic) : this.options.gfm && (t.block = K.gfm, this.options.breaks ? t.inline = V.breaks : t.inline = V.gfm), this.tokenizer.rules = t;
  }
  /**
   * Expose Rules
   */
  static get rules() {
    return {
      block: K,
      inline: V
    };
  }
  /**
   * Static Lex Method
   */
  static lex(e, t) {
    return new M(t).lex(e);
  }
  /**
   * Static Lex Inline Method
   */
  static lexInline(e, t) {
    return new M(t).inlineTokens(e);
  }
  /**
   * Preprocessing
   */
  lex(e) {
    e = e.replace(/\r\n|\r/g, `
`), this.blockTokens(e, this.tokens);
    for (let t = 0; t < this.inlineQueue.length; t++) {
      const n = this.inlineQueue[t];
      this.inlineTokens(n.src, n.tokens);
    }
    return this.inlineQueue = [], this.tokens;
  }
  blockTokens(e, t = []) {
    this.options.pedantic ? e = e.replace(/\t/g, "    ").replace(/^ +$/gm, "") : e = e.replace(/^( *)(\t+)/gm, (o, a, p) => a + "    ".repeat(p.length));
    let n, i, l, s;
    for (; e; )
      if (!(this.options.extensions && this.options.extensions.block && this.options.extensions.block.some((o) => (n = o.call({ lexer: this }, e, t)) ? (e = e.substring(n.raw.length), t.push(n), !0) : !1))) {
        if (n = this.tokenizer.space(e)) {
          e = e.substring(n.raw.length), n.raw.length === 1 && t.length > 0 ? t[t.length - 1].raw += `
` : t.push(n);
          continue;
        }
        if (n = this.tokenizer.code(e)) {
          e = e.substring(n.raw.length), i = t[t.length - 1], i && (i.type === "paragraph" || i.type === "text") ? (i.raw += `
` + n.raw, i.text += `
` + n.text, this.inlineQueue[this.inlineQueue.length - 1].src = i.text) : t.push(n);
          continue;
        }
        if (n = this.tokenizer.fences(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.heading(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.hr(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.blockquote(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.list(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.html(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.def(e)) {
          e = e.substring(n.raw.length), i = t[t.length - 1], i && (i.type === "paragraph" || i.type === "text") ? (i.raw += `
` + n.raw, i.text += `
` + n.raw, this.inlineQueue[this.inlineQueue.length - 1].src = i.text) : this.tokens.links[n.tag] || (this.tokens.links[n.tag] = {
            href: n.href,
            title: n.title
          });
          continue;
        }
        if (n = this.tokenizer.table(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.lheading(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (l = e, this.options.extensions && this.options.extensions.startBlock) {
          let o = 1 / 0;
          const a = e.slice(1);
          let p;
          this.options.extensions.startBlock.forEach((c) => {
            p = c.call({ lexer: this }, a), typeof p == "number" && p >= 0 && (o = Math.min(o, p));
          }), o < 1 / 0 && o >= 0 && (l = e.substring(0, o + 1));
        }
        if (this.state.top && (n = this.tokenizer.paragraph(l))) {
          i = t[t.length - 1], s && i.type === "paragraph" ? (i.raw += `
` + n.raw, i.text += `
` + n.text, this.inlineQueue.pop(), this.inlineQueue[this.inlineQueue.length - 1].src = i.text) : t.push(n), s = l.length !== e.length, e = e.substring(n.raw.length);
          continue;
        }
        if (n = this.tokenizer.text(e)) {
          e = e.substring(n.raw.length), i = t[t.length - 1], i && i.type === "text" ? (i.raw += `
` + n.raw, i.text += `
` + n.text, this.inlineQueue.pop(), this.inlineQueue[this.inlineQueue.length - 1].src = i.text) : t.push(n);
          continue;
        }
        if (e) {
          const o = "Infinite loop on byte: " + e.charCodeAt(0);
          if (this.options.silent) {
            console.error(o);
            break;
          } else
            throw new Error(o);
        }
      }
    return this.state.top = !0, t;
  }
  inline(e, t = []) {
    return this.inlineQueue.push({ src: e, tokens: t }), t;
  }
  /**
   * Lexing/Compiling
   */
  inlineTokens(e, t = []) {
    let n, i, l, s = e, o, a, p;
    if (this.tokens.links) {
      const c = Object.keys(this.tokens.links);
      if (c.length > 0)
        for (; (o = this.tokenizer.rules.inline.reflinkSearch.exec(s)) != null; )
          c.includes(o[0].slice(o[0].lastIndexOf("[") + 1, -1)) && (s = s.slice(0, o.index) + "[" + "a".repeat(o[0].length - 2) + "]" + s.slice(this.tokenizer.rules.inline.reflinkSearch.lastIndex));
    }
    for (; (o = this.tokenizer.rules.inline.blockSkip.exec(s)) != null; )
      s = s.slice(0, o.index) + "[" + "a".repeat(o[0].length - 2) + "]" + s.slice(this.tokenizer.rules.inline.blockSkip.lastIndex);
    for (; (o = this.tokenizer.rules.inline.anyPunctuation.exec(s)) != null; )
      s = s.slice(0, o.index) + "++" + s.slice(this.tokenizer.rules.inline.anyPunctuation.lastIndex);
    for (; e; )
      if (a || (p = ""), a = !1, !(this.options.extensions && this.options.extensions.inline && this.options.extensions.inline.some((c) => (n = c.call({ lexer: this }, e, t)) ? (e = e.substring(n.raw.length), t.push(n), !0) : !1))) {
        if (n = this.tokenizer.escape(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.tag(e)) {
          e = e.substring(n.raw.length), i = t[t.length - 1], i && n.type === "text" && i.type === "text" ? (i.raw += n.raw, i.text += n.text) : t.push(n);
          continue;
        }
        if (n = this.tokenizer.link(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.reflink(e, this.tokens.links)) {
          e = e.substring(n.raw.length), i = t[t.length - 1], i && n.type === "text" && i.type === "text" ? (i.raw += n.raw, i.text += n.text) : t.push(n);
          continue;
        }
        if (n = this.tokenizer.emStrong(e, s, p)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.codespan(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.br(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.del(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (n = this.tokenizer.autolink(e)) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (!this.state.inLink && (n = this.tokenizer.url(e))) {
          e = e.substring(n.raw.length), t.push(n);
          continue;
        }
        if (l = e, this.options.extensions && this.options.extensions.startInline) {
          let c = 1 / 0;
          const g = e.slice(1);
          let u;
          this.options.extensions.startInline.forEach((h) => {
            u = h.call({ lexer: this }, g), typeof u == "number" && u >= 0 && (c = Math.min(c, u));
          }), c < 1 / 0 && c >= 0 && (l = e.substring(0, c + 1));
        }
        if (n = this.tokenizer.inlineText(l)) {
          e = e.substring(n.raw.length), n.raw.slice(-1) !== "_" && (p = n.raw.slice(-1)), a = !0, i = t[t.length - 1], i && i.type === "text" ? (i.raw += n.raw, i.text += n.text) : t.push(n);
          continue;
        }
        if (e) {
          const c = "Infinite loop on byte: " + e.charCodeAt(0);
          if (this.options.silent) {
            console.error(c);
            break;
          } else
            throw new Error(c);
        }
      }
    return t;
  }
}
class ne {
  constructor(e) {
    _(this, "options");
    this.options = e || D;
  }
  code(e, t, n) {
    var l;
    const i = (l = (t || "").match(/^\S*/)) == null ? void 0 : l[0];
    return e = e.replace(/\n$/, "") + `
`, i ? '<pre><code class="language-' + R(i) + '">' + (n ? e : R(e, !0)) + `</code></pre>
` : "<pre><code>" + (n ? e : R(e, !0)) + `</code></pre>
`;
  }
  blockquote(e) {
    return `<blockquote>
${e}</blockquote>
`;
  }
  html(e, t) {
    return e;
  }
  heading(e, t, n) {
    return `<h${t}>${e}</h${t}>
`;
  }
  hr() {
    return `<hr>
`;
  }
  list(e, t, n) {
    const i = t ? "ol" : "ul", l = t && n !== 1 ? ' start="' + n + '"' : "";
    return "<" + i + l + `>
` + e + "</" + i + `>
`;
  }
  listitem(e, t, n) {
    return `<li>${e}</li>
`;
  }
  checkbox(e) {
    return "<input " + (e ? 'checked="" ' : "") + 'disabled="" type="checkbox">';
  }
  paragraph(e) {
    return `<p>${e}</p>
`;
  }
  table(e, t) {
    return t && (t = `<tbody>${t}</tbody>`), `<table>
<thead>
` + e + `</thead>
` + t + `</table>
`;
  }
  tablerow(e) {
    return `<tr>
${e}</tr>
`;
  }
  tablecell(e, t) {
    const n = t.header ? "th" : "td";
    return (t.align ? `<${n} align="${t.align}">` : `<${n}>`) + e + `</${n}>
`;
  }
  /**
   * span level renderer
   */
  strong(e) {
    return `<strong>${e}</strong>`;
  }
  em(e) {
    return `<em>${e}</em>`;
  }
  codespan(e) {
    return `<code>${e}</code>`;
  }
  br() {
    return "<br>";
  }
  del(e) {
    return `<del>${e}</del>`;
  }
  link(e, t, n) {
    const i = ye(e);
    if (i === null)
      return n;
    e = i;
    let l = '<a href="' + e + '"';
    return t && (l += ' title="' + t + '"'), l += ">" + n + "</a>", l;
  }
  image(e, t, n) {
    const i = ye(e);
    if (i === null)
      return n;
    e = i;
    let l = `<img src="${e}" alt="${n}"`;
    return t && (l += ` title="${t}"`), l += ">", l;
  }
  text(e) {
    return e;
  }
}
class de {
  // no need for block level renderers
  strong(e) {
    return e;
  }
  em(e) {
    return e;
  }
  codespan(e) {
    return e;
  }
  del(e) {
    return e;
  }
  html(e) {
    return e;
  }
  text(e) {
    return e;
  }
  link(e, t, n) {
    return "" + n;
  }
  image(e, t, n) {
    return "" + n;
  }
  br() {
    return "";
  }
}
class B {
  constructor(e) {
    _(this, "options");
    _(this, "renderer");
    _(this, "textRenderer");
    this.options = e || D, this.options.renderer = this.options.renderer || new ne(), this.renderer = this.options.renderer, this.renderer.options = this.options, this.textRenderer = new de();
  }
  /**
   * Static Parse Method
   */
  static parse(e, t) {
    return new B(t).parse(e);
  }
  /**
   * Static Parse Inline Method
   */
  static parseInline(e, t) {
    return new B(t).parseInline(e);
  }
  /**
   * Parse Loop
   */
  parse(e, t = !0) {
    let n = "";
    for (let i = 0; i < e.length; i++) {
      const l = e[i];
      if (this.options.extensions && this.options.extensions.renderers && this.options.extensions.renderers[l.type]) {
        const s = l, o = this.options.extensions.renderers[s.type].call({ parser: this }, s);
        if (o !== !1 || !["space", "hr", "heading", "code", "table", "blockquote", "list", "html", "paragraph", "text"].includes(s.type)) {
          n += o || "";
          continue;
        }
      }
      switch (l.type) {
        case "space":
          continue;
        case "hr": {
          n += this.renderer.hr();
          continue;
        }
        case "heading": {
          const s = l;
          n += this.renderer.heading(this.parseInline(s.tokens), s.depth, nt(this.parseInline(s.tokens, this.textRenderer)));
          continue;
        }
        case "code": {
          const s = l;
          n += this.renderer.code(s.text, s.lang, !!s.escaped);
          continue;
        }
        case "table": {
          const s = l;
          let o = "", a = "";
          for (let c = 0; c < s.header.length; c++)
            a += this.renderer.tablecell(this.parseInline(s.header[c].tokens), { header: !0, align: s.align[c] });
          o += this.renderer.tablerow(a);
          let p = "";
          for (let c = 0; c < s.rows.length; c++) {
            const g = s.rows[c];
            a = "";
            for (let u = 0; u < g.length; u++)
              a += this.renderer.tablecell(this.parseInline(g[u].tokens), { header: !1, align: s.align[u] });
            p += this.renderer.tablerow(a);
          }
          n += this.renderer.table(o, p);
          continue;
        }
        case "blockquote": {
          const s = l, o = this.parse(s.tokens);
          n += this.renderer.blockquote(o);
          continue;
        }
        case "list": {
          const s = l, o = s.ordered, a = s.start, p = s.loose;
          let c = "";
          for (let g = 0; g < s.items.length; g++) {
            const u = s.items[g], h = u.checked, m = u.task;
            let d = "";
            if (u.task) {
              const y = this.renderer.checkbox(!!h);
              p ? u.tokens.length > 0 && u.tokens[0].type === "paragraph" ? (u.tokens[0].text = y + " " + u.tokens[0].text, u.tokens[0].tokens && u.tokens[0].tokens.length > 0 && u.tokens[0].tokens[0].type === "text" && (u.tokens[0].tokens[0].text = y + " " + u.tokens[0].tokens[0].text)) : u.tokens.unshift({
                type: "text",
                text: y + " "
              }) : d += y + " ";
            }
            d += this.parse(u.tokens, p), c += this.renderer.listitem(d, m, !!h);
          }
          n += this.renderer.list(c, o, a);
          continue;
        }
        case "html": {
          const s = l;
          n += this.renderer.html(s.text, s.block);
          continue;
        }
        case "paragraph": {
          const s = l;
          n += this.renderer.paragraph(this.parseInline(s.tokens));
          continue;
        }
        case "text": {
          let s = l, o = s.tokens ? this.parseInline(s.tokens) : s.text;
          for (; i + 1 < e.length && e[i + 1].type === "text"; )
            s = e[++i], o += `
` + (s.tokens ? this.parseInline(s.tokens) : s.text);
          n += t ? this.renderer.paragraph(o) : o;
          continue;
        }
        default: {
          const s = 'Token with "' + l.type + '" type was not found.';
          if (this.options.silent)
            return console.error(s), "";
          throw new Error(s);
        }
      }
    }
    return n;
  }
  /**
   * Parse Inline Tokens
   */
  parseInline(e, t) {
    t = t || this.renderer;
    let n = "";
    for (let i = 0; i < e.length; i++) {
      const l = e[i];
      if (this.options.extensions && this.options.extensions.renderers && this.options.extensions.renderers[l.type]) {
        const s = this.options.extensions.renderers[l.type].call({ parser: this }, l);
        if (s !== !1 || !["escape", "html", "link", "image", "strong", "em", "codespan", "br", "del", "text"].includes(l.type)) {
          n += s || "";
          continue;
        }
      }
      switch (l.type) {
        case "escape": {
          const s = l;
          n += t.text(s.text);
          break;
        }
        case "html": {
          const s = l;
          n += t.html(s.text);
          break;
        }
        case "link": {
          const s = l;
          n += t.link(s.href, s.title, this.parseInline(s.tokens, t));
          break;
        }
        case "image": {
          const s = l;
          n += t.image(s.href, s.title, s.text);
          break;
        }
        case "strong": {
          const s = l;
          n += t.strong(this.parseInline(s.tokens, t));
          break;
        }
        case "em": {
          const s = l;
          n += t.em(this.parseInline(s.tokens, t));
          break;
        }
        case "codespan": {
          const s = l;
          n += t.codespan(s.text);
          break;
        }
        case "br": {
          n += t.br();
          break;
        }
        case "del": {
          const s = l;
          n += t.del(this.parseInline(s.tokens, t));
          break;
        }
        case "text": {
          const s = l;
          n += t.text(s.text);
          break;
        }
        default: {
          const s = 'Token with "' + l.type + '" type was not found.';
          if (this.options.silent)
            return console.error(s), "";
          throw new Error(s);
        }
      }
    }
    return n;
  }
}
class F {
  constructor(e) {
    _(this, "options");
    this.options = e || D;
  }
  /**
   * Process markdown before marked
   */
  preprocess(e) {
    return e;
  }
  /**
   * Process HTML after marked is finished
   */
  postprocess(e) {
    return e;
  }
  /**
   * Process all tokens before walk tokens
   */
  processAllTokens(e) {
    return e;
  }
}
_(F, "passThroughHooks", /* @__PURE__ */ new Set([
  "preprocess",
  "postprocess",
  "processAllTokens"
]));
var Z, le, je;
class $t {
  constructor(...e) {
    xe(this, Z);
    _(this, "defaults", ce());
    _(this, "options", this.setOptions);
    _(this, "parse", X(this, Z, le).call(this, M.lex, B.parse));
    _(this, "parseInline", X(this, Z, le).call(this, M.lexInline, B.parseInline));
    _(this, "Parser", B);
    _(this, "Renderer", ne);
    _(this, "TextRenderer", de);
    _(this, "Lexer", M);
    _(this, "Tokenizer", ee);
    _(this, "Hooks", F);
    this.use(...e);
  }
  /**
   * Run callback for every token
   */
  walkTokens(e, t) {
    var i, l;
    let n = [];
    for (const s of e)
      switch (n = n.concat(t.call(this, s)), s.type) {
        case "table": {
          const o = s;
          for (const a of o.header)
            n = n.concat(this.walkTokens(a.tokens, t));
          for (const a of o.rows)
            for (const p of a)
              n = n.concat(this.walkTokens(p.tokens, t));
          break;
        }
        case "list": {
          const o = s;
          n = n.concat(this.walkTokens(o.items, t));
          break;
        }
        default: {
          const o = s;
          (l = (i = this.defaults.extensions) == null ? void 0 : i.childTokens) != null && l[o.type] ? this.defaults.extensions.childTokens[o.type].forEach((a) => {
            const p = o[a].flat(1 / 0);
            n = n.concat(this.walkTokens(p, t));
          }) : o.tokens && (n = n.concat(this.walkTokens(o.tokens, t)));
        }
      }
    return n;
  }
  use(...e) {
    const t = this.defaults.extensions || { renderers: {}, childTokens: {} };
    return e.forEach((n) => {
      const i = { ...n };
      if (i.async = this.defaults.async || i.async || !1, n.extensions && (n.extensions.forEach((l) => {
        if (!l.name)
          throw new Error("extension name required");
        if ("renderer" in l) {
          const s = t.renderers[l.name];
          s ? t.renderers[l.name] = function(...o) {
            let a = l.renderer.apply(this, o);
            return a === !1 && (a = s.apply(this, o)), a;
          } : t.renderers[l.name] = l.renderer;
        }
        if ("tokenizer" in l) {
          if (!l.level || l.level !== "block" && l.level !== "inline")
            throw new Error("extension level must be 'block' or 'inline'");
          const s = t[l.level];
          s ? s.unshift(l.tokenizer) : t[l.level] = [l.tokenizer], l.start && (l.level === "block" ? t.startBlock ? t.startBlock.push(l.start) : t.startBlock = [l.start] : l.level === "inline" && (t.startInline ? t.startInline.push(l.start) : t.startInline = [l.start]));
        }
        "childTokens" in l && l.childTokens && (t.childTokens[l.name] = l.childTokens);
      }), i.extensions = t), n.renderer) {
        const l = this.defaults.renderer || new ne(this.defaults);
        for (const s in n.renderer) {
          if (!(s in l))
            throw new Error(`renderer '${s}' does not exist`);
          if (s === "options")
            continue;
          const o = s, a = n.renderer[o], p = l[o];
          l[o] = (...c) => {
            let g = a.apply(l, c);
            return g === !1 && (g = p.apply(l, c)), g || "";
          };
        }
        i.renderer = l;
      }
      if (n.tokenizer) {
        const l = this.defaults.tokenizer || new ee(this.defaults);
        for (const s in n.tokenizer) {
          if (!(s in l))
            throw new Error(`tokenizer '${s}' does not exist`);
          if (["options", "rules", "lexer"].includes(s))
            continue;
          const o = s, a = n.tokenizer[o], p = l[o];
          l[o] = (...c) => {
            let g = a.apply(l, c);
            return g === !1 && (g = p.apply(l, c)), g;
          };
        }
        i.tokenizer = l;
      }
      if (n.hooks) {
        const l = this.defaults.hooks || new F();
        for (const s in n.hooks) {
          if (!(s in l))
            throw new Error(`hook '${s}' does not exist`);
          if (s === "options")
            continue;
          const o = s, a = n.hooks[o], p = l[o];
          F.passThroughHooks.has(s) ? l[o] = (c) => {
            if (this.defaults.async)
              return Promise.resolve(a.call(l, c)).then((u) => p.call(l, u));
            const g = a.call(l, c);
            return p.call(l, g);
          } : l[o] = (...c) => {
            let g = a.apply(l, c);
            return g === !1 && (g = p.apply(l, c)), g;
          };
        }
        i.hooks = l;
      }
      if (n.walkTokens) {
        const l = this.defaults.walkTokens, s = n.walkTokens;
        i.walkTokens = function(o) {
          let a = [];
          return a.push(s.call(this, o)), l && (a = a.concat(l.call(this, o))), a;
        };
      }
      this.defaults = { ...this.defaults, ...i };
    }), this;
  }
  setOptions(e) {
    return this.defaults = { ...this.defaults, ...e }, this;
  }
  lexer(e, t) {
    return M.lex(e, t ?? this.defaults);
  }
  parser(e, t) {
    return B.parse(e, t ?? this.defaults);
  }
}
Z = new WeakSet(), le = function(e, t) {
  return (n, i) => {
    const l = { ...i }, s = { ...this.defaults, ...l };
    this.defaults.async === !0 && l.async === !1 && (s.silent || console.warn("marked(): The async option was set to true by an extension. The async: false option sent to parse will be ignored."), s.async = !0);
    const o = X(this, Z, je).call(this, !!s.silent, !!s.async);
    if (typeof n > "u" || n === null)
      return o(new Error("marked(): input parameter is undefined or null"));
    if (typeof n != "string")
      return o(new Error("marked(): input parameter is of type " + Object.prototype.toString.call(n) + ", string expected"));
    if (s.hooks && (s.hooks.options = s), s.async)
      return Promise.resolve(s.hooks ? s.hooks.preprocess(n) : n).then((a) => e(a, s)).then((a) => s.hooks ? s.hooks.processAllTokens(a) : a).then((a) => s.walkTokens ? Promise.all(this.walkTokens(a, s.walkTokens)).then(() => a) : a).then((a) => t(a, s)).then((a) => s.hooks ? s.hooks.postprocess(a) : a).catch(o);
    try {
      s.hooks && (n = s.hooks.preprocess(n));
      let a = e(n, s);
      s.hooks && (a = s.hooks.processAllTokens(a)), s.walkTokens && this.walkTokens(a, s.walkTokens);
      let p = t(a, s);
      return s.hooks && (p = s.hooks.postprocess(p)), p;
    } catch (a) {
      return o(a);
    }
  };
}, je = function(e, t) {
  return (n) => {
    if (n.message += `
Please report this to https://github.com/markedjs/marked.`, e) {
      const i = "<p>An error occurred:</p><pre>" + R(n.message + "", !0) + "</pre>";
      return t ? Promise.resolve(i) : i;
    }
    if (t)
      return Promise.reject(n);
    throw n;
  };
};
const P = new $t();
function b(r, e) {
  return P.parse(r, e);
}
b.options = b.setOptions = function(r) {
  return P.setOptions(r), b.defaults = P.defaults, $e(b.defaults), b;
};
b.getDefaults = ce;
b.defaults = D;
b.use = function(...r) {
  return P.use(...r), b.defaults = P.defaults, $e(b.defaults), b;
};
b.walkTokens = function(r, e) {
  return P.walkTokens(r, e);
};
b.parseInline = P.parseInline;
b.Parser = B;
b.parser = B.parse;
b.Renderer = ne;
b.TextRenderer = de;
b.Lexer = M;
b.lexer = M.lex;
b.Tokenizer = ee;
b.Hooks = F;
b.parse = b;
b.options;
b.setOptions;
b.use;
b.walkTokens;
b.parseInline;
B.parse;
M.lex;
const {
  HtmlTagHydration: Lt,
  SvelteComponent: Mt,
  append_hydration: T,
  attr: v,
  children: L,
  claim_element: A,
  claim_html_tag: Bt,
  claim_space: j,
  claim_text: re,
  destroy_each: qt,
  detach: S,
  element: E,
  ensure_array_like: Re,
  get_svelte_dataset: Pt,
  init: Zt,
  insert_hydration: ke,
  noop: Se,
  null_to_empty: Ie,
  safe_not_equal: Dt,
  set_data: oe,
  set_style: O,
  space: N,
  text: ae,
  toggle_class: $
} = window.__gradio__svelte__internal;
function Ae(r, e, t) {
  const n = r.slice();
  return n[27] = e[t], n[29] = t, n;
}
function Ee(r) {
  let e, t;
  return {
    c() {
      e = E("label"), t = ae(
        /*label*/
        r[2]
      ), this.h();
    },
    l(n) {
      e = A(n, "LABEL", { class: !0, for: !0 });
      var i = L(e);
      t = re(
        i,
        /*label*/
        r[2]
      ), i.forEach(S), this.h();
    },
    h() {
      v(e, "class", "block-title svelte-17afuan"), v(e, "for", "consilium-roundtable");
    },
    m(n, i) {
      ke(n, e, i), T(e, t);
    },
    p(n, i) {
      i & /*label*/
      4 && oe(
        t,
        /*label*/
        n[2]
      );
    },
    d(n) {
      n && S(e);
    }
  };
}
function Ce(r) {
  let e, t, n, i, l = (
    /*renderMarkdown*/
    r[10](
      /*getLatestMessage*/
      r[12](
        /*participant*/
        r[27]
      )
    ) + ""
  ), s, o, a, p, c = (
    /*getEmoji*/
    r[11](
      /*participant*/
      r[27]
    ) + ""
  ), g, u, h, m = (
    /*participant*/
    r[27] + ""
  ), d, y;
  return {
    c() {
      e = E("div"), t = E("div"), n = E("div"), i = new Lt(!1), s = N(), o = E("div"), a = N(), p = E("div"), g = ae(c), u = N(), h = E("div"), d = ae(m), y = N(), this.h();
    },
    l(k) {
      e = A(k, "DIV", { class: !0, style: !0 });
      var x = L(e);
      t = A(x, "DIV", { class: !0 });
      var z = L(t);
      n = A(z, "DIV", { class: !0 });
      var I = L(n);
      i = Bt(I, !1), I.forEach(S), s = j(z), o = A(z, "DIV", { class: !0 }), L(o).forEach(S), z.forEach(S), a = j(x), p = A(x, "DIV", { class: !0, role: !0, tabindex: !0 });
      var C = L(p);
      g = re(C, c), C.forEach(S), u = j(x), h = A(x, "DIV", { class: !0 });
      var W = L(h);
      d = re(W, m), W.forEach(S), y = j(x), x.forEach(S), this.h();
    },
    h() {
      i.a = null, v(n, "class", "bubble-content svelte-17afuan"), v(o, "class", "bubble-arrow svelte-17afuan"), v(t, "class", "speech-bubble svelte-17afuan"), $(
        t,
        "visible",
        /*isBubbleVisible*/
        r[13](
          /*participant*/
          r[27]
        )
      ), v(p, "class", "avatar svelte-17afuan"), v(p, "role", "button"), v(p, "tabindex", "0"), $(
        p,
        "speaking",
        /*isAvatarActive*/
        r[14](
          /*participant*/
          r[27]
        )
      ), $(
        p,
        "thinking",
        /*thinking*/
        r[6].includes(
          /*participant*/
          r[27]
        )
      ), $(
        p,
        "responding",
        /*currentSpeaker*/
        r[5] === /*participant*/
        r[27]
      ), v(h, "class", "participant-name svelte-17afuan"), v(e, "class", "participant-seat svelte-17afuan"), O(e, "left", Q(
        /*index*/
        r[29],
        /*participants*/
        r[4].length
      ).left), O(e, "top", Q(
        /*index*/
        r[29],
        /*participants*/
        r[4].length
      ).top), O(e, "transform", Q(
        /*index*/
        r[29],
        /*participants*/
        r[4].length
      ).transform);
    },
    m(k, x) {
      ke(k, e, x), T(e, t), T(t, n), i.m(l, n), T(t, s), T(t, o), T(e, a), T(e, p), T(p, g), T(e, u), T(e, h), T(h, d), T(e, y);
    },
    p(k, x) {
      x & /*participants*/
      16 && l !== (l = /*renderMarkdown*/
      k[10](
        /*getLatestMessage*/
        k[12](
          /*participant*/
          k[27]
        )
      ) + "") && i.p(l), x & /*isBubbleVisible, participants*/
      8208 && $(
        t,
        "visible",
        /*isBubbleVisible*/
        k[13](
          /*participant*/
          k[27]
        )
      ), x & /*participants*/
      16 && c !== (c = /*getEmoji*/
      k[11](
        /*participant*/
        k[27]
      ) + "") && oe(g, c), x & /*isAvatarActive, participants*/
      16400 && $(
        p,
        "speaking",
        /*isAvatarActive*/
        k[14](
          /*participant*/
          k[27]
        )
      ), x & /*thinking, participants*/
      80 && $(
        p,
        "thinking",
        /*thinking*/
        k[6].includes(
          /*participant*/
          k[27]
        )
      ), x & /*currentSpeaker, participants*/
      48 && $(
        p,
        "responding",
        /*currentSpeaker*/
        k[5] === /*participant*/
        k[27]
      ), x & /*participants*/
      16 && m !== (m = /*participant*/
      k[27] + "") && oe(d, m), x & /*participants*/
      16 && O(e, "left", Q(
        /*index*/
        k[29],
        /*participants*/
        k[4].length
      ).left), x & /*participants*/
      16 && O(e, "top", Q(
        /*index*/
        k[29],
        /*participants*/
        k[4].length
      ).top), x & /*participants*/
      16 && O(e, "transform", Q(
        /*index*/
        k[29],
        /*participants*/
        k[4].length
      ).transform);
    },
    d(k) {
      k && S(e);
    }
  };
}
function Ot(r) {
  let e, t, n, i, l = '<div class="consensus-flame svelte-17afuan">🎭</div> <div class="table-label svelte-17afuan">CONSILIUM</div>', s, o, a, p, c = (
    /*show_label*/
    r[3] && /*label*/
    r[2] && Ee(r)
  ), g = Re(
    /*participants*/
    r[4]
  ), u = [];
  for (let h = 0; h < g.length; h += 1)
    u[h] = Ce(Ae(r, g, h));
  return {
    c() {
      e = E("div"), c && c.c(), t = N(), n = E("div"), i = E("div"), i.innerHTML = l, s = N(), o = E("div");
      for (let h = 0; h < u.length; h += 1)
        u[h].c();
      this.h();
    },
    l(h) {
      e = A(h, "DIV", { class: !0, id: !0, style: !0 });
      var m = L(e);
      c && c.l(m), t = j(m), n = A(m, "DIV", { class: !0, id: !0 });
      var d = L(n);
      i = A(d, "DIV", { class: !0, "data-svelte-h": !0 }), Pt(i) !== "svelte-fj2hkt" && (i.innerHTML = l), s = j(d), o = A(d, "DIV", { class: !0 });
      var y = L(o);
      for (let k = 0; k < u.length; k += 1)
        u[k].l(y);
      y.forEach(S), d.forEach(S), m.forEach(S), this.h();
    },
    h() {
      v(i, "class", "table-center svelte-17afuan"), v(o, "class", "participants-circle"), v(n, "class", "consilium-container svelte-17afuan"), v(n, "id", "consilium-roundtable"), v(e, "class", a = Ie(
        /*containerClasses*/
        r[9]
      ) + " svelte-17afuan"), v(
        e,
        "id",
        /*elem_id*/
        r[0]
      ), v(e, "style", p = /*containerStyle*/
      r[8] + "; " + /*minWidthStyle*/
      r[7]), $(e, "hidden", !/*visible*/
      r[1]);
    },
    m(h, m) {
      ke(h, e, m), c && c.m(e, null), T(e, t), T(e, n), T(n, i), T(n, s), T(n, o);
      for (let d = 0; d < u.length; d += 1)
        u[d] && u[d].m(o, null);
    },
    p(h, [m]) {
      if (/*show_label*/
      h[3] && /*label*/
      h[2] ? c ? c.p(h, m) : (c = Ee(h), c.c(), c.m(e, t)) : c && (c.d(1), c = null), m & /*getPosition, participants, isAvatarActive, thinking, currentSpeaker, getEmoji, isBubbleVisible, renderMarkdown, getLatestMessage*/
      31856) {
        g = Re(
          /*participants*/
          h[4]
        );
        let d;
        for (d = 0; d < g.length; d += 1) {
          const y = Ae(h, g, d);
          u[d] ? u[d].p(y, m) : (u[d] = Ce(y), u[d].c(), u[d].m(o, null));
        }
        for (; d < u.length; d += 1)
          u[d].d(1);
        u.length = g.length;
      }
      m & /*containerClasses*/
      512 && a !== (a = Ie(
        /*containerClasses*/
        h[9]
      ) + " svelte-17afuan") && v(e, "class", a), m & /*elem_id*/
      1 && v(
        e,
        "id",
        /*elem_id*/
        h[0]
      ), m & /*containerStyle, minWidthStyle*/
      384 && p !== (p = /*containerStyle*/
      h[8] + "; " + /*minWidthStyle*/
      h[7]) && v(e, "style", p), m & /*containerClasses, visible*/
      514 && $(e, "hidden", !/*visible*/
      h[1]);
    },
    i: Se,
    o: Se,
    d(h) {
      h && S(e), c && c.d(), qt(u, h);
    }
  };
}
function Q(r, e) {
  const n = (360 / e * r - 90) * (Math.PI / 180), i = 260, l = 180, s = Math.cos(n) * i, o = Math.sin(n) * l;
  return {
    left: `calc(50% + ${s}px)`,
    top: `calc(50% + ${o}px)`,
    transform: "translate(-50%, -50%)"
  };
}
function Qt(r, e, t) {
  let n, i, l, { gradio: s } = e, { elem_id: o = "" } = e, { elem_classes: a = [] } = e, { visible: p = !0 } = e, { value: c = "{}" } = e, { label: g = "Consilium Roundtable" } = e, { show_label: u = !0 } = e, { scale: h = null } = e, { min_width: m = void 0 } = e, { loading_status: d } = e, { interactive: y = !0 } = e, k = [], x = [], z = null, I = [], C = [];
  function W() {
    try {
      const f = JSON.parse(c);
      t(4, k = f.participants || []), x = f.messages || [], t(5, z = f.currentSpeaker || null), t(6, I = f.thinking || []), C = f.showBubbles || [], console.log("Clean JSON parsed:", {
        participants: k,
        messages: x,
        currentSpeaker: z,
        thinking: I,
        showBubbles: C
      });
    } catch (f) {
      console.error("Invalid JSON:", c, f);
    }
  }
  function Ne(f) {
    if (!f) return f;
    try {
      return b.setOptions({
        breaks: !0,
        // Convert line breaks to <br>
        gfm: !0,
        // GitHub flavored markdown
        sanitize: !1,
        // Allow HTML (safe since we control input)
        smartypants: !1
        // Don't convert quotes/dashes
      }), f.includes(`
`) ? b.parse(f) : b.parseInline(f);
    } catch (q) {
      return console.error("Markdown parsing error:", q), f;
    }
  }
  const Ve = {
    Anthropic: "🤖",
    Claude: "🤖",
    Search: "🔍",
    "Web Search Agent": "🔍",
    OpenAI: "🧠",
    "GPT-4": "🧠",
    Google: "💎",
    Gemini: "💎",
    "QwQ-32B": "😊",
    "DeepSeek-R1": "🔮",
    Mistral: "🐱",
    "Mistral Large": "🐱",
    "Meta-Llama-3.1-8B": "🦙"
  };
  function He(f) {
    return Ve[f] || "🤖";
  }
  function Fe(f) {
    if (I.includes(f))
      return `${f} is thinking...`;
    if (z === f)
      return `${f} is responding...`;
    const q = x.filter((J) => J.speaker === f);
    return q.length === 0 ? `${f} is ready to discuss...` : q[q.length - 1].text || `${f} responded`;
  }
  function Ge(f) {
    const q = I.includes(f), J = z === f, me = C.includes(f), be = q || J || me;
    return console.log(`${f} bubble visible:`, be, { isThinking: q, isSpeaking: J, shouldShow: me }), be;
  }
  function Ue(f) {
    return I.includes(f) || z === f;
  }
  return r.$$set = (f) => {
    "gradio" in f && t(15, s = f.gradio), "elem_id" in f && t(0, o = f.elem_id), "elem_classes" in f && t(16, a = f.elem_classes), "visible" in f && t(1, p = f.visible), "value" in f && t(17, c = f.value), "label" in f && t(2, g = f.label), "show_label" in f && t(3, u = f.show_label), "scale" in f && t(18, h = f.scale), "min_width" in f && t(19, m = f.min_width), "loading_status" in f && t(20, d = f.loading_status), "interactive" in f && t(21, y = f.interactive);
  }, r.$$.update = () => {
    r.$$.dirty & /*elem_classes*/
    65536 && t(9, n = `wrapper ${a.join(" ")}`), r.$$.dirty & /*scale*/
    262144 && t(8, i = h ? `--scale: ${h}` : ""), r.$$.dirty & /*min_width*/
    524288 && t(7, l = m ? `min-width: ${m}px` : ""), r.$$.dirty & /*interactive*/
    2097152, r.$$.dirty & /*value*/
    131072 && W();
  }, [
    o,
    p,
    g,
    u,
    k,
    z,
    I,
    l,
    i,
    n,
    Ne,
    He,
    Fe,
    Ge,
    Ue,
    s,
    a,
    c,
    h,
    m,
    d,
    y
  ];
}
class jt extends Mt {
  constructor(e) {
    super(), Zt(this, e, Qt, Ot, Dt, {
      gradio: 15,
      elem_id: 0,
      elem_classes: 16,
      visible: 1,
      value: 17,
      label: 2,
      show_label: 3,
      scale: 18,
      min_width: 19,
      loading_status: 20,
      interactive: 21
    });
  }
}
const {
  SvelteComponent: Nt,
  claim_component: Vt,
  create_component: Ht,
  destroy_component: Ft,
  init: Gt,
  mount_component: Ut,
  noop: Wt,
  safe_not_equal: Jt,
  transition_in: Xt,
  transition_out: Yt
} = window.__gradio__svelte__internal, { onMount: nn } = window.__gradio__svelte__internal;
function Kt(r) {
  let e, t;
  return e = new jt({
    props: {
      value: (
        /*value*/
        r[0]
      ),
      label: "Example Roundtable",
      visible: !0,
      elem_id: "example",
      elem_classes: [],
      scale: null,
      min_width: 600,
      interactive: !0,
      gradio: {},
      loading_status: {},
      show_label: !0
    }
  }), {
    c() {
      Ht(e.$$.fragment);
    },
    l(n) {
      Vt(e.$$.fragment, n);
    },
    m(n, i) {
      Ut(e, n, i), t = !0;
    },
    p: Wt,
    i(n) {
      t || (Xt(e.$$.fragment, n), t = !0);
    },
    o(n) {
      Yt(e.$$.fragment, n), t = !1;
    },
    d(n) {
      Ft(e, n);
    }
  };
}
function en(r) {
  return [JSON.stringify({
    participants: ["Claude", "GPT-4", "Mistral"],
    messages: [
      {
        speaker: "Claude",
        text: "Welcome to the roundtable!"
      }
    ],
    currentSpeaker: "Claude",
    thinking: []
  })];
}
class sn extends Nt {
  constructor(e) {
    super(), Gt(this, e, en, Kt, Jt, {});
  }
}
export {
  sn as default
};
