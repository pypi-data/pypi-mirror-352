var Xe = Object.defineProperty;
var we = (o) => {
  throw TypeError(o);
};
var Je = (o, e, t) => e in o ? Xe(o, e, { enumerable: !0, configurable: !0, writable: !0, value: t }) : o[e] = t;
var _ = (o, e, t) => Je(o, typeof e != "symbol" ? e + "" : e, t), We = (o, e, t) => e.has(o) || we("Cannot " + t);
var xe = (o, e, t) => e.has(o) ? we("Cannot add the same private member more than once") : e instanceof WeakSet ? e.add(o) : e.set(o, t);
var W = (o, e, t) => (We(o, e, "access private method"), t);
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
function Le(o) {
  D = o;
}
const Me = /[&<>"']/, Ye = new RegExp(Me.source, "g"), $e = /[<>"']|&(?!(#\d{1,7}|#[Xx][a-fA-F0-9]{1,6}|\w+);)/, Ke = new RegExp($e.source, "g"), et = {
  "&": "&amp;",
  "<": "&lt;",
  ">": "&gt;",
  '"': "&quot;",
  "'": "&#39;"
}, _e = (o) => et[o];
function R(o, e) {
  if (e) {
    if (Me.test(o))
      return o.replace(Ye, _e);
  } else if ($e.test(o))
    return o.replace(Ke, _e);
  return o;
}
const tt = /&(#(?:\d+)|(?:#x[0-9A-Fa-f]+)|(?:\w+));?/ig;
function nt(o) {
  return o.replace(tt, (e, t) => (t = t.toLowerCase(), t === "colon" ? ":" : t.charAt(0) === "#" ? t.charAt(1) === "x" ? String.fromCharCode(parseInt(t.substring(2), 16)) : String.fromCharCode(+t.substring(1)) : ""));
}
const st = /(^|[^\[])\^/g;
function w(o, e) {
  let t = typeof o == "string" ? o : o.source;
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
function ye(o) {
  try {
    o = encodeURI(o).replace(/%25/g, "%");
  } catch {
    return null;
  }
  return o;
}
const H = { exec: () => null };
function Te(o, e) {
  const t = o.replace(/\|/g, (l, s, r) => {
    let a = !1, p = s;
    for (; --p >= 0 && r[p] === "\\"; )
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
function Y(o, e, t) {
  const n = o.length;
  if (n === 0)
    return "";
  let i = 0;
  for (; i < n && o.charAt(n - i - 1) === e; )
    i++;
  return o.slice(0, n - i);
}
function it(o, e) {
  if (o.indexOf(e[1]) === -1)
    return -1;
  let t = 0;
  for (let n = 0; n < o.length; n++)
    if (o[n] === "\\")
      n++;
    else if (o[n] === e[0])
      t++;
    else if (o[n] === e[1] && (t--, t < 0))
      return n;
  return -1;
}
function ve(o, e, t, n) {
  const i = e.href, l = e.title ? R(e.title) : null, s = o[1].replace(/\\([\[\]])/g, "$1");
  if (o[0].charAt(0) !== "!") {
    n.state.inLink = !0;
    const r = {
      type: "link",
      raw: t,
      href: i,
      title: l,
      text: s,
      tokens: n.inlineTokens(s)
    };
    return n.state.inLink = !1, r;
  }
  return {
    type: "image",
    raw: t,
    href: i,
    title: l,
    text: R(s)
  };
}
function lt(o, e) {
  const t = o.match(/^(\s+)(?:```)/);
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
      let r = "", a = "", p = !1;
      for (; e; ) {
        let c = !1;
        if (!(t = s.exec(e)) || this.rules.block.hr.test(e))
          break;
        r = t[0], e = e.substring(r.length);
        let g = t[2].split(`
`, 1)[0].replace(/^\t+/, (k) => " ".repeat(3 * k.length)), h = e.split(`
`, 1)[0], u = 0;
        this.options.pedantic ? (u = 2, a = g.trimStart()) : (u = t[2].search(/[^ ]/), u = u > 4 ? 1 : u, a = g.slice(u), u += t[1].length);
        let b = !1;
        if (!g && /^ *$/.test(h) && (r += h + `
`, e = e.substring(h.length + 1), c = !0), !c) {
          const k = new RegExp(`^ {0,${Math.min(3, u - 1)}}(?:[*+-]|\\d{1,9}[.)])((?:[ 	][^\\n]*)?(?:\\n|$))`), x = new RegExp(`^ {0,${Math.min(3, u - 1)}}((?:- *){3,}|(?:_ *){3,}|(?:\\* *){3,})(?:\\n+|$)`), z = new RegExp(`^ {0,${Math.min(3, u - 1)}}(?:\`\`\`|~~~)`), S = new RegExp(`^ {0,${Math.min(3, u - 1)}}#`);
          for (; e; ) {
            const C = e.split(`
`, 1)[0];
            if (h = C, this.options.pedantic && (h = h.replace(/^ {1,4}(?=( {4})*[^ ])/g, "  ")), z.test(h) || S.test(h) || k.test(h) || x.test(e))
              break;
            if (h.search(/[^ ]/) >= u || !h.trim())
              a += `
` + h.slice(u);
            else {
              if (b || g.search(/[^ ]/) >= 4 || z.test(g) || S.test(g) || x.test(g))
                break;
              a += `
` + h;
            }
            !b && !h.trim() && (b = !0), r += C + `
`, e = e.substring(C.length + 1), g = h.slice(u);
          }
        }
        l.loose || (p ? l.loose = !0 : /\n *\n *$/.test(r) && (p = !0));
        let d = null, y;
        this.options.gfm && (d = /^\[[ xX]\] /.exec(a), d && (y = d[0] !== "[ ] ", a = a.replace(/^\[[ xX]\] +/, ""))), l.items.push({
          type: "list_item",
          raw: r,
          task: !!d,
          checked: y,
          loose: !1,
          text: a,
          tokens: []
        }), l.raw += r;
      }
      l.items[l.items.length - 1].raw = r.trimEnd(), l.items[l.items.length - 1].text = a.trimEnd(), l.raw = l.raw.trimEnd();
      for (let c = 0; c < l.items.length; c++)
        if (this.lexer.state.top = !1, l.items[c].tokens = this.lexer.blockTokens(l.items[c].text, []), !l.loose) {
          const g = l.items[c].tokens.filter((u) => u.type === "space"), h = g.length > 0 && g.some((u) => /\n.*\n/.test(u.raw));
          l.loose = h;
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
    const n = Te(t[1]), i = t[2].replace(/^\||\| *$/g, "").split("|"), l = t[3] && t[3].trim() ? t[3].replace(/\n[ \t]*$/, "").split(`
`) : [], s = {
      type: "table",
      raw: t[0],
      header: [],
      align: [],
      rows: []
    };
    if (n.length === i.length) {
      for (const r of i)
        /^ *-+: *$/.test(r) ? s.align.push("right") : /^ *:-+: *$/.test(r) ? s.align.push("center") : /^ *:-+ *$/.test(r) ? s.align.push("left") : s.align.push(null);
      for (const r of n)
        s.header.push({
          text: r,
          tokens: this.lexer.inline(r)
        });
      for (const r of l)
        s.rows.push(Te(r, s.header.length).map((a) => ({
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
      return i = i.trim(), /^</.test(i) && (this.options.pedantic && !/>$/.test(n) ? i = i.slice(1) : i = i.slice(1, -1)), ve(t, {
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
      return ve(n, l, n[0], this.lexer);
    }
  }
  emStrong(e, t, n = "") {
    let i = this.rules.inline.emStrongLDelim.exec(e);
    if (!i || i[3] && n.match(/[\p{L}\p{N}]/u))
      return;
    if (!(i[1] || i[2] || "") || !n || this.rules.inline.punctuation.exec(n)) {
      const s = [...i[0]].length - 1;
      let r, a, p = s, c = 0;
      const g = i[0][0] === "*" ? this.rules.inline.emStrongRDelimAst : this.rules.inline.emStrongRDelimUnd;
      for (g.lastIndex = 0, t = t.slice(-1 * e.length + s); (i = g.exec(t)) != null; ) {
        if (r = i[1] || i[2] || i[3] || i[4] || i[5] || i[6], !r)
          continue;
        if (a = [...r].length, i[3] || i[4]) {
          p += a;
          continue;
        } else if ((i[5] || i[6]) && s % 3 && !((s + a) % 3)) {
          c += a;
          continue;
        }
        if (p -= a, p > 0)
          continue;
        a = Math.min(a, a + p + c);
        const h = [...i[0]][0].length, u = e.slice(0, s + i.index + h + a);
        if (Math.min(s, a) % 2) {
          const d = u.slice(1, -1);
          return {
            type: "em",
            raw: u,
            text: d,
            tokens: this.lexer.inlineTokens(d)
          };
        }
        const b = u.slice(2, -2);
        return {
          type: "strong",
          raw: u,
          text: b,
          tokens: this.lexer.inlineTokens(b)
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
const rt = /^(?: *(?:\n|$))+/, ot = /^( {4}[^\n]+(?:\n(?: *(?:\n|$))*)?)+/, at = /^ {0,3}(`{3,}(?=[^`\n]*(?:\n|$))|~{3,})([^\n]*)(?:\n|$)(?:|([\s\S]*?)(?:\n|$))(?: {0,3}\1[~`]* *(?=\n|$)|$)/, U = /^ {0,3}((?:-[\t ]*){3,}|(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})(?:\n+|$)/, ct = /^ {0,3}(#{1,6})(?=\s|$)(.*)(?:\n+|$)/, Be = /(?:[*+-]|\d{1,9}[.)])/, Pe = w(/^(?!bull |blockCode|fences|blockquote|heading|html)((?:.|\n(?!\s*?\n|bull |blockCode|fences|blockquote|heading|html))+?)\n {0,3}(=+|-+) *(?:\n+|$)/).replace(/bull/g, Be).replace(/blockCode/g, / {4}/).replace(/fences/g, / {0,3}(?:`{3,}|~{3,})/).replace(/blockquote/g, / {0,3}>/).replace(/heading/g, / {0,3}#{1,6}/).replace(/html/g, / {0,3}<[^\n>]+>\n/).getRegex(), he = /^([^\n]+(?:\n(?!hr|heading|lheading|blockquote|fences|list|html|table| +\n)[^\n]+)*)/, ht = /^[^\n]+/, ue = /(?!\s*\])(?:\\.|[^\[\]\\])+/, ut = w(/^ {0,3}\[(label)\]: *(?:\n *)?([^<\s][^\s]*|<.*?>)(?:(?: +(?:\n *)?| *\n *)(title))? *(?:\n+|$)/).replace("label", ue).replace("title", /(?:"(?:\\"?|[^"\\])*"|'[^'\n]*(?:\n[^'\n]+)*\n?'|\([^()]*\))/).getRegex(), pt = w(/^( {0,3}bull)([ \t][^\n]+?)?(?:\n|$)/).replace(/bull/g, Be).getRegex(), se = "address|article|aside|base|basefont|blockquote|body|caption|center|col|colgroup|dd|details|dialog|dir|div|dl|dt|fieldset|figcaption|figure|footer|form|frame|frameset|h[1-6]|head|header|hr|html|iframe|legend|li|link|main|menu|menuitem|meta|nav|noframes|ol|optgroup|option|p|param|search|section|summary|table|tbody|td|tfoot|th|thead|title|tr|track|ul", pe = /<!--(?:-?>|[\s\S]*?(?:-->|$))/, ft = w("^ {0,3}(?:<(script|pre|style|textarea)[\\s>][\\s\\S]*?(?:</\\1>[^\\n]*\\n+|$)|comment[^\\n]*(\\n+|$)|<\\?[\\s\\S]*?(?:\\?>\\n*|$)|<![A-Z][\\s\\S]*?(?:>\\n*|$)|<!\\[CDATA\\[[\\s\\S]*?(?:\\]\\]>\\n*|$)|</?(tag)(?: +|\\n|/?>)[\\s\\S]*?(?:(?:\\n *)+\\n|$)|<(?!script|pre|style|textarea)([a-z][\\w-]*)(?:attribute)*? */?>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n *)+\\n|$)|</(?!script|pre|style|textarea)[a-z][\\w-]*\\s*>(?=[ \\t]*(?:\\n|$))[\\s\\S]*?(?:(?:\\n *)+\\n|$))", "i").replace("comment", pe).replace("tag", se).replace("attribute", / +[a-zA-Z:_][\w.:-]*(?: *= *"[^"\n]*"| *= *'[^'\n]*'| *= *[^\s"'=<>`]+)?/).getRegex(), qe = w(he).replace("hr", U).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("|lheading", "").replace("|table", "").replace("blockquote", " {0,3}>").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", se).getRegex(), gt = w(/^( {0,3}> ?(paragraph|[^\n]*)(?:\n|$))+/).replace("paragraph", qe).getRegex(), fe = {
  blockquote: gt,
  code: ot,
  def: ut,
  fences: at,
  heading: ct,
  hr: U,
  html: ft,
  lheading: Pe,
  list: pt,
  newline: rt,
  paragraph: qe,
  table: H,
  text: ht
}, ze = w("^ *([^\\n ].*)\\n {0,3}((?:\\| *)?:?-+:? *(?:\\| *:?-+:? *)*(?:\\| *)?)(?:\\n((?:(?! *\\n|hr|heading|blockquote|code|fences|list|html).*(?:\\n|$))*)\\n*|$)").replace("hr", U).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("blockquote", " {0,3}>").replace("code", " {4}[^\\n]").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", se).getRegex(), dt = {
  ...fe,
  table: ze,
  paragraph: w(he).replace("hr", U).replace("heading", " {0,3}#{1,6}(?:\\s|$)").replace("|lheading", "").replace("table", ze).replace("blockquote", " {0,3}>").replace("fences", " {0,3}(?:`{3,}(?=[^`\\n]*\\n)|~{3,})[^\\n]*\\n").replace("list", " {0,3}(?:[*+-]|1[.)]) ").replace("html", "</?(?:tag)(?: +|\\n|/?>)|<(?:script|pre|style|textarea|!--)").replace("tag", se).getRegex()
}, kt = {
  ...fe,
  html: w(`^ *(?:comment *(?:\\n|\\s*$)|<(tag)[\\s\\S]+?</\\1> *(?:\\n{2,}|\\s*$)|<tag(?:"[^"]*"|'[^']*'|\\s[^'"/>\\s]*)*?/?> *(?:\\n{2,}|\\s*$))`).replace("comment", pe).replace(/tag/g, "(?!(?:a|em|strong|small|s|cite|q|dfn|abbr|data|time|code|var|samp|kbd|sub|sup|i|b|u|mark|ruby|rt|rp|bdi|bdo|span|br|wbr|ins|del|img)\\b)\\w+(?!:|[^\\w\\s@]*@)\\b").getRegex(),
  def: /^ *\[([^\]]+)\]: *<?([^\s>]+)>?(?: +(["(][^\n]+[")]))? *(?:\n+|$)/,
  heading: /^(#{1,6})(.*)(?:\n+|$)/,
  fences: H,
  // fences not supported
  lheading: /^(.+?)\n {0,3}(=+|-+) *(?:\n+|$)/,
  paragraph: w(he).replace("hr", U).replace("heading", ` *#{1,6} *[^
]`).replace("lheading", Pe).replace("|table", "").replace("blockquote", " {0,3}>").replace("|fences", "").replace("|list", "").replace("|html", "").replace("|tag", "").getRegex()
}, Ze = /^\\([!"#$%&'()*+,\-./:;<=>?@\[\]\\^_`{|}~])/, bt = /^(`+)([^`]|[^`][\s\S]*?[^`])\1(?!`)/, De = /^( {2,}|\\)\n(?!\s*$)/, mt = /^(`+|[^`])(?:(?= {2,}\n)|[\s\S]*?(?:(?=[\\<!\[`*_]|\b_|$)|[^ ](?= {2,}\n)))/, G = "\\p{P}\\p{S}", wt = w(/^((?![*_])[\spunctuation])/, "u").replace(/punctuation/g, G).getRegex(), xt = /\[[^[\]]*?\]\([^\(\)]*?\)|`[^`]*?`|<[^<>]*?>/g, _t = w(/^(?:\*+(?:((?!\*)[punct])|[^\s*]))|^_+(?:((?!_)[punct])|([^\s_]))/, "u").replace(/punct/g, G).getRegex(), yt = w("^[^_*]*?__[^_*]*?\\*[^_*]*?(?=__)|[^*]+(?=[^*])|(?!\\*)[punct](\\*+)(?=[\\s]|$)|[^punct\\s](\\*+)(?!\\*)(?=[punct\\s]|$)|(?!\\*)[punct\\s](\\*+)(?=[^punct\\s])|[\\s](\\*+)(?!\\*)(?=[punct])|(?!\\*)[punct](\\*+)(?!\\*)(?=[punct])|[^punct\\s](\\*+)(?=[^punct\\s])", "gu").replace(/punct/g, G).getRegex(), Tt = w("^[^_*]*?\\*\\*[^_*]*?_[^_*]*?(?=\\*\\*)|[^_]+(?=[^_])|(?!_)[punct](_+)(?=[\\s]|$)|[^punct\\s](_+)(?!_)(?=[punct\\s]|$)|(?!_)[punct\\s](_+)(?=[^punct\\s])|[\\s](_+)(?!_)(?=[punct])|(?!_)[punct](_+)(?!_)(?=[punct])", "gu").replace(/punct/g, G).getRegex(), vt = w(/\\([punct])/, "gu").replace(/punct/g, G).getRegex(), zt = w(/^<(scheme:[^\s\x00-\x1f<>]*|email)>/).replace("scheme", /[a-zA-Z][a-zA-Z0-9+.-]{1,31}/).replace("email", /[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+(@)[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+(?![-_])/).getRegex(), Rt = w(pe).replace("(?:-->|$)", "-->").getRegex(), It = w("^comment|^</[a-zA-Z][\\w:-]*\\s*>|^<[a-zA-Z][\\w-]*(?:attribute)*?\\s*/?>|^<\\?[\\s\\S]*?\\?>|^<![a-zA-Z]+\\s[\\s\\S]*?>|^<!\\[CDATA\\[[\\s\\S]*?\\]\\]>").replace("comment", Rt).replace("attribute", /\s+[a-zA-Z:_][\w.:-]*(?:\s*=\s*"[^"]*"|\s*=\s*'[^']*'|\s*=\s*[^\s"'=<>`]+)?/).getRegex(), te = /(?:\[(?:\\.|[^\[\]\\])*\]|\\.|`[^`]*`|[^\[\]\\`])*?/, St = w(/^!?\[(label)\]\(\s*(href)(?:\s+(title))?\s*\)/).replace("label", te).replace("href", /<(?:\\.|[^\n<>\\])+>|[^\s\x00-\x1f]*/).replace("title", /"(?:\\"?|[^"\\])*"|'(?:\\'?|[^'\\])*'|\((?:\\\)?|[^)\\])*\)/).getRegex(), Oe = w(/^!?\[(label)\]\[(ref)\]/).replace("label", te).replace("ref", ue).getRegex(), Qe = w(/^!?\[(ref)\](?:\[\])?/).replace("ref", ue).getRegex(), At = w("reflink|nolink(?!\\()", "g").replace("reflink", Oe).replace("nolink", Qe).getRegex(), ge = {
  _backpedal: H,
  // only used for GFM url
  anyPunctuation: vt,
  autolink: zt,
  blockSkip: xt,
  br: De,
  code: bt,
  del: H,
  emStrongLDelim: _t,
  emStrongRDelimAst: yt,
  emStrongRDelimUnd: Tt,
  escape: Ze,
  link: St,
  nolink: Qe,
  punctuation: wt,
  reflink: Oe,
  reflinkSearch: At,
  tag: It,
  text: mt,
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
}, N = {
  normal: ge,
  gfm: ie,
  breaks: Ct,
  pedantic: Et
};
class $ {
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
      inline: N.normal
    };
    this.options.pedantic ? (t.block = K.pedantic, t.inline = N.pedantic) : this.options.gfm && (t.block = K.gfm, this.options.breaks ? t.inline = N.breaks : t.inline = N.gfm), this.tokenizer.rules = t;
  }
  /**
   * Expose Rules
   */
  static get rules() {
    return {
      block: K,
      inline: N
    };
  }
  /**
   * Static Lex Method
   */
  static lex(e, t) {
    return new $(t).lex(e);
  }
  /**
   * Static Lex Inline Method
   */
  static lexInline(e, t) {
    return new $(t).inlineTokens(e);
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
    this.options.pedantic ? e = e.replace(/\t/g, "    ").replace(/^ +$/gm, "") : e = e.replace(/^( *)(\t+)/gm, (r, a, p) => a + "    ".repeat(p.length));
    let n, i, l, s;
    for (; e; )
      if (!(this.options.extensions && this.options.extensions.block && this.options.extensions.block.some((r) => (n = r.call({ lexer: this }, e, t)) ? (e = e.substring(n.raw.length), t.push(n), !0) : !1))) {
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
          let r = 1 / 0;
          const a = e.slice(1);
          let p;
          this.options.extensions.startBlock.forEach((c) => {
            p = c.call({ lexer: this }, a), typeof p == "number" && p >= 0 && (r = Math.min(r, p));
          }), r < 1 / 0 && r >= 0 && (l = e.substring(0, r + 1));
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
          const r = "Infinite loop on byte: " + e.charCodeAt(0);
          if (this.options.silent) {
            console.error(r);
            break;
          } else
            throw new Error(r);
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
    let n, i, l, s = e, r, a, p;
    if (this.tokens.links) {
      const c = Object.keys(this.tokens.links);
      if (c.length > 0)
        for (; (r = this.tokenizer.rules.inline.reflinkSearch.exec(s)) != null; )
          c.includes(r[0].slice(r[0].lastIndexOf("[") + 1, -1)) && (s = s.slice(0, r.index) + "[" + "a".repeat(r[0].length - 2) + "]" + s.slice(this.tokenizer.rules.inline.reflinkSearch.lastIndex));
    }
    for (; (r = this.tokenizer.rules.inline.blockSkip.exec(s)) != null; )
      s = s.slice(0, r.index) + "[" + "a".repeat(r[0].length - 2) + "]" + s.slice(this.tokenizer.rules.inline.blockSkip.lastIndex);
    for (; (r = this.tokenizer.rules.inline.anyPunctuation.exec(s)) != null; )
      s = s.slice(0, r.index) + "++" + s.slice(this.tokenizer.rules.inline.anyPunctuation.lastIndex);
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
          let h;
          this.options.extensions.startInline.forEach((u) => {
            h = u.call({ lexer: this }, g), typeof h == "number" && h >= 0 && (c = Math.min(c, h));
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
        const s = l, r = this.options.extensions.renderers[s.type].call({ parser: this }, s);
        if (r !== !1 || !["space", "hr", "heading", "code", "table", "blockquote", "list", "html", "paragraph", "text"].includes(s.type)) {
          n += r || "";
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
          let r = "", a = "";
          for (let c = 0; c < s.header.length; c++)
            a += this.renderer.tablecell(this.parseInline(s.header[c].tokens), { header: !0, align: s.align[c] });
          r += this.renderer.tablerow(a);
          let p = "";
          for (let c = 0; c < s.rows.length; c++) {
            const g = s.rows[c];
            a = "";
            for (let h = 0; h < g.length; h++)
              a += this.renderer.tablecell(this.parseInline(g[h].tokens), { header: !1, align: s.align[h] });
            p += this.renderer.tablerow(a);
          }
          n += this.renderer.table(r, p);
          continue;
        }
        case "blockquote": {
          const s = l, r = this.parse(s.tokens);
          n += this.renderer.blockquote(r);
          continue;
        }
        case "list": {
          const s = l, r = s.ordered, a = s.start, p = s.loose;
          let c = "";
          for (let g = 0; g < s.items.length; g++) {
            const h = s.items[g], u = h.checked, b = h.task;
            let d = "";
            if (h.task) {
              const y = this.renderer.checkbox(!!u);
              p ? h.tokens.length > 0 && h.tokens[0].type === "paragraph" ? (h.tokens[0].text = y + " " + h.tokens[0].text, h.tokens[0].tokens && h.tokens[0].tokens.length > 0 && h.tokens[0].tokens[0].type === "text" && (h.tokens[0].tokens[0].text = y + " " + h.tokens[0].tokens[0].text)) : h.tokens.unshift({
                type: "text",
                text: y + " "
              }) : d += y + " ";
            }
            d += this.parse(h.tokens, p), c += this.renderer.listitem(d, b, !!u);
          }
          n += this.renderer.list(c, r, a);
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
          let s = l, r = s.tokens ? this.parseInline(s.tokens) : s.text;
          for (; i + 1 < e.length && e[i + 1].type === "text"; )
            s = e[++i], r += `
` + (s.tokens ? this.parseInline(s.tokens) : s.text);
          n += t ? this.renderer.paragraph(r) : r;
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
class Lt {
  constructor(...e) {
    xe(this, Z);
    _(this, "defaults", ce());
    _(this, "options", this.setOptions);
    _(this, "parse", W(this, Z, le).call(this, $.lex, B.parse));
    _(this, "parseInline", W(this, Z, le).call(this, $.lexInline, B.parseInline));
    _(this, "Parser", B);
    _(this, "Renderer", ne);
    _(this, "TextRenderer", de);
    _(this, "Lexer", $);
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
          const r = s;
          for (const a of r.header)
            n = n.concat(this.walkTokens(a.tokens, t));
          for (const a of r.rows)
            for (const p of a)
              n = n.concat(this.walkTokens(p.tokens, t));
          break;
        }
        case "list": {
          const r = s;
          n = n.concat(this.walkTokens(r.items, t));
          break;
        }
        default: {
          const r = s;
          (l = (i = this.defaults.extensions) == null ? void 0 : i.childTokens) != null && l[r.type] ? this.defaults.extensions.childTokens[r.type].forEach((a) => {
            const p = r[a].flat(1 / 0);
            n = n.concat(this.walkTokens(p, t));
          }) : r.tokens && (n = n.concat(this.walkTokens(r.tokens, t)));
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
          s ? t.renderers[l.name] = function(...r) {
            let a = l.renderer.apply(this, r);
            return a === !1 && (a = s.apply(this, r)), a;
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
          const r = s, a = n.renderer[r], p = l[r];
          l[r] = (...c) => {
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
          const r = s, a = n.tokenizer[r], p = l[r];
          l[r] = (...c) => {
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
          const r = s, a = n.hooks[r], p = l[r];
          F.passThroughHooks.has(s) ? l[r] = (c) => {
            if (this.defaults.async)
              return Promise.resolve(a.call(l, c)).then((h) => p.call(l, h));
            const g = a.call(l, c);
            return p.call(l, g);
          } : l[r] = (...c) => {
            let g = a.apply(l, c);
            return g === !1 && (g = p.apply(l, c)), g;
          };
        }
        i.hooks = l;
      }
      if (n.walkTokens) {
        const l = this.defaults.walkTokens, s = n.walkTokens;
        i.walkTokens = function(r) {
          let a = [];
          return a.push(s.call(this, r)), l && (a = a.concat(l.call(this, r))), a;
        };
      }
      this.defaults = { ...this.defaults, ...i };
    }), this;
  }
  setOptions(e) {
    return this.defaults = { ...this.defaults, ...e }, this;
  }
  lexer(e, t) {
    return $.lex(e, t ?? this.defaults);
  }
  parser(e, t) {
    return B.parse(e, t ?? this.defaults);
  }
}
Z = new WeakSet(), le = function(e, t) {
  return (n, i) => {
    const l = { ...i }, s = { ...this.defaults, ...l };
    this.defaults.async === !0 && l.async === !1 && (s.silent || console.warn("marked(): The async option was set to true by an extension. The async: false option sent to parse will be ignored."), s.async = !0);
    const r = W(this, Z, je).call(this, !!s.silent, !!s.async);
    if (typeof n > "u" || n === null)
      return r(new Error("marked(): input parameter is undefined or null"));
    if (typeof n != "string")
      return r(new Error("marked(): input parameter is of type " + Object.prototype.toString.call(n) + ", string expected"));
    if (s.hooks && (s.hooks.options = s), s.async)
      return Promise.resolve(s.hooks ? s.hooks.preprocess(n) : n).then((a) => e(a, s)).then((a) => s.hooks ? s.hooks.processAllTokens(a) : a).then((a) => s.walkTokens ? Promise.all(this.walkTokens(a, s.walkTokens)).then(() => a) : a).then((a) => t(a, s)).then((a) => s.hooks ? s.hooks.postprocess(a) : a).catch(r);
    try {
      s.hooks && (n = s.hooks.preprocess(n));
      let a = e(n, s);
      s.hooks && (a = s.hooks.processAllTokens(a)), s.walkTokens && this.walkTokens(a, s.walkTokens);
      let p = t(a, s);
      return s.hooks && (p = s.hooks.postprocess(p)), p;
    } catch (a) {
      return r(a);
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
const q = new Lt();
function m(o, e) {
  return q.parse(o, e);
}
m.options = m.setOptions = function(o) {
  return q.setOptions(o), m.defaults = q.defaults, Le(m.defaults), m;
};
m.getDefaults = ce;
m.defaults = D;
m.use = function(...o) {
  return q.use(...o), m.defaults = q.defaults, Le(m.defaults), m;
};
m.walkTokens = function(o, e) {
  return q.walkTokens(o, e);
};
m.parseInline = q.parseInline;
m.Parser = B;
m.parser = B.parse;
m.Renderer = ne;
m.TextRenderer = de;
m.Lexer = $;
m.lexer = $.lex;
m.Tokenizer = ee;
m.Hooks = F;
m.parse = m;
m.options;
m.setOptions;
m.use;
m.walkTokens;
m.parseInline;
B.parse;
$.lex;
const {
  HtmlTagHydration: Mt,
  SvelteComponent: $t,
  append_hydration: v,
  attr: T,
  children: M,
  claim_element: A,
  claim_html_tag: Bt,
  claim_space: j,
  claim_text: re,
  destroy_each: Pt,
  detach: I,
  element: E,
  ensure_array_like: Re,
  get_svelte_dataset: qt,
  init: Zt,
  insert_hydration: ke,
  noop: Ie,
  null_to_empty: Se,
  safe_not_equal: Dt,
  set_data: oe,
  set_style: O,
  space: V,
  text: ae,
  toggle_class: L
} = window.__gradio__svelte__internal;
function Ae(o, e, t) {
  const n = o.slice();
  return n[27] = e[t], n[29] = t, n;
}
function Ee(o) {
  let e, t;
  return {
    c() {
      e = E("label"), t = ae(
        /*label*/
        o[2]
      ), this.h();
    },
    l(n) {
      e = A(n, "LABEL", { class: !0, for: !0 });
      var i = M(e);
      t = re(
        i,
        /*label*/
        o[2]
      ), i.forEach(I), this.h();
    },
    h() {
      T(e, "class", "block-title svelte-1eo2cb7"), T(e, "for", "consilium-roundtable");
    },
    m(n, i) {
      ke(n, e, i), v(e, t);
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
      n && I(e);
    }
  };
}
function Ce(o) {
  let e, t, n, i, l = (
    /*renderMarkdown*/
    o[10](
      /*getLatestMessage*/
      o[12](
        /*participant*/
        o[27]
      )
    ) + ""
  ), s, r, a, p, c = (
    /*getEmoji*/
    o[11](
      /*participant*/
      o[27]
    ) + ""
  ), g, h, u, b = (
    /*participant*/
    o[27] + ""
  ), d, y;
  return {
    c() {
      e = E("div"), t = E("div"), n = E("div"), i = new Mt(!1), s = V(), r = E("div"), a = V(), p = E("div"), g = ae(c), h = V(), u = E("div"), d = ae(b), y = V(), this.h();
    },
    l(k) {
      e = A(k, "DIV", { class: !0, style: !0 });
      var x = M(e);
      t = A(x, "DIV", { class: !0 });
      var z = M(t);
      n = A(z, "DIV", { class: !0 });
      var S = M(n);
      i = Bt(S, !1), S.forEach(I), s = j(z), r = A(z, "DIV", { class: !0 }), M(r).forEach(I), z.forEach(I), a = j(x), p = A(x, "DIV", { class: !0, role: !0, tabindex: !0 });
      var C = M(p);
      g = re(C, c), C.forEach(I), h = j(x), u = A(x, "DIV", { class: !0 });
      var X = M(u);
      d = re(X, b), X.forEach(I), y = j(x), x.forEach(I), this.h();
    },
    h() {
      i.a = null, T(n, "class", "bubble-content svelte-1eo2cb7"), T(r, "class", "bubble-arrow svelte-1eo2cb7"), T(t, "class", "speech-bubble svelte-1eo2cb7"), L(
        t,
        "visible",
        /*isBubbleVisible*/
        o[13](
          /*participant*/
          o[27]
        )
      ), T(p, "class", "avatar svelte-1eo2cb7"), T(p, "role", "button"), T(p, "tabindex", "0"), L(
        p,
        "speaking",
        /*isAvatarActive*/
        o[14](
          /*participant*/
          o[27]
        )
      ), L(
        p,
        "thinking",
        /*thinking*/
        o[6].includes(
          /*participant*/
          o[27]
        )
      ), L(
        p,
        "responding",
        /*currentSpeaker*/
        o[5] === /*participant*/
        o[27]
      ), T(u, "class", "participant-name svelte-1eo2cb7"), T(e, "class", "participant-seat svelte-1eo2cb7"), O(e, "left", Q(
        /*index*/
        o[29],
        /*participants*/
        o[4].length
      ).left), O(e, "top", Q(
        /*index*/
        o[29],
        /*participants*/
        o[4].length
      ).top), O(e, "transform", Q(
        /*index*/
        o[29],
        /*participants*/
        o[4].length
      ).transform);
    },
    m(k, x) {
      ke(k, e, x), v(e, t), v(t, n), i.m(l, n), v(t, s), v(t, r), v(e, a), v(e, p), v(p, g), v(e, h), v(e, u), v(u, d), v(e, y);
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
      8208 && L(
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
      16400 && L(
        p,
        "speaking",
        /*isAvatarActive*/
        k[14](
          /*participant*/
          k[27]
        )
      ), x & /*thinking, participants*/
      80 && L(
        p,
        "thinking",
        /*thinking*/
        k[6].includes(
          /*participant*/
          k[27]
        )
      ), x & /*currentSpeaker, participants*/
      48 && L(
        p,
        "responding",
        /*currentSpeaker*/
        k[5] === /*participant*/
        k[27]
      ), x & /*participants*/
      16 && b !== (b = /*participant*/
      k[27] + "") && oe(d, b), x & /*participants*/
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
      k && I(e);
    }
  };
}
function Ot(o) {
  let e, t, n, i, l = '<div class="consensus-flame svelte-1eo2cb7">🎭</div> <div class="table-label svelte-1eo2cb7">CONSILIUM</div>', s, r, a, p, c = (
    /*show_label*/
    o[3] && /*label*/
    o[2] && Ee(o)
  ), g = Re(
    /*participants*/
    o[4]
  ), h = [];
  for (let u = 0; u < g.length; u += 1)
    h[u] = Ce(Ae(o, g, u));
  return {
    c() {
      e = E("div"), c && c.c(), t = V(), n = E("div"), i = E("div"), i.innerHTML = l, s = V(), r = E("div");
      for (let u = 0; u < h.length; u += 1)
        h[u].c();
      this.h();
    },
    l(u) {
      e = A(u, "DIV", { class: !0, id: !0, style: !0 });
      var b = M(e);
      c && c.l(b), t = j(b), n = A(b, "DIV", { class: !0, id: !0 });
      var d = M(n);
      i = A(d, "DIV", { class: !0, "data-svelte-h": !0 }), qt(i) !== "svelte-fj2hkt" && (i.innerHTML = l), s = j(d), r = A(d, "DIV", { class: !0 });
      var y = M(r);
      for (let k = 0; k < h.length; k += 1)
        h[k].l(y);
      y.forEach(I), d.forEach(I), b.forEach(I), this.h();
    },
    h() {
      T(i, "class", "table-center svelte-1eo2cb7"), T(r, "class", "participants-circle"), T(n, "class", "consilium-container svelte-1eo2cb7"), T(n, "id", "consilium-roundtable"), T(e, "class", a = Se(
        /*containerClasses*/
        o[9]
      ) + " svelte-1eo2cb7"), T(
        e,
        "id",
        /*elem_id*/
        o[0]
      ), T(e, "style", p = /*containerStyle*/
      o[8] + "; " + /*minWidthStyle*/
      o[7]), L(e, "hidden", !/*visible*/
      o[1]);
    },
    m(u, b) {
      ke(u, e, b), c && c.m(e, null), v(e, t), v(e, n), v(n, i), v(n, s), v(n, r);
      for (let d = 0; d < h.length; d += 1)
        h[d] && h[d].m(r, null);
    },
    p(u, [b]) {
      if (/*show_label*/
      u[3] && /*label*/
      u[2] ? c ? c.p(u, b) : (c = Ee(u), c.c(), c.m(e, t)) : c && (c.d(1), c = null), b & /*getPosition, participants, isAvatarActive, thinking, currentSpeaker, getEmoji, isBubbleVisible, renderMarkdown, getLatestMessage*/
      31856) {
        g = Re(
          /*participants*/
          u[4]
        );
        let d;
        for (d = 0; d < g.length; d += 1) {
          const y = Ae(u, g, d);
          h[d] ? h[d].p(y, b) : (h[d] = Ce(y), h[d].c(), h[d].m(r, null));
        }
        for (; d < h.length; d += 1)
          h[d].d(1);
        h.length = g.length;
      }
      b & /*containerClasses*/
      512 && a !== (a = Se(
        /*containerClasses*/
        u[9]
      ) + " svelte-1eo2cb7") && T(e, "class", a), b & /*elem_id*/
      1 && T(
        e,
        "id",
        /*elem_id*/
        u[0]
      ), b & /*containerStyle, minWidthStyle*/
      384 && p !== (p = /*containerStyle*/
      u[8] + "; " + /*minWidthStyle*/
      u[7]) && T(e, "style", p), b & /*containerClasses, visible*/
      514 && L(e, "hidden", !/*visible*/
      u[1]);
    },
    i: Ie,
    o: Ie,
    d(u) {
      u && I(e), c && c.d(), Pt(h, u);
    }
  };
}
function Q(o, e) {
  const n = (360 / e * o - 90) * (Math.PI / 180), i = 260, l = 180, s = Math.cos(n) * i, r = Math.sin(n) * l;
  return {
    left: `calc(50% + ${s}px)`,
    top: `calc(50% + ${r}px)`,
    transform: "translate(-50%, -50%)"
  };
}
function Qt(o, e, t) {
  let n, i, l, { gradio: s } = e, { elem_id: r = "" } = e, { elem_classes: a = [] } = e, { visible: p = !0 } = e, { value: c = "{}" } = e, { label: g = "Consilium Roundtable" } = e, { show_label: h = !0 } = e, { scale: u = null } = e, { min_width: b = void 0 } = e, { loading_status: d } = e, { interactive: y = !0 } = e, k = [], x = [], z = null, S = [], C = [];
  function X() {
    try {
      const f = JSON.parse(c);
      t(4, k = f.participants || []), x = f.messages || [], t(5, z = f.currentSpeaker || null), t(6, S = f.thinking || []), C = f.showBubbles || [], console.log("Clean JSON parsed:", {
        participants: k,
        messages: x,
        currentSpeaker: z,
        thinking: S,
        showBubbles: C
      });
    } catch (f) {
      console.error("Invalid JSON:", c, f);
    }
  }
  function Ve(f) {
    if (!f) return f;
    try {
      return m.setOptions({
        breaks: !0,
        // Convert line breaks to <br>
        gfm: !0,
        // GitHub flavored markdown
        sanitize: !1,
        // Allow HTML (safe since we control input)
        smartypants: !1
        // Don't convert quotes/dashes
      }), f.includes(`
`) ? m.parse(f) : m.parseInline(f);
    } catch (P) {
      return console.error("Markdown parsing error:", P), f;
    }
  }
  const Ne = {
    Claude: "🤖",
    "GPT-4": "🧠",
    Mistral: "🦾",
    Gemini: "💎",
    Search: "🔍",
    OpenAI: "🧠",
    Anthropic: "🤖",
    Google: "💎"
  };
  function He(f) {
    return Ne[f] || "🤖";
  }
  function Fe(f) {
    if (S.includes(f))
      return `${f} is thinking...`;
    if (z === f)
      return `${f} is responding...`;
    const P = x.filter((J) => J.speaker === f);
    return P.length === 0 ? `${f} is ready to discuss...` : P[P.length - 1].text || `${f} responded`;
  }
  function Ue(f) {
    const P = S.includes(f), J = z === f, be = C.includes(f), me = P || J || be;
    return console.log(`${f} bubble visible:`, me, { isThinking: P, isSpeaking: J, shouldShow: be }), me;
  }
  function Ge(f) {
    return S.includes(f) || z === f;
  }
  return o.$$set = (f) => {
    "gradio" in f && t(15, s = f.gradio), "elem_id" in f && t(0, r = f.elem_id), "elem_classes" in f && t(16, a = f.elem_classes), "visible" in f && t(1, p = f.visible), "value" in f && t(17, c = f.value), "label" in f && t(2, g = f.label), "show_label" in f && t(3, h = f.show_label), "scale" in f && t(18, u = f.scale), "min_width" in f && t(19, b = f.min_width), "loading_status" in f && t(20, d = f.loading_status), "interactive" in f && t(21, y = f.interactive);
  }, o.$$.update = () => {
    o.$$.dirty & /*elem_classes*/
    65536 && t(9, n = `wrapper ${a.join(" ")}`), o.$$.dirty & /*scale*/
    262144 && t(8, i = u ? `--scale: ${u}` : ""), o.$$.dirty & /*min_width*/
    524288 && t(7, l = b ? `min-width: ${b}px` : ""), o.$$.dirty & /*interactive*/
    2097152, o.$$.dirty & /*value*/
    131072 && X();
  }, [
    r,
    p,
    g,
    h,
    k,
    z,
    S,
    l,
    i,
    n,
    Ve,
    He,
    Fe,
    Ue,
    Ge,
    s,
    a,
    c,
    u,
    b,
    d,
    y
  ];
}
class Vt extends $t {
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
export {
  Vt as default
};
