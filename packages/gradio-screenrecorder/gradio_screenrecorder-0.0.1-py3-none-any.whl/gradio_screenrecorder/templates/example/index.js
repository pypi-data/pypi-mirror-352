const {
  SvelteComponent: U,
  append_hydration: d,
  attr: u,
  children: p,
  claim_element: _,
  claim_space: O,
  claim_text: R,
  detach: c,
  element: f,
  get_svelte_dataset: $,
  init: j,
  insert_hydration: y,
  noop: V,
  safe_not_equal: z,
  set_data: x,
  set_style: I,
  space: A,
  src_url_equal: M,
  text: N
} = window.__gradio__svelte__internal;
function B(r) {
  let e, t = "📹 Screen Recording";
  return {
    c() {
      e = f("div"), e.textContent = t, this.h();
    },
    l(a) {
      e = _(a, "DIV", { class: !0, "data-svelte-h": !0 }), $(e) !== "svelte-1bxe4bf" && (e.textContent = t), this.h();
    },
    h() {
      u(e, "class", "placeholder svelte-118e1ql");
    },
    m(a, s) {
      y(a, e, s);
    },
    p: V,
    d(a) {
      a && c(e);
    }
  };
}
function F(r) {
  var C, S;
  let e, t, a, s, l, n, m = (
    /*value*/
    (r[0].duration ? P(
      /*value*/
      r[0].duration
    ) : "Recording") + ""
  ), E, D, h, g = (
    /*value*/
    (((S = (C = r[0].video.orig_name) == null ? void 0 : C.split(".").pop()) == null ? void 0 : S.toUpperCase()) || "VIDEO") + ""
  ), b;
  return {
    c() {
      e = f("div"), t = f("video"), s = A(), l = f("div"), n = f("span"), E = N(m), D = A(), h = f("span"), b = N(g), this.h();
    },
    l(i) {
      e = _(i, "DIV", { class: !0 });
      var o = p(e);
      t = _(o, "VIDEO", { src: !0, style: !0 });
      var q = p(t);
      q.forEach(c), s = O(o), l = _(o, "DIV", { class: !0 });
      var v = p(l);
      n = _(v, "SPAN", { class: !0 });
      var k = p(n);
      E = R(k, m), k.forEach(c), D = O(v), h = _(v, "SPAN", { class: !0 });
      var w = p(h);
      b = R(w, g), w.forEach(c), v.forEach(c), o.forEach(c), this.h();
    },
    h() {
      M(t.src, a = /*value*/
      r[0].video.path) || u(t, "src", a), t.controls = !1, t.muted = !0, I(t, "width", "100%"), I(t, "height", "60px"), I(t, "object-fit", "cover"), u(n, "class", "duration svelte-118e1ql"), u(h, "class", "format svelte-118e1ql"), u(l, "class", "overlay svelte-118e1ql"), u(e, "class", "video-thumbnail svelte-118e1ql");
    },
    m(i, o) {
      y(i, e, o), d(e, t), d(e, s), d(e, l), d(l, n), d(n, E), d(l, D), d(l, h), d(h, b);
    },
    p(i, o) {
      var q, v;
      o & /*value*/
      1 && !M(t.src, a = /*value*/
      i[0].video.path) && u(t, "src", a), o & /*value*/
      1 && m !== (m = /*value*/
      (i[0].duration ? P(
        /*value*/
        i[0].duration
      ) : "Recording") + "") && x(E, m), o & /*value*/
      1 && g !== (g = /*value*/
      (((v = (q = i[0].video.orig_name) == null ? void 0 : q.split(".").pop()) == null ? void 0 : v.toUpperCase()) || "VIDEO") + "") && x(b, g);
    },
    d(i) {
      i && c(e);
    }
  };
}
function G(r) {
  let e;
  function t(l, n) {
    return (
      /*value*/
      l[0] && /*value*/
      l[0].video ? F : B
    );
  }
  let a = t(r), s = a(r);
  return {
    c() {
      e = f("div"), s.c(), this.h();
    },
    l(l) {
      e = _(l, "DIV", { class: !0 });
      var n = p(e);
      s.l(n), n.forEach(c), this.h();
    },
    h() {
      u(e, "class", "example-container svelte-118e1ql");
    },
    m(l, n) {
      y(l, e, n), s.m(e, null);
    },
    p(l, [n]) {
      a === (a = t(l)) && s ? s.p(l, n) : (s.d(1), s = a(l), s && (s.c(), s.m(e, null)));
    },
    i: V,
    o: V,
    d(l) {
      l && c(e), s.d();
    }
  };
}
function P(r) {
  const e = Math.floor(r / 60), t = Math.floor(r % 60);
  return `${e}:${t.toString().padStart(2, "0")}`;
}
function H(r, e, t) {
  let { value: a } = e;
  return r.$$set = (s) => {
    "value" in s && t(0, a = s.value);
  }, [a];
}
class J extends U {
  constructor(e) {
    super(), j(this, e, H, G, z, { value: 0 });
  }
}
export {
  J as default
};
