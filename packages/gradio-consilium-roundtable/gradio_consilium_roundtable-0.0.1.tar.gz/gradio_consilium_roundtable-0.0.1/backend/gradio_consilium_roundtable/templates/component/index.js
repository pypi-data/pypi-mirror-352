const {
  SvelteComponent: x,
  append_hydration: g,
  attr: _,
  children: C,
  claim_element: S,
  claim_space: j,
  claim_text: P,
  destroy_each: $,
  detach: m,
  element: D,
  ensure_array_like: R,
  get_svelte_dataset: ee,
  init: le,
  insert_hydration: q,
  noop: U,
  null_to_empty: W,
  safe_not_equal: te,
  set_data: B,
  set_style: A,
  space: N,
  text: H,
  toggle_class: M
} = window.__gradio__svelte__internal;
function X(l, e, i) {
  const s = l.slice();
  return s[25] = e[i], s[27] = i, s;
}
function Y(l) {
  let e, i;
  return {
    c() {
      e = D("label"), i = H(
        /*label*/
        l[2]
      ), this.h();
    },
    l(s) {
      e = S(s, "LABEL", { class: !0, for: !0 });
      var u = C(e);
      i = P(
        u,
        /*label*/
        l[2]
      ), u.forEach(m), this.h();
    },
    h() {
      _(e, "class", "block-title svelte-1egwo09"), _(e, "for", "consilium-roundtable");
    },
    m(s, u) {
      q(s, e, u), g(e, i);
    },
    p(s, u) {
      u & /*label*/
      4 && B(
        i,
        /*label*/
        s[2]
      );
    },
    d(s) {
      s && m(e);
    }
  };
}
function z(l) {
  let e, i, s, u = (
    /*getLatestMessage*/
    l[11](
      /*participant*/
      l[25]
    ) + ""
  ), w, I, v, E, h, r = (
    /*getEmoji*/
    l[10](
      /*participant*/
      l[25]
    ) + ""
  ), b, d, n, c = (
    /*participant*/
    l[25] + ""
  ), o, V;
  return {
    c() {
      e = D("div"), i = D("div"), s = D("div"), w = H(u), I = N(), v = D("div"), E = N(), h = D("div"), b = H(r), d = N(), n = D("div"), o = H(c), V = N(), this.h();
    },
    l(a) {
      e = S(a, "DIV", { class: !0, style: !0 });
      var f = C(e);
      i = S(f, "DIV", { class: !0 });
      var k = C(i);
      s = S(k, "DIV", { class: !0 });
      var y = C(s);
      w = P(y, u), y.forEach(m), I = j(k), v = S(k, "DIV", { class: !0 }), C(v).forEach(m), k.forEach(m), E = j(f), h = S(f, "DIV", { class: !0, role: !0, tabindex: !0 });
      var T = C(h);
      b = P(T, r), T.forEach(m), d = j(f), n = S(f, "DIV", { class: !0 });
      var G = C(n);
      o = P(G, c), G.forEach(m), V = j(f), f.forEach(m), this.h();
    },
    h() {
      _(s, "class", "bubble-content svelte-1egwo09"), _(v, "class", "bubble-arrow svelte-1egwo09"), _(i, "class", "speech-bubble svelte-1egwo09"), M(
        i,
        "visible",
        /*isBubbleVisible*/
        l[12](
          /*participant*/
          l[25]
        )
      ), _(h, "class", "avatar svelte-1egwo09"), _(h, "role", "button"), _(h, "tabindex", "0"), M(
        h,
        "speaking",
        /*isAvatarActive*/
        l[13](
          /*participant*/
          l[25]
        )
      ), M(
        h,
        "thinking",
        /*thinking*/
        l[6].includes(
          /*participant*/
          l[25]
        )
      ), M(
        h,
        "responding",
        /*currentSpeaker*/
        l[5] === /*participant*/
        l[25]
      ), _(n, "class", "participant-name svelte-1egwo09"), _(e, "class", "participant-seat svelte-1egwo09"), A(e, "left", O(
        /*index*/
        l[27],
        /*participants*/
        l[4].length
      ).left), A(e, "top", O(
        /*index*/
        l[27],
        /*participants*/
        l[4].length
      ).top), A(e, "transform", O(
        /*index*/
        l[27],
        /*participants*/
        l[4].length
      ).transform);
    },
    m(a, f) {
      q(a, e, f), g(e, i), g(i, s), g(s, w), g(i, I), g(i, v), g(e, E), g(e, h), g(h, b), g(e, d), g(e, n), g(n, o), g(e, V);
    },
    p(a, f) {
      f & /*participants*/
      16 && u !== (u = /*getLatestMessage*/
      a[11](
        /*participant*/
        a[25]
      ) + "") && B(w, u), f & /*isBubbleVisible, participants*/
      4112 && M(
        i,
        "visible",
        /*isBubbleVisible*/
        a[12](
          /*participant*/
          a[25]
        )
      ), f & /*participants*/
      16 && r !== (r = /*getEmoji*/
      a[10](
        /*participant*/
        a[25]
      ) + "") && B(b, r), f & /*isAvatarActive, participants*/
      8208 && M(
        h,
        "speaking",
        /*isAvatarActive*/
        a[13](
          /*participant*/
          a[25]
        )
      ), f & /*thinking, participants*/
      80 && M(
        h,
        "thinking",
        /*thinking*/
        a[6].includes(
          /*participant*/
          a[25]
        )
      ), f & /*currentSpeaker, participants*/
      48 && M(
        h,
        "responding",
        /*currentSpeaker*/
        a[5] === /*participant*/
        a[25]
      ), f & /*participants*/
      16 && c !== (c = /*participant*/
      a[25] + "") && B(o, c), f & /*participants*/
      16 && A(e, "left", O(
        /*index*/
        a[27],
        /*participants*/
        a[4].length
      ).left), f & /*participants*/
      16 && A(e, "top", O(
        /*index*/
        a[27],
        /*participants*/
        a[4].length
      ).top), f & /*participants*/
      16 && A(e, "transform", O(
        /*index*/
        a[27],
        /*participants*/
        a[4].length
      ).transform);
    },
    d(a) {
      a && m(e);
    }
  };
}
function ie(l) {
  let e, i, s, u, w = '<div class="consensus-flame svelte-1egwo09">🎭</div> <div class="table-label svelte-1egwo09">CONSILIUM</div>', I, v, E, h, r = (
    /*show_label*/
    l[3] && /*label*/
    l[2] && Y(l)
  ), b = R(
    /*participants*/
    l[4]
  ), d = [];
  for (let n = 0; n < b.length; n += 1)
    d[n] = z(X(l, b, n));
  return {
    c() {
      e = D("div"), r && r.c(), i = N(), s = D("div"), u = D("div"), u.innerHTML = w, I = N(), v = D("div");
      for (let n = 0; n < d.length; n += 1)
        d[n].c();
      this.h();
    },
    l(n) {
      e = S(n, "DIV", { class: !0, id: !0, style: !0 });
      var c = C(e);
      r && r.l(c), i = j(c), s = S(c, "DIV", { class: !0, id: !0 });
      var o = C(s);
      u = S(o, "DIV", { class: !0, "data-svelte-h": !0 }), ee(u) !== "svelte-fj2hkt" && (u.innerHTML = w), I = j(o), v = S(o, "DIV", { class: !0 });
      var V = C(v);
      for (let a = 0; a < d.length; a += 1)
        d[a].l(V);
      V.forEach(m), o.forEach(m), c.forEach(m), this.h();
    },
    h() {
      _(u, "class", "table-center svelte-1egwo09"), _(v, "class", "participants-circle"), _(s, "class", "consilium-container svelte-1egwo09"), _(s, "id", "consilium-roundtable"), _(e, "class", E = W(
        /*containerClasses*/
        l[9]
      ) + " svelte-1egwo09"), _(
        e,
        "id",
        /*elem_id*/
        l[0]
      ), _(e, "style", h = /*containerStyle*/
      l[8] + "; " + /*minWidthStyle*/
      l[7]), M(e, "hidden", !/*visible*/
      l[1]);
    },
    m(n, c) {
      q(n, e, c), r && r.m(e, null), g(e, i), g(e, s), g(s, u), g(s, I), g(s, v);
      for (let o = 0; o < d.length; o += 1)
        d[o] && d[o].m(v, null);
    },
    p(n, [c]) {
      if (/*show_label*/
      n[3] && /*label*/
      n[2] ? r ? r.p(n, c) : (r = Y(n), r.c(), r.m(e, i)) : r && (r.d(1), r = null), c & /*getPosition, participants, isAvatarActive, thinking, currentSpeaker, getEmoji, isBubbleVisible, getLatestMessage*/
      15472) {
        b = R(
          /*participants*/
          n[4]
        );
        let o;
        for (o = 0; o < b.length; o += 1) {
          const V = X(n, b, o);
          d[o] ? d[o].p(V, c) : (d[o] = z(V), d[o].c(), d[o].m(v, null));
        }
        for (; o < d.length; o += 1)
          d[o].d(1);
        d.length = b.length;
      }
      c & /*containerClasses*/
      512 && E !== (E = W(
        /*containerClasses*/
        n[9]
      ) + " svelte-1egwo09") && _(e, "class", E), c & /*elem_id*/
      1 && _(
        e,
        "id",
        /*elem_id*/
        n[0]
      ), c & /*containerStyle, minWidthStyle*/
      384 && h !== (h = /*containerStyle*/
      n[8] + "; " + /*minWidthStyle*/
      n[7]) && _(e, "style", h), c & /*containerClasses, visible*/
      514 && M(e, "hidden", !/*visible*/
      n[1]);
    },
    i: U,
    o: U,
    d(n) {
      n && m(e), r && r.d(), $(d, n);
    }
  };
}
function O(l, e) {
  const s = (360 / e * l - 90) * (Math.PI / 180), u = 260, w = 180, I = Math.cos(s) * u, v = Math.sin(s) * w;
  return {
    left: `calc(50% + ${I}px)`,
    top: `calc(50% + ${v}px)`,
    transform: "translate(-50%, -50%)"
  };
}
function ne(l, e, i) {
  let s, u, w, { gradio: I } = e, { elem_id: v = "" } = e, { elem_classes: E = [] } = e, { visible: h = !0 } = e, { value: r = "{}" } = e, { label: b = "Consilium Roundtable" } = e, { show_label: d = !0 } = e, { scale: n = null } = e, { min_width: c = void 0 } = e, { loading_status: o } = e, { interactive: V = !0 } = e, a = [], f = [], k = null, y = [];
  function T() {
    try {
      const t = JSON.parse(r);
      i(4, a = t.participants || []), f = t.messages || [], i(5, k = t.currentSpeaker || null), i(6, y = t.thinking || []), console.log("Clean JSON parsed:", {
        participants: a,
        messages: f,
        currentSpeaker: k,
        thinking: y
      });
    } catch (t) {
      console.error("Invalid JSON:", r, t);
    }
  }
  const G = {
    Claude: "🤖",
    "GPT-4": "🧠",
    Mistral: "🦾",
    Gemini: "💎",
    Search: "🔍",
    OpenAI: "🧠",
    Anthropic: "🤖",
    Google: "💎"
  };
  function K(t) {
    return G[t] || "🤖";
  }
  function Q(t) {
    if (y.includes(t))
      return `${t} is thinking...`;
    if (k === t)
      return `${t} is responding...`;
    const L = f.filter((J) => J.speaker === t);
    return L.length === 0 ? `${t} is ready to discuss...` : L[L.length - 1].text || `${t} responded`;
  }
  function Z(t) {
    const L = y.includes(t), J = k === t, F = L || J;
    return console.log(`${t} bubble visible:`, F, { isThinking: L, isSpeaking: J }), F;
  }
  function p(t) {
    return y.includes(t) || k === t;
  }
  return l.$$set = (t) => {
    "gradio" in t && i(14, I = t.gradio), "elem_id" in t && i(0, v = t.elem_id), "elem_classes" in t && i(15, E = t.elem_classes), "visible" in t && i(1, h = t.visible), "value" in t && i(16, r = t.value), "label" in t && i(2, b = t.label), "show_label" in t && i(3, d = t.show_label), "scale" in t && i(17, n = t.scale), "min_width" in t && i(18, c = t.min_width), "loading_status" in t && i(19, o = t.loading_status), "interactive" in t && i(20, V = t.interactive);
  }, l.$$.update = () => {
    l.$$.dirty & /*elem_classes*/
    32768 && i(9, s = `wrapper ${E.join(" ")}`), l.$$.dirty & /*scale*/
    131072 && i(8, u = n ? `--scale: ${n}` : ""), l.$$.dirty & /*min_width*/
    262144 && i(7, w = c ? `min-width: ${c}px` : ""), l.$$.dirty & /*interactive*/
    1048576, l.$$.dirty & /*value*/
    65536 && T();
  }, [
    v,
    h,
    b,
    d,
    a,
    k,
    y,
    w,
    u,
    s,
    K,
    Q,
    Z,
    p,
    I,
    E,
    r,
    n,
    c,
    o,
    V
  ];
}
class se extends x {
  constructor(e) {
    super(), le(this, e, ne, ie, te, {
      gradio: 14,
      elem_id: 0,
      elem_classes: 15,
      visible: 1,
      value: 16,
      label: 2,
      show_label: 3,
      scale: 17,
      min_width: 18,
      loading_status: 19,
      interactive: 20
    });
  }
}
export {
  se as default
};
