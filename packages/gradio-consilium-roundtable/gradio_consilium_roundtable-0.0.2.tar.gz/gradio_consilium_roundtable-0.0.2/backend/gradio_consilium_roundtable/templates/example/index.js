const {
  SvelteComponent: x,
  append_hydration: g,
  attr: h,
  children: D,
  claim_element: V,
  claim_space: N,
  claim_text: P,
  destroy_each: $,
  detach: b,
  element: C,
  ensure_array_like: W,
  get_svelte_dataset: ee,
  init: te,
  insert_hydration: H,
  noop: p,
  null_to_empty: F,
  safe_not_equal: le,
  set_data: q,
  set_style: O,
  space: T,
  text: B,
  toggle_class: M
} = window.__gradio__svelte__internal;
function U(t, e, l) {
  const i = t.slice();
  return i[25] = e[l], i[27] = l, i;
}
function X(t) {
  let e, l;
  return {
    c() {
      e = C("label"), l = B(
        /*label*/
        t[2]
      ), this.h();
    },
    l(i) {
      e = V(i, "LABEL", { class: !0, for: !0 });
      var r = D(e);
      l = P(
        r,
        /*label*/
        t[2]
      ), r.forEach(b), this.h();
    },
    h() {
      h(e, "class", "block-title svelte-1egwo09"), h(e, "for", "consilium-roundtable");
    },
    m(i, r) {
      H(i, e, r), g(e, l);
    },
    p(i, r) {
      r & /*label*/
      4 && q(
        l,
        /*label*/
        i[2]
      );
    },
    d(i) {
      i && b(e);
    }
  };
}
function Y(t) {
  let e, l, i, r = (
    /*getLatestMessage*/
    t[11](
      /*participant*/
      t[25]
    ) + ""
  ), w, I, v, E, _, u = (
    /*getEmoji*/
    t[10](
      /*participant*/
      t[25]
    ) + ""
  ), m, d, s, c = (
    /*participant*/
    t[25] + ""
  ), o, S;
  return {
    c() {
      e = C("div"), l = C("div"), i = C("div"), w = B(r), I = T(), v = C("div"), E = T(), _ = C("div"), m = B(u), d = T(), s = C("div"), o = B(c), S = T(), this.h();
    },
    l(a) {
      e = V(a, "DIV", { class: !0, style: !0 });
      var f = D(e);
      l = V(f, "DIV", { class: !0 });
      var k = D(l);
      i = V(k, "DIV", { class: !0 });
      var y = D(i);
      w = P(y, r), y.forEach(b), I = N(k), v = V(k, "DIV", { class: !0 }), D(v).forEach(b), k.forEach(b), E = N(f), _ = V(f, "DIV", { class: !0, role: !0, tabindex: !0 });
      var j = D(_);
      m = P(j, u), j.forEach(b), d = N(f), s = V(f, "DIV", { class: !0 });
      var G = D(s);
      o = P(G, c), G.forEach(b), S = N(f), f.forEach(b), this.h();
    },
    h() {
      h(i, "class", "bubble-content svelte-1egwo09"), h(v, "class", "bubble-arrow svelte-1egwo09"), h(l, "class", "speech-bubble svelte-1egwo09"), M(
        l,
        "visible",
        /*isBubbleVisible*/
        t[12](
          /*participant*/
          t[25]
        )
      ), h(_, "class", "avatar svelte-1egwo09"), h(_, "role", "button"), h(_, "tabindex", "0"), M(
        _,
        "speaking",
        /*isAvatarActive*/
        t[13](
          /*participant*/
          t[25]
        )
      ), M(
        _,
        "thinking",
        /*thinking*/
        t[6].includes(
          /*participant*/
          t[25]
        )
      ), M(
        _,
        "responding",
        /*currentSpeaker*/
        t[5] === /*participant*/
        t[25]
      ), h(s, "class", "participant-name svelte-1egwo09"), h(e, "class", "participant-seat svelte-1egwo09"), O(e, "left", A(
        /*index*/
        t[27],
        /*participants*/
        t[4].length
      ).left), O(e, "top", A(
        /*index*/
        t[27],
        /*participants*/
        t[4].length
      ).top), O(e, "transform", A(
        /*index*/
        t[27],
        /*participants*/
        t[4].length
      ).transform);
    },
    m(a, f) {
      H(a, e, f), g(e, l), g(l, i), g(i, w), g(l, I), g(l, v), g(e, E), g(e, _), g(_, m), g(e, d), g(e, s), g(s, o), g(e, S);
    },
    p(a, f) {
      f & /*participants*/
      16 && r !== (r = /*getLatestMessage*/
      a[11](
        /*participant*/
        a[25]
      ) + "") && q(w, r), f & /*isBubbleVisible, participants*/
      4112 && M(
        l,
        "visible",
        /*isBubbleVisible*/
        a[12](
          /*participant*/
          a[25]
        )
      ), f & /*participants*/
      16 && u !== (u = /*getEmoji*/
      a[10](
        /*participant*/
        a[25]
      ) + "") && q(m, u), f & /*isAvatarActive, participants*/
      8208 && M(
        _,
        "speaking",
        /*isAvatarActive*/
        a[13](
          /*participant*/
          a[25]
        )
      ), f & /*thinking, participants*/
      80 && M(
        _,
        "thinking",
        /*thinking*/
        a[6].includes(
          /*participant*/
          a[25]
        )
      ), f & /*currentSpeaker, participants*/
      48 && M(
        _,
        "responding",
        /*currentSpeaker*/
        a[5] === /*participant*/
        a[25]
      ), f & /*participants*/
      16 && c !== (c = /*participant*/
      a[25] + "") && q(o, c), f & /*participants*/
      16 && O(e, "left", A(
        /*index*/
        a[27],
        /*participants*/
        a[4].length
      ).left), f & /*participants*/
      16 && O(e, "top", A(
        /*index*/
        a[27],
        /*participants*/
        a[4].length
      ).top), f & /*participants*/
      16 && O(e, "transform", A(
        /*index*/
        a[27],
        /*participants*/
        a[4].length
      ).transform);
    },
    d(a) {
      a && b(e);
    }
  };
}
function ne(t) {
  let e, l, i, r, w = '<div class="consensus-flame svelte-1egwo09">🎭</div> <div class="table-label svelte-1egwo09">CONSILIUM</div>', I, v, E, _, u = (
    /*show_label*/
    t[3] && /*label*/
    t[2] && X(t)
  ), m = W(
    /*participants*/
    t[4]
  ), d = [];
  for (let s = 0; s < m.length; s += 1)
    d[s] = Y(U(t, m, s));
  return {
    c() {
      e = C("div"), u && u.c(), l = T(), i = C("div"), r = C("div"), r.innerHTML = w, I = T(), v = C("div");
      for (let s = 0; s < d.length; s += 1)
        d[s].c();
      this.h();
    },
    l(s) {
      e = V(s, "DIV", { class: !0, id: !0, style: !0 });
      var c = D(e);
      u && u.l(c), l = N(c), i = V(c, "DIV", { class: !0, id: !0 });
      var o = D(i);
      r = V(o, "DIV", { class: !0, "data-svelte-h": !0 }), ee(r) !== "svelte-fj2hkt" && (r.innerHTML = w), I = N(o), v = V(o, "DIV", { class: !0 });
      var S = D(v);
      for (let a = 0; a < d.length; a += 1)
        d[a].l(S);
      S.forEach(b), o.forEach(b), c.forEach(b), this.h();
    },
    h() {
      h(r, "class", "table-center svelte-1egwo09"), h(v, "class", "participants-circle"), h(i, "class", "consilium-container svelte-1egwo09"), h(i, "id", "consilium-roundtable"), h(e, "class", E = F(
        /*containerClasses*/
        t[9]
      ) + " svelte-1egwo09"), h(
        e,
        "id",
        /*elem_id*/
        t[0]
      ), h(e, "style", _ = /*containerStyle*/
      t[8] + "; " + /*minWidthStyle*/
      t[7]), M(e, "hidden", !/*visible*/
      t[1]);
    },
    m(s, c) {
      H(s, e, c), u && u.m(e, null), g(e, l), g(e, i), g(i, r), g(i, I), g(i, v);
      for (let o = 0; o < d.length; o += 1)
        d[o] && d[o].m(v, null);
    },
    p(s, [c]) {
      if (/*show_label*/
      s[3] && /*label*/
      s[2] ? u ? u.p(s, c) : (u = X(s), u.c(), u.m(e, l)) : u && (u.d(1), u = null), c & /*getPosition, participants, isAvatarActive, thinking, currentSpeaker, getEmoji, isBubbleVisible, getLatestMessage*/
      15472) {
        m = W(
          /*participants*/
          s[4]
        );
        let o;
        for (o = 0; o < m.length; o += 1) {
          const S = U(s, m, o);
          d[o] ? d[o].p(S, c) : (d[o] = Y(S), d[o].c(), d[o].m(v, null));
        }
        for (; o < d.length; o += 1)
          d[o].d(1);
        d.length = m.length;
      }
      c & /*containerClasses*/
      512 && E !== (E = F(
        /*containerClasses*/
        s[9]
      ) + " svelte-1egwo09") && h(e, "class", E), c & /*elem_id*/
      1 && h(
        e,
        "id",
        /*elem_id*/
        s[0]
      ), c & /*containerStyle, minWidthStyle*/
      384 && _ !== (_ = /*containerStyle*/
      s[8] + "; " + /*minWidthStyle*/
      s[7]) && h(e, "style", _), c & /*containerClasses, visible*/
      514 && M(e, "hidden", !/*visible*/
      s[1]);
    },
    i: p,
    o: p,
    d(s) {
      s && b(e), u && u.d(), $(d, s);
    }
  };
}
function A(t, e) {
  const i = (360 / e * t - 90) * (Math.PI / 180), r = 260, w = 180, I = Math.cos(i) * r, v = Math.sin(i) * w;
  return {
    left: `calc(50% + ${I}px)`,
    top: `calc(50% + ${v}px)`,
    transform: "translate(-50%, -50%)"
  };
}
function ie(t, e, l) {
  let i, r, w, { gradio: I } = e, { elem_id: v = "" } = e, { elem_classes: E = [] } = e, { visible: _ = !0 } = e, { value: u = "{}" } = e, { label: m = "Consilium Roundtable" } = e, { show_label: d = !0 } = e, { scale: s = null } = e, { min_width: c = void 0 } = e, { loading_status: o } = e, { interactive: S = !0 } = e, a = [], f = [], k = null, y = [];
  function j() {
    try {
      const n = JSON.parse(u);
      l(4, a = n.participants || []), f = n.messages || [], l(5, k = n.currentSpeaker || null), l(6, y = n.thinking || []), console.log("Clean JSON parsed:", {
        participants: a,
        messages: f,
        currentSpeaker: k,
        thinking: y
      });
    } catch (n) {
      console.error("Invalid JSON:", u, n);
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
  function z(n) {
    return G[n] || "🤖";
  }
  function K(n) {
    if (y.includes(n))
      return `${n} is thinking...`;
    if (k === n)
      return `${n} is responding...`;
    const L = f.filter((J) => J.speaker === n);
    return L.length === 0 ? `${n} is ready to discuss...` : L[L.length - 1].text || `${n} responded`;
  }
  function Q(n) {
    const L = y.includes(n), J = k === n, R = L || J;
    return console.log(`${n} bubble visible:`, R, { isThinking: L, isSpeaking: J }), R;
  }
  function Z(n) {
    return y.includes(n) || k === n;
  }
  return t.$$set = (n) => {
    "gradio" in n && l(14, I = n.gradio), "elem_id" in n && l(0, v = n.elem_id), "elem_classes" in n && l(15, E = n.elem_classes), "visible" in n && l(1, _ = n.visible), "value" in n && l(16, u = n.value), "label" in n && l(2, m = n.label), "show_label" in n && l(3, d = n.show_label), "scale" in n && l(17, s = n.scale), "min_width" in n && l(18, c = n.min_width), "loading_status" in n && l(19, o = n.loading_status), "interactive" in n && l(20, S = n.interactive);
  }, t.$$.update = () => {
    t.$$.dirty & /*elem_classes*/
    32768 && l(9, i = `wrapper ${E.join(" ")}`), t.$$.dirty & /*scale*/
    131072 && l(8, r = s ? `--scale: ${s}` : ""), t.$$.dirty & /*min_width*/
    262144 && l(7, w = c ? `min-width: ${c}px` : ""), t.$$.dirty & /*interactive*/
    1048576, t.$$.dirty & /*value*/
    65536 && j();
  }, [
    v,
    _,
    m,
    d,
    a,
    k,
    y,
    w,
    r,
    i,
    z,
    K,
    Q,
    Z,
    I,
    E,
    u,
    s,
    c,
    o,
    S
  ];
}
class se extends x {
  constructor(e) {
    super(), te(this, e, ie, ne, le, {
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
const {
  SvelteComponent: ae,
  claim_component: oe,
  create_component: re,
  destroy_component: ue,
  init: ce,
  mount_component: de,
  noop: fe,
  safe_not_equal: _e,
  transition_in: he,
  transition_out: ve
} = window.__gradio__svelte__internal, { onMount: be } = window.__gradio__svelte__internal;
function ge(t) {
  let e, l;
  return e = new se({
    props: {
      value: (
        /*value*/
        t[0]
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
      re(e.$$.fragment);
    },
    l(i) {
      oe(e.$$.fragment, i);
    },
    m(i, r) {
      de(e, i, r), l = !0;
    },
    p: fe,
    i(i) {
      l || (he(e.$$.fragment, i), l = !0);
    },
    o(i) {
      ve(e.$$.fragment, i), l = !1;
    },
    d(i) {
      ue(e, i);
    }
  };
}
function me(t) {
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
class we extends ae {
  constructor(e) {
    super(), ce(this, e, me, ge, _e, {});
  }
}
export {
  we as default
};
