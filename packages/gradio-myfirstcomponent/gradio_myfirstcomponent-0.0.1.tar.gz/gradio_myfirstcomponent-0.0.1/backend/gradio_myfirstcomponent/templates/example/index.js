const {
  SvelteComponent: h,
  add_iframe_resize_listener: g,
  add_render_callback: v,
  append_hydration: y,
  attr: b,
  binding_callbacks: m,
  children: w,
  claim_element: z,
  claim_text: k,
  detach: c,
  element: p,
  init: E,
  insert_hydration: S,
  noop: o,
  safe_not_equal: q,
  set_data: C,
  text: D,
  toggle_class: _
} = window.__gradio__svelte__internal, { onMount: I } = window.__gradio__svelte__internal;
function M(t) {
  let e, i = (
    /*value*/
    (t[0] ? (
      /*value*/
      t[0]
    ) : "") + ""
  ), s, d;
  return {
    c() {
      e = p("div"), s = D(i), this.h();
    },
    l(l) {
      e = z(l, "DIV", { class: !0 });
      var n = w(e);
      s = k(n, i), n.forEach(c), this.h();
    },
    h() {
      b(e, "class", "svelte-84cxb8"), v(() => (
        /*div_elementresize_handler*/
        t[5].call(e)
      )), _(
        e,
        "table",
        /*type*/
        t[1] === "table"
      ), _(
        e,
        "gallery",
        /*type*/
        t[1] === "gallery"
      ), _(
        e,
        "selected",
        /*selected*/
        t[2]
      );
    },
    m(l, n) {
      S(l, e, n), y(e, s), d = g(
        e,
        /*div_elementresize_handler*/
        t[5].bind(e)
      ), t[6](e);
    },
    p(l, [n]) {
      n & /*value*/
      1 && i !== (i = /*value*/
      (l[0] ? (
        /*value*/
        l[0]
      ) : "") + "") && C(s, i), n & /*type*/
      2 && _(
        e,
        "table",
        /*type*/
        l[1] === "table"
      ), n & /*type*/
      2 && _(
        e,
        "gallery",
        /*type*/
        l[1] === "gallery"
      ), n & /*selected*/
      4 && _(
        e,
        "selected",
        /*selected*/
        l[2]
      );
    },
    i: o,
    o,
    d(l) {
      l && c(e), d(), t[6](null);
    }
  };
}
function P(t, e) {
  t.style.setProperty("--local-text-width", `${e && e < 150 ? e : 200}px`), t.style.whiteSpace = "unset";
}
function V(t, e, i) {
  let { value: s } = e, { type: d } = e, { selected: l = !1 } = e, n, r;
  I(() => {
    P(r, n);
  });
  function u() {
    n = this.clientWidth, i(3, n);
  }
  function f(a) {
    m[a ? "unshift" : "push"](() => {
      r = a, i(4, r);
    });
  }
  return t.$$set = (a) => {
    "value" in a && i(0, s = a.value), "type" in a && i(1, d = a.type), "selected" in a && i(2, l = a.selected);
  }, [s, d, l, n, r, u, f];
}
class W extends h {
  constructor(e) {
    super(), E(this, e, V, M, q, { value: 0, type: 1, selected: 2 });
  }
}
export {
  W as default
};
