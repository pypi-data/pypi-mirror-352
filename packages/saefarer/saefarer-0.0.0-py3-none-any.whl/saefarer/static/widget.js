var $i = Object.defineProperty;
var oa = (e) => {
  throw TypeError(e);
};
var el = (e, t, n) => t in e ? $i(e, t, { enumerable: !0, configurable: !0, writable: !0, value: n }) : e[t] = n;
var sa = (e, t, n) => el(e, typeof t != "symbol" ? t + "" : t, n), dr = (e, t, n) => t.has(e) || oa("Cannot " + n);
var ie = (e, t, n) => (dr(e, t, "read from private field"), n ? n.call(e) : t.get(e)), qe = (e, t, n) => t.has(e) ? oa("Cannot add the same private member more than once") : t instanceof WeakSet ? t.add(e) : t.set(e, n), Be = (e, t, n, r) => (dr(e, t, "write to private field"), r ? r.call(e, n) : t.set(e, n), n), ua = (e, t, n) => (dr(e, t, "access private method"), n);
const tl = "5";
var $a;
typeof window < "u" && (($a = window.__svelte ?? (window.__svelte = {})).v ?? ($a.v = /* @__PURE__ */ new Set())).add(tl);
const Rr = 1, Ir = 2, ei = 4, nl = 8, rl = 16, al = 1, il = 4, ll = 8, fl = 16, ti = 1, ol = 2, Pe = Symbol(), sl = "http://www.w3.org/1999/xhtml", ca = !1;
var Zn = Array.isArray, ul = Array.prototype.indexOf, Dr = Array.from, cl = Object.defineProperty, mt = Object.getOwnPropertyDescriptor, dl = Object.getOwnPropertyDescriptors, vl = Object.prototype, gl = Array.prototype, ni = Object.getPrototypeOf, da = Object.isExtensible;
function $t(e) {
  return typeof e == "function";
}
const hl = () => {
};
function bl(e) {
  for (var t = 0; t < e.length; t++)
    e[t]();
}
const Qe = 2, ri = 4, Qn = 8, Or = 16, vt = 32, Xt = 64, Ln = 128, We = 256, Nn = 512, De = 1024, at = 2048, Et = 4096, ct = 8192, Jn = 16384, _l = 32768, $n = 65536, ml = 1 << 19, ai = 1 << 20, wr = 1 << 21, xt = Symbol("$state"), ii = Symbol("legacy props"), xl = Symbol("");
function li(e) {
  return e === this.v;
}
function pl(e, t) {
  return e != e ? t == t : e !== t || e !== null && typeof e == "object" || typeof e == "function";
}
function Br(e) {
  return !pl(e, this.v);
}
function wl(e) {
  throw new Error("https://svelte.dev/e/effect_in_teardown");
}
function kl() {
  throw new Error("https://svelte.dev/e/effect_in_unowned_derived");
}
function yl(e) {
  throw new Error("https://svelte.dev/e/effect_orphan");
}
function Ml() {
  throw new Error("https://svelte.dev/e/effect_update_depth_exceeded");
}
function Al(e) {
  throw new Error("https://svelte.dev/e/props_invalid_value");
}
function Tl() {
  throw new Error("https://svelte.dev/e/state_descriptors_fixed");
}
function ql() {
  throw new Error("https://svelte.dev/e/state_prototype_fixed");
}
function Sl() {
  throw new Error("https://svelte.dev/e/state_unsafe_mutation");
}
let El = !1, je = null;
function va(e) {
  je = e;
}
function pe(e, t = !1, n) {
  var r = je = {
    p: je,
    c: null,
    d: !1,
    e: null,
    m: !1,
    s: e,
    x: null,
    l: null
  };
  bi(() => {
    r.d = !0;
  });
}
function we(e) {
  const t = je;
  if (t !== null) {
    const f = t.e;
    if (f !== null) {
      var n = he, r = ge;
      t.e = null;
      try {
        for (var a = 0; a < f.length; a++) {
          var i = f[a];
          pt(i.effect), it(i.reaction), Ut(i.fn);
        }
      } finally {
        pt(n), it(r);
      }
    }
    je = t.p, t.m = !0;
  }
  return (
    /** @type {T} */
    {}
  );
}
function fi() {
  return !0;
}
function et(e) {
  if (typeof e != "object" || e === null || xt in e)
    return e;
  const t = ni(e);
  if (t !== vl && t !== gl)
    return e;
  var n = /* @__PURE__ */ new Map(), r = Zn(e), a = /* @__PURE__ */ ee(0), i = ge, f = (o) => {
    var u = ge;
    it(i);
    var s = o();
    return it(u), s;
  };
  return r && n.set("length", /* @__PURE__ */ ee(
    /** @type {any[]} */
    e.length
  )), new Proxy(
    /** @type {any} */
    e,
    {
      defineProperty(o, u, s) {
        (!("value" in s) || s.configurable === !1 || s.enumerable === !1 || s.writable === !1) && Tl();
        var v = n.get(u);
        return v === void 0 ? (v = f(() => /* @__PURE__ */ ee(s.value)), n.set(u, v)) : V(
          v,
          f(() => et(s.value))
        ), !0;
      },
      deleteProperty(o, u) {
        var s = n.get(u);
        if (s === void 0)
          u in o && (n.set(
            u,
            f(() => /* @__PURE__ */ ee(Pe))
          ), vr(a));
        else {
          if (r && typeof u == "string") {
            var v = (
              /** @type {Source<number>} */
              n.get("length")
            ), c = Number(u);
            Number.isInteger(c) && c < v.v && V(v, c);
          }
          V(s, Pe), vr(a);
        }
        return !0;
      },
      get(o, u, s) {
        var g;
        if (u === xt)
          return e;
        var v = n.get(u), c = u in o;
        if (v === void 0 && (!c || (g = mt(o, u)) != null && g.writable) && (v = f(() => /* @__PURE__ */ ee(et(c ? o[u] : Pe))), n.set(u, v)), v !== void 0) {
          var d = l(v);
          return d === Pe ? void 0 : d;
        }
        return Reflect.get(o, u, s);
      },
      getOwnPropertyDescriptor(o, u) {
        var s = Reflect.getOwnPropertyDescriptor(o, u);
        if (s && "value" in s) {
          var v = n.get(u);
          v && (s.value = l(v));
        } else if (s === void 0) {
          var c = n.get(u), d = c == null ? void 0 : c.v;
          if (c !== void 0 && d !== Pe)
            return {
              enumerable: !0,
              configurable: !0,
              value: d,
              writable: !0
            };
        }
        return s;
      },
      has(o, u) {
        var d;
        if (u === xt)
          return !0;
        var s = n.get(u), v = s !== void 0 && s.v !== Pe || Reflect.has(o, u);
        if (s !== void 0 || he !== null && (!v || (d = mt(o, u)) != null && d.writable)) {
          s === void 0 && (s = f(() => /* @__PURE__ */ ee(v ? et(o[u]) : Pe)), n.set(u, s));
          var c = l(s);
          if (c === Pe)
            return !1;
        }
        return v;
      },
      set(o, u, s, v) {
        var w;
        var c = n.get(u), d = u in o;
        if (r && u === "length")
          for (var g = s; g < /** @type {Source<number>} */
          c.v; g += 1) {
            var h = n.get(g + "");
            h !== void 0 ? V(h, Pe) : g in o && (h = f(() => /* @__PURE__ */ ee(Pe)), n.set(g + "", h));
          }
        c === void 0 ? (!d || (w = mt(o, u)) != null && w.writable) && (c = f(() => /* @__PURE__ */ ee(void 0)), V(
          c,
          f(() => et(s))
        ), n.set(u, c)) : (d = c.v !== Pe, V(
          c,
          f(() => et(s))
        ));
        var b = Reflect.getOwnPropertyDescriptor(o, u);
        if (b != null && b.set && b.set.call(v, s), !d) {
          if (r && typeof u == "string") {
            var m = (
              /** @type {Source<number>} */
              n.get("length")
            ), p = Number(u);
            Number.isInteger(p) && p >= m.v && V(m, p + 1);
          }
          vr(a);
        }
        return !0;
      },
      ownKeys(o) {
        l(a);
        var u = Reflect.ownKeys(o).filter((c) => {
          var d = n.get(c);
          return d === void 0 || d.v !== Pe;
        });
        for (var [s, v] of n)
          v.v !== Pe && !(s in o) && u.push(s);
        return u;
      },
      setPrototypeOf() {
        ql();
      }
    }
  );
}
function vr(e, t = 1) {
  V(e, e.v + t);
}
function ga(e) {
  try {
    if (e !== null && typeof e == "object" && xt in e)
      return e[xt];
  } catch {
  }
  return e;
}
function Ll(e, t) {
  return Object.is(ga(e), ga(t));
}
// @__NO_SIDE_EFFECTS__
function er(e) {
  var t = Qe | at, n = ge !== null && (ge.f & Qe) !== 0 ? (
    /** @type {Derived} */
    ge
  ) : null;
  return he === null || n !== null && (n.f & We) !== 0 ? t |= We : he.f |= ai, {
    ctx: je,
    deps: null,
    effects: null,
    equals: li,
    f: t,
    fn: e,
    reactions: null,
    rv: 0,
    v: (
      /** @type {V} */
      null
    ),
    wv: 0,
    parent: n ?? he
  };
}
// @__NO_SIDE_EFFECTS__
function x(e) {
  const t = /* @__PURE__ */ er(e);
  return ki(t), t;
}
// @__NO_SIDE_EFFECTS__
function Nl(e) {
  const t = /* @__PURE__ */ er(e);
  return t.equals = Br, t;
}
function oi(e) {
  var t = e.effects;
  if (t !== null) {
    e.effects = null;
    for (var n = 0; n < t.length; n += 1)
      dt(
        /** @type {Effect} */
        t[n]
      );
  }
}
function Fl(e) {
  for (var t = e.parent; t !== null; ) {
    if ((t.f & Qe) === 0)
      return (
        /** @type {Effect} */
        t
      );
    t = t.parent;
  }
  return null;
}
function si(e) {
  var t, n = he;
  pt(Fl(e));
  try {
    oi(e), t = Ti(e);
  } finally {
    pt(n);
  }
  return t;
}
function ui(e) {
  var t = si(e);
  if (e.equals(t) || (e.v = t, e.wv = Mi()), !Kt) {
    var n = (_t || (e.f & We) !== 0) && e.deps !== null ? Et : De;
    Je(e, n);
  }
}
const ln = /* @__PURE__ */ new Map();
function Fn(e, t) {
  var n = {
    f: 0,
    // TODO ideally we could skip this altogether, but it causes type errors
    v: e,
    reactions: null,
    equals: li,
    rv: 0,
    wv: 0
  };
  return n;
}
// @__NO_SIDE_EFFECTS__
function ee(e, t) {
  const n = Fn(e);
  return ki(n), n;
}
// @__NO_SIDE_EFFECTS__
function ci(e, t = !1) {
  const n = Fn(e);
  return t || (n.equals = Br), n;
}
function V(e, t, n = !1) {
  ge !== null && !tt && fi() && (ge.f & (Qe | Or)) !== 0 && !(Fe != null && Fe.includes(e)) && Sl();
  let r = n ? et(t) : t;
  return kr(e, r);
}
function kr(e, t) {
  if (!e.equals(t)) {
    var n = e.v;
    Kt ? ln.set(e, t) : ln.set(e, n), e.v = t, (e.f & Qe) !== 0 && ((e.f & at) !== 0 && si(
      /** @type {Derived} */
      e
    ), Je(e, (e.f & We) === 0 ? De : Et)), e.wv = Mi(), di(e, at), he !== null && (he.f & De) !== 0 && (he.f & (vt | Xt)) === 0 && (Ve === null ? jl([e]) : Ve.push(e));
  }
  return t;
}
function di(e, t) {
  var n = e.reactions;
  if (n !== null)
    for (var r = n.length, a = 0; a < r; a++) {
      var i = n[a], f = i.f;
      (f & at) === 0 && (Je(i, t), (f & (De | We)) !== 0 && ((f & Qe) !== 0 ? di(
        /** @type {Derived} */
        i,
        Et
      ) : ar(
        /** @type {Effect} */
        i
      )));
    }
}
function zl() {
  console.warn("https://svelte.dev/e/select_multiple_invalid_value");
}
let Cl = !1;
var ha, vi, gi, hi;
function Pl() {
  if (ha === void 0) {
    ha = window, vi = /Firefox/.test(navigator.userAgent);
    var e = Element.prototype, t = Node.prototype, n = Text.prototype;
    gi = mt(t, "firstChild").get, hi = mt(t, "nextSibling").get, da(e) && (e.__click = void 0, e.__className = void 0, e.__attributes = null, e.__style = void 0, e.__e = void 0), da(n) && (n.__t = void 0);
  }
}
function Hr(e = "") {
  return document.createTextNode(e);
}
// @__NO_SIDE_EFFECTS__
function ut(e) {
  return gi.call(e);
}
// @__NO_SIDE_EFFECTS__
function tr(e) {
  return hi.call(e);
}
function _(e, t) {
  return /* @__PURE__ */ ut(e);
}
function Ne(e, t) {
  {
    var n = (
      /** @type {DocumentFragment} */
      /* @__PURE__ */ ut(
        /** @type {Node} */
        e
      )
    );
    return n instanceof Comment && n.data === "" ? /* @__PURE__ */ tr(n) : n;
  }
}
function k(e, t = 1, n = !1) {
  let r = e;
  for (; t--; )
    r = /** @type {TemplateNode} */
    /* @__PURE__ */ tr(r);
  return r;
}
function Rl(e) {
  e.textContent = "";
}
function Il(e) {
  he === null && ge === null && yl(), ge !== null && (ge.f & We) !== 0 && he === null && kl(), Kt && wl();
}
function Dl(e, t) {
  var n = t.last;
  n === null ? t.last = t.first = e : (n.next = e, e.prev = n, t.last = e);
}
function Gt(e, t, n, r = !0) {
  var a = he, i = {
    ctx: je,
    deps: null,
    nodes_start: null,
    nodes_end: null,
    f: e | at,
    first: null,
    fn: t,
    last: null,
    next: null,
    parent: a,
    prev: null,
    teardown: null,
    transitions: null,
    wv: 0
  };
  if (n)
    try {
      Vr(i), i.f |= _l;
    } catch (u) {
      throw dt(i), u;
    }
  else t !== null && ar(i);
  var f = n && i.deps === null && i.first === null && i.nodes_start === null && i.teardown === null && (i.f & (ai | Ln)) === 0;
  if (!f && r && (a !== null && Dl(i, a), ge !== null && (ge.f & Qe) !== 0)) {
    var o = (
      /** @type {Derived} */
      ge
    );
    (o.effects ?? (o.effects = [])).push(i);
  }
  return i;
}
function bi(e) {
  const t = Gt(Qn, null, !1);
  return Je(t, De), t.teardown = e, t;
}
function yr(e) {
  Il();
  var t = he !== null && (he.f & vt) !== 0 && je !== null && !je.m;
  if (t) {
    var n = (
      /** @type {ComponentContext} */
      je
    );
    (n.e ?? (n.e = [])).push({
      fn: e,
      effect: he,
      reaction: ge
    });
  } else {
    var r = Ut(e);
    return r;
  }
}
function Ol(e) {
  const t = Gt(Xt, e, !0);
  return (n = {}) => new Promise((r) => {
    n.outro ? zn(t, () => {
      dt(t), r(void 0);
    }) : (dt(t), r(void 0));
  });
}
function Ut(e) {
  return Gt(ri, e, !1);
}
function Wr(e) {
  return Gt(Qn, e, !0);
}
function $(e, t = [], n = er) {
  const r = t.map(n);
  return nr(() => e(...r.map(l)));
}
function nr(e, t = 0) {
  return Gt(Qn | Or | t, e, !0);
}
function Wt(e, t = !0) {
  return Gt(Qn | vt, e, !0, t);
}
function _i(e) {
  var t = e.teardown;
  if (t !== null) {
    const n = Kt, r = ge;
    ba(!0), it(null);
    try {
      t.call(null);
    } finally {
      ba(n), it(r);
    }
  }
}
function mi(e, t = !1) {
  var n = e.first;
  for (e.first = e.last = null; n !== null; ) {
    var r = n.next;
    (n.f & Xt) !== 0 ? n.parent = null : dt(n, t), n = r;
  }
}
function Bl(e) {
  for (var t = e.first; t !== null; ) {
    var n = t.next;
    (t.f & vt) === 0 && dt(t), t = n;
  }
}
function dt(e, t = !0) {
  var n = !1;
  (t || (e.f & ml) !== 0) && e.nodes_start !== null && (Hl(
    e.nodes_start,
    /** @type {TemplateNode} */
    e.nodes_end
  ), n = !0), mi(e, t && !n), Dn(e, 0), Je(e, Jn);
  var r = e.transitions;
  if (r !== null)
    for (const i of r)
      i.stop();
  _i(e);
  var a = e.parent;
  a !== null && a.first !== null && xi(e), e.next = e.prev = e.teardown = e.ctx = e.deps = e.fn = e.nodes_start = e.nodes_end = null;
}
function Hl(e, t) {
  for (; e !== null; ) {
    var n = e === t ? null : (
      /** @type {TemplateNode} */
      /* @__PURE__ */ tr(e)
    );
    e.remove(), e = n;
  }
}
function xi(e) {
  var t = e.parent, n = e.prev, r = e.next;
  n !== null && (n.next = r), r !== null && (r.prev = n), t !== null && (t.first === e && (t.first = r), t.last === e && (t.last = n));
}
function zn(e, t) {
  var n = [];
  jr(e, n, !0), pi(n, () => {
    dt(e), t && t();
  });
}
function pi(e, t) {
  var n = e.length;
  if (n > 0) {
    var r = () => --n || t();
    for (var a of e)
      a.out(r);
  } else
    t();
}
function jr(e, t, n) {
  if ((e.f & ct) === 0) {
    if (e.f ^= ct, e.transitions !== null)
      for (const f of e.transitions)
        (f.is_global || n) && t.push(f);
    for (var r = e.first; r !== null; ) {
      var a = r.next, i = (r.f & $n) !== 0 || (r.f & vt) !== 0;
      jr(r, t, i ? n : !1), r = a;
    }
  }
}
function Cn(e) {
  wi(e, !0);
}
function wi(e, t) {
  if ((e.f & ct) !== 0) {
    e.f ^= ct, (e.f & De) === 0 && (e.f ^= De), mn(e) && (Je(e, at), ar(e));
    for (var n = e.first; n !== null; ) {
      var r = n.next, a = (n.f & $n) !== 0 || (n.f & vt) !== 0;
      wi(n, a ? t : !1), n = r;
    }
    if (e.transitions !== null)
      for (const i of e.transitions)
        (i.is_global || t) && i.in();
  }
}
let Pn = [];
function Wl() {
  var e = Pn;
  Pn = [], bl(e);
}
function Yr(e) {
  Pn.length === 0 && queueMicrotask(Wl), Pn.push(e);
}
let An = !1, Mr = !1, Rn = null, At = !1, Kt = !1;
function ba(e) {
  Kt = e;
}
let Tn = [];
let ge = null, tt = !1;
function it(e) {
  ge = e;
}
let he = null;
function pt(e) {
  he = e;
}
let Fe = null;
function ki(e) {
  ge !== null && ge.f & wr && (Fe === null ? Fe = [e] : Fe.push(e));
}
let Se = null, He = 0, Ve = null;
function jl(e) {
  Ve = e;
}
let yi = 1, In = 0, _t = !1;
function Mi() {
  return ++yi;
}
function mn(e) {
  var c;
  var t = e.f;
  if ((t & at) !== 0)
    return !0;
  if ((t & Et) !== 0) {
    var n = e.deps, r = (t & We) !== 0;
    if (n !== null) {
      var a, i, f = (t & Nn) !== 0, o = r && he !== null && !_t, u = n.length;
      if (f || o) {
        var s = (
          /** @type {Derived} */
          e
        ), v = s.parent;
        for (a = 0; a < u; a++)
          i = n[a], (f || !((c = i == null ? void 0 : i.reactions) != null && c.includes(s))) && (i.reactions ?? (i.reactions = [])).push(s);
        f && (s.f ^= Nn), o && v !== null && (v.f & We) === 0 && (s.f ^= We);
      }
      for (a = 0; a < u; a++)
        if (i = n[a], mn(
          /** @type {Derived} */
          i
        ) && ui(
          /** @type {Derived} */
          i
        ), i.wv > e.wv)
          return !0;
    }
    (!r || he !== null && !_t) && Je(e, De);
  }
  return !1;
}
function Yl(e, t) {
  for (var n = t; n !== null; ) {
    if ((n.f & Ln) !== 0)
      try {
        n.fn(e);
        return;
      } catch {
        n.f ^= Ln;
      }
    n = n.parent;
  }
  throw An = !1, e;
}
function _a(e) {
  return (e.f & Jn) === 0 && (e.parent === null || (e.parent.f & Ln) === 0);
}
function rr(e, t, n, r) {
  if (An) {
    if (n === null && (An = !1), _a(t))
      throw e;
    return;
  }
  if (n !== null && (An = !0), Yl(e, t), _a(t))
    throw e;
}
function Ai(e, t, n = !0) {
  var r = e.reactions;
  if (r !== null)
    for (var a = 0; a < r.length; a++) {
      var i = r[a];
      Fe != null && Fe.includes(e) || ((i.f & Qe) !== 0 ? Ai(
        /** @type {Derived} */
        i,
        t,
        !1
      ) : t === i && (n ? Je(i, at) : (i.f & De) !== 0 && Je(i, Et), ar(
        /** @type {Effect} */
        i
      )));
    }
}
function Ti(e) {
  var g;
  var t = Se, n = He, r = Ve, a = ge, i = _t, f = Fe, o = je, u = tt, s = e.f;
  Se = /** @type {null | Value[]} */
  null, He = 0, Ve = null, _t = (s & We) !== 0 && (tt || !At || ge === null), ge = (s & (vt | Xt)) === 0 ? e : null, Fe = null, va(e.ctx), tt = !1, In++, e.f |= wr;
  try {
    var v = (
      /** @type {Function} */
      (0, e.fn)()
    ), c = e.deps;
    if (Se !== null) {
      var d;
      if (Dn(e, He), c !== null && He > 0)
        for (c.length = He + Se.length, d = 0; d < Se.length; d++)
          c[He + d] = Se[d];
      else
        e.deps = c = Se;
      if (!_t)
        for (d = He; d < c.length; d++)
          ((g = c[d]).reactions ?? (g.reactions = [])).push(e);
    } else c !== null && He < c.length && (Dn(e, He), c.length = He);
    if (fi() && Ve !== null && !tt && c !== null && (e.f & (Qe | Et | at)) === 0)
      for (d = 0; d < /** @type {Source[]} */
      Ve.length; d++)
        Ai(
          Ve[d],
          /** @type {Effect} */
          e
        );
    return a !== null && a !== e && (In++, Ve !== null && (r === null ? r = Ve : r.push(.../** @type {Source[]} */
    Ve))), v;
  } finally {
    Se = t, He = n, Ve = r, ge = a, _t = i, Fe = f, va(o), tt = u, e.f ^= wr;
  }
}
function Vl(e, t) {
  let n = t.reactions;
  if (n !== null) {
    var r = ul.call(n, e);
    if (r !== -1) {
      var a = n.length - 1;
      a === 0 ? n = t.reactions = null : (n[r] = n[a], n.pop());
    }
  }
  n === null && (t.f & Qe) !== 0 && // Destroying a child effect while updating a parent effect can cause a dependency to appear
  // to be unused, when in fact it is used by the currently-updating parent. Checking `new_deps`
  // allows us to skip the expensive work of disconnecting and immediately reconnecting it
  (Se === null || !Se.includes(t)) && (Je(t, Et), (t.f & (We | Nn)) === 0 && (t.f ^= Nn), oi(
    /** @type {Derived} **/
    t
  ), Dn(
    /** @type {Derived} **/
    t,
    0
  ));
}
function Dn(e, t) {
  var n = e.deps;
  if (n !== null)
    for (var r = t; r < n.length; r++)
      Vl(e, n[r]);
}
function Vr(e) {
  var t = e.f;
  if ((t & Jn) === 0) {
    Je(e, De);
    var n = he, r = je, a = At;
    he = e, At = !0;
    try {
      (t & Or) !== 0 ? Bl(e) : mi(e), _i(e);
      var i = Ti(e);
      e.teardown = typeof i == "function" ? i : null, e.wv = yi;
      var f = e.deps, o;
      ca && El && e.f & at;
    } catch (u) {
      rr(u, e, n, r || e.ctx);
    } finally {
      At = a, he = n;
    }
  }
}
function Xl() {
  try {
    Ml();
  } catch (e) {
    if (Rn !== null)
      rr(e, Rn, null);
    else
      throw e;
  }
}
function Gl() {
  var e = At;
  try {
    var t = 0;
    for (At = !0; Tn.length > 0; ) {
      t++ > 1e3 && Xl();
      var n = Tn, r = n.length;
      Tn = [];
      for (var a = 0; a < r; a++) {
        var i = Kl(n[a]);
        Ul(i);
      }
      ln.clear();
    }
  } finally {
    Mr = !1, At = e, Rn = null;
  }
}
function Ul(e) {
  var t = e.length;
  if (t !== 0)
    for (var n = 0; n < t; n++) {
      var r = e[n];
      if ((r.f & (Jn | ct)) === 0)
        try {
          mn(r) && (Vr(r), r.deps === null && r.first === null && r.nodes_start === null && (r.teardown === null ? xi(r) : r.fn = null));
        } catch (a) {
          rr(a, r, null, r.ctx);
        }
    }
}
function ar(e) {
  Mr || (Mr = !0, queueMicrotask(Gl));
  for (var t = Rn = e; t.parent !== null; ) {
    t = t.parent;
    var n = t.f;
    if ((n & (Xt | vt)) !== 0) {
      if ((n & De) === 0) return;
      t.f ^= De;
    }
  }
  Tn.push(t);
}
function Kl(e) {
  for (var t = [], n = e; n !== null; ) {
    var r = n.f, a = (r & (vt | Xt)) !== 0, i = a && (r & De) !== 0;
    if (!i && (r & ct) === 0) {
      if ((r & ri) !== 0)
        t.push(n);
      else if (a)
        n.f ^= De;
      else
        try {
          mn(n) && Vr(n);
        } catch (u) {
          rr(u, n, null, n.ctx);
        }
      var f = n.first;
      if (f !== null) {
        n = f;
        continue;
      }
    }
    var o = n.parent;
    for (n = n.next; n === null && o !== null; )
      n = o.next, o = o.parent;
  }
  return t;
}
function l(e) {
  var t = e.f, n = (t & Qe) !== 0;
  if (ge !== null && !tt) {
    if (!(Fe != null && Fe.includes(e))) {
      var r = ge.deps;
      e.rv < In && (e.rv = In, Se === null && r !== null && r[He] === e ? He++ : Se === null ? Se = [e] : (!_t || !Se.includes(e)) && Se.push(e));
    }
  } else if (n && /** @type {Derived} */
  e.deps === null && /** @type {Derived} */
  e.effects === null) {
    var a = (
      /** @type {Derived} */
      e
    ), i = a.parent;
    i !== null && (i.f & We) === 0 && (a.f ^= We);
  }
  return n && (a = /** @type {Derived} */
  e, mn(a) && ui(a)), Kt && ln.has(e) ? ln.get(e) : e.v;
}
function qt(e) {
  var t = tt;
  try {
    return tt = !0, e();
  } finally {
    tt = t;
  }
}
const Zl = -7169;
function Je(e, t) {
  e.f = e.f & Zl | t;
}
let ma = !1;
function Ql() {
  ma || (ma = !0, document.addEventListener(
    "reset",
    (e) => {
      Promise.resolve().then(() => {
        var t;
        if (!e.defaultPrevented)
          for (
            const n of
            /**@type {HTMLFormElement} */
            e.target.elements
          )
            (t = n.__on_r) == null || t.call(n);
      });
    },
    // In the capture phase to guarantee we get noticed of it (no possiblity of stopPropagation)
    { capture: !0 }
  ));
}
function qi(e) {
  var t = ge, n = he;
  it(null), pt(null);
  try {
    return e();
  } finally {
    it(t), pt(n);
  }
}
function Xr(e, t, n, r = n) {
  e.addEventListener(t, () => qi(n));
  const a = e.__on_r;
  a ? e.__on_r = () => {
    a(), r(!0);
  } : e.__on_r = () => r(!0), Ql();
}
const Si = /* @__PURE__ */ new Set(), Ar = /* @__PURE__ */ new Set();
function Jl(e, t, n, r = {}) {
  function a(i) {
    if (r.capture || tn.call(t, i), !i.cancelBubble)
      return qi(() => n == null ? void 0 : n.call(this, i));
  }
  return e.startsWith("pointer") || e.startsWith("touch") || e === "wheel" ? Yr(() => {
    t.addEventListener(e, a, r);
  }) : t.addEventListener(e, a, r), a;
}
function Ge(e, t, n, r, a) {
  var i = { capture: r, passive: a }, f = Jl(e, t, n, i);
  (t === document.body || // @ts-ignore
  t === window || // @ts-ignore
  t === document || // Firefox has quirky behavior, it can happen that we still get "canplay" events when the element is already removed
  t instanceof HTMLMediaElement) && bi(() => {
    t.removeEventListener(e, f, i);
  });
}
function Lt(e) {
  for (var t = 0; t < e.length; t++)
    Si.add(e[t]);
  for (var n of Ar)
    n(e);
}
function tn(e) {
  var w;
  var t = this, n = (
    /** @type {Node} */
    t.ownerDocument
  ), r = e.type, a = ((w = e.composedPath) == null ? void 0 : w.call(e)) || [], i = (
    /** @type {null | Element} */
    a[0] || e.target
  ), f = 0, o = e.__root;
  if (o) {
    var u = a.indexOf(o);
    if (u !== -1 && (t === document || t === /** @type {any} */
    window)) {
      e.__root = t;
      return;
    }
    var s = a.indexOf(t);
    if (s === -1)
      return;
    u <= s && (f = u);
  }
  if (i = /** @type {Element} */
  a[f] || e.target, i !== t) {
    cl(e, "currentTarget", {
      configurable: !0,
      get() {
        return i || n;
      }
    });
    var v = ge, c = he;
    it(null), pt(null);
    try {
      for (var d, g = []; i !== null; ) {
        var h = i.assignedSlot || i.parentNode || /** @type {any} */
        i.host || null;
        try {
          var b = i["__" + r];
          if (b != null && (!/** @type {any} */
          i.disabled || // DOM could've been updated already by the time this is reached, so we check this as well
          // -> the target could not have been disabled because it emits the event in the first place
          e.target === i))
            if (Zn(b)) {
              var [m, ...p] = b;
              m.apply(i, [e, ...p]);
            } else
              b.call(i, e);
        } catch (y) {
          d ? g.push(y) : d = y;
        }
        if (e.cancelBubble || h === t || h === null)
          break;
        i = h;
      }
      if (d) {
        for (let y of g)
          queueMicrotask(() => {
            throw y;
          });
        throw d;
      }
    } finally {
      e.__root = t, delete e.currentTarget, it(v), pt(c);
    }
  }
}
function Ei(e) {
  var t = document.createElement("template");
  return t.innerHTML = e.replaceAll("<!>", "<!---->"), t.content;
}
function fn(e, t) {
  var n = (
    /** @type {Effect} */
    he
  );
  n.nodes_start === null && (n.nodes_start = e, n.nodes_end = t);
}
// @__NO_SIDE_EFFECTS__
function oe(e, t) {
  var n = (t & ti) !== 0, r = (t & ol) !== 0, a, i = !e.startsWith("<!>");
  return () => {
    a === void 0 && (a = Ei(i ? e : "<!>" + e), n || (a = /** @type {Node} */
    /* @__PURE__ */ ut(a)));
    var f = (
      /** @type {TemplateNode} */
      r || vi ? document.importNode(a, !0) : a.cloneNode(!0)
    );
    if (n) {
      var o = (
        /** @type {TemplateNode} */
        /* @__PURE__ */ ut(f)
      ), u = (
        /** @type {TemplateNode} */
        f.lastChild
      );
      fn(o, u);
    } else
      fn(f, f);
    return f;
  };
}
// @__NO_SIDE_EFFECTS__
function $l(e, t, n = "svg") {
  var r = !e.startsWith("<!>"), a = (t & ti) !== 0, i = `<${n}>${r ? e : "<!>" + e}</${n}>`, f;
  return () => {
    if (!f) {
      var o = (
        /** @type {DocumentFragment} */
        Ei(i)
      ), u = (
        /** @type {Element} */
        /* @__PURE__ */ ut(o)
      );
      if (a)
        for (f = document.createDocumentFragment(); /* @__PURE__ */ ut(u); )
          f.appendChild(
            /** @type {Node} */
            /* @__PURE__ */ ut(u)
          );
      else
        f = /** @type {Element} */
        /* @__PURE__ */ ut(u);
    }
    var s = (
      /** @type {TemplateNode} */
      f.cloneNode(!0)
    );
    if (a) {
      var v = (
        /** @type {TemplateNode} */
        /* @__PURE__ */ ut(s)
      ), c = (
        /** @type {TemplateNode} */
        s.lastChild
      );
      fn(v, c);
    } else
      fn(s, s);
    return s;
  };
}
// @__NO_SIDE_EFFECTS__
function ke(e, t) {
  return /* @__PURE__ */ $l(e, t, "svg");
}
function St() {
  var e = document.createDocumentFragment(), t = document.createComment(""), n = Hr();
  return e.append(t, n), fn(t, n), e;
}
function H(e, t) {
  e !== null && e.before(
    /** @type {Node} */
    t
  );
}
const ef = ["touchstart", "touchmove"];
function tf(e) {
  return ef.includes(e);
}
function de(e, t) {
  var n = t == null ? "" : typeof t == "object" ? t + "" : t;
  n !== (e.__t ?? (e.__t = e.nodeValue)) && (e.__t = n, e.nodeValue = n + "");
}
function nf(e, t) {
  return rf(e, t);
}
const Nt = /* @__PURE__ */ new Map();
function rf(e, { target: t, anchor: n, props: r = {}, events: a, context: i, intro: f = !0 }) {
  Pl();
  var o = /* @__PURE__ */ new Set(), u = (c) => {
    for (var d = 0; d < c.length; d++) {
      var g = c[d];
      if (!o.has(g)) {
        o.add(g);
        var h = tf(g);
        t.addEventListener(g, tn, { passive: h });
        var b = Nt.get(g);
        b === void 0 ? (document.addEventListener(g, tn, { passive: h }), Nt.set(g, 1)) : Nt.set(g, b + 1);
      }
    }
  };
  u(Dr(Si)), Ar.add(u);
  var s = void 0, v = Ol(() => {
    var c = n ?? t.appendChild(Hr());
    return Wt(() => {
      if (i) {
        pe({});
        var d = (
          /** @type {ComponentContext} */
          je
        );
        d.c = i;
      }
      a && (r.$$events = a), s = e(c, r) || {}, i && we();
    }), () => {
      var h;
      for (var d of o) {
        t.removeEventListener(d, tn);
        var g = (
          /** @type {number} */
          Nt.get(d)
        );
        --g === 0 ? (document.removeEventListener(d, tn), Nt.delete(d)) : Nt.set(d, g);
      }
      Ar.delete(u), c !== n && ((h = c.parentNode) == null || h.removeChild(c));
    };
  });
  return Tr.set(s, v), s;
}
let Tr = /* @__PURE__ */ new WeakMap();
function af(e, t) {
  const n = Tr.get(e);
  return n ? (Tr.delete(e), n(t)) : Promise.resolve();
}
function qr(e, t, ...n) {
  var r = e, a = hl, i;
  nr(() => {
    a !== (a = t()) && (i && (dt(i), i = null), i = Wt(() => (
      /** @type {SnippetFn} */
      a(r, ...n)
    )));
  }, $n);
}
function le(e, t, [n, r] = [0, 0]) {
  var a = e, i = null, f = null, o = Pe, u = n > 0 ? $n : 0, s = !1;
  const v = (d, g = !0) => {
    s = !0, c(g, d);
  }, c = (d, g) => {
    o !== (o = d) && (o ? (i ? Cn(i) : g && (i = Wt(() => g(a))), f && zn(f, () => {
      f = null;
    })) : (f ? Cn(f) : g && (f = Wt(() => g(a, [n + 1, r]))), i && zn(i, () => {
      i = null;
    })));
  };
  nr(() => {
    s = !1, t(v), s || c(null, null);
  }, u);
}
function Me(e, t) {
  return t;
}
function lf(e, t, n, r) {
  for (var a = [], i = t.length, f = 0; f < i; f++)
    jr(t[f].e, a, !0);
  var o = i > 0 && a.length === 0 && n !== null;
  if (o) {
    var u = (
      /** @type {Element} */
      /** @type {Element} */
      n.parentNode
    );
    Rl(u), u.append(
      /** @type {Element} */
      n
    ), r.clear(), gt(e, t[0].prev, t[i - 1].next);
  }
  pi(a, () => {
    for (var s = 0; s < i; s++) {
      var v = t[s];
      o || (r.delete(v.k), gt(e, v.prev, v.next)), dt(v.e, !o);
    }
  });
}
function Ae(e, t, n, r, a, i = null) {
  var f = e, o = { flags: t, items: /* @__PURE__ */ new Map(), first: null }, u = (t & ei) !== 0;
  if (u) {
    var s = (
      /** @type {Element} */
      e
    );
    f = s.appendChild(Hr());
  }
  var v = null, c = !1, d = /* @__PURE__ */ Nl(() => {
    var g = n();
    return Zn(g) ? g : g == null ? [] : Dr(g);
  });
  nr(() => {
    var g = l(d), h = g.length;
    c && h === 0 || (c = h === 0, ff(g, o, f, a, t, r, n), i !== null && (h === 0 ? v ? Cn(v) : v = Wt(() => i(f)) : v !== null && zn(v, () => {
      v = null;
    })), l(d));
  });
}
function ff(e, t, n, r, a, i, f) {
  var I, B, D, X;
  var o = (a & nl) !== 0, u = (a & (Rr | Ir)) !== 0, s = e.length, v = t.items, c = t.first, d = c, g, h = null, b, m = [], p = [], w, y, M, q;
  if (o)
    for (q = 0; q < s; q += 1)
      w = e[q], y = i(w, q), M = v.get(y), M !== void 0 && ((I = M.a) == null || I.measure(), (b ?? (b = /* @__PURE__ */ new Set())).add(M));
  for (q = 0; q < s; q += 1) {
    if (w = e[q], y = i(w, q), M = v.get(y), M === void 0) {
      var E = d ? (
        /** @type {TemplateNode} */
        d.e.nodes_start
      ) : n;
      h = sf(
        E,
        t,
        h,
        h === null ? t.first : h.next,
        w,
        y,
        q,
        r,
        a,
        f
      ), v.set(y, h), m = [], p = [], d = h.next;
      continue;
    }
    if (u && of(M, w, q, a), (M.e.f & ct) !== 0 && (Cn(M.e), o && ((B = M.a) == null || B.unfix(), (b ?? (b = /* @__PURE__ */ new Set())).delete(M))), M !== d) {
      if (g !== void 0 && g.has(M)) {
        if (m.length < p.length) {
          var O = p[0], L;
          h = O.prev;
          var C = m[0], j = m[m.length - 1];
          for (L = 0; L < m.length; L += 1)
            xa(m[L], O, n);
          for (L = 0; L < p.length; L += 1)
            g.delete(p[L]);
          gt(t, C.prev, j.next), gt(t, h, C), gt(t, j, O), d = O, h = j, q -= 1, m = [], p = [];
        } else
          g.delete(M), xa(M, d, n), gt(t, M.prev, M.next), gt(t, M, h === null ? t.first : h.next), gt(t, h, M), h = M;
        continue;
      }
      for (m = [], p = []; d !== null && d.k !== y; )
        (d.e.f & ct) === 0 && (g ?? (g = /* @__PURE__ */ new Set())).add(d), p.push(d), d = d.next;
      if (d === null)
        continue;
      M = d;
    }
    m.push(M), h = M, d = M.next;
  }
  if (d !== null || g !== void 0) {
    for (var A = g === void 0 ? [] : Dr(g); d !== null; )
      (d.e.f & ct) === 0 && A.push(d), d = d.next;
    var z = A.length;
    if (z > 0) {
      var R = (a & ei) !== 0 && s === 0 ? n : null;
      if (o) {
        for (q = 0; q < z; q += 1)
          (D = A[q].a) == null || D.measure();
        for (q = 0; q < z; q += 1)
          (X = A[q].a) == null || X.fix();
      }
      lf(t, A, R, v);
    }
  }
  o && Yr(() => {
    var Y;
    if (b !== void 0)
      for (M of b)
        (Y = M.a) == null || Y.apply();
  }), he.first = t.first && t.first.e, he.last = h && h.e;
}
function of(e, t, n, r) {
  (r & Rr) !== 0 && kr(e.v, t), (r & Ir) !== 0 ? kr(
    /** @type {Value<number>} */
    e.i,
    n
  ) : e.i = n;
}
function sf(e, t, n, r, a, i, f, o, u, s) {
  var v = (u & Rr) !== 0, c = (u & rl) === 0, d = v ? c ? /* @__PURE__ */ ci(a) : Fn(a) : a, g = (u & Ir) === 0 ? f : Fn(f), h = {
    i: g,
    v: d,
    k: i,
    a: null,
    // @ts-expect-error
    e: null,
    prev: n,
    next: r
  };
  try {
    return h.e = Wt(() => o(e, d, g, s), Cl), h.e.prev = n && n.e, h.e.next = r && r.e, n === null ? t.first = h : (n.next = h, n.e.next = h.e), r !== null && (r.prev = h, r.e.prev = h.e), h;
  } finally {
  }
}
function xa(e, t, n) {
  for (var r = e.next ? (
    /** @type {TemplateNode} */
    e.next.e.nodes_start
  ) : n, a = t ? (
    /** @type {TemplateNode} */
    t.e.nodes_start
  ) : n, i = (
    /** @type {TemplateNode} */
    e.e.nodes_start
  ); i !== r; ) {
    var f = (
      /** @type {TemplateNode} */
      /* @__PURE__ */ tr(i)
    );
    a.before(i), i = f;
  }
}
function gt(e, t, n) {
  t === null ? e.first = n : (t.next = n, t.e.next = n && n.e), n !== null && (n.prev = t, n.e.prev = t && t.e);
}
function Li(e) {
  var t, n, r = "";
  if (typeof e == "string" || typeof e == "number") r += e;
  else if (typeof e == "object") if (Array.isArray(e)) {
    var a = e.length;
    for (t = 0; t < a; t++) e[t] && (n = Li(e[t])) && (r && (r += " "), r += n);
  } else for (n in e) e[n] && (r && (r += " "), r += n);
  return r;
}
function uf() {
  for (var e, t, n = 0, r = "", a = arguments.length; n < a; n++) (e = arguments[n]) && (t = Li(e)) && (r && (r += " "), r += t);
  return r;
}
function cf(e) {
  return typeof e == "object" ? uf(e) : e ?? "";
}
const pa = [...` 	
\r\f \v\uFEFF`];
function df(e, t, n) {
  var r = e == null ? "" : "" + e;
  if (t && (r = r ? r + " " + t : t), n) {
    for (var a in n)
      if (n[a])
        r = r ? r + " " + a : a;
      else if (r.length)
        for (var i = a.length, f = 0; (f = r.indexOf(a, f)) >= 0; ) {
          var o = f + i;
          (f === 0 || pa.includes(r[f - 1])) && (o === r.length || pa.includes(r[o])) ? r = (f === 0 ? "" : r.substring(0, f)) + r.substring(o + 1) : f = o;
        }
  }
  return r === "" ? null : r;
}
function wa(e, t = !1) {
  var n = t ? " !important;" : ";", r = "";
  for (var a in e) {
    var i = e[a];
    i != null && i !== "" && (r += " " + a + ": " + i + n);
  }
  return r;
}
function gr(e) {
  return e[0] !== "-" || e[1] !== "-" ? e.toLowerCase() : e;
}
function vf(e, t) {
  if (t) {
    var n = "", r, a;
    if (Array.isArray(t) ? (r = t[0], a = t[1]) : r = t, e) {
      e = String(e).replaceAll(/\s*\/\*.*?\*\/\s*/g, "").trim();
      var i = !1, f = 0, o = !1, u = [];
      r && u.push(...Object.keys(r).map(gr)), a && u.push(...Object.keys(a).map(gr));
      var s = 0, v = -1;
      const b = e.length;
      for (var c = 0; c < b; c++) {
        var d = e[c];
        if (o ? d === "/" && e[c - 1] === "*" && (o = !1) : i ? i === d && (i = !1) : d === "/" && e[c + 1] === "*" ? o = !0 : d === '"' || d === "'" ? i = d : d === "(" ? f++ : d === ")" && f--, !o && i === !1 && f === 0) {
          if (d === ":" && v === -1)
            v = c;
          else if (d === ";" || c === b - 1) {
            if (v !== -1) {
              var g = gr(e.substring(s, v).trim());
              if (!u.includes(g)) {
                d !== ";" && c++;
                var h = e.substring(s, c).trim();
                n += " " + h + ";";
              }
            }
            s = c + 1, v = -1;
          }
        }
      }
    }
    return r && (n += wa(r)), a && (n += wa(a, !0)), n = n.trim(), n === "" ? null : n;
  }
  return e == null ? null : String(e);
}
function Ee(e, t, n, r, a, i) {
  var f = e.__className;
  if (f !== n || f === void 0) {
    var o = df(n, r, i);
    o == null ? e.removeAttribute("class") : e.className = o, e.__className = n;
  } else if (i && a !== i)
    for (var u in i) {
      var s = !!i[u];
      (a == null || s !== !!a[u]) && e.classList.toggle(u, s);
    }
  return i;
}
function hr(e, t = {}, n, r) {
  for (var a in n) {
    var i = n[a];
    t[a] !== i && (n[a] == null ? e.style.removeProperty(a) : e.style.setProperty(a, i, r));
  }
}
function me(e, t, n, r) {
  var a = e.__style;
  if (a !== t) {
    var i = vf(t, r);
    i == null ? e.removeAttribute("style") : e.style.cssText = i, e.__style = t;
  } else r && (Array.isArray(r) ? (hr(e, n == null ? void 0 : n[0], r[0]), hr(e, n == null ? void 0 : n[1], r[1], "important")) : hr(e, n, r));
  return r;
}
function Ct(e, t, n) {
  if (e.multiple) {
    if (t == null)
      return;
    if (!Zn(t))
      return zl();
    for (var r of e.options)
      r.selected = t.includes(rn(r));
    return;
  }
  for (r of e.options) {
    var a = rn(r);
    if (Ll(a, t)) {
      r.selected = !0;
      return;
    }
  }
  (!n || t !== void 0) && (e.selectedIndex = -1);
}
function qn(e, t) {
  let n = !0;
  Ut(() => {
    t && Ct(e, qt(t), n), n = !1;
    var r = new MutationObserver(() => {
      var a = e.__value;
      Ct(e, a);
    });
    return r.observe(e, {
      // Listen to option element changes
      childList: !0,
      subtree: !0,
      // because of <optgroup>
      // Listen to option element value attribute changes
      // (doesn't get notified of select value changes,
      // because that property is not reflected as an attribute)
      attributes: !0,
      attributeFilter: ["value"]
    }), () => {
      r.disconnect();
    };
  });
}
function gf(e, t, n = t) {
  var r = !0;
  Xr(e, "change", (a) => {
    var i = a ? "[selected]" : ":checked", f;
    if (e.multiple)
      f = [].map.call(e.querySelectorAll(i), rn);
    else {
      var o = e.querySelector(i) ?? // will fall back to first non-disabled option if no option is selected
      e.querySelector("option:not([disabled])");
      f = o && rn(o);
    }
    n(f);
  }), Ut(() => {
    var a = t();
    if (Ct(e, a, r), r && a === void 0) {
      var i = e.querySelector(":checked");
      i !== null && (a = rn(i), n(a));
    }
    e.__value = a, r = !1;
  }), qn(e);
}
function rn(e) {
  return "__value" in e ? e.__value : e.value;
}
const hf = Symbol("is custom element"), bf = Symbol("is html");
function ka(e, t) {
  var n = Gr(e);
  n.value === (n.value = // treat null and undefined the same for the initial value
  t ?? void 0) || // @ts-expect-error
  // `progress` elements always need their value set when it's `0`
  e.value === t && (t !== 0 || e.nodeName !== "PROGRESS") || (e.value = t ?? "");
}
function ya(e, t) {
  var n = Gr(e);
  n.checked !== (n.checked = // treat null and undefined the same for the initial value
  t ?? void 0) && (e.checked = t);
}
function T(e, t, n, r) {
  var a = Gr(e);
  a[t] !== (a[t] = n) && (t === "loading" && (e[xl] = n), n == null ? e.removeAttribute(t) : typeof n != "string" && _f(e).includes(t) ? e[t] = n : e.setAttribute(t, n));
}
function Gr(e) {
  return (
    /** @type {Record<string | symbol, unknown>} **/
    // @ts-expect-error
    e.__attributes ?? (e.__attributes = {
      [hf]: e.nodeName.includes("-"),
      [bf]: e.namespaceURI === sl
    })
  );
}
var Ma = /* @__PURE__ */ new Map();
function _f(e) {
  var t = Ma.get(e.nodeName);
  if (t) return t;
  Ma.set(e.nodeName, t = []);
  for (var n, r = e, a = Element.prototype; a !== r; ) {
    n = dl(r);
    for (var i in n)
      n[i].set && t.push(i);
    r = ni(r);
  }
  return t;
}
function ir(e, t, n = t) {
  Xr(e, "input", (r) => {
    var a = r ? e.defaultValue : e.value;
    if (a = br(e) ? _r(a) : a, n(a), a !== (a = t())) {
      var i = e.selectionStart, f = e.selectionEnd;
      e.value = a ?? "", f !== null && (e.selectionStart = i, e.selectionEnd = Math.min(f, e.value.length));
    }
  }), // If we are hydrating and the value has since changed,
  // then use the updated value from the input instead.
  // If defaultValue is set, then value == defaultValue
  // TODO Svelte 6: remove input.value check and set to empty string?
  qt(t) == null && e.value && n(br(e) ? _r(e.value) : e.value), Wr(() => {
    var r = t();
    br(e) && r === _r(e.value) || e.type === "date" && !r && !e.value || r !== e.value && (e.value = r ?? "");
  });
}
function on(e, t, n = t) {
  Xr(e, "change", (r) => {
    var a = r ? e.defaultChecked : e.checked;
    n(a);
  }), // If we are hydrating and the value has since changed,
  // then use the update value from the input instead.
  // If defaultChecked is set, then checked == defaultChecked
  qt(t) == null && n(e.checked), Wr(() => {
    var r = t();
    e.checked = !!r;
  });
}
function br(e) {
  var t = e.type;
  return t === "number" || t === "range";
}
function _r(e) {
  return e === "" ? null : +e;
}
var ht, Dt, vn, Un, Ni;
const Kn = class Kn {
  /** @param {ResizeObserverOptions} options */
  constructor(t) {
    qe(this, Un);
    /** */
    qe(this, ht, /* @__PURE__ */ new WeakMap());
    /** @type {ResizeObserver | undefined} */
    qe(this, Dt);
    /** @type {ResizeObserverOptions} */
    qe(this, vn);
    Be(this, vn, t);
  }
  /**
   * @param {Element} element
   * @param {(entry: ResizeObserverEntry) => any} listener
   */
  observe(t, n) {
    var r = ie(this, ht).get(t) || /* @__PURE__ */ new Set();
    return r.add(n), ie(this, ht).set(t, r), ua(this, Un, Ni).call(this).observe(t, ie(this, vn)), () => {
      var a = ie(this, ht).get(t);
      a.delete(n), a.size === 0 && (ie(this, ht).delete(t), ie(this, Dt).unobserve(t));
    };
  }
};
ht = new WeakMap(), Dt = new WeakMap(), vn = new WeakMap(), Un = new WeakSet(), Ni = function() {
  return ie(this, Dt) ?? Be(this, Dt, new ResizeObserver(
    /** @param {any} entries */
    (t) => {
      for (var n of t) {
        Kn.entries.set(n.target, n);
        for (var r of ie(this, ht).get(n.target) || [])
          r(n);
      }
    }
  ));
}, /** @static */
sa(Kn, "entries", /* @__PURE__ */ new WeakMap());
let Sr = Kn;
var mf = /* @__PURE__ */ new Sr({
  box: "border-box"
});
function Xe(e, t, n) {
  var r = mf.observe(e, () => n(e[t]));
  Ut(() => (qt(() => n(e[t])), r));
}
function Aa(e, t) {
  return e === t || (e == null ? void 0 : e[xt]) === t;
}
function Ur(e = {}, t, n, r) {
  return Ut(() => {
    var a, i;
    return Wr(() => {
      a = i, i = [], qt(() => {
        e !== n(...i) && (t(e, ...i), a && Aa(n(...a), e) && t(null, ...a));
      });
    }), () => {
      Yr(() => {
        i && Aa(n(...i), e) && t(null, ...i);
      });
    };
  }), e;
}
let wn = !1;
function xf(e) {
  var t = wn;
  try {
    return wn = !1, [e(), wn];
  } finally {
    wn = t;
  }
}
const pf = {
  get(e, t) {
    let n = e.props.length;
    for (; n--; ) {
      let r = e.props[n];
      if ($t(r) && (r = r()), typeof r == "object" && r !== null && t in r) return r[t];
    }
  },
  set(e, t, n) {
    let r = e.props.length;
    for (; r--; ) {
      let a = e.props[r];
      $t(a) && (a = a());
      const i = mt(a, t);
      if (i && i.set)
        return i.set(n), !0;
    }
    return !1;
  },
  getOwnPropertyDescriptor(e, t) {
    let n = e.props.length;
    for (; n--; ) {
      let r = e.props[n];
      if ($t(r) && (r = r()), typeof r == "object" && r !== null && t in r) {
        const a = mt(r, t);
        return a && !a.configurable && (a.configurable = !0), a;
      }
    }
  },
  has(e, t) {
    if (t === xt || t === ii) return !1;
    for (let n of e.props)
      if ($t(n) && (n = n()), n != null && t in n) return !0;
    return !1;
  },
  ownKeys(e) {
    const t = [];
    for (let n of e.props)
      if ($t(n) && (n = n()), !!n) {
        for (const r in n)
          t.includes(r) || t.push(r);
        for (const r of Object.getOwnPropertySymbols(n))
          t.includes(r) || t.push(r);
      }
    return t;
  }
};
function lr(...e) {
  return new Proxy({ props: e }, pf);
}
function Ta(e) {
  var t;
  return ((t = e.ctx) == null ? void 0 : t.d) ?? !1;
}
function S(e, t, n, r) {
  var q;
  var a = (n & al) !== 0, i = !0, f = (n & ll) !== 0, o = (n & fl) !== 0, u = !1, s;
  f ? [s, u] = xf(() => (
    /** @type {V} */
    e[t]
  )) : s = /** @type {V} */
  e[t];
  var v = xt in e || ii in e, c = f && (((q = mt(e, t)) == null ? void 0 : q.set) ?? (v && t in e && ((E) => e[t] = E))) || void 0, d = (
    /** @type {V} */
    r
  ), g = !0, h = !1, b = () => (h = !0, g && (g = !1, o ? d = qt(
    /** @type {() => V} */
    r
  ) : d = /** @type {V} */
  r), d);
  s === void 0 && r !== void 0 && (c && i && Al(), s = b(), c && c(s));
  var m;
  if (m = () => {
    var E = (
      /** @type {V} */
      e[t]
    );
    return E === void 0 ? b() : (g = !0, h = !1, E);
  }, (n & il) === 0)
    return m;
  if (c) {
    var p = e.$$legacy;
    return function(E, O) {
      return arguments.length > 0 ? ((!O || p || u) && c(O ? m() : E), E) : m();
    };
  }
  var w = !1, y = /* @__PURE__ */ ci(s), M = /* @__PURE__ */ er(() => {
    var E = m(), O = l(y);
    return w ? (w = !1, O) : y.v = E;
  });
  return f && l(M), a || (M.equals = Br), function(E, O) {
    if (arguments.length > 0) {
      const L = O ? l(M) : f ? et(E) : E;
      if (!M.equals(L)) {
        if (w = !0, V(y, L), h && d !== void 0 && (d = L), Ta(M))
          return E;
        qt(() => l(M));
      }
      return E;
    }
    return Ta(M) ? M.v : l(M);
  };
}
var wf = (e, t, n) => t.changeTab(n()), kf = /* @__PURE__ */ oe('<li class="svelte-1fi7f2s"><button> </button></li>'), yf = /* @__PURE__ */ oe('<div class="svelte-1fi7f2s"><ul class="svelte-1fi7f2s"></ul></div>');
function Mf(e, t) {
  pe(t, !0);
  const n = [
    { value: "overview", title: "Overview" },
    { value: "table", title: "Feature Table" },
    { value: "detail", title: "Feature Detail" }
  ];
  var r = yf(), a = _(r);
  Ae(a, 21, () => n, Me, (i, f) => {
    let o = () => l(f).value, u = () => l(f).title;
    var s = kf(), v = _(s);
    v.__click = [wf, t, o];
    let c;
    var d = _(v);
    $(
      (g) => {
        c = Ee(v, 1, "svelte-1fi7f2s", null, c, g), de(d, u());
      },
      [
        () => ({
          "tab-selected": o() === t.selectedTab
        })
      ]
    ), H(i, s);
  }), H(e, r), we();
}
Lt(["click"]);
var bt, ot, Ot;
class en {
  constructor(t, n) {
    qe(this, bt);
    qe(this, ot);
    qe(this, Ot);
    Be(this, bt, t), Be(this, ot, n), Be(this, Ot, /* @__PURE__ */ ee(et(ie(this, ot).get(ie(this, bt))))), ie(this, ot).on(`change:${ie(this, bt)}`, () => V(ie(this, Ot), ie(this, ot).get(ie(this, bt)), !0));
  }
  get value() {
    return l(ie(this, Ot));
  }
  set value(t) {
    ie(this, ot).set(ie(this, bt), t), ie(this, ot).save_changes();
  }
}
bt = new WeakMap(), ot = new WeakMap(), Ot = new WeakMap();
var Bt;
class Re {
  constructor(t, n) {
    qe(this, Bt);
    Be(this, Bt, /* @__PURE__ */ ee(et(n.get(t)))), n.on(`change:${t}`, () => V(ie(this, Bt), n.get(t), !0));
  }
  get value() {
    return l(ie(this, Bt));
  }
}
Bt = new WeakMap();
var st, gn, hn, bn, _n;
class Af {
  constructor(t) {
    qe(this, st);
    qe(this, gn);
    qe(this, hn);
    qe(this, bn);
    qe(this, _n);
    Be(this, st, new Re("base_font_size", t)), Be(this, gn, /* @__PURE__ */ x(() => ie(this, st).value * 0.75)), Be(this, hn, /* @__PURE__ */ x(() => ie(this, st).value * 0.875)), Be(this, bn, /* @__PURE__ */ x(() => ie(this, st).value * 1.125)), Be(this, _n, /* @__PURE__ */ x(() => ie(this, st).value * 1.25));
  }
  get base() {
    return ie(this, st).value;
  }
  get xs() {
    return l(ie(this, gn));
  }
  get sm() {
    return l(ie(this, hn));
  }
  get lg() {
    return l(ie(this, bn));
  }
  get xl() {
    return l(ie(this, _n));
  }
}
st = new WeakMap(), gn = new WeakMap(), hn = new WeakMap(), bn = new WeakMap(), _n = new WeakMap();
let Fi, Le, Pt, kt, ve, Er, Ft, nn, Lr, ft, an, Nr, Sn, zt, ce;
function Tf(e) {
  Fi = new Re("height", e), new Re("n_table_rows", e), Le = new Re("dataset_info", e), Pt = new Re("model_info", e), new Re("sae_ids", e), new Re("sae_id", e), kt = new Re("sae_data", e), ve = new en("table_ranking_option", e), Er = new en("table_min_act_rate", e), Ft = new en("table_page_index", e), nn = new Re("max_table_page_index", e), new Re("num_filtered_features", e), Lr = new Re("table_features", e), ft = new Re("detail_feature", e), an = new en("detail_feature_id", e), Nr = new Re("can_inference", e), Sn = new en("inference_input", e), zt = new Re("inference_output", e), ce = new Af(e);
}
function En(e, t) {
  return e == null || t == null ? NaN : e < t ? -1 : e > t ? 1 : e >= t ? 0 : NaN;
}
function zi(e, t) {
  return e == null || t == null ? NaN : t < e ? -1 : t > e ? 1 : t >= e ? 0 : NaN;
}
function Ci(e) {
  let t, n, r;
  e.length !== 2 ? (t = En, n = (o, u) => En(e(o), u), r = (o, u) => e(o) - u) : (t = e === En || e === zi ? e : qf, n = e, r = e);
  function a(o, u, s = 0, v = o.length) {
    if (s < v) {
      if (t(u, u) !== 0) return v;
      do {
        const c = s + v >>> 1;
        n(o[c], u) < 0 ? s = c + 1 : v = c;
      } while (s < v);
    }
    return s;
  }
  function i(o, u, s = 0, v = o.length) {
    if (s < v) {
      if (t(u, u) !== 0) return v;
      do {
        const c = s + v >>> 1;
        n(o[c], u) <= 0 ? s = c + 1 : v = c;
      } while (s < v);
    }
    return s;
  }
  function f(o, u, s = 0, v = o.length) {
    const c = a(o, u, s, v - 1);
    return c > s && r(o[c - 1], u) > -r(o[c], u) ? c - 1 : c;
  }
  return { left: a, center: f, right: i };
}
function qf() {
  return 0;
}
function Sf(e) {
  return e === null ? NaN : +e;
}
const Ef = Ci(En), Lf = Ef.right;
Ci(Sf).center;
function Nf(e, t) {
  let n, r;
  if (t === void 0)
    for (const a of e)
      a != null && (n === void 0 ? a >= a && (n = r = a) : (n > a && (n = a), r < a && (r = a)));
  else {
    let a = -1;
    for (let i of e)
      (i = t(i, ++a, e)) != null && (n === void 0 ? i >= i && (n = r = i) : (n > i && (n = i), r < i && (r = i)));
  }
  return [n, r];
}
class qa extends Map {
  constructor(t, n = Cf) {
    if (super(), Object.defineProperties(this, { _intern: { value: /* @__PURE__ */ new Map() }, _key: { value: n } }), t != null) for (const [r, a] of t) this.set(r, a);
  }
  get(t) {
    return super.get(Sa(this, t));
  }
  has(t) {
    return super.has(Sa(this, t));
  }
  set(t, n) {
    return super.set(Ff(this, t), n);
  }
  delete(t) {
    return super.delete(zf(this, t));
  }
}
function Sa({ _intern: e, _key: t }, n) {
  const r = t(n);
  return e.has(r) ? e.get(r) : n;
}
function Ff({ _intern: e, _key: t }, n) {
  const r = t(n);
  return e.has(r) ? e.get(r) : (e.set(r, n), n);
}
function zf({ _intern: e, _key: t }, n) {
  const r = t(n);
  return e.has(r) && (n = e.get(r), e.delete(r)), n;
}
function Cf(e) {
  return e !== null && typeof e == "object" ? e.valueOf() : e;
}
const Pf = Math.sqrt(50), Rf = Math.sqrt(10), If = Math.sqrt(2);
function On(e, t, n) {
  const r = (t - e) / Math.max(0, n), a = Math.floor(Math.log10(r)), i = r / Math.pow(10, a), f = i >= Pf ? 10 : i >= Rf ? 5 : i >= If ? 2 : 1;
  let o, u, s;
  return a < 0 ? (s = Math.pow(10, -a) / f, o = Math.round(e * s), u = Math.round(t * s), o / s < e && ++o, u / s > t && --u, s = -s) : (s = Math.pow(10, a) * f, o = Math.round(e / s), u = Math.round(t / s), o * s < e && ++o, u * s > t && --u), u < o && 0.5 <= n && n < 2 ? On(e, t, n * 2) : [o, u, s];
}
function Df(e, t, n) {
  if (t = +t, e = +e, n = +n, !(n > 0)) return [];
  if (e === t) return [e];
  const r = t < e, [a, i, f] = r ? On(t, e, n) : On(e, t, n);
  if (!(i >= a)) return [];
  const o = i - a + 1, u = new Array(o);
  if (r)
    if (f < 0) for (let s = 0; s < o; ++s) u[s] = (i - s) / -f;
    else for (let s = 0; s < o; ++s) u[s] = (i - s) * f;
  else if (f < 0) for (let s = 0; s < o; ++s) u[s] = (a + s) / -f;
  else for (let s = 0; s < o; ++s) u[s] = (a + s) * f;
  return u;
}
function Fr(e, t, n) {
  return t = +t, e = +e, n = +n, On(e, t, n)[2];
}
function Of(e, t, n) {
  t = +t, e = +e, n = +n;
  const r = t < e, a = r ? Fr(t, e, n) : Fr(e, t, n);
  return (r ? -1 : 1) * (a < 0 ? 1 / -a : a);
}
function Bf(e, t) {
  let n;
  if (t === void 0)
    for (const r of e)
      r != null && (n < r || n === void 0 && r >= r) && (n = r);
  else {
    let r = -1;
    for (let a of e)
      (a = t(a, ++r, e)) != null && (n < a || n === void 0 && a >= a) && (n = a);
  }
  return n;
}
function Hf(e, t) {
  let n;
  if (t === void 0)
    for (const r of e)
      r != null && (n > r || n === void 0 && r >= r) && (n = r);
  else {
    let r = -1;
    for (let a of e)
      (a = t(a, ++r, e)) != null && (n > a || n === void 0 && a >= a) && (n = a);
  }
  return n;
}
function Pi(e, t = Wf) {
  const n = [];
  let r, a = !1;
  for (const i of e)
    a && n.push(t(r, i)), r = i, a = !0;
  return n;
}
function Wf(e, t) {
  return [e, t];
}
function Kr(e, t, n) {
  e = +e, t = +t, n = (a = arguments.length) < 2 ? (t = e, e = 0, 1) : a < 3 ? 1 : +n;
  for (var r = -1, a = Math.max(0, Math.ceil((t - e) / n)) | 0, i = new Array(a); ++r < a; )
    i[r] = e + r * n;
  return i;
}
function jf(e) {
  if (!(i = e.length)) return [];
  for (var t = -1, n = Hf(e, Yf), r = new Array(n); ++t < n; )
    for (var a = -1, i, f = r[t] = new Array(i); ++a < i; )
      f[a] = e[a][t];
  return r;
}
function Yf(e) {
  return e.length;
}
function Vf() {
  return jf(arguments);
}
function Zr(e, t) {
  switch (arguments.length) {
    case 0:
      break;
    case 1:
      this.range(e);
      break;
    default:
      this.range(t).domain(e);
      break;
  }
  return this;
}
function Ri(e, t) {
  switch (arguments.length) {
    case 0:
      break;
    case 1: {
      typeof e == "function" ? this.interpolator(e) : this.range(e);
      break;
    }
    default: {
      this.domain(e), typeof t == "function" ? this.interpolator(t) : this.range(t);
      break;
    }
  }
  return this;
}
const Ea = Symbol("implicit");
function Ii() {
  var e = new qa(), t = [], n = [], r = Ea;
  function a(i) {
    let f = e.get(i);
    if (f === void 0) {
      if (r !== Ea) return r;
      e.set(i, f = t.push(i) - 1);
    }
    return n[f % n.length];
  }
  return a.domain = function(i) {
    if (!arguments.length) return t.slice();
    t = [], e = new qa();
    for (const f of i)
      e.has(f) || e.set(f, t.push(f) - 1);
    return a;
  }, a.range = function(i) {
    return arguments.length ? (n = Array.from(i), a) : n.slice();
  }, a.unknown = function(i) {
    return arguments.length ? (r = i, a) : r;
  }, a.copy = function() {
    return Ii(t, n).unknown(r);
  }, Zr.apply(a, arguments), a;
}
function Bn() {
  var e = Ii().unknown(void 0), t = e.domain, n = e.range, r = 0, a = 1, i, f, o = !1, u = 0, s = 0, v = 0.5;
  delete e.unknown;
  function c() {
    var d = t().length, g = a < r, h = g ? a : r, b = g ? r : a;
    i = (b - h) / Math.max(1, d - u + s * 2), o && (i = Math.floor(i)), h += (b - h - i * (d - u)) * v, f = i * (1 - u), o && (h = Math.round(h), f = Math.round(f));
    var m = Kr(d).map(function(p) {
      return h + i * p;
    });
    return n(g ? m.reverse() : m);
  }
  return e.domain = function(d) {
    return arguments.length ? (t(d), c()) : t();
  }, e.range = function(d) {
    return arguments.length ? ([r, a] = d, r = +r, a = +a, c()) : [r, a];
  }, e.rangeRound = function(d) {
    return [r, a] = d, r = +r, a = +a, o = !0, c();
  }, e.bandwidth = function() {
    return f;
  }, e.step = function() {
    return i;
  }, e.round = function(d) {
    return arguments.length ? (o = !!d, c()) : o;
  }, e.padding = function(d) {
    return arguments.length ? (u = Math.min(1, s = +d), c()) : u;
  }, e.paddingInner = function(d) {
    return arguments.length ? (u = Math.min(1, d), c()) : u;
  }, e.paddingOuter = function(d) {
    return arguments.length ? (s = +d, c()) : s;
  }, e.align = function(d) {
    return arguments.length ? (v = Math.max(0, Math.min(1, d)), c()) : v;
  }, e.copy = function() {
    return Bn(t(), [r, a]).round(o).paddingInner(u).paddingOuter(s).align(v);
  }, Zr.apply(c(), arguments);
}
function Qr(e, t, n) {
  e.prototype = t.prototype = n, n.constructor = e;
}
function Di(e, t) {
  var n = Object.create(e.prototype);
  for (var r in t) n[r] = t[r];
  return n;
}
function xn() {
}
var sn = 0.7, Hn = 1 / sn, Rt = "\\s*([+-]?\\d+)\\s*", un = "\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)\\s*", rt = "\\s*([+-]?(?:\\d*\\.)?\\d+(?:[eE][+-]?\\d+)?)%\\s*", Xf = /^#([0-9a-f]{3,8})$/, Gf = new RegExp(`^rgb\\(${Rt},${Rt},${Rt}\\)$`), Uf = new RegExp(`^rgb\\(${rt},${rt},${rt}\\)$`), Kf = new RegExp(`^rgba\\(${Rt},${Rt},${Rt},${un}\\)$`), Zf = new RegExp(`^rgba\\(${rt},${rt},${rt},${un}\\)$`), Qf = new RegExp(`^hsl\\(${un},${rt},${rt}\\)$`), Jf = new RegExp(`^hsla\\(${un},${rt},${rt},${un}\\)$`), La = {
  aliceblue: 15792383,
  antiquewhite: 16444375,
  aqua: 65535,
  aquamarine: 8388564,
  azure: 15794175,
  beige: 16119260,
  bisque: 16770244,
  black: 0,
  blanchedalmond: 16772045,
  blue: 255,
  blueviolet: 9055202,
  brown: 10824234,
  burlywood: 14596231,
  cadetblue: 6266528,
  chartreuse: 8388352,
  chocolate: 13789470,
  coral: 16744272,
  cornflowerblue: 6591981,
  cornsilk: 16775388,
  crimson: 14423100,
  cyan: 65535,
  darkblue: 139,
  darkcyan: 35723,
  darkgoldenrod: 12092939,
  darkgray: 11119017,
  darkgreen: 25600,
  darkgrey: 11119017,
  darkkhaki: 12433259,
  darkmagenta: 9109643,
  darkolivegreen: 5597999,
  darkorange: 16747520,
  darkorchid: 10040012,
  darkred: 9109504,
  darksalmon: 15308410,
  darkseagreen: 9419919,
  darkslateblue: 4734347,
  darkslategray: 3100495,
  darkslategrey: 3100495,
  darkturquoise: 52945,
  darkviolet: 9699539,
  deeppink: 16716947,
  deepskyblue: 49151,
  dimgray: 6908265,
  dimgrey: 6908265,
  dodgerblue: 2003199,
  firebrick: 11674146,
  floralwhite: 16775920,
  forestgreen: 2263842,
  fuchsia: 16711935,
  gainsboro: 14474460,
  ghostwhite: 16316671,
  gold: 16766720,
  goldenrod: 14329120,
  gray: 8421504,
  green: 32768,
  greenyellow: 11403055,
  grey: 8421504,
  honeydew: 15794160,
  hotpink: 16738740,
  indianred: 13458524,
  indigo: 4915330,
  ivory: 16777200,
  khaki: 15787660,
  lavender: 15132410,
  lavenderblush: 16773365,
  lawngreen: 8190976,
  lemonchiffon: 16775885,
  lightblue: 11393254,
  lightcoral: 15761536,
  lightcyan: 14745599,
  lightgoldenrodyellow: 16448210,
  lightgray: 13882323,
  lightgreen: 9498256,
  lightgrey: 13882323,
  lightpink: 16758465,
  lightsalmon: 16752762,
  lightseagreen: 2142890,
  lightskyblue: 8900346,
  lightslategray: 7833753,
  lightslategrey: 7833753,
  lightsteelblue: 11584734,
  lightyellow: 16777184,
  lime: 65280,
  limegreen: 3329330,
  linen: 16445670,
  magenta: 16711935,
  maroon: 8388608,
  mediumaquamarine: 6737322,
  mediumblue: 205,
  mediumorchid: 12211667,
  mediumpurple: 9662683,
  mediumseagreen: 3978097,
  mediumslateblue: 8087790,
  mediumspringgreen: 64154,
  mediumturquoise: 4772300,
  mediumvioletred: 13047173,
  midnightblue: 1644912,
  mintcream: 16121850,
  mistyrose: 16770273,
  moccasin: 16770229,
  navajowhite: 16768685,
  navy: 128,
  oldlace: 16643558,
  olive: 8421376,
  olivedrab: 7048739,
  orange: 16753920,
  orangered: 16729344,
  orchid: 14315734,
  palegoldenrod: 15657130,
  palegreen: 10025880,
  paleturquoise: 11529966,
  palevioletred: 14381203,
  papayawhip: 16773077,
  peachpuff: 16767673,
  peru: 13468991,
  pink: 16761035,
  plum: 14524637,
  powderblue: 11591910,
  purple: 8388736,
  rebeccapurple: 6697881,
  red: 16711680,
  rosybrown: 12357519,
  royalblue: 4286945,
  saddlebrown: 9127187,
  salmon: 16416882,
  sandybrown: 16032864,
  seagreen: 3050327,
  seashell: 16774638,
  sienna: 10506797,
  silver: 12632256,
  skyblue: 8900331,
  slateblue: 6970061,
  slategray: 7372944,
  slategrey: 7372944,
  snow: 16775930,
  springgreen: 65407,
  steelblue: 4620980,
  tan: 13808780,
  teal: 32896,
  thistle: 14204888,
  tomato: 16737095,
  turquoise: 4251856,
  violet: 15631086,
  wheat: 16113331,
  white: 16777215,
  whitesmoke: 16119285,
  yellow: 16776960,
  yellowgreen: 10145074
};
Qr(xn, cn, {
  copy(e) {
    return Object.assign(new this.constructor(), this, e);
  },
  displayable() {
    return this.rgb().displayable();
  },
  hex: Na,
  // Deprecated! Use color.formatHex.
  formatHex: Na,
  formatHex8: $f,
  formatHsl: eo,
  formatRgb: Fa,
  toString: Fa
});
function Na() {
  return this.rgb().formatHex();
}
function $f() {
  return this.rgb().formatHex8();
}
function eo() {
  return Oi(this).formatHsl();
}
function Fa() {
  return this.rgb().formatRgb();
}
function cn(e) {
  var t, n;
  return e = (e + "").trim().toLowerCase(), (t = Xf.exec(e)) ? (n = t[1].length, t = parseInt(t[1], 16), n === 6 ? za(t) : n === 3 ? new Ie(t >> 8 & 15 | t >> 4 & 240, t >> 4 & 15 | t & 240, (t & 15) << 4 | t & 15, 1) : n === 8 ? kn(t >> 24 & 255, t >> 16 & 255, t >> 8 & 255, (t & 255) / 255) : n === 4 ? kn(t >> 12 & 15 | t >> 8 & 240, t >> 8 & 15 | t >> 4 & 240, t >> 4 & 15 | t & 240, ((t & 15) << 4 | t & 15) / 255) : null) : (t = Gf.exec(e)) ? new Ie(t[1], t[2], t[3], 1) : (t = Uf.exec(e)) ? new Ie(t[1] * 255 / 100, t[2] * 255 / 100, t[3] * 255 / 100, 1) : (t = Kf.exec(e)) ? kn(t[1], t[2], t[3], t[4]) : (t = Zf.exec(e)) ? kn(t[1] * 255 / 100, t[2] * 255 / 100, t[3] * 255 / 100, t[4]) : (t = Qf.exec(e)) ? Ra(t[1], t[2] / 100, t[3] / 100, 1) : (t = Jf.exec(e)) ? Ra(t[1], t[2] / 100, t[3] / 100, t[4]) : La.hasOwnProperty(e) ? za(La[e]) : e === "transparent" ? new Ie(NaN, NaN, NaN, 0) : null;
}
function za(e) {
  return new Ie(e >> 16 & 255, e >> 8 & 255, e & 255, 1);
}
function kn(e, t, n, r) {
  return r <= 0 && (e = t = n = NaN), new Ie(e, t, n, r);
}
function to(e) {
  return e instanceof xn || (e = cn(e)), e ? (e = e.rgb(), new Ie(e.r, e.g, e.b, e.opacity)) : new Ie();
}
function Wn(e, t, n, r) {
  return arguments.length === 1 ? to(e) : new Ie(e, t, n, r ?? 1);
}
function Ie(e, t, n, r) {
  this.r = +e, this.g = +t, this.b = +n, this.opacity = +r;
}
Qr(Ie, Wn, Di(xn, {
  brighter(e) {
    return e = e == null ? Hn : Math.pow(Hn, e), new Ie(this.r * e, this.g * e, this.b * e, this.opacity);
  },
  darker(e) {
    return e = e == null ? sn : Math.pow(sn, e), new Ie(this.r * e, this.g * e, this.b * e, this.opacity);
  },
  rgb() {
    return this;
  },
  clamp() {
    return new Ie(Tt(this.r), Tt(this.g), Tt(this.b), jn(this.opacity));
  },
  displayable() {
    return -0.5 <= this.r && this.r < 255.5 && -0.5 <= this.g && this.g < 255.5 && -0.5 <= this.b && this.b < 255.5 && 0 <= this.opacity && this.opacity <= 1;
  },
  hex: Ca,
  // Deprecated! Use color.formatHex.
  formatHex: Ca,
  formatHex8: no,
  formatRgb: Pa,
  toString: Pa
}));
function Ca() {
  return `#${Mt(this.r)}${Mt(this.g)}${Mt(this.b)}`;
}
function no() {
  return `#${Mt(this.r)}${Mt(this.g)}${Mt(this.b)}${Mt((isNaN(this.opacity) ? 1 : this.opacity) * 255)}`;
}
function Pa() {
  const e = jn(this.opacity);
  return `${e === 1 ? "rgb(" : "rgba("}${Tt(this.r)}, ${Tt(this.g)}, ${Tt(this.b)}${e === 1 ? ")" : `, ${e})`}`;
}
function jn(e) {
  return isNaN(e) ? 1 : Math.max(0, Math.min(1, e));
}
function Tt(e) {
  return Math.max(0, Math.min(255, Math.round(e) || 0));
}
function Mt(e) {
  return e = Tt(e), (e < 16 ? "0" : "") + e.toString(16);
}
function Ra(e, t, n, r) {
  return r <= 0 ? e = t = n = NaN : n <= 0 || n >= 1 ? e = t = NaN : t <= 0 && (e = NaN), new Ze(e, t, n, r);
}
function Oi(e) {
  if (e instanceof Ze) return new Ze(e.h, e.s, e.l, e.opacity);
  if (e instanceof xn || (e = cn(e)), !e) return new Ze();
  if (e instanceof Ze) return e;
  e = e.rgb();
  var t = e.r / 255, n = e.g / 255, r = e.b / 255, a = Math.min(t, n, r), i = Math.max(t, n, r), f = NaN, o = i - a, u = (i + a) / 2;
  return o ? (t === i ? f = (n - r) / o + (n < r) * 6 : n === i ? f = (r - t) / o + 2 : f = (t - n) / o + 4, o /= u < 0.5 ? i + a : 2 - i - a, f *= 60) : o = u > 0 && u < 1 ? 0 : f, new Ze(f, o, u, e.opacity);
}
function ro(e, t, n, r) {
  return arguments.length === 1 ? Oi(e) : new Ze(e, t, n, r ?? 1);
}
function Ze(e, t, n, r) {
  this.h = +e, this.s = +t, this.l = +n, this.opacity = +r;
}
Qr(Ze, ro, Di(xn, {
  brighter(e) {
    return e = e == null ? Hn : Math.pow(Hn, e), new Ze(this.h, this.s, this.l * e, this.opacity);
  },
  darker(e) {
    return e = e == null ? sn : Math.pow(sn, e), new Ze(this.h, this.s, this.l * e, this.opacity);
  },
  rgb() {
    var e = this.h % 360 + (this.h < 0) * 360, t = isNaN(e) || isNaN(this.s) ? 0 : this.s, n = this.l, r = n + (n < 0.5 ? n : 1 - n) * t, a = 2 * n - r;
    return new Ie(
      mr(e >= 240 ? e - 240 : e + 120, a, r),
      mr(e, a, r),
      mr(e < 120 ? e + 240 : e - 120, a, r),
      this.opacity
    );
  },
  clamp() {
    return new Ze(Ia(this.h), yn(this.s), yn(this.l), jn(this.opacity));
  },
  displayable() {
    return (0 <= this.s && this.s <= 1 || isNaN(this.s)) && 0 <= this.l && this.l <= 1 && 0 <= this.opacity && this.opacity <= 1;
  },
  formatHsl() {
    const e = jn(this.opacity);
    return `${e === 1 ? "hsl(" : "hsla("}${Ia(this.h)}, ${yn(this.s) * 100}%, ${yn(this.l) * 100}%${e === 1 ? ")" : `, ${e})`}`;
  }
}));
function Ia(e) {
  return e = (e || 0) % 360, e < 0 ? e + 360 : e;
}
function yn(e) {
  return Math.max(0, Math.min(1, e || 0));
}
function mr(e, t, n) {
  return (e < 60 ? t + (n - t) * e / 60 : e < 180 ? n : e < 240 ? t + (n - t) * (240 - e) / 60 : t) * 255;
}
function ao(e, t, n, r, a) {
  var i = e * e, f = i * e;
  return ((1 - 3 * e + 3 * i - f) * t + (4 - 6 * i + 3 * f) * n + (1 + 3 * e + 3 * i - 3 * f) * r + f * a) / 6;
}
function io(e) {
  var t = e.length - 1;
  return function(n) {
    var r = n <= 0 ? n = 0 : n >= 1 ? (n = 1, t - 1) : Math.floor(n * t), a = e[r], i = e[r + 1], f = r > 0 ? e[r - 1] : 2 * a - i, o = r < t - 1 ? e[r + 2] : 2 * i - a;
    return ao((n - r / t) * t, f, a, i, o);
  };
}
const Jr = (e) => () => e;
function lo(e, t) {
  return function(n) {
    return e + n * t;
  };
}
function fo(e, t, n) {
  return e = Math.pow(e, n), t = Math.pow(t, n) - e, n = 1 / n, function(r) {
    return Math.pow(e + r * t, n);
  };
}
function oo(e) {
  return (e = +e) == 1 ? Bi : function(t, n) {
    return n - t ? fo(t, n, e) : Jr(isNaN(t) ? n : t);
  };
}
function Bi(e, t) {
  var n = t - e;
  return n ? lo(e, n) : Jr(isNaN(e) ? t : e);
}
const Da = function e(t) {
  var n = oo(t);
  function r(a, i) {
    var f = n((a = Wn(a)).r, (i = Wn(i)).r), o = n(a.g, i.g), u = n(a.b, i.b), s = Bi(a.opacity, i.opacity);
    return function(v) {
      return a.r = f(v), a.g = o(v), a.b = u(v), a.opacity = s(v), a + "";
    };
  }
  return r.gamma = e, r;
}(1);
function so(e) {
  return function(t) {
    var n = t.length, r = new Array(n), a = new Array(n), i = new Array(n), f, o;
    for (f = 0; f < n; ++f)
      o = Wn(t[f]), r[f] = o.r || 0, a[f] = o.g || 0, i[f] = o.b || 0;
    return r = e(r), a = e(a), i = e(i), o.opacity = 1, function(u) {
      return o.r = r(u), o.g = a(u), o.b = i(u), o + "";
    };
  };
}
var uo = so(io);
function co(e, t) {
  t || (t = []);
  var n = e ? Math.min(t.length, e.length) : 0, r = t.slice(), a;
  return function(i) {
    for (a = 0; a < n; ++a) r[a] = e[a] * (1 - i) + t[a] * i;
    return r;
  };
}
function vo(e) {
  return ArrayBuffer.isView(e) && !(e instanceof DataView);
}
function go(e, t) {
  var n = t ? t.length : 0, r = e ? Math.min(n, e.length) : 0, a = new Array(r), i = new Array(n), f;
  for (f = 0; f < r; ++f) a[f] = Zt(e[f], t[f]);
  for (; f < n; ++f) i[f] = t[f];
  return function(o) {
    for (f = 0; f < r; ++f) i[f] = a[f](o);
    return i;
  };
}
function ho(e, t) {
  var n = /* @__PURE__ */ new Date();
  return e = +e, t = +t, function(r) {
    return n.setTime(e * (1 - r) + t * r), n;
  };
}
function Yn(e, t) {
  return e = +e, t = +t, function(n) {
    return e * (1 - n) + t * n;
  };
}
function bo(e, t) {
  var n = {}, r = {}, a;
  (e === null || typeof e != "object") && (e = {}), (t === null || typeof t != "object") && (t = {});
  for (a in t)
    a in e ? n[a] = Zt(e[a], t[a]) : r[a] = t[a];
  return function(i) {
    for (a in n) r[a] = n[a](i);
    return r;
  };
}
var zr = /[-+]?(?:\d+\.?\d*|\.?\d+)(?:[eE][-+]?\d+)?/g, xr = new RegExp(zr.source, "g");
function _o(e) {
  return function() {
    return e;
  };
}
function mo(e) {
  return function(t) {
    return e(t) + "";
  };
}
function xo(e, t) {
  var n = zr.lastIndex = xr.lastIndex = 0, r, a, i, f = -1, o = [], u = [];
  for (e = e + "", t = t + ""; (r = zr.exec(e)) && (a = xr.exec(t)); )
    (i = a.index) > n && (i = t.slice(n, i), o[f] ? o[f] += i : o[++f] = i), (r = r[0]) === (a = a[0]) ? o[f] ? o[f] += a : o[++f] = a : (o[++f] = null, u.push({ i: f, x: Yn(r, a) })), n = xr.lastIndex;
  return n < t.length && (i = t.slice(n), o[f] ? o[f] += i : o[++f] = i), o.length < 2 ? u[0] ? mo(u[0].x) : _o(t) : (t = u.length, function(s) {
    for (var v = 0, c; v < t; ++v) o[(c = u[v]).i] = c.x(s);
    return o.join("");
  });
}
function Zt(e, t) {
  var n = typeof t, r;
  return t == null || n === "boolean" ? Jr(t) : (n === "number" ? Yn : n === "string" ? (r = cn(t)) ? (t = r, Da) : xo : t instanceof cn ? Da : t instanceof Date ? ho : vo(t) ? co : Array.isArray(t) ? go : typeof t.valueOf != "function" && typeof t.toString != "function" || isNaN(t) ? bo : Yn)(e, t);
}
function $r(e, t) {
  return e = +e, t = +t, function(n) {
    return Math.round(e * (1 - n) + t * n);
  };
}
function po(e, t) {
  t === void 0 && (t = e, e = Zt);
  for (var n = 0, r = t.length - 1, a = t[0], i = new Array(r < 0 ? 0 : r); n < r; ) i[n] = e(a, a = t[++n]);
  return function(f) {
    var o = Math.max(0, Math.min(r - 1, Math.floor(f *= r)));
    return i[o](f - o);
  };
}
function wo(e) {
  return function() {
    return e;
  };
}
function ko(e) {
  return +e;
}
var Oa = [0, 1];
function nt(e) {
  return e;
}
function Cr(e, t) {
  return (t -= e = +e) ? function(n) {
    return (n - e) / t;
  } : wo(isNaN(t) ? NaN : 0.5);
}
function yo(e, t) {
  var n;
  return e > t && (n = e, e = t, t = n), function(r) {
    return Math.max(e, Math.min(t, r));
  };
}
function Mo(e, t, n) {
  var r = e[0], a = e[1], i = t[0], f = t[1];
  return a < r ? (r = Cr(a, r), i = n(f, i)) : (r = Cr(r, a), i = n(i, f)), function(o) {
    return i(r(o));
  };
}
function Ao(e, t, n) {
  var r = Math.min(e.length, t.length) - 1, a = new Array(r), i = new Array(r), f = -1;
  for (e[r] < e[0] && (e = e.slice().reverse(), t = t.slice().reverse()); ++f < r; )
    a[f] = Cr(e[f], e[f + 1]), i[f] = n(t[f], t[f + 1]);
  return function(o) {
    var u = Lf(e, o, 1, r) - 1;
    return i[u](a[u](o));
  };
}
function To(e, t) {
  return t.domain(e.domain()).range(e.range()).interpolate(e.interpolate()).clamp(e.clamp()).unknown(e.unknown());
}
function qo() {
  var e = Oa, t = Oa, n = Zt, r, a, i, f = nt, o, u, s;
  function v() {
    var d = Math.min(e.length, t.length);
    return f !== nt && (f = yo(e[0], e[d - 1])), o = d > 2 ? Ao : Mo, u = s = null, c;
  }
  function c(d) {
    return d == null || isNaN(d = +d) ? i : (u || (u = o(e.map(r), t, n)))(r(f(d)));
  }
  return c.invert = function(d) {
    return f(a((s || (s = o(t, e.map(r), Yn)))(d)));
  }, c.domain = function(d) {
    return arguments.length ? (e = Array.from(d, ko), v()) : e.slice();
  }, c.range = function(d) {
    return arguments.length ? (t = Array.from(d), v()) : t.slice();
  }, c.rangeRound = function(d) {
    return t = Array.from(d), n = $r, v();
  }, c.clamp = function(d) {
    return arguments.length ? (f = d ? !0 : nt, v()) : f !== nt;
  }, c.interpolate = function(d) {
    return arguments.length ? (n = d, v()) : n;
  }, c.unknown = function(d) {
    return arguments.length ? (i = d, c) : i;
  }, function(d, g) {
    return r = d, a = g, v();
  };
}
function So() {
  return qo()(nt, nt);
}
function Eo(e) {
  return Math.abs(e = Math.round(e)) >= 1e21 ? e.toLocaleString("en").replace(/,/g, "") : e.toString(10);
}
function Vn(e, t) {
  if ((n = (e = t ? e.toExponential(t - 1) : e.toExponential()).indexOf("e")) < 0) return null;
  var n, r = e.slice(0, n);
  return [
    r.length > 1 ? r[0] + r.slice(2) : r,
    +e.slice(n + 1)
  ];
}
function jt(e) {
  return e = Vn(Math.abs(e)), e ? e[1] : NaN;
}
function Lo(e, t) {
  return function(n, r) {
    for (var a = n.length, i = [], f = 0, o = e[0], u = 0; a > 0 && o > 0 && (u + o + 1 > r && (o = Math.max(1, r - u)), i.push(n.substring(a -= o, a + o)), !((u += o + 1) > r)); )
      o = e[f = (f + 1) % e.length];
    return i.reverse().join(t);
  };
}
function No(e) {
  return function(t) {
    return t.replace(/[0-9]/g, function(n) {
      return e[+n];
    });
  };
}
var Fo = /^(?:(.)?([<>=^]))?([+\-( ])?([$#])?(0)?(\d+)?(,)?(\.\d+)?(~)?([a-z%])?$/i;
function Xn(e) {
  if (!(t = Fo.exec(e))) throw new Error("invalid format: " + e);
  var t;
  return new ea({
    fill: t[1],
    align: t[2],
    sign: t[3],
    symbol: t[4],
    zero: t[5],
    width: t[6],
    comma: t[7],
    precision: t[8] && t[8].slice(1),
    trim: t[9],
    type: t[10]
  });
}
Xn.prototype = ea.prototype;
function ea(e) {
  this.fill = e.fill === void 0 ? " " : e.fill + "", this.align = e.align === void 0 ? ">" : e.align + "", this.sign = e.sign === void 0 ? "-" : e.sign + "", this.symbol = e.symbol === void 0 ? "" : e.symbol + "", this.zero = !!e.zero, this.width = e.width === void 0 ? void 0 : +e.width, this.comma = !!e.comma, this.precision = e.precision === void 0 ? void 0 : +e.precision, this.trim = !!e.trim, this.type = e.type === void 0 ? "" : e.type + "";
}
ea.prototype.toString = function() {
  return this.fill + this.align + this.sign + this.symbol + (this.zero ? "0" : "") + (this.width === void 0 ? "" : Math.max(1, this.width | 0)) + (this.comma ? "," : "") + (this.precision === void 0 ? "" : "." + Math.max(0, this.precision | 0)) + (this.trim ? "~" : "") + this.type;
};
function zo(e) {
  e: for (var t = e.length, n = 1, r = -1, a; n < t; ++n)
    switch (e[n]) {
      case ".":
        r = a = n;
        break;
      case "0":
        r === 0 && (r = n), a = n;
        break;
      default:
        if (!+e[n]) break e;
        r > 0 && (r = 0);
        break;
    }
  return r > 0 ? e.slice(0, r) + e.slice(a + 1) : e;
}
var Hi;
function Co(e, t) {
  var n = Vn(e, t);
  if (!n) return e + "";
  var r = n[0], a = n[1], i = a - (Hi = Math.max(-8, Math.min(8, Math.floor(a / 3))) * 3) + 1, f = r.length;
  return i === f ? r : i > f ? r + new Array(i - f + 1).join("0") : i > 0 ? r.slice(0, i) + "." + r.slice(i) : "0." + new Array(1 - i).join("0") + Vn(e, Math.max(0, t + i - 1))[0];
}
function Ba(e, t) {
  var n = Vn(e, t);
  if (!n) return e + "";
  var r = n[0], a = n[1];
  return a < 0 ? "0." + new Array(-a).join("0") + r : r.length > a + 1 ? r.slice(0, a + 1) + "." + r.slice(a + 1) : r + new Array(a - r.length + 2).join("0");
}
const Ha = {
  "%": (e, t) => (e * 100).toFixed(t),
  b: (e) => Math.round(e).toString(2),
  c: (e) => e + "",
  d: Eo,
  e: (e, t) => e.toExponential(t),
  f: (e, t) => e.toFixed(t),
  g: (e, t) => e.toPrecision(t),
  o: (e) => Math.round(e).toString(8),
  p: (e, t) => Ba(e * 100, t),
  r: Ba,
  s: Co,
  X: (e) => Math.round(e).toString(16).toUpperCase(),
  x: (e) => Math.round(e).toString(16)
};
function Wa(e) {
  return e;
}
var ja = Array.prototype.map, Ya = ["y", "z", "a", "f", "p", "n", "µ", "m", "", "k", "M", "G", "T", "P", "E", "Z", "Y"];
function Po(e) {
  var t = e.grouping === void 0 || e.thousands === void 0 ? Wa : Lo(ja.call(e.grouping, Number), e.thousands + ""), n = e.currency === void 0 ? "" : e.currency[0] + "", r = e.currency === void 0 ? "" : e.currency[1] + "", a = e.decimal === void 0 ? "." : e.decimal + "", i = e.numerals === void 0 ? Wa : No(ja.call(e.numerals, String)), f = e.percent === void 0 ? "%" : e.percent + "", o = e.minus === void 0 ? "−" : e.minus + "", u = e.nan === void 0 ? "NaN" : e.nan + "";
  function s(c) {
    c = Xn(c);
    var d = c.fill, g = c.align, h = c.sign, b = c.symbol, m = c.zero, p = c.width, w = c.comma, y = c.precision, M = c.trim, q = c.type;
    q === "n" ? (w = !0, q = "g") : Ha[q] || (y === void 0 && (y = 12), M = !0, q = "g"), (m || d === "0" && g === "=") && (m = !0, d = "0", g = "=");
    var E = b === "$" ? n : b === "#" && /[boxX]/.test(q) ? "0" + q.toLowerCase() : "", O = b === "$" ? r : /[%p]/.test(q) ? f : "", L = Ha[q], C = /[defgprs%]/.test(q);
    y = y === void 0 ? 6 : /[gprs]/.test(q) ? Math.max(1, Math.min(21, y)) : Math.max(0, Math.min(20, y));
    function j(A) {
      var z = E, R = O, I, B, D;
      if (q === "c")
        R = L(A) + R, A = "";
      else {
        A = +A;
        var X = A < 0 || 1 / A < 0;
        if (A = isNaN(A) ? u : L(Math.abs(A), y), M && (A = zo(A)), X && +A == 0 && h !== "+" && (X = !1), z = (X ? h === "(" ? h : o : h === "-" || h === "(" ? "" : h) + z, R = (q === "s" ? Ya[8 + Hi / 3] : "") + R + (X && h === "(" ? ")" : ""), C) {
          for (I = -1, B = A.length; ++I < B; )
            if (D = A.charCodeAt(I), 48 > D || D > 57) {
              R = (D === 46 ? a + A.slice(I + 1) : A.slice(I)) + R, A = A.slice(0, I);
              break;
            }
        }
      }
      w && !m && (A = t(A, 1 / 0));
      var Y = z.length + A.length + R.length, Z = Y < p ? new Array(p - Y + 1).join(d) : "";
      switch (w && m && (A = t(Z + A, Z.length ? p - R.length : 1 / 0), Z = ""), g) {
        case "<":
          A = z + A + R + Z;
          break;
        case "=":
          A = z + Z + A + R;
          break;
        case "^":
          A = Z.slice(0, Y = Z.length >> 1) + z + A + R + Z.slice(Y);
          break;
        default:
          A = Z + z + A + R;
          break;
      }
      return i(A);
    }
    return j.toString = function() {
      return c + "";
    }, j;
  }
  function v(c, d) {
    var g = s((c = Xn(c), c.type = "f", c)), h = Math.max(-8, Math.min(8, Math.floor(jt(d) / 3))) * 3, b = Math.pow(10, -h), m = Ya[8 + h / 3];
    return function(p) {
      return g(b * p) + m;
    };
  }
  return {
    format: s,
    formatPrefix: v
  };
}
var Mn, ze, Wi;
Ro({
  thousands: ",",
  grouping: [3],
  currency: ["$", ""]
});
function Ro(e) {
  return Mn = Po(e), ze = Mn.format, Wi = Mn.formatPrefix, Mn;
}
function Io(e) {
  return Math.max(0, -jt(Math.abs(e)));
}
function Do(e, t) {
  return Math.max(0, Math.max(-8, Math.min(8, Math.floor(jt(t) / 3))) * 3 - jt(Math.abs(e)));
}
function Oo(e, t) {
  return e = Math.abs(e), t = Math.abs(t) - e, Math.max(0, jt(t) - jt(e)) + 1;
}
function Bo(e, t, n, r) {
  var a = Of(e, t, n), i;
  switch (r = Xn(r ?? ",f"), r.type) {
    case "s": {
      var f = Math.max(Math.abs(e), Math.abs(t));
      return r.precision == null && !isNaN(i = Do(a, f)) && (r.precision = i), Wi(r, f);
    }
    case "":
    case "e":
    case "g":
    case "p":
    case "r": {
      r.precision == null && !isNaN(i = Oo(a, Math.max(Math.abs(e), Math.abs(t)))) && (r.precision = i - (r.type === "e"));
      break;
    }
    case "f":
    case "%": {
      r.precision == null && !isNaN(i = Io(a)) && (r.precision = i - (r.type === "%") * 2);
      break;
    }
  }
  return ze(r);
}
function ta(e) {
  var t = e.domain;
  return e.ticks = function(n) {
    var r = t();
    return Df(r[0], r[r.length - 1], n ?? 10);
  }, e.tickFormat = function(n, r) {
    var a = t();
    return Bo(a[0], a[a.length - 1], n ?? 10, r);
  }, e.nice = function(n) {
    n == null && (n = 10);
    var r = t(), a = 0, i = r.length - 1, f = r[a], o = r[i], u, s, v = 10;
    for (o < f && (s = f, f = o, o = s, s = a, a = i, i = s); v-- > 0; ) {
      if (s = Fr(f, o, n), s === u)
        return r[a] = f, r[i] = o, t(r);
      if (s > 0)
        f = Math.floor(f / s) * s, o = Math.ceil(o / s) * s;
      else if (s < 0)
        f = Math.ceil(f * s) / s, o = Math.floor(o * s) / s;
      else
        break;
      u = s;
    }
    return e;
  }, e;
}
function Yt() {
  var e = So();
  return e.copy = function() {
    return To(e, Yt());
  }, Zr.apply(e, arguments), ta(e);
}
function Ho() {
  var e = 0, t = 1, n, r, a, i, f = nt, o = !1, u;
  function s(c) {
    return c == null || isNaN(c = +c) ? u : f(a === 0 ? 0.5 : (c = (i(c) - n) * a, o ? Math.max(0, Math.min(1, c)) : c));
  }
  s.domain = function(c) {
    return arguments.length ? ([e, t] = c, n = i(e = +e), r = i(t = +t), a = n === r ? 0 : 1 / (r - n), s) : [e, t];
  }, s.clamp = function(c) {
    return arguments.length ? (o = !!c, s) : o;
  }, s.interpolator = function(c) {
    return arguments.length ? (f = c, s) : f;
  };
  function v(c) {
    return function(d) {
      var g, h;
      return arguments.length ? ([g, h] = d, f = c(g, h), s) : [f(0), f(1)];
    };
  }
  return s.range = v(Zt), s.rangeRound = v($r), s.unknown = function(c) {
    return arguments.length ? (u = c, s) : u;
  }, function(c) {
    return i = c, n = c(e), r = c(t), a = n === r ? 0 : 1 / (r - n), s;
  };
}
function ji(e, t) {
  return t.domain(e.domain()).interpolator(e.interpolator()).clamp(e.clamp()).unknown(e.unknown());
}
function pn() {
  var e = ta(Ho()(nt));
  return e.copy = function() {
    return ji(e, pn());
  }, Ri.apply(e, arguments);
}
function Wo() {
  var e = 0, t = 0.5, n = 1, r = 1, a, i, f, o, u, s = nt, v, c = !1, d;
  function g(b) {
    return isNaN(b = +b) ? d : (b = 0.5 + ((b = +v(b)) - i) * (r * b < r * i ? o : u), s(c ? Math.max(0, Math.min(1, b)) : b));
  }
  g.domain = function(b) {
    return arguments.length ? ([e, t, n] = b, a = v(e = +e), i = v(t = +t), f = v(n = +n), o = a === i ? 0 : 0.5 / (i - a), u = i === f ? 0 : 0.5 / (f - i), r = i < a ? -1 : 1, g) : [e, t, n];
  }, g.clamp = function(b) {
    return arguments.length ? (c = !!b, g) : c;
  }, g.interpolator = function(b) {
    return arguments.length ? (s = b, g) : s;
  };
  function h(b) {
    return function(m) {
      var p, w, y;
      return arguments.length ? ([p, w, y] = m, s = po(b, [p, w, y]), g) : [s(0), s(0.5), s(1)];
    };
  }
  return g.range = h(Zt), g.rangeRound = h($r), g.unknown = function(b) {
    return arguments.length ? (d = b, g) : d;
  }, function(b) {
    return v = b, a = b(e), i = b(t), f = b(n), o = a === i ? 0 : 0.5 / (i - a), u = i === f ? 0 : 0.5 / (f - i), r = i < a ? -1 : 1, g;
  };
}
function na() {
  var e = ta(Wo()(nt));
  return e.copy = function() {
    return ji(e, na());
  }, Ri.apply(e, arguments);
}
function jo(e, t, n) {
  let r = 0;
  for (; r <= e; ) {
    const a = Math.floor((r + e) / 2), i = t(a);
    if (i === n)
      return a;
    i < n ? r = a + 1 : e = a - 1;
  }
  return e;
}
function Va(e, t, n) {
  const r = e.measureText(t).width, a = "…", i = e.measureText(a).width;
  if (r <= n || r <= i)
    return t;
  const f = jo(
    t.length - 1,
    (o) => e.measureText(t.substring(0, o)).width,
    n - i
  );
  return t.substring(0, f) + a;
}
function Yi(e, t, n, r, a, i, f, o) {
  const u = Math.min(...n.range()), s = Math.max(...n.range()), v = (u + s) / 2, c = e === "left", d = e === "right", g = e === "top";
  if (c || d) {
    const h = c ? -r : i;
    if (t === "top") {
      const b = u - a, m = 0.71 * o;
      return {
        textAlign: c ? "start" : "end",
        x: h,
        y: b + m,
        rotate: 0
      };
    } else {
      if (t === "bottom")
        return {
          textAlign: c ? "start" : "end",
          x: h,
          y: s + f,
          rotate: 0
        };
      {
        const b = c ? 1 : -1, m = h + b * o / 2, p = v, w = b * 0.71 * o;
        return {
          textAlign: "center",
          x: m + w,
          y: p,
          rotate: c ? -90 : 90
        };
      }
    }
  } else {
    const h = g ? -a + o / 2 : f - o / 2, b = g ? o * 0.71 : 0;
    return t === "left" ? {
      textAlign: "start",
      x: u - r,
      y: h + b,
      rotate: 0
    } : t === "right" ? {
      textAlign: "end",
      x: s + i,
      y: h + b,
      rotate: 0
    } : {
      textAlign: "center",
      x: v,
      y: h + b,
      rotate: 0
    };
  }
}
function Xa(e, t) {
  return e === "left" ? "end" : e === "right" ? "start" : t === 0 ? "center" : t > 0 && e === "top" ? "end" : t < 0 && e === "top" || t > 0 && e === "bottom" ? "start" : "end";
}
const pr = {
  start: "start",
  center: "middle",
  end: "end"
};
function Ga(e, t, n, {
  translateX: r = 0,
  translateY: a = 0,
  marginLeft: i = 0,
  marginTop: f = 0,
  marginRight: o = 0,
  marginBottom: u = 0,
  tickLineSize: s = 6,
  tickLabelFontSize: v = 10,
  tickLabelFontFamily: c = "ui-sans-serif, system-ui, sans-serif",
  tickLabelAngle: d = 0,
  tickPadding: g = 3,
  tickFormat: h,
  numTicks: b,
  tickValues: m,
  showTickMarks: p = !0,
  showTickLabels: w = !0,
  maxTickLabelSpace: y,
  tickLineColor: M = "black",
  tickLabelColor: q = "black",
  showDomain: E = !1,
  domainColor: O = "black",
  title: L = "",
  titleFontSize: C = 12,
  titleFontFamily: j = "ui-sans-serif, system-ui, sans-serif",
  titleFontWeight: A = 400,
  titleAnchor: z = "center",
  titleOffsetX: R = 0,
  titleOffsetY: I = 0,
  titleColor: B = "black"
} = {}) {
  const D = t === "top" || t === "left" ? -1 : 1, X = Math.max(s, 0) + g, Y = n.bandwidth ? n.bandwidth() / 2 : 0, Z = Yi(
    t,
    z,
    n,
    i,
    f,
    o,
    u,
    C
  ), se = m ?? (n.ticks ? n.ticks(b) : n.domain()), W = h ?? (n.tickFormat ? n.tickFormat(b) : (P) => String(P).toString());
  e.save(), e.translate(r, a), e.font = `${v}px ${c}`, e.globalAlpha = 1, e.fillStyle = q, e.strokeStyle = M, t === "left" || t === "right" ? (se.forEach((P) => {
    const N = (n(P) ?? 0) + Y;
    if (p && (e.beginPath(), e.moveTo(s * D, N), e.lineTo(0, N), e.stroke()), w) {
      e.save(), e.translate(X * D, N), e.rotate(d * Math.PI / 180), e.textBaseline = "middle", e.textAlign = t === "left" ? "end" : "start";
      const G = y ? Va(e, W(P), y) : W(P);
      e.fillText(G, 0, 0), e.restore();
    }
  }), e.strokeStyle = O, e.lineWidth = 1, E && (e.beginPath(), e.moveTo(0, n.range()[0]), e.lineTo(0, n.range()[1]), e.stroke())) : (se.forEach((P) => {
    const N = (n(P) ?? 0) + Y;
    if (p && (e.beginPath(), e.moveTo(N, s * D), e.lineTo(N, 0), e.stroke()), w) {
      e.save(), e.translate(N, X * D), e.rotate(d * Math.PI / 180), e.textBaseline = t === "top" ? "bottom" : "top", e.textAlign = "center";
      const G = y ? Va(e, W(P), y) : W(P);
      e.fillText(G, 0, 0), e.restore();
    }
  }), e.strokeStyle = O, e.lineWidth = 1, E && (e.beginPath(), e.moveTo(n.range()[0], 0), e.lineTo(n.range()[1], 0), e.stroke())), L && (e.fillStyle = B, e.textAlign = Z.textAlign, e.textBaseline = "alphabetic", e.font = `${A} ${C}px ${j}`, e.translate(Z.x, Z.y), e.rotate(Z.rotate * Math.PI / 180), e.fillText(L, R, I)), e.restore();
}
var Yo = /* @__PURE__ */ ke("<text><tspan></tspan> <title> </title></text>");
function Ua(e, t) {
  pe(t, !0);
  let n = S(t, "angle", 3, 0), r = S(t, "fontSize", 3, 10), a = S(t, "fontFamily", 3, "ui-sans-serif, system-ui, sans-serif"), i = S(t, "fontColor", 3, "black"), f = S(t, "fontWeight", 3, 400), o = S(t, "dominantBaseline", 3, "auto"), u = S(t, "textAnchor", 3, "start"), s = /* @__PURE__ */ ee(void 0);
  function v(b, m, p) {
    p.textContent = b;
    let w = b;
    for (; w.length > 0 && p.getComputedTextLength() > m; )
      w = w.slice(0, -1), p.textContent = w + "…";
  }
  yr(() => {
    l(s) && v(t.label, t.width, l(s));
  });
  var c = Yo(), d = _(c);
  Ur(d, (b) => V(s, b), () => l(s));
  var g = k(d, 2), h = _(g);
  $(() => {
    T(c, "fill", i()), T(c, "font-size", r()), T(c, "font-family", a()), T(c, "font-weight", f()), T(c, "transform", `translate(${t.x ?? ""} ${t.y ?? ""}) rotate(${n() ?? ""})`), T(d, "dominant-baseline", o()), T(d, "text-anchor", u()), de(h, t.label);
  }), H(e, c), we();
}
var Vo = /* @__PURE__ */ ke("<line></line>"), Xo = /* @__PURE__ */ ke("<text> </text>"), Go = /* @__PURE__ */ ke("<g><!><!></g>"), Uo = /* @__PURE__ */ ke("<line></line>"), Ko = /* @__PURE__ */ ke("<g></g><!>", 1), Zo = /* @__PURE__ */ ke("<line></line>"), Qo = /* @__PURE__ */ ke("<text> </text>"), Jo = /* @__PURE__ */ ke("<g><!><!></g>"), $o = /* @__PURE__ */ ke("<line></line>"), es = /* @__PURE__ */ ke("<g></g><!>", 1), ts = /* @__PURE__ */ ke("<text> </text>"), ns = /* @__PURE__ */ ke("<g><!><!></g>");
function Vt(e, t) {
  pe(t, !0);
  let n = S(t, "translateX", 3, 0), r = S(t, "translateY", 3, 0), a = S(t, "marginLeft", 3, 0), i = S(t, "marginTop", 3, 0), f = S(t, "marginRight", 3, 0), o = S(t, "marginBottom", 3, 0), u = S(t, "tickLineSize", 3, 6), s = S(t, "tickLabelFontSize", 3, 10), v = S(t, "tickLabelFontFamily", 3, "ui-sans-serif, system-ui, sans-serif"), c = S(t, "tickLabelAngle", 3, 0), d = S(t, "tickPadding", 3, 3), g = S(t, "showTickMarks", 3, !0), h = S(t, "showTickLabels", 3, !0), b = S(t, "tickLineColor", 3, "black"), m = S(t, "tickLabelColor", 3, "black"), p = S(t, "showDomain", 3, !1), w = S(t, "domainColor", 3, "black"), y = S(t, "title", 3, ""), M = S(t, "titleFontSize", 3, 12), q = S(t, "titleFontFamily", 3, "ui-sans-serif, system-ui, sans-serif"), E = S(t, "titleFontWeight", 3, 400), O = S(t, "titleAnchor", 3, "center"), L = S(t, "titleOffsetX", 3, 0), C = S(t, "titleOffsetY", 3, 0), j = S(t, "titleColor", 3, "black");
  const A = /* @__PURE__ */ x(() => t.orientation === "top" || t.orientation === "left" ? -1 : 1), z = /* @__PURE__ */ x(() => Math.max(u(), 0) + d()), R = /* @__PURE__ */ x(() => t.scale.bandwidth ? t.scale.bandwidth() / 2 : 0), I = /* @__PURE__ */ x(() => Yi(t.orientation, O(), t.scale, a(), i(), f(), o(), M()));
  let B = /* @__PURE__ */ x(() => t.tickValues ?? (t.scale.ticks ? t.scale.ticks(t.numTicks) : t.scale.domain())), D = /* @__PURE__ */ x(() => t.tickFormat ?? (t.scale.tickFormat ? t.scale.tickFormat(t.numTicks) : (N) => String(N).toString()));
  var X = ns(), Y = _(X);
  {
    var Z = (N) => {
      var G = Ko(), fe = Ne(G);
      Ae(fe, 21, () => l(B), Me, (U, F) => {
        var te = Go();
        const ue = /* @__PURE__ */ x(() => (t.scale(l(F)) ?? 0) + l(R));
        var Te = _(te);
        {
          var K = (J) => {
            var ae = Vo();
            T(ae, "y1", 0), T(ae, "x2", 0), T(ae, "y2", 0), $(() => {
              T(ae, "x1", u() * l(A)), T(ae, "stroke", b());
            }), H(J, ae);
          };
          le(Te, (J) => {
            g() && J(K);
          });
        }
        var ye = k(Te);
        {
          var Q = (J) => {
            var ae = St();
            const xe = /* @__PURE__ */ x(() => pr[Xa(t.orientation, c())]);
            var Oe = Ne(ae);
            {
              var Ue = (be) => {
                const _e = /* @__PURE__ */ x(() => l(D)(l(F))), $e = /* @__PURE__ */ x(() => l(z) * l(A));
                Ua(be, {
                  get label() {
                    return l(_e);
                  },
                  get width() {
                    return t.maxTickLabelSpace;
                  },
                  get x() {
                    return l($e);
                  },
                  y: 0,
                  dominantBaseline: "middle",
                  get textAnchor() {
                    return l(xe);
                  },
                  get fontSize() {
                    return s();
                  },
                  get fontColor() {
                    return m();
                  },
                  get fontFamily() {
                    return v();
                  },
                  get angle() {
                    return c();
                  }
                });
              }, Ke = (be) => {
                var _e = Xo();
                T(_e, "dominant-baseline", "middle");
                var $e = _(_e);
                $(
                  (Ce) => {
                    T(_e, "text-anchor", l(xe)), T(_e, "transform", `translate(${l(z) * l(A)} 0) rotate(${c() ?? ""})`), T(_e, "fill", m()), T(_e, "font-size", s()), T(_e, "font-family", v()), de($e, Ce);
                  },
                  [() => l(D)(l(F))]
                ), H(be, _e);
              };
              le(Oe, (be) => {
                t.maxTickLabelSpace ? be(Ue) : be(Ke, !1);
              });
            }
            H(J, ae);
          };
          le(ye, (J) => {
            h() && J(Q);
          });
        }
        $(() => T(te, "transform", `translate(0,${l(ue) ?? ""})`)), H(U, te);
      });
      var ne = k(fe);
      {
        var re = (U) => {
          var F = Uo();
          T(F, "x1", 0), T(F, "x2", 0), T(F, "stroke-width", 1), $(
            (te, ue) => {
              T(F, "y1", te), T(F, "y2", ue), T(F, "stroke", w());
            },
            [
              () => t.scale.range()[0],
              () => t.scale.range()[1]
            ]
          ), H(U, F);
        };
        le(ne, (U) => {
          p() && U(re);
        });
      }
      H(N, G);
    }, se = (N) => {
      var G = es(), fe = Ne(G);
      Ae(fe, 21, () => l(B), Me, (U, F) => {
        var te = Jo();
        const ue = /* @__PURE__ */ x(() => (t.scale(l(F)) ?? 0) + l(R));
        var Te = _(te);
        {
          var K = (J) => {
            var ae = Zo();
            T(ae, "x1", 0), T(ae, "x2", 0), T(ae, "y2", 0), $(() => {
              T(ae, "y1", u() * l(A)), T(ae, "stroke", b());
            }), H(J, ae);
          };
          le(Te, (J) => {
            g() && J(K);
          });
        }
        var ye = k(Te);
        {
          var Q = (J) => {
            var ae = St();
            const xe = /* @__PURE__ */ x(() => pr[Xa(t.orientation, c())]);
            var Oe = Ne(ae);
            {
              var Ue = (be) => {
                const _e = /* @__PURE__ */ x(() => l(D)(l(F))), $e = /* @__PURE__ */ x(() => l(z) * l(A)), Ce = /* @__PURE__ */ x(() => t.orientation === "top" ? "text-top" : "hanging");
                Ua(be, {
                  get label() {
                    return l(_e);
                  },
                  get width() {
                    return t.maxTickLabelSpace;
                  },
                  x: 0,
                  get y() {
                    return l($e);
                  },
                  get dominantBaseline() {
                    return l(Ce);
                  },
                  get textAnchor() {
                    return l(xe);
                  },
                  get fontSize() {
                    return s();
                  },
                  get fontFamily() {
                    return v();
                  },
                  get fontColor() {
                    return m();
                  },
                  get angle() {
                    return c();
                  }
                });
              }, Ke = (be) => {
                var _e = Qo(), $e = _(_e);
                $(
                  (Ce) => {
                    T(_e, "dominant-baseline", t.orientation === "top" ? "text-top" : "hanging"), T(_e, "text-anchor", l(xe)), T(_e, "transform", `translate(0 ${l(z) * l(A)}) rotate(${c() ?? ""})`), T(_e, "font-size", s()), T(_e, "font-family", v()), T(_e, "fill", m()), de($e, Ce);
                  },
                  [() => l(D)(l(F))]
                ), H(be, _e);
              };
              le(Oe, (be) => {
                t.maxTickLabelSpace ? be(Ue) : be(Ke, !1);
              });
            }
            H(J, ae);
          };
          le(ye, (J) => {
            h() && J(Q);
          });
        }
        $(() => T(te, "transform", `translate(${l(ue) ?? ""},0)`)), H(U, te);
      });
      var ne = k(fe);
      {
        var re = (U) => {
          var F = $o();
          T(F, "y1", 0), T(F, "y2", 0), T(F, "stroke-width", 1), $(
            (te, ue) => {
              T(F, "x1", te), T(F, "x2", ue), T(F, "stroke", w());
            },
            [
              () => t.scale.range()[0],
              () => t.scale.range()[1]
            ]
          ), H(U, F);
        };
        le(ne, (U) => {
          p() && U(re);
        });
      }
      H(N, G);
    };
    le(Y, (N) => {
      t.orientation === "left" || t.orientation == "right" ? N(Z) : N(se, !1);
    });
  }
  var W = k(Y);
  {
    var P = (N) => {
      var G = ts(), fe = _(G);
      $(() => {
        T(G, "fill", j()), T(G, "font-size", M()), T(G, "font-family", q()), T(G, "font-weight", E()), T(G, "text-anchor", pr[l(I).textAlign]), T(G, "transform", `translate(${l(I).x ?? ""} ${l(I).y ?? ""}) rotate(${l(I).rotate ?? ""}) translate(${L() ?? ""} ${C() ?? ""})`), de(fe, y());
      }), H(N, G);
    };
    le(W, (N) => {
      y() && N(P);
    });
  }
  $(() => T(X, "transform", `translate(${n() ?? ""},${r() ?? ""})`)), H(e, X), we();
}
function wt(e) {
  for (var t = e.length / 6 | 0, n = new Array(t), r = 0; r < t; ) n[r] = "#" + e.slice(r * 6, ++r * 6);
  return n;
}
const fr = (e) => uo(e[e.length - 1]);
var rs = new Array(3).concat(
  "af8dc3f7f7f77fbf7b",
  "7b3294c2a5cfa6dba0008837",
  "7b3294c2a5cff7f7f7a6dba0008837",
  "762a83af8dc3e7d4e8d9f0d37fbf7b1b7837",
  "762a83af8dc3e7d4e8f7f7f7d9f0d37fbf7b1b7837",
  "762a839970abc2a5cfe7d4e8d9f0d3a6dba05aae611b7837",
  "762a839970abc2a5cfe7d4e8f7f7f7d9f0d3a6dba05aae611b7837",
  "40004b762a839970abc2a5cfe7d4e8d9f0d3a6dba05aae611b783700441b",
  "40004b762a839970abc2a5cfe7d4e8f7f7f7d9f0d3a6dba05aae611b783700441b"
).map(wt);
const as = fr(rs);
var is = new Array(3).concat(
  "e9a3c9f7f7f7a1d76a",
  "d01c8bf1b6dab8e1864dac26",
  "d01c8bf1b6daf7f7f7b8e1864dac26",
  "c51b7de9a3c9fde0efe6f5d0a1d76a4d9221",
  "c51b7de9a3c9fde0eff7f7f7e6f5d0a1d76a4d9221",
  "c51b7dde77aef1b6dafde0efe6f5d0b8e1867fbc414d9221",
  "c51b7dde77aef1b6dafde0eff7f7f7e6f5d0b8e1867fbc414d9221",
  "8e0152c51b7dde77aef1b6dafde0efe6f5d0b8e1867fbc414d9221276419",
  "8e0152c51b7dde77aef1b6dafde0eff7f7f7e6f5d0b8e1867fbc414d9221276419"
).map(wt);
const ls = fr(is);
var fs = new Array(3).concat(
  "deebf79ecae13182bd",
  "eff3ffbdd7e76baed62171b5",
  "eff3ffbdd7e76baed63182bd08519c",
  "eff3ffc6dbef9ecae16baed63182bd08519c",
  "eff3ffc6dbef9ecae16baed64292c62171b5084594",
  "f7fbffdeebf7c6dbef9ecae16baed64292c62171b5084594",
  "f7fbffdeebf7c6dbef9ecae16baed64292c62171b508519c08306b"
).map(wt);
const os = fr(fs);
var ss = new Array(3).concat(
  "fee6cefdae6be6550d",
  "feeddefdbe85fd8d3cd94701",
  "feeddefdbe85fd8d3ce6550da63603",
  "feeddefdd0a2fdae6bfd8d3ce6550da63603",
  "feeddefdd0a2fdae6bfd8d3cf16913d948018c2d04",
  "fff5ebfee6cefdd0a2fdae6bfd8d3cf16913d948018c2d04",
  "fff5ebfee6cefdd0a2fdae6bfd8d3cf16913d94801a636037f2704"
).map(wt);
const us = fr(ss);
function or(e) {
  var t = e.length;
  return function(n) {
    return e[Math.max(0, Math.min(t - 1, Math.floor(n * t)))];
  };
}
or(wt("44015444025645045745055946075a46085c460a5d460b5e470d60470e6147106347116447136548146748166848176948186a481a6c481b6d481c6e481d6f481f70482071482173482374482475482576482677482878482979472a7a472c7a472d7b472e7c472f7d46307e46327e46337f463480453581453781453882443983443a83443b84433d84433e85423f854240864241864142874144874045884046883f47883f48893e49893e4a893e4c8a3d4d8a3d4e8a3c4f8a3c508b3b518b3b528b3a538b3a548c39558c39568c38588c38598c375a8c375b8d365c8d365d8d355e8d355f8d34608d34618d33628d33638d32648e32658e31668e31678e31688e30698e306a8e2f6b8e2f6c8e2e6d8e2e6e8e2e6f8e2d708e2d718e2c718e2c728e2c738e2b748e2b758e2a768e2a778e2a788e29798e297a8e297b8e287c8e287d8e277e8e277f8e27808e26818e26828e26828e25838e25848e25858e24868e24878e23888e23898e238a8d228b8d228c8d228d8d218e8d218f8d21908d21918c20928c20928c20938c1f948c1f958b1f968b1f978b1f988b1f998a1f9a8a1e9b8a1e9c891e9d891f9e891f9f881fa0881fa1881fa1871fa28720a38620a48621a58521a68522a78522a88423a98324aa8325ab8225ac8226ad8127ad8128ae8029af7f2ab07f2cb17e2db27d2eb37c2fb47c31b57b32b67a34b67935b77937b87838b9773aba763bbb753dbc743fbc7340bd7242be7144bf7046c06f48c16e4ac16d4cc26c4ec36b50c46a52c56954c56856c66758c7655ac8645cc8635ec96260ca6063cb5f65cb5e67cc5c69cd5b6ccd5a6ece5870cf5773d05675d05477d1537ad1517cd2507fd34e81d34d84d44b86d54989d5488bd6468ed64590d74393d74195d84098d83e9bd93c9dd93ba0da39a2da37a5db36a8db34aadc32addc30b0dd2fb2dd2db5de2bb8de29bade28bddf26c0df25c2df23c5e021c8e020cae11fcde11dd0e11cd2e21bd5e21ad8e219dae319dde318dfe318e2e418e5e419e7e419eae51aece51befe51cf1e51df4e61ef6e620f8e621fbe723fde725"));
or(wt("00000401000501010601010802010902020b02020d03030f03031204041405041606051806051a07061c08071e0907200a08220b09240c09260d0a290e0b2b100b2d110c2f120d31130d34140e36150e38160f3b180f3d19103f1a10421c10441d11471e114920114b21114e22115024125325125527125829115a2a115c2c115f2d11612f116331116533106734106936106b38106c390f6e3b0f703d0f713f0f72400f74420f75440f764510774710784910784a10794c117a4e117b4f127b51127c52137c54137d56147d57157e59157e5a167e5c167f5d177f5f187f601880621980641a80651a80671b80681c816a1c816b1d816d1d816e1e81701f81721f817320817521817621817822817922827b23827c23827e24828025828125818326818426818627818827818928818b29818c29818e2a81902a81912b81932b80942c80962c80982d80992d809b2e7f9c2e7f9e2f7fa02f7fa1307ea3307ea5317ea6317da8327daa337dab337cad347cae347bb0357bb2357bb3367ab5367ab73779b83779ba3878bc3978bd3977bf3a77c03a76c23b75c43c75c53c74c73d73c83e73ca3e72cc3f71cd4071cf4070d0416fd2426fd3436ed5446dd6456cd8456cd9466bdb476adc4869de4968df4a68e04c67e24d66e34e65e44f64e55064e75263e85362e95462ea5661eb5760ec5860ed5a5fee5b5eef5d5ef05f5ef1605df2625df2645cf3655cf4675cf4695cf56b5cf66c5cf66e5cf7705cf7725cf8745cf8765cf9785df9795df97b5dfa7d5efa7f5efa815ffb835ffb8560fb8761fc8961fc8a62fc8c63fc8e64fc9065fd9266fd9467fd9668fd9869fd9a6afd9b6bfe9d6cfe9f6dfea16efea36ffea571fea772fea973feaa74feac76feae77feb078feb27afeb47bfeb67cfeb77efeb97ffebb81febd82febf84fec185fec287fec488fec68afec88cfeca8dfecc8ffecd90fecf92fed194fed395fed597fed799fed89afdda9cfddc9efddea0fde0a1fde2a3fde3a5fde5a7fde7a9fde9aafdebacfcecaefceeb0fcf0b2fcf2b4fcf4b6fcf6b8fcf7b9fcf9bbfcfbbdfcfdbf"));
or(wt("00000401000501010601010802010a02020c02020e03021004031204031405041706041907051b08051d09061f0a07220b07240c08260d08290e092b10092d110a30120a32140b34150b37160b39180c3c190c3e1b0c411c0c431e0c451f0c48210c4a230c4c240c4f260c51280b53290b552b0b572d0b592f0a5b310a5c320a5e340a5f3609613809623909633b09643d09653e0966400a67420a68440a68450a69470b6a490b6a4a0c6b4c0c6b4d0d6c4f0d6c510e6c520e6d540f6d550f6d57106e59106e5a116e5c126e5d126e5f136e61136e62146e64156e65156e67166e69166e6a176e6c186e6d186e6f196e71196e721a6e741a6e751b6e771c6d781c6d7a1d6d7c1d6d7d1e6d7f1e6c801f6c82206c84206b85216b87216b88226a8a226a8c23698d23698f24699025689225689326679526679727669827669a28659b29649d29649f2a63a02a63a22b62a32c61a52c60a62d60a82e5fa92e5eab2f5ead305dae305cb0315bb1325ab3325ab43359b63458b73557b93556ba3655bc3754bd3853bf3952c03a51c13a50c33b4fc43c4ec63d4dc73e4cc83f4bca404acb4149cc4248ce4347cf4446d04545d24644d34743d44842d54a41d74b3fd84c3ed94d3dda4e3cdb503bdd513ade5238df5337e05536e15635e25734e35933e45a31e55c30e65d2fe75e2ee8602de9612bea632aeb6429eb6628ec6726ed6925ee6a24ef6c23ef6e21f06f20f1711ff1731df2741cf3761bf37819f47918f57b17f57d15f67e14f68013f78212f78410f8850ff8870ef8890cf98b0bf98c0af98e09fa9008fa9207fa9407fb9606fb9706fb9906fb9b06fb9d07fc9f07fca108fca309fca50afca60cfca80dfcaa0ffcac11fcae12fcb014fcb216fcb418fbb61afbb81dfbba1ffbbc21fbbe23fac026fac228fac42afac62df9c72ff9c932f9cb35f8cd37f8cf3af7d13df7d340f6d543f6d746f5d949f5db4cf4dd4ff4df53f4e156f3e35af3e55df2e661f2e865f2ea69f1ec6df1ed71f1ef75f1f179f2f27df2f482f3f586f3f68af4f88ef5f992f6fa96f8fb9af9fc9dfafda1fcffa4"));
var Vi = or(wt("0d088710078813078916078a19068c1b068d1d068e20068f2206902406912605912805922a05932c05942e05952f059631059733059735049837049938049a3a049a3c049b3e049c3f049c41049d43039e44039e46039f48039f4903a04b03a14c02a14e02a25002a25102a35302a35502a45601a45801a45901a55b01a55c01a65e01a66001a66100a76300a76400a76600a76700a86900a86a00a86c00a86e00a86f00a87100a87201a87401a87501a87701a87801a87a02a87b02a87d03a87e03a88004a88104a78305a78405a78606a68707a68808a68a09a58b0aa58d0ba58e0ca48f0da4910ea3920fa39410a29511a19613a19814a099159f9a169f9c179e9d189d9e199da01a9ca11b9ba21d9aa31e9aa51f99a62098a72197a82296aa2395ab2494ac2694ad2793ae2892b02991b12a90b22b8fb32c8eb42e8db52f8cb6308bb7318ab83289ba3388bb3488bc3587bd3786be3885bf3984c03a83c13b82c23c81c33d80c43e7fc5407ec6417dc7427cc8437bc9447aca457acb4679cc4778cc4977cd4a76ce4b75cf4c74d04d73d14e72d24f71d35171d45270d5536fd5546ed6556dd7566cd8576bd9586ada5a6ada5b69db5c68dc5d67dd5e66de5f65de6164df6263e06363e16462e26561e26660e3685fe4695ee56a5de56b5de66c5ce76e5be76f5ae87059e97158e97257ea7457eb7556eb7655ec7754ed7953ed7a52ee7b51ef7c51ef7e50f07f4ff0804ef1814df1834cf2844bf3854bf3874af48849f48948f58b47f58c46f68d45f68f44f79044f79143f79342f89441f89540f9973ff9983ef99a3efa9b3dfa9c3cfa9e3bfb9f3afba139fba238fca338fca537fca636fca835fca934fdab33fdac33fdae32fdaf31fdb130fdb22ffdb42ffdb52efeb72dfeb82cfeba2cfebb2bfebd2afebe2afec029fdc229fdc328fdc527fdc627fdc827fdca26fdcb26fccd25fcce25fcd025fcd225fbd324fbd524fbd724fad824fada24f9dc24f9dd25f8df25f8e125f7e225f7e425f6e626f6e826f5e926f5eb27f4ed27f3ee27f3f027f2f227f1f426f1f525f0f724f0f921"));
function cs(e, t, n, r) {
  const a = window.devicePixelRatio || 1;
  e.width = n * a, e.height = r * a, e.style.width = `${n}px`, e.style.height = `${r}px`, t.scale(a, a);
}
function ra(e, t, n) {
  const r = Math.min(e / n, t);
  return {
    width: n * r,
    height: r
  };
}
function Xi(e, t, n, r, a, i, f) {
  const o = e - a - f, u = t - r - i, s = ra(o, u, n);
  return {
    width: s.width + a + f,
    height: s.height + r + i
  };
}
function Pr(e) {
  return e >= 1e-3 && e <= 1 || e >= -1 && e <= 1e-3 ? ze(".3~f")(e) : ze("~s")(e);
}
function Gn(e) {
  return e < 1e-5 ? ze(".1~p")(e) : e < 1e-3 ? ze(".2~p")(e) : ze(".3~p")(e);
}
const Ka = ze(".3~f"), yt = ze(".2~f"), Za = ze(".2~f"), ds = ze(".3~f"), dn = ze(".2~%"), Qa = (e) => ze(".2~f")(e * 100), It = ze(",d"), Ja = ze(".3~s");
var vs = /* @__PURE__ */ oe("<canvas></canvas>");
function aa(e, t) {
  pe(t, !0);
  let n = S(t, "orientation", 3, "horizontal"), r = S(t, "marginTop", 3, 10), a = S(t, "marginRight", 3, 10), i = S(t, "marginBottom", 3, 10), f = S(t, "marginLeft", 3, 10), o = S(t, "title", 3, ""), u = S(t, "tickLabelFontSize", 3, 10), s = S(t, "titleFontSize", 3, 12), v = /* @__PURE__ */ ee(null), c = /* @__PURE__ */ x(() => l(v) ? l(v).getContext("2d", { alpha: !1 }) : null);
  function d(b, m, p, w, y, M, q, E) {
    const O = Yt().domain([
      m.domain()[0],
      m.domain()[m.domain().length - 1]
    ]).range([E, p - M]), L = O.range()[1] - O.range()[0], C = w - y - q, j = m.domain().length, A = O.ticks(Math.max(Math.min(L / 50, 10), j));
    b.fillStyle = "white", b.fillRect(0, 0, p, w);
    for (let z = 0; z < L; z++)
      b.fillStyle = m.interpolator()(z / L), b.fillRect(z + E, y, 1, C);
    Ga(b, "bottom", O, {
      translateY: w - q,
      tickValues: A,
      tickFormat: t.tickFormat,
      title: o(),
      titleAnchor: "left",
      titleOffsetX: E,
      titleOffsetY: -q - C,
      marginTop: y,
      marginRight: M,
      marginBottom: q,
      marginLeft: E,
      tickLabelFontSize: u(),
      titleFontSize: s()
    });
  }
  function g(b, m, p, w, y, M, q, E) {
    const O = Yt().domain([
      m.domain()[0],
      m.domain()[m.domain().length - 1]
    ]).range([w - q, y]), L = p - E - M, C = O.range()[0] - O.range()[1], j = O.ticks();
    b.fillStyle = "white", b.fillRect(0, 0, p, w);
    for (let A = 0; A < C; A++)
      b.fillStyle = m.interpolator()(1 - A / C), b.fillRect(E, A + y, L, 1);
    Ga(b, "right", O, {
      translateX: p - M,
      tickValues: j,
      tickFormat: t.tickFormat,
      title: o(),
      marginTop: y,
      marginRight: M,
      marginBottom: q,
      marginLeft: E,
      tickLabelFontSize: u(),
      titleFontSize: s()
    });
  }
  yr(() => {
    l(v) && l(c) && cs(l(v), l(c), t.width, t.height);
  }), yr(() => {
    l(c) && (n() === "horizontal" ? d(l(c), t.color, t.width, t.height, r(), a(), i(), f()) : g(l(c), t.color, t.width, t.height, r(), a(), i(), f()));
  });
  var h = vs();
  Ur(h, (b) => V(v, b), () => l(v)), H(e, h), we();
}
var Ht;
class gs {
  constructor(t) {
    qe(this, Ht);
    Be(this, Ht, /* @__PURE__ */ ee(et(t)));
  }
  get value() {
    return l(ie(this, Ht));
  }
  set value(t) {
    V(ie(this, Ht), t, !0);
  }
}
Ht = new WeakMap();
let ia;
function hs(e) {
  ia = new gs(e);
}
var bs = /* @__PURE__ */ oe('<div class="sae-tooltip svelte-medmur"><!></div>');
function sr(e, t) {
  pe(t, !0);
  function n(g, h, b, m) {
    return b.top - g < h.top ? b.bottom - h.top + m : b.top - h.top - g - m;
  }
  function r(g, h, b, m) {
    const p = g / 2, w = (b.left + b.right) / 2;
    return w - p < h.left ? b.right - h.left + m : w + p > h.right ? b.left - h.left - g - m : b.left - h.left + b.width / 2 - p;
  }
  const a = 4;
  let i = /* @__PURE__ */ ee(0), f = /* @__PURE__ */ ee(0);
  const o = /* @__PURE__ */ x(() => t.anchor.getBoundingClientRect()), u = /* @__PURE__ */ x(() => ia.value.getBoundingClientRect());
  let s = /* @__PURE__ */ x(() => n(l(f), l(u), l(o), a)), v = /* @__PURE__ */ x(() => r(l(i), l(u), l(o), a));
  var c = bs(), d = _(c);
  qr(d, () => t.children), $(() => me(c, `left: ${l(v) ?? ""}px; top: ${l(s) ?? ""}px;`)), Xe(c, "offsetWidth", (g) => V(i, g)), Xe(c, "offsetHeight", (g) => V(f, g)), H(e, c), we();
}
var _s = /* @__PURE__ */ ke('<g><rect fill="none"></rect><rect fill="none"></rect></g>');
function Gi(e, t) {
  let n = S(t, "color1", 3, "var(--color-black)"), r = S(t, "color2", 3, "var(--color-white)"), a = S(t, "strokeWidth", 3, 1), i = S(t, "strokeDashArray", 3, "4");
  var f = _s(), o = _(f), u = k(o);
  $(() => {
    T(f, "transform", `translate(${t.x ?? ""},${t.y ?? ""})`), T(o, "width", t.width), T(o, "height", t.height), T(o, "stroke-width", a()), T(o, "stroke", n()), T(u, "width", t.width), T(u, "height", t.height), T(u, "stroke-width", a()), T(u, "stroke", r()), T(u, "stroke-dasharray", i());
  }), H(e, f);
}
var ms = /* @__PURE__ */ oe('<tr class="svelte-1u00ohp"><td class="svelte-1u00ohp"> </td><td class="svelte-1u00ohp"> </td></tr>'), xs = /* @__PURE__ */ oe('<table class="svelte-1u00ohp"><tbody class="svelte-1u00ohp"></tbody></table>');
function Qt(e, t) {
  var n = xs(), r = _(n);
  Ae(r, 21, () => t.data, Me, (a, i) => {
    let f = () => l(i).key, o = () => l(i).value;
    var u = ms(), s = _(u), v = _(s), c = k(s), d = _(c);
    $(() => {
      de(v, f()), de(d, o());
    }), H(a, u);
  }), H(e, n);
}
var ps = /* @__PURE__ */ ke('<rect class="sae-cm-cell"></rect><!>', 1), ws = /* @__PURE__ */ oe('<div class="sae-cm-container svelte-kw462c"><svg><g></g><!><!></svg> <!> <!></div>');
function Ui(e, t) {
  pe(t, !0);
  let n = S(t, "showDifference", 3, !1), r = S(t, "marginTop", 3, 72), a = S(t, "marginRight", 3, 72), i = S(t, "marginBottom", 3, 72), f = S(t, "marginLeft", 3, 72), o = S(t, "legend", 3, "horizontal");
  function u(W, P, N, G, fe, ne, re) {
    if (re === "none")
      return {
        svgWidth: W,
        svgHeight: P,
        legendWidth: 0,
        legendHeight: 0,
        legendMarginTop: 0,
        legendMarginRight: 0,
        legendMarginBottom: 0,
        legendMarginLeft: 0
      };
    if (re === "horizontal") {
      const F = fe - 16;
      return {
        svgWidth: W,
        svgHeight: P - F,
        legendWidth: W,
        legendHeight: F,
        legendMarginTop: 16,
        legendMarginRight: G,
        legendMarginBottom: 32,
        legendMarginLeft: ne
      };
    } else {
      const F = G - 16;
      return {
        svgWidth: W - F,
        svgHeight: P,
        legendWidth: F,
        legendHeight: P,
        legendMarginTop: N,
        legendMarginRight: 60,
        legendMarginBottom: fe,
        legendMarginLeft: 0
      };
    }
  }
  const s = /* @__PURE__ */ x(() => u(t.width, t.height, r(), a(), i(), f(), o()));
  function v(W, P) {
    return P !== void 0 ? Vf(W.cells, P.cells).map(([N, G]) => ({
      ...N,
      pp_delta: N.pct - G.pct
    })) : W.cells.map((N) => ({ ...N, pp_delta: 0 }));
  }
  const c = /* @__PURE__ */ x(() => v(t.cm, t.other)), d = /* @__PURE__ */ x(() => Bn().domain(Le.value.label_indices).range([
    f(),
    t.width - a()
  ]).padding(0)), g = /* @__PURE__ */ x(() => Bn().domain(Le.value.label_indices).range([
    r(),
    t.height - i()
  ]).padding(0));
  function h(W, P) {
    if (P) {
      const [N, G] = Nf(W, (ne) => ne.pp_delta), fe = Math.max(Math.abs(N ?? 0), Math.abs(G ?? 0));
      return na().domain([-fe, 0, fe]).interpolator(ls);
    }
    return pn().domain([0, Bf(W, (N) => N.pct) ?? 0]).interpolator(us);
  }
  const b = /* @__PURE__ */ x(() => h(l(c), n()));
  function m(W) {
    return Le.value.labels[W];
  }
  const p = ce.xs, w = 3, y = 6, M = /* @__PURE__ */ x(() => i() - p - w - y), q = /* @__PURE__ */ x(() => f() - p - w - y);
  let E = /* @__PURE__ */ ee(null);
  function O(W, P, N) {
    V(E, { data: P, anchor: W.currentTarget, index: N }, !0);
  }
  function L() {
    V(E, null);
  }
  var C = ws();
  let j;
  var A = _(C), z = _(A);
  Ae(z, 21, () => l(c), Me, (W, P, N) => {
    var G = ps();
    const fe = /* @__PURE__ */ x(() => n() ? l(b)(l(P).pp_delta) : l(b)(l(P).pct));
    var ne = Ne(G), re = k(ne);
    {
      var U = (F) => {
        const te = /* @__PURE__ */ x(() => (l(d)(l(P).label) ?? 0) + 0.5), ue = /* @__PURE__ */ x(() => l(d).bandwidth() - 1), Te = /* @__PURE__ */ x(() => (l(g)(l(P).pred_label) ?? 0) + 1), K = /* @__PURE__ */ x(() => l(g).bandwidth() - 1);
        Gi(F, {
          get x() {
            return l(te);
          },
          get width() {
            return l(ue);
          },
          get y() {
            return l(Te);
          },
          get height() {
            return l(K);
          }
        });
      };
      le(re, (F) => {
        var te;
        N === ((te = l(E)) == null ? void 0 : te.index) && F(U);
      });
    }
    $(
      (F, te, ue, Te) => {
        T(ne, "x", F), T(ne, "width", te), T(ne, "y", ue), T(ne, "height", Te), T(ne, "fill", l(fe));
      },
      [
        () => (l(d)(l(P).label) ?? 0) + 0.5,
        () => l(d).bandwidth() - 1,
        () => (l(g)(l(P).pred_label) ?? 0) + 1,
        () => l(g).bandwidth() - 1
      ]
    ), Ge("mouseenter", ne, (F) => O(F, l(P), N)), Ge("mouseleave", ne, L), H(W, G);
  });
  var R = k(z);
  const I = /* @__PURE__ */ x(() => l(s).svgHeight - i()), B = /* @__PURE__ */ x(() => l(M) <= l(d).bandwidth() ? 0 : -45);
  Vt(R, {
    orientation: "bottom",
    get scale() {
      return l(d);
    },
    get translateY() {
      return l(I);
    },
    title: "True label",
    titleAnchor: "center",
    tickFormat: m,
    get tickLabelAngle() {
      return l(B);
    },
    get marginTop() {
      return r();
    },
    get marginRight() {
      return a();
    },
    get marginBottom() {
      return i();
    },
    get marginLeft() {
      return f();
    },
    get tickLabelFontSize() {
      return p;
    },
    tickPadding: w,
    tickLineSize: y,
    get maxTickLabelSpace() {
      return l(M);
    },
    get titleFontSize() {
      return ce.sm;
    }
  });
  var D = k(R);
  Vt(D, {
    orientation: "left",
    get scale() {
      return l(g);
    },
    get translateX() {
      return f();
    },
    title: "Predicted label",
    titleAnchor: "center",
    tickFormat: m,
    get marginTop() {
      return r();
    },
    get marginRight() {
      return a();
    },
    get marginBottom() {
      return i();
    },
    get marginLeft() {
      return f();
    },
    get tickLabelFontSize() {
      return p;
    },
    tickPadding: w,
    tickLineSize: y,
    get maxTickLabelSpace() {
      return l(q);
    },
    get titleFontSize() {
      return ce.sm;
    }
  });
  var X = k(A, 2);
  {
    var Y = (W) => {
      const P = /* @__PURE__ */ x(() => n() ? "Percentage point difference" : "Percent of data"), N = /* @__PURE__ */ x(() => n() ? Qa : dn);
      aa(W, {
        get width() {
          return l(s).legendWidth;
        },
        get height() {
          return l(s).legendHeight;
        },
        get color() {
          return l(b);
        },
        get orientation() {
          return o();
        },
        get marginTop() {
          return l(s).legendMarginTop;
        },
        get marginRight() {
          return l(s).legendMarginRight;
        },
        get marginBottom() {
          return l(s).legendMarginBottom;
        },
        get marginLeft() {
          return l(s).legendMarginLeft;
        },
        get title() {
          return l(P);
        },
        get tickLabelFontSize() {
          return p;
        },
        get titleFontSize() {
          return ce.sm;
        },
        get tickFormat() {
          return l(N);
        }
      });
    };
    le(X, (W) => {
      o() !== "none" && W(Y);
    });
  }
  var Z = k(X, 2);
  {
    var se = (W) => {
      sr(W, lr(() => l(E), {
        children: (P, N) => {
          var G = St(), fe = Ne(G);
          {
            var ne = (re) => {
              const U = /* @__PURE__ */ x(() => [
                {
                  key: "True label",
                  value: Le.value.labels[l(E).data.label]
                },
                {
                  key: "Predicted label",
                  value: Le.value.labels[l(E).data.pred_label]
                },
                {
                  key: "Percent of data",
                  value: dn(l(E).data.pct)
                },
                {
                  key: "Instance count",
                  value: It(l(E).data.count)
                },
                ...n() ? [
                  {
                    key: "Difference",
                    value: `${Qa(l(E).data.pp_delta)} pp`
                  }
                ] : []
              ]);
              Qt(re, {
                get data() {
                  return l(U);
                }
              });
            };
            le(fe, (re) => {
              l(E) && re(ne);
            });
          }
          H(P, G);
        },
        $$slots: { default: !0 }
      }));
    };
    le(Z, (W) => {
      l(E) && W(se);
    });
  }
  $(() => {
    j = me(C, "", j, {
      "flex-direction": o() === "vertical" ? "row" : "column"
    }), T(A, "width", l(s).svgWidth), T(A, "height", l(s).svgHeight);
  }), H(e, C), we();
}
var ks = /* @__PURE__ */ ke("<rect></rect><rect></rect>", 1), ys = /* @__PURE__ */ oe("<div><svg><g></g><!><!></svg> <!></div>");
function la(e, t) {
  pe(t, !0);
  let n = S(t, "marginLeft", 3, 0), r = S(t, "marginTop", 3, 0), a = S(t, "marginRight", 3, 0), i = S(t, "marginBottom", 3, 0), f = S(t, "xAxisLabel", 3, ""), o = S(t, "yAxisLabel", 3, ""), u = S(t, "showXAxis", 3, !0), s = S(t, "showYAxis", 3, !0), v = S(t, "xFormat", 3, Pr), c = S(t, "yFormat", 3, Pr), d = S(t, "tooltipEnabled", 3, !0), g = S(t, "tooltipData", 19, () => [
    {
      key: f(),
      value: (B, D, X) => `${v()(B)} - ${v()(D)}`
    },
    {
      key: o(),
      value: (B, D, X) => c()(X)
    }
  ]), h = /* @__PURE__ */ x(() => Yt().domain([
    t.data.thresholds[0],
    t.data.thresholds[t.data.thresholds.length - 1]
  ]).range([
    n(),
    t.width - a()
  ])), b = /* @__PURE__ */ x(() => Math.max(...t.data.counts)), m = /* @__PURE__ */ x(() => Yt().domain([0, l(b)]).nice().range([
    t.height - i(),
    r()
  ])), p = /* @__PURE__ */ x(() => Kr(t.data.counts.length)), w = /* @__PURE__ */ x(() => Pi(t.data.thresholds)), y = /* @__PURE__ */ ee(null);
  function M(B, D, X, Y, Z) {
    V(
      y,
      {
        count: D,
        xMin: X,
        xMax: Y,
        anchor: B.currentTarget,
        index: Z
      },
      !0
    );
  }
  function q() {
    V(y, null);
  }
  var E = ys(), O = _(E), L = _(O);
  Ae(L, 21, () => l(p), Me, (B, D) => {
    var X = ks(), Y = Ne(X), Z = k(Y);
    me(Z, "", {}, { "pointer-events": "none" }), $(
      (se, W, P, N, G, fe, ne, re) => {
        var U, F;
        T(Y, "x", se), T(Y, "width", W), T(Y, "y", P), T(Y, "height", N), T(Y, "fill", l(D) === ((U = l(y)) == null ? void 0 : U.index) ? "var(--color-neutral-200)" : "var(--color-white)"), T(Z, "x", G), T(Z, "width", fe), T(Z, "y", ne), T(Z, "height", re), T(Z, "fill", l(D) === ((F = l(y)) == null ? void 0 : F.index) ? "var(--color-black)" : "var(--color-neutral-500)");
      },
      [
        () => l(h)(l(w)[l(D)][0]),
        () => Math.max(0, l(h)(l(w)[l(D)][1]) - l(h)(l(w)[l(D)][0])),
        () => l(m).range()[1],
        () => l(m).range()[0] - l(m).range()[1],
        () => l(h)(l(w)[l(D)][0]) + 0.5,
        () => Math.max(0, l(h)(l(w)[l(D)][1]) - l(h)(l(w)[l(D)][0]) - 1),
        () => l(m)(t.data.counts[l(D)]),
        () => l(m)(0) - l(m)(t.data.counts[l(D)])
      ]
    ), Ge("mouseenter", Y, function(...se) {
      var W;
      (W = d() ? (P) => M(P, t.data.counts[l(D)], l(w)[l(D)][0], l(w)[l(D)][1], l(D)) : null) == null || W.apply(this, se);
    }), Ge("mouseleave", Y, function(...se) {
      var W;
      (W = d() ? q : null) == null || W.apply(this, se);
    }), H(B, X);
  });
  var C = k(L);
  {
    var j = (B) => {
      const D = /* @__PURE__ */ x(() => t.height - i());
      Vt(B, {
        orientation: "bottom",
        get scale() {
          return l(h);
        },
        get translateY() {
          return l(D);
        },
        get title() {
          return f();
        },
        titleAnchor: "right",
        get tickFormat() {
          return v();
        },
        get marginTop() {
          return r();
        },
        get marginRight() {
          return a();
        },
        get marginBottom() {
          return i();
        },
        get marginLeft() {
          return n();
        },
        numTicks: 5,
        get titleFontSize() {
          return ce.sm;
        },
        get tickLabelFontSize() {
          return ce.xs;
        },
        showDomain: !0
      });
    };
    le(C, (B) => {
      u() && B(j);
    });
  }
  var A = k(C);
  {
    var z = (B) => {
      Vt(B, {
        orientation: "left",
        get scale() {
          return l(m);
        },
        get translateX() {
          return n();
        },
        get title() {
          return o();
        },
        titleAnchor: "top",
        get tickFormat() {
          return c();
        },
        get marginTop() {
          return r();
        },
        get marginRight() {
          return a();
        },
        get marginBottom() {
          return i();
        },
        get marginLeft() {
          return n();
        },
        numTicks: 5,
        get titleFontSize() {
          return ce.sm;
        },
        get tickLabelFontSize() {
          return ce.xs;
        }
      });
    };
    le(A, (B) => {
      s() && B(z);
    });
  }
  var R = k(O, 2);
  {
    var I = (B) => {
      sr(B, lr(() => l(y), {
        children: (D, X) => {
          const Y = /* @__PURE__ */ x(() => g().map(({ key: Z, value: se }) => {
            var W, P, N;
            return {
              key: Z,
              value: se(((W = l(y)) == null ? void 0 : W.xMin) ?? 0, ((P = l(y)) == null ? void 0 : P.xMax) ?? 0, ((N = l(y)) == null ? void 0 : N.count) ?? 0)
            };
          }));
          Qt(D, {
            get data() {
              return l(Y);
            }
          });
        },
        $$slots: { default: !0 }
      }));
    };
    le(R, (B) => {
      l(y) && B(I);
    });
  }
  $(() => {
    T(O, "width", t.width), T(O, "height", t.height);
  }), H(e, E), we();
}
var Ms = /* @__PURE__ */ oe('<div class="sae-overview-container svelte-1kiuvfz"><div class="sae-col svelte-1kiuvfz"><div class="sae-section svelte-1kiuvfz"><div class="sae-section-header svelte-1kiuvfz">Summary</div> <div class="sae-table-container svelte-1kiuvfz"><table class="svelte-1kiuvfz"><thead class="svelte-1kiuvfz"><tr><th colspan="2" class="svelte-1kiuvfz">Dataset</th></tr></thead><tbody><tr class="svelte-1kiuvfz"><td class="svelte-1kiuvfz">Instances</td><td class="svelte-1kiuvfz"> </td></tr><tr class="svelte-1kiuvfz"><td class="svelte-1kiuvfz">Tokens</td><td class="svelte-1kiuvfz"> </td></tr></tbody></table> <table class="svelte-1kiuvfz"><thead class="svelte-1kiuvfz"><tr><th colspan="2" class="svelte-1kiuvfz">Model</th></tr></thead><tbody><tr class="svelte-1kiuvfz"><td class="svelte-1kiuvfz">Error rate</td><td class="svelte-1kiuvfz"> </td></tr><tr class="svelte-1kiuvfz"><td class="svelte-1kiuvfz">Log loss</td><td class="svelte-1kiuvfz"> </td></tr></tbody></table> <table class="svelte-1kiuvfz"><thead class="svelte-1kiuvfz"><tr><th colspan="2" class="svelte-1kiuvfz">SAE</th></tr></thead><tbody><tr class="svelte-1kiuvfz"><td class="svelte-1kiuvfz">Total features</td><td class="svelte-1kiuvfz"> </td></tr><tr class="svelte-1kiuvfz"><td class="svelte-1kiuvfz">Inactive features</td><td class="svelte-1kiuvfz"> </td></tr></tbody></table></div></div> <div class="sae-section svelte-1kiuvfz"><div class="sae-section-header svelte-1kiuvfz">Feature activation rate distribution</div> <div class="sae-vis svelte-1kiuvfz"><!></div></div></div> <div class="sae-col svelte-1kiuvfz"><div class="sae-section svelte-1kiuvfz"><div class="sae-section-header svelte-1kiuvfz">Confusion Matrix</div> <div class="sae-vis svelte-1kiuvfz"><!></div></div></div></div>');
function As(e, t) {
  pe(t, !0);
  const n = /* @__PURE__ */ x(() => kt.value.n_non_activating_features + kt.value.n_dead_features), r = /* @__PURE__ */ x(() => l(n) / kt.value.n_total_features);
  let a = /* @__PURE__ */ ee(0), i = /* @__PURE__ */ ee(0);
  const f = /* @__PURE__ */ x(() => ra(l(a), l(i), 1.6)), o = 8, u = 88, s = 80, v = 80;
  let c = /* @__PURE__ */ ee(0), d = /* @__PURE__ */ ee(0);
  const g = /* @__PURE__ */ x(() => Xi(l(c), l(d), 1, o, u, s, v));
  var h = Ms(), b = _(h), m = _(b), p = k(_(m), 2), w = _(p), y = k(_(w)), M = _(y), q = k(_(M)), E = _(q), O = k(M), L = k(_(O)), C = _(L), j = k(w, 2), A = k(_(j)), z = _(A), R = k(_(z)), I = _(R), B = k(z), D = k(_(B)), X = _(D), Y = k(j, 2), Z = k(_(Y)), se = _(Z), W = k(_(se)), P = _(W), N = k(se), G = k(_(N)), fe = _(G), ne = k(m, 2);
  me(ne, "", {}, { flex: "1" });
  var re = k(_(ne), 2), U = _(re);
  la(U, {
    get data() {
      return kt.value.sequence_act_rate_histogram;
    },
    marginTop: 20,
    marginRight: 20,
    marginLeft: 50,
    marginBottom: 40,
    get width() {
      return l(f).width;
    },
    get height() {
      return l(f).height;
    },
    xAxisLabel: "lg activation rate →",
    yAxisLabel: "↑ Feature count",
    tooltipData: [
      {
        key: "Feature count",
        value: (K, ye, Q) => It(Q)
      },
      {
        key: "Activation rate",
        value: (K, ye, Q) => `${Gn(10 ** K)} to ${Gn(10 ** ye)}`
      },
      {
        key: "Log 10 act. rate",
        value: (K, ye, Q) => `${Ka(K)} to ${Ka(ye)}`
      }
    ]
  });
  var F = k(b, 2), te = _(F);
  me(te, "", {}, { flex: "1" });
  var ue = k(_(te), 2), Te = _(ue);
  Ui(Te, {
    get cm() {
      return Pt.value.cm;
    },
    legend: "vertical",
    get width() {
      return l(g).width;
    },
    get height() {
      return l(g).height;
    },
    marginTop: o,
    marginRight: u,
    marginBottom: s,
    marginLeft: v
  }), $(
    (K, ye, Q, J, ae, xe, Oe) => {
      de(E, K), de(C, ye), de(I, Q), de(X, J), de(P, ae), de(fe, `${xe ?? ""} (${Oe ?? ""})`);
    },
    [
      () => Ja(Le.value.n_sequences),
      () => Ja(Le.value.n_tokens),
      () => dn(Pt.value.cm.error_pct),
      () => ds(Pt.value.log_loss),
      () => It(kt.value.n_total_features),
      () => It(l(n)),
      () => dn(l(r))
    ]
  ), Xe(re, "offsetWidth", (K) => V(a, K)), Xe(re, "offsetHeight", (K) => V(i, K)), Xe(ue, "offsetWidth", (K) => V(c, K)), Xe(ue, "offsetHeight", (K) => V(d, K)), H(e, h), we();
}
function Ts(e, t) {
  e.key === "Enter" && t();
}
var qs = /* @__PURE__ */ oe("<option> </option>"), Ss = (e, t) => t(e, "pred_label"), Es = /* @__PURE__ */ oe("<option> </option>"), Ls = /* @__PURE__ */ oe("<option> </option>"), Ns = (e, t) => t(e, "true_label"), Fs = /* @__PURE__ */ oe("<option> </option>"), zs = /* @__PURE__ */ oe("<option> </option>"), Cs = /* @__PURE__ */ oe('<label class="svelte-16q8vtd"><span>Predicted label:</span> <select class="svelte-16q8vtd"><optgroup label="Wildcards"></optgroup><optgroup label="Labels"></optgroup></select></label> <label class="svelte-16q8vtd"><span>True label:</span> <select class="svelte-16q8vtd"><optgroup label="Wildcards"></optgroup><optgroup label="Labels"></optgroup></select></label>', 1), Ps = /* @__PURE__ */ oe('<div class="sae-container svelte-16q8vtd"><div class="sae-control-row svelte-16q8vtd"><label class="svelte-16q8vtd"><span>Ranking:</span> <select class="svelte-16q8vtd"></select></label> <!></div> <div class="sae-control-row svelte-16q8vtd"><div class="sae-feature-table-order svelte-16q8vtd"><span>Order:</span> <label class="svelte-16q8vtd"><input type="radio" name="direction" class="svelte-16q8vtd"/> <span>Ascending</span></label> <label class="svelte-16q8vtd"><input type="radio" name="direction" class="svelte-16q8vtd"/> <span>Descending</span></label></div> <div class="sae-feature-table-min-act-rate"><label class="svelte-16q8vtd"><span>Min. activation rate:</span> <input type="number" step="0.0001" class="svelte-16q8vtd"/> <span>%</span></label></div></div></div>');
function Rs(e, t) {
  pe(t, !0);
  const n = [
    { label: "ID", value: "feature_id" },
    {
      label: "Act. Rate",
      value: "sequence_act_rate"
    },
    { label: "Confusion Matrix", value: "label" }
  ], r = [
    { label: "Any", value: "any" },
    { label: "Different", value: "different" }
  ], a = /* @__PURE__ */ x(() => Le.value.labels.map((R, I) => ({ label: R, value: `${I}` })));
  function i(R) {
    const I = R.currentTarget.value;
    I === "feature_id" ? ve.value = {
      kind: "feature_id",
      descending: ve.value.descending
    } : I === "sequence_act_rate" ? ve.value = {
      kind: "sequence_act_rate",
      descending: ve.value.descending
    } : ve.value = {
      kind: "label",
      true_label: "any",
      pred_label: "different",
      descending: ve.value.descending
    };
  }
  function f(R, I) {
    if (ve.value.kind !== "label")
      return;
    const B = R.currentTarget.value;
    ve.value = { ...ve.value, [I]: B };
  }
  function o(R) {
    const I = R.currentTarget.value;
    ve.value = {
      ...ve.value,
      descending: I === "descending"
    };
  }
  let u = /* @__PURE__ */ x(() => Er.value * 100);
  function s() {
    Er.value = l(u) / 100;
  }
  var v = Ps(), c = _(v), d = _(c), g = _(d);
  me(g, "", {}, { "font-weight": "var(--font-medium)" });
  var h = k(g, 2);
  qn(h, () => ve.value.kind);
  var b;
  h.__change = i, Ae(h, 21, () => n, Me, (R, I) => {
    var B = qs(), D = {}, X = _(B);
    $(() => {
      D !== (D = l(I).value) && (B.value = (B.__value = l(I).value) ?? ""), de(X, l(I).label);
    }), H(R, B);
  });
  var m = k(d, 2);
  {
    var p = (R) => {
      var I = Cs(), B = Ne(I), D = _(B);
      me(D, "", {}, { "font-weight": "var(--font-medium)" });
      var X = k(D, 2);
      qn(X, () => ve.value.pred_label);
      var Y;
      X.__change = [Ss, f];
      var Z = _(X);
      Ae(Z, 21, () => r, Me, (re, U) => {
        var F = Es(), te = {}, ue = _(F);
        $(() => {
          te !== (te = l(U).value) && (F.value = (F.__value = l(U).value) ?? ""), de(ue, l(U).label);
        }), H(re, F);
      });
      var se = k(Z);
      Ae(se, 21, () => l(a), Me, (re, U) => {
        var F = Ls(), te = {}, ue = _(F);
        $(() => {
          te !== (te = l(U).value) && (F.value = (F.__value = l(U).value) ?? ""), de(ue, l(U).label);
        }), H(re, F);
      });
      var W = k(B, 2), P = _(W);
      me(P, "", {}, { "font-weight": "var(--font-medium)" });
      var N = k(P, 2);
      qn(N, () => ve.value.true_label);
      var G;
      N.__change = [Ns, f];
      var fe = _(N);
      Ae(fe, 21, () => r, Me, (re, U) => {
        var F = Fs(), te = {}, ue = _(F);
        $(() => {
          te !== (te = l(U).value) && (F.value = (F.__value = l(U).value) ?? ""), de(ue, l(U).label);
        }), H(re, F);
      });
      var ne = k(fe);
      Ae(ne, 21, () => l(a), Me, (re, U) => {
        var F = zs(), te = {}, ue = _(F);
        $(() => {
          te !== (te = l(U).value) && (F.value = (F.__value = l(U).value) ?? ""), de(ue, l(U).label);
        }), H(re, F);
      }), $(() => {
        Y !== (Y = ve.value.pred_label) && (X.value = (X.__value = ve.value.pred_label) ?? "", Ct(X, ve.value.pred_label)), G !== (G = ve.value.true_label) && (N.value = (N.__value = ve.value.true_label) ?? "", Ct(N, ve.value.true_label));
      }), H(R, I);
    };
    le(m, (R) => {
      ve.value.kind === "label" && R(p);
    });
  }
  var w = k(c, 2), y = _(w), M = _(y);
  me(M, "", {}, { "font-weight": "var(--font-medium)" });
  var q = k(M, 2), E = _(q);
  ka(E, "ascending"), E.__change = o;
  var O = k(q, 2), L = _(O);
  ka(L, "descending"), L.__change = o;
  var C = k(y, 2), j = _(C), A = _(j);
  me(A, "", {}, { "font-weight": "var(--font-medium)" });
  var z = k(A, 2);
  z.__keydown = [Ts, s], me(z, "", {}, { width: "7em" }), $(() => {
    b !== (b = ve.value.kind) && (h.value = (h.__value = ve.value.kind) ?? "", Ct(h, ve.value.kind)), ya(E, !ve.value.descending), ya(L, ve.value.descending);
  }), Ge("blur", z, () => s()), ir(z, () => l(u), (R) => V(u, R)), H(e, v), we();
}
Lt(["change", "keydown"]);
var Is = /* @__PURE__ */ ke("<rect></rect><!>", 1), Ds = /* @__PURE__ */ oe('<div class="sae-heatmap-container svelte-k83kh4"><div><!> <svg><!><!><g></g></svg></div> <!> <!></div>');
function Ki(e, t) {
  pe(t, !0);
  let n = S(t, "distribution", 3, null), r = S(t, "compareToBaseProbs", 3, !1), a = S(t, "maxColorDomain", 3, null), i = S(t, "marginTop", 3, 0), f = S(t, "marginRight", 3, 0), o = S(t, "marginBottom", 3, 0), u = S(t, "marginLeft", 3, 0), s = S(t, "xAxisLabel", 3, ""), v = S(t, "yAxisLabel", 3, ""), c = S(t, "showColorLegend", 3, !0), d = S(t, "showXAxis", 3, !0), g = S(t, "showYAxis", 3, !0), h = S(t, "tooltipEnabled", 3, !0);
  const b = 16, m = /* @__PURE__ */ x(() => c() ? f() - b : 0), p = /* @__PURE__ */ x(() => c() ? t.height : 0), w = /* @__PURE__ */ x(() => n() ? i() - 2 : 0), y = /* @__PURE__ */ x(() => i() - l(w)), M = /* @__PURE__ */ x(() => f() - l(m)), q = /* @__PURE__ */ x(() => t.width - l(m)), E = /* @__PURE__ */ x(() => t.height - l(w)), O = /* @__PURE__ */ x(() => c() ? i() : 0), L = /* @__PURE__ */ x(() => c() ? 60 : 0), C = /* @__PURE__ */ x(() => c() ? o() : 0), j = /* @__PURE__ */ x(() => 0), A = /* @__PURE__ */ x(() => t.marginalEffects.probs.map((Q, J) => ({
    labelIndex: J,
    points: Pi(t.marginalEffects.thresholds).map(([ae, xe], Oe) => {
      const Ue = Q[Oe] >= 0 ? Q[Oe] : NaN, Ke = Number.isNaN(Ue) ? NaN : Ue - Pt.value.cm.pred_label_pcts[J];
      return {
        startAct: ae,
        endAct: xe,
        prob: Ue,
        delta: Ke
      };
    })
  }))), z = /* @__PURE__ */ x(() => Yt().domain([
    t.marginalEffects.thresholds[0],
    t.marginalEffects.thresholds[t.marginalEffects.thresholds.length - 1]
  ]).range([
    u(),
    l(q) - l(M)
  ])), R = /* @__PURE__ */ x(() => Bn().domain(t.classes).range([
    l(y),
    l(E) - o()
  ])), I = /* @__PURE__ */ x(() => a() ?? Math.max(...l(A).flatMap((Q) => Q.points.map((J) => Number.isNaN(J.prob) ? 0 : J.prob)))), B = /* @__PURE__ */ x(() => a() ?? Math.max(...l(A).flatMap((Q) => Q.points.map((J) => Math.abs(Number.isNaN(J.delta) ? 0 : J.delta))))), D = /* @__PURE__ */ x(() => pn().domain([0, l(I)]).interpolator(os).unknown("var(--color-neutral-300)")), X = /* @__PURE__ */ x(() => na().domain([-l(B), 0, l(B)]).interpolator(as).unknown("var(--color-neutral-300)"));
  let Y = /* @__PURE__ */ ee(null);
  function Z(Q, J, ae, xe) {
    V(
      Y,
      {
        point: J,
        anchor: Q.currentTarget,
        labelIndex: ae,
        pointIndex: xe
      },
      !0
    );
  }
  function se() {
    V(Y, null);
  }
  var W = Ds(), P = _(W), N = _(P);
  {
    var G = (Q) => {
      la(Q, {
        get data() {
          return n();
        },
        marginTop: 0,
        get marginRight() {
          return l(M);
        },
        get marginLeft() {
          return u();
        },
        marginBottom: 0,
        get width() {
          return l(q);
        },
        get height() {
          return l(w);
        },
        showXAxis: !1,
        showYAxis: !1,
        get xFormat() {
          return yt;
        },
        get tooltipEnabled() {
          return h();
        },
        tooltipData: [
          {
            key: "Instance count",
            value: (J, ae, xe) => It(xe)
          },
          {
            key: "Activation value",
            value: (J, ae, xe) => `${yt(J)} to ${yt(ae)}`
          }
        ]
      });
    };
    le(N, (Q) => {
      n() && Q(G);
    });
  }
  var fe = k(N, 2), ne = _(fe);
  {
    var re = (Q) => {
      const J = /* @__PURE__ */ x(() => l(E) - o());
      Vt(Q, {
        orientation: "bottom",
        get scale() {
          return l(z);
        },
        get translateY() {
          return l(J);
        },
        get title() {
          return s();
        },
        get marginTop() {
          return l(y);
        },
        get marginRight() {
          return l(M);
        },
        get marginBottom() {
          return o();
        },
        get marginLeft() {
          return u();
        },
        numTicks: 5,
        get tickLabelFontSize() {
          return ce.xs;
        },
        get titleFontSize() {
          return ce.sm;
        }
      });
    };
    le(ne, (Q) => {
      d() && Q(re);
    });
  }
  var U = k(ne);
  {
    var F = (Q) => {
      Vt(Q, {
        orientation: "left",
        get scale() {
          return l(R);
        },
        get translateX() {
          return u();
        },
        tickFormat: (J) => Le.value.labels[J],
        get title() {
          return v();
        },
        get marginTop() {
          return l(y);
        },
        get marginRight() {
          return l(M);
        },
        get marginBottom() {
          return o();
        },
        get marginLeft() {
          return u();
        },
        get tickLabelFontSize() {
          return ce.xs;
        },
        get titleFontSize() {
          return ce.sm;
        }
      });
    };
    le(U, (Q) => {
      g() && Q(F);
    });
  }
  var te = k(U);
  Ae(te, 21, () => l(A), Me, (Q, J) => {
    let ae = () => l(J).points, xe = () => l(J).labelIndex;
    var Oe = St(), Ue = Ne(Oe);
    Ae(Ue, 17, ae, Me, (Ke, be, _e) => {
      var $e = Is(), Ce = Ne($e), Qi = k(Ce);
      {
        var Ji = (lt) => {
          const Ye = /* @__PURE__ */ x(() => l(z)(l(be).startAct) + 0.5), Jt = /* @__PURE__ */ x(() => l(z)(l(be).endAct) - l(z)(l(be).startAct) - 1), ur = /* @__PURE__ */ x(() => (l(R)(xe()) ?? 0) + 0.5), cr = /* @__PURE__ */ x(() => l(R).bandwidth() - 1);
          Gi(lt, {
            get x() {
              return l(Ye);
            },
            get width() {
              return l(Jt);
            },
            get y() {
              return l(ur);
            },
            get height() {
              return l(cr);
            }
          });
        };
        le(Qi, (lt) => {
          var Ye;
          xe() === ((Ye = l(Y)) == null ? void 0 : Ye.labelIndex) && _e === l(Y).pointIndex && lt(Ji);
        });
      }
      $(
        (lt, Ye, Jt, ur, cr) => {
          T(Ce, "x", lt), T(Ce, "width", Ye), T(Ce, "y", Jt), T(Ce, "height", ur), T(Ce, "fill", cr);
        },
        [
          () => l(z)(l(be).startAct) + 0.5,
          () => l(z)(l(be).endAct) - l(z)(l(be).startAct) - 1,
          () => (l(R)(xe()) ?? 0) + 0.5,
          () => l(R).bandwidth() - 1,
          () => r() ? l(X)(l(be).delta) : l(D)(l(be).prob)
        ]
      ), Ge("mouseenter", Ce, function(...lt) {
        var Ye;
        (Ye = h() ? (Jt) => Z(Jt, l(be), xe(), _e) : null) == null || Ye.apply(this, lt);
      }), Ge("mouseleave", Ce, function(...lt) {
        var Ye;
        (Ye = h() ? se : null) == null || Ye.apply(this, lt);
      }), H(Ke, $e);
    }), H(Q, Oe);
  });
  var ue = k(P, 2);
  {
    var Te = (Q) => {
      const J = /* @__PURE__ */ x(() => r() ? l(X) : l(D)), ae = /* @__PURE__ */ x(() => r() ? "Difference from base prob." : "Mean predicted probability");
      aa(Q, {
        get width() {
          return l(m);
        },
        get height() {
          return l(p);
        },
        get color() {
          return l(J);
        },
        orientation: "vertical",
        get marginTop() {
          return l(O);
        },
        get marginRight() {
          return l(L);
        },
        get marginBottom() {
          return l(C);
        },
        marginLeft: l(j),
        get title() {
          return l(ae);
        },
        get tickLabelFontSize() {
          return ce.xs;
        },
        get titleFontSize() {
          return ce.sm;
        },
        get tickFormat() {
          return Pr;
        }
      });
    };
    le(ue, (Q) => {
      c() && Q(Te);
    });
  }
  var K = k(ue, 2);
  {
    var ye = (Q) => {
      sr(Q, lr(() => l(Y), {
        children: (J, ae) => {
          var xe = St(), Oe = Ne(xe);
          {
            var Ue = (Ke) => {
              const be = /* @__PURE__ */ x(() => [
                {
                  key: "Activation value",
                  value: `${yt(l(Y).point.startAct)} to ${yt(l(Y).point.endAct)}`
                },
                {
                  key: "Predicted label",
                  value: Le.value.labels[l(Y).labelIndex]
                },
                {
                  key: "Mean probability",
                  value: Number.isNaN(l(Y).point.prob) ? "No data" : Za(l(Y).point.prob)
                },
                ...r() ? [
                  {
                    key: "Diff. from base prob.",
                    value: Za(l(Y).point.delta)
                  }
                ] : []
              ]);
              Qt(Ke, {
                get data() {
                  return l(be);
                }
              });
            };
            le(Oe, (Ke) => {
              l(Y) && Ke(Ue);
            });
          }
          H(J, xe);
        },
        $$slots: { default: !0 }
      }));
    };
    le(K, (Q) => {
      l(Y) && Q(ye);
    });
  }
  $(() => {
    T(fe, "width", l(q)), T(fe, "height", l(E));
  }), H(e, W), we();
}
var Os = /* @__PURE__ */ oe('<div class="sae-token svelte-165qlb"><span class="sae-token-name svelte-165qlb"> </span></div>'), Bs = /* @__PURE__ */ oe('<div class="sae-sequence svelte-165qlb"><!> <!></div>');
function fa(e, t) {
  pe(t, !0);
  let n = S(t, "tooltipEnabled", 3, !0), r = S(t, "hidePadding", 3, !1), a = /* @__PURE__ */ ee(null);
  function i(d, g, h) {
    V(a, { data: g, anchor: d.currentTarget, index: h }, !0);
  }
  function f() {
    V(a, null);
  }
  var o = Bs();
  let u;
  var s = _(o);
  Ae(s, 17, () => t.sequence.display_tokens, Me, (d, g, h) => {
    var b = St(), m = Ne(b);
    {
      var p = (w) => {
        var y = Os();
        const M = /* @__PURE__ */ x(() => l(g).max_act > 0 ? t.colorScale(l(g).max_act) : "var(--color-white)");
        let q;
        var E = _(y), O = _(E);
        $(() => {
          var L;
          q = me(y, "", q, {
            "--token-color": l(M),
            "font-weight": h === t.sequence.max_token_index && l(g).max_act > 0 ? "var(--font-bold)" : "var(--font-normal)",
            "background-color": n() && ((L = l(a)) == null ? void 0 : L.index) === h ? "var(--color-neutral-300)" : "var(--color-white)"
          }), de(O, l(g).display);
        }), Ge("mouseenter", y, function(...L) {
          var C;
          (C = n() ? (j) => i(j, l(g), h) : null) == null || C.apply(this, L);
        }), Ge("mouseleave", y, function(...L) {
          var C;
          (C = n() ? f : null) == null || C.apply(this, L);
        }), H(w, y);
      };
      le(m, (w) => {
        (!r() || l(g).display !== "<pad>") && w(p);
      });
    }
    H(d, b);
  });
  var v = k(s, 2);
  {
    var c = (d) => {
      sr(d, lr(() => l(a), {
        children: (g, h) => {
          var b = St(), m = Ne(b);
          {
            var p = (w) => {
              const y = /* @__PURE__ */ x(() => [
                {
                  key: "Token",
                  value: l(a).data.display
                },
                {
                  key: "Activation",
                  value: yt(l(a).data.max_act)
                }
              ]);
              Qt(w, {
                get data() {
                  return l(y);
                }
              });
            };
            le(m, (w) => {
              l(a) && w(p);
            });
          }
          H(g, b);
        },
        $$slots: { default: !0 }
      }));
    };
    le(v, (d) => {
      l(a) && d(c);
    });
  }
  $(() => u = me(o, "", u, { "flex-wrap": t.wrap ? "wrap" : "nowrap" })), H(e, o), we();
}
function Hs(e, t, n) {
  return e < t ? t : e > n ? n : e;
}
function Ws(e, t, n) {
  e.key === "Enter" && t(l(n) - 1);
}
var js = (e, t, n) => t(l(n) - 2), Ys = (e, t, n) => t(l(n)), Vs = /* @__PURE__ */ oe('<div class="sae-page-container svelte-xg014a"><button class="svelte-xg014a">←</button> <div class="sae-page-select svelte-xg014a"><span>Page</span> <input type="number" class="svelte-xg014a"/> <span>/</span> <span> </span></div> <button class="svelte-xg014a">→</button></div>');
function Xs(e, t) {
  pe(t, !0);
  let n = /* @__PURE__ */ x(() => Ft.value + 1);
  const r = /* @__PURE__ */ x(() => Math.log10(nn.value + 1) + 1);
  function a(g) {
    const h = Hs(g, 0, nn.value);
    h === Ft.value ? V(n, h + 1) : Ft.value = h;
  }
  var i = Vs(), f = _(i);
  f.__click = [js, a, n];
  var o = k(f, 2), u = k(_(o), 2);
  u.__keydown = [
    Ws,
    a,
    n
  ];
  let s;
  var v = k(u, 4), c = _(v), d = k(o, 2);
  d.__click = [Ys, a, n], $(() => {
    f.disabled = Ft.value <= 0, s = me(u, "", s, { width: `${l(r) ?? ""}em` }), de(c, nn.value + 1), d.disabled = Ft.value >= nn.value;
  }), Ge("blur", u, () => a(l(n) - 1)), ir(u, () => l(n), (g) => V(n, g)), H(e, i), we();
}
Lt(["click", "keydown"]);
var Gs = (e, t, n) => t.onClickFeature(l(n).feature_id), Us = /* @__PURE__ */ oe('<div><div><button class="sae-table-feature-id-btn svelte-1hyqnjv"> </button></div></div> <div><div> </div></div> <div><!></div> <div><!></div> <div><!></div>', 1), Ks = /* @__PURE__ */ oe('<div class="sae-table-container svelte-1hyqnjv"><div class="sae-table-controls"><!></div> <div class="sae-table svelte-1hyqnjv"><div class="sae-table-cell sae-table-header sae-table-header-align-right svelte-1hyqnjv">ID</div> <div class="sae-table-cell sae-table-header sae-table-header-align-right svelte-1hyqnjv">Act. Rate</div> <div class="sae-table-cell sae-table-header sae-table-header-align-right svelte-1hyqnjv">Act. Distribution</div> <div class="sae-table-cell sae-table-header sae-table-header-align-right svelte-1hyqnjv">Top Class Probabilities</div> <div class="sae-table-cell sae-table-header svelte-1hyqnjv">Example</div> <!></div> <div class="sae-table-pagination"><!></div></div>');
function Zs(e, t) {
  pe(t, !0);
  const n = /* @__PURE__ */ x(() => ce.base * 0.5), r = /* @__PURE__ */ x(() => ce.base * 0.25), a = /* @__PURE__ */ x(() => ce.base * 3), i = /* @__PURE__ */ x(() => l(a) * 3), f = 80;
  function o(m) {
    return m.cm.pred_label_pcts.map((p, w) => ({ pct: p, label: w })).sort((p, w) => zi(p.pct, w.pct)).slice(0, 3).map(({ label: p }) => p);
  }
  var u = Ks(), s = _(u), v = _(s);
  Rs(v, {});
  var c = k(s, 2);
  let d;
  var g = k(_(c), 10);
  Ae(g, 17, () => Lr.value, Me, (m, p, w) => {
    var y = Us();
    const M = /* @__PURE__ */ x(() => w !== Lr.value.length - 1);
    var q = Ne(y);
    let E;
    var O = _(q), L = _(O);
    L.__click = [Gs, t, p];
    var C = _(L), j = k(q, 2);
    let A;
    var z = _(j), R = _(z), I = k(j, 2);
    let B;
    var D = _(I);
    la(D, {
      get data() {
        return l(p).sequence_acts_histogram;
      },
      get width() {
        return l(i);
      },
      get height() {
        return l(a);
      },
      tooltipEnabled: !1
    });
    var X = k(I, 2);
    let Y;
    var Z = _(X);
    const se = /* @__PURE__ */ x(() => o(l(p))), W = /* @__PURE__ */ x(() => l(i) + f);
    Ki(Z, {
      get marginalEffects() {
        return l(p).marginal_effects;
      },
      get classes() {
        return l(se);
      },
      get width() {
        return l(W);
      },
      get height() {
        return l(a);
      },
      maxColorDomain: 1,
      showColorLegend: !1,
      marginTop: 0,
      marginRight: 0,
      marginBottom: 0,
      marginLeft: f,
      showXAxis: !1,
      showYAxis: !0,
      tooltipEnabled: !1
    });
    var P = k(X, 2);
    let N;
    var G = _(P);
    const fe = /* @__PURE__ */ x(() => pn([0, l(p).max_act], (ne) => Vi(1 - ne)));
    fa(G, {
      get colorScale() {
        return l(fe);
      },
      get sequence() {
        return l(p).sequence_intervals[0].sequences[0];
      },
      wrap: !1,
      tooltipEnabled: !1
    }), $(
      (ne, re, U, F, te, ue) => {
        E = Ee(q, 1, "sae-table-cell sae-table-number-value svelte-1hyqnjv", null, E, ne), de(C, l(p).feature_id), A = Ee(j, 1, "sae-table-cell sae-table-number-value svelte-1hyqnjv", null, A, re), de(R, U), B = Ee(I, 1, "sae-table-cell svelte-1hyqnjv", null, B, F), Y = Ee(X, 1, "sae-table-cell svelte-1hyqnjv", null, Y, te), N = Ee(P, 1, "sae-table-cell sae-table-example-sequence svelte-1hyqnjv", null, N, ue);
      },
      [
        () => ({ "sae-table-border": l(M) }),
        () => ({ "sae-table-border": l(M) }),
        () => Gn(l(p).sequence_act_rate),
        () => ({ "sae-table-border": l(M) }),
        () => ({ "sae-table-border": l(M) }),
        () => ({ "sae-table-border": l(M) })
      ]
    ), H(m, y);
  });
  var h = k(c, 2), b = _(h);
  Xs(b, {}), $(() => d = me(c, "", d, {
    "--cell-padding-x": `${l(n) ?? ""}px`,
    "--cell-padding-y": `${l(r) ?? ""}px`
  })), H(e, u), we();
}
Lt(["click"]);
var Qs = /* @__PURE__ */ oe('<div class="sae-tooltip-content svelte-ib6w91"><!></div>'), Js = /* @__PURE__ */ oe('<div class="sae-tooltip-container svelte-ib6w91"><button class="svelte-ib6w91"><!></button> <!></div>');
function Zi(e, t) {
  pe(t, !0);
  let n = S(t, "position", 3, "auto"), r = S(t, "clickingEnabled", 3, !1);
  function a(L, C, j, A, z) {
    if (C === null || j === null)
      return 0;
    const R = L / 2, I = j.height / 2;
    return z === "right" || z === "left" ? j.top - C.top + I - R : z === "bottom" || z === "auto" && j.top - L < C.top ? j.bottom - C.top + A : j.top - C.top - L - A;
  }
  function i(L, C, j, A, z) {
    if (C === null || j === null)
      return 0;
    const R = L / 2, I = j.left - C.left + j.width / 2;
    return z === "right" || z === "auto" && I - R < C.left ? j.right - C.left + A : z === "left" || z === "auto" && I + R > C.right ? j.left - C.left - L - A : I - R;
  }
  const f = 4;
  let o = /* @__PURE__ */ ee(void 0), u = /* @__PURE__ */ ee(0), s = /* @__PURE__ */ ee(0), v = /* @__PURE__ */ ee(null), c = /* @__PURE__ */ ee(null), d = /* @__PURE__ */ x(() => a(l(s), l(c), l(v), f, n())), g = /* @__PURE__ */ x(() => i(l(u), l(c), l(v), f, n())), h = /* @__PURE__ */ ee(!1), b = /* @__PURE__ */ ee(!1);
  function m() {
    V(b, !l(b)), V(h, l(b), !0);
  }
  function p() {
    !l(b) && l(o) && (V(v, l(o).getBoundingClientRect(), !0), V(c, ia.value.getBoundingClientRect(), !0), V(h, !0));
  }
  function w() {
    l(b) || V(h, !1);
  }
  var y = Js(), M = _(y);
  M.__click = function(...L) {
    var C;
    (C = r() ? m : null) == null || C.apply(this, L);
  };
  var q = _(M);
  qr(q, () => t.trigger), Ur(M, (L) => V(o, L), () => l(o));
  var E = k(M, 2);
  {
    var O = (L) => {
      var C = Qs();
      let j;
      var A = _(C);
      qr(A, () => t.content), $(() => j = me(C, "", j, {
        top: `${l(d) ?? ""}px`,
        left: `${l(g) ?? ""}px`
      })), Xe(C, "offsetWidth", (z) => V(u, z)), Xe(C, "offsetHeight", (z) => V(s, z)), H(L, C);
    };
    le(E, (L) => {
      l(h) && L(O);
    });
  }
  Ge("mouseenter", M, p), Ge("mouseleave", M, w), H(e, y), we();
}
Lt(["click"]);
var $s = /* @__PURE__ */ oe("<option> </option>"), eu = /* @__PURE__ */ ke('<svg stroke-width="2" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" color="currentcolor"><path d="M12 11.5V16.5" stroke="currentcolor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path><path d="M12 7.51L12.01 7.49889" stroke="currentcolor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path><path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentcolor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>'), tu = /* @__PURE__ */ oe("<div><!></div> <div> </div> <div> </div> <div><!></div>", 1), nu = /* @__PURE__ */ oe('<div class="sae-sequence-container svelte-i85elo"><div class="sae-sequences-header svelte-i85elo"><div class="sae-sequences-controls svelte-i85elo"><span>Example Activations</span> <label class="svelte-i85elo"><span>Range:</span> <select class="svelte-i85elo"><option>Max activations</option><!></select></label> <label class="svelte-i85elo"><input type="checkbox"/> <span>Wrap text</span></label></div> <div class="sae-sequences-color-legend"><!></div></div> <div class="sae-sequences-table svelte-i85elo"><div class="sae-sequences-table-cell sae-sequences-table-header svelte-i85elo"></div> <div class="sae-sequences-table-cell sae-sequences-table-header svelte-i85elo">Pred.</div> <div class="sae-sequences-table-cell sae-sequences-table-header svelte-i85elo">True</div> <div class="sae-sequences-table-cell sae-sequences-table-header svelte-i85elo">Tokens</div> <!></div></div>');
function ru(e, t) {
  pe(t, !0);
  let n = /* @__PURE__ */ ee(0), r = /* @__PURE__ */ x(() => ft.value.sequence_intervals[l(n)]), a = /* @__PURE__ */ ee(!1);
  var i = nu(), f = _(i), o = _(f), u = _(o);
  me(u, "", {}, { "font-weight": "var(--font-medium)" });
  var s = k(u, 2), v = k(_(s), 2), c = _(v);
  c.value = c.__value = 0;
  var d = k(c);
  Ae(d, 17, () => Kr(ft.value.sequence_intervals.length - 1, 0, -1), Me, (y, M) => {
    var q = $s(), E = {}, O = _(q);
    $(() => {
      E !== (E = l(M)) && (q.value = (q.__value = l(M)) ?? ""), de(O, `Interval ${l(M) ?? ""}`);
    }), H(y, q);
  });
  var g = k(s, 2), h = _(g), b = k(o, 2), m = _(b);
  aa(m, {
    width: 256,
    height: 56,
    get color() {
      return t.tokenColor;
    },
    orientation: "horizontal",
    title: "Activation value",
    marginTop: 18,
    marginBottom: 24,
    get titleFontSize() {
      return ce.sm;
    },
    get tickLabelFontSize() {
      return ce.xs;
    },
    tickFormat: (y) => y === 0 ? "> 0" : yt(y)
  });
  var p = k(f, 2), w = k(_(p), 8);
  Ae(w, 17, () => l(r).sequences, Me, (y, M, q) => {
    var E = tu();
    const O = /* @__PURE__ */ x(() => q !== l(r).sequences.length - 1);
    var L = Ne(E);
    let C;
    var j = _(L);
    Zi(j, {
      position: "left",
      trigger: (P) => {
        var N = eu();
        $(() => {
          T(N, "width", `${ce.base ?? ""}px`), T(N, "height", `${ce.base ?? ""}px`);
        }), H(P, N);
      },
      content: (P) => {
        const N = /* @__PURE__ */ x(() => [
          {
            key: "Instance index",
            value: `${l(M).sequence_index}`
          }
        ]);
        Qt(P, {
          get data() {
            return l(N);
          }
        });
      },
      $$slots: { trigger: !0, content: !0 }
    });
    var A = k(L, 2);
    let z;
    var R = _(A), I = k(A, 2);
    let B;
    var D = _(I), X = k(I, 2);
    let Y;
    var Z = _(X);
    fa(Z, {
      get colorScale() {
        return t.tokenColor;
      },
      get sequence() {
        return l(M);
      },
      get wrap() {
        return l(a);
      },
      hidePadding: !1
    }), $(
      (se, W, P, N) => {
        C = Ee(L, 1, "sae-sequences-table-cell svelte-i85elo", null, C, se), z = Ee(A, 1, "sae-sequences-table-cell svelte-i85elo", null, z, W), de(R, Le.value.labels[l(M).pred_label]), B = Ee(I, 1, "sae-sequences-table-cell svelte-i85elo", null, B, P), de(D, Le.value.labels[l(M).label]), Y = Ee(X, 1, "sae-sequences-table-cell sae-sequences-table-tokens svelte-i85elo", null, Y, N);
      },
      [
        () => ({
          "sae-sequences-table-border": l(O)
        }),
        () => ({
          "sae-sequences-table-border": l(O)
        }),
        () => ({
          "sae-sequences-table-border": l(O)
        }),
        () => ({
          "sae-sequences-table-border": l(O)
        })
      ]
    ), H(y, E);
  }), gf(v, () => l(n), (y) => V(n, y)), on(h, () => l(a), (y) => V(a, y)), H(e, i), we();
}
var au = /* @__PURE__ */ ke('<svg stroke-width="2" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" color="currentcolor"><path d="M12 11.5V16.5" stroke="currentcolor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path><path d="M12 7.51L12.01 7.49889" stroke="currentcolor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path><path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" stroke="currentcolor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>'), iu = /* @__PURE__ */ oe('<div class="sae-sequences-table svelte-1g9xqzl"><div class="sae-sequences-table-cell sae-sequences-table-header svelte-1g9xqzl"></div> <div class="sae-sequences-table-cell sae-sequences-table-header svelte-1g9xqzl">Pred.</div> <div class="sae-sequences-table-cell sae-sequences-table-header svelte-1g9xqzl">Prob.</div> <div class="sae-sequences-table-cell sae-sequences-table-header svelte-1g9xqzl">Tokens</div> <div><!></div> <div> </div> <div> </div> <div><!></div></div>'), lu = /* @__PURE__ */ oe('<div class="sae-feature-testing-container svelte-1g9xqzl"><div class="sae-controls svelte-1g9xqzl"><span>Test Feature</span> <label><input type="checkbox"/> <span>Hide padding</span></label> <label><input type="checkbox"/> <span>Wrap text</span></label></div> <div class="sae-input-row svelte-1g9xqzl"><input type="text" class="svelte-1g9xqzl"/> <button>Test</button></div> <!></div>');
function fu(e, t) {
  pe(t, !0);
  let n = /* @__PURE__ */ ee(!1), r = /* @__PURE__ */ ee(!0), a = /* @__PURE__ */ x(() => t.featureId === Sn.value.feature_index ? Sn.value.sequence : "");
  function i() {
    Sn.value = {
      feature_index: t.featureId,
      sequence: l(a)
    };
  }
  var f = lu(), o = _(f), u = _(o);
  me(u, "", {}, { "font-weight": "var(--font-medium)" });
  var s = k(u, 2), v = _(s), c = k(s, 2), d = _(c), g = k(o, 2), h = _(g), b = k(h, 2);
  b.__click = i;
  var m = k(g, 2);
  {
    var p = (w) => {
      var y = iu(), M = k(_(y), 8);
      Ee(M, 1, "sae-sequences-table-cell svelte-1g9xqzl", null, {}, { "sae-sequences-table-border": !0 });
      var q = _(M);
      Zi(q, {
        position: "left",
        trigger: (I) => {
          var B = au();
          $(() => {
            T(B, "width", `${ce.base ?? ""}px`), T(B, "height", `${ce.base ?? ""}px`);
          }), H(I, B);
        },
        content: (I) => {
          Qt(I, {
            data: [{ key: "Instance index", value: "-1" }]
          });
        },
        $$slots: { trigger: !0, content: !0 }
      });
      var E = k(M, 2);
      Ee(E, 1, "sae-sequences-table-cell svelte-1g9xqzl", null, {}, { "sae-sequences-table-border": !0 });
      var O = _(E), L = k(E, 2);
      Ee(L, 1, "sae-sequences-table-cell svelte-1g9xqzl", null, {}, { "sae-sequences-table-border": !0 });
      var C = _(L), j = k(L, 2);
      Ee(j, 1, "sae-sequences-table-cell sae-sequences-table-tokens svelte-1g9xqzl", null, {}, { "sae-sequences-table-border": !0 });
      var A = _(j);
      fa(A, {
        get colorScale() {
          return t.tokenColor;
        },
        get sequence() {
          return zt.value;
        },
        get wrap() {
          return l(n);
        },
        get hidePadding() {
          return l(r);
        }
      }), $(
        (z) => {
          de(O, Le.value.labels[zt.value.pred_label]), de(C, z);
        },
        [
          () => dn(zt.value.pred_probs[zt.value.pred_label])
        ]
      ), H(w, y);
    };
    le(m, (w) => {
      zt.value.feature_index === t.featureId && w(p);
    });
  }
  on(v, () => l(r), (w) => V(r, w)), on(d, () => l(n), (w) => V(n, w)), ir(h, () => l(a), (w) => V(a, w)), H(e, f), we();
}
Lt(["click"]);
var ou = /* @__PURE__ */ oe('<div class="sae-inference-container svelte-il95ok"><!></div>'), su = /* @__PURE__ */ oe('<div class="sae-container svelte-il95ok"><div class="sae-controls svelte-il95ok"><div class="sae-feature-input svelte-il95ok"><label class="svelte-il95ok"><span>Feature ID:</span> <input type="number" class="svelte-il95ok"/></label> <button class="svelte-il95ok">Go</button></div> <div><span>Activation Rate:</span> <span> </span></div></div> <div><div class="sae-effects-container svelte-il95ok"><div class="sae-effects-controls svelte-il95ok"><div>Predicted Probabilities</div> <label class="svelte-il95ok"><input type="checkbox"/> <span>Compare to base probabilities</span></label></div> <div class="sae-effects-vis svelte-il95ok"><!></div></div> <div class="sae-cm-container svelte-il95ok"><div class="sae-cm-controls svelte-il95ok"><div>Confusion Matrix</div> <label class="svelte-il95ok"><input type="checkbox"/> <span>Compare to whole dataset</span></label></div> <div class="sae-cm-vis svelte-il95ok"><!></div></div> <div class="sae-sequences-container svelte-il95ok"><!></div> <!></div></div>');
function uu(e, t) {
  pe(t, !0);
  const n = /* @__PURE__ */ x(() => Math.log10(kt.value.n_total_features) + 1), r = /* @__PURE__ */ x(() => pn().domain([0, ft.value.max_act]).interpolator((K) => Vi(1 - K)));
  let a = /* @__PURE__ */ x(() => an.value);
  function i() {
    an.value = l(a);
  }
  let f = /* @__PURE__ */ ee(0), o = /* @__PURE__ */ ee(0), u = /* @__PURE__ */ x(() => ra(l(o), l(f), 1.6));
  const s = 8, v = 88, c = 80, d = 80;
  let g = /* @__PURE__ */ ee(0), h = /* @__PURE__ */ ee(0);
  const b = /* @__PURE__ */ x(() => Xi(l(g), l(h), 1, s, v, c, d));
  let m = /* @__PURE__ */ ee(!1), p = /* @__PURE__ */ ee(!1);
  var w = su(), y = _(w), M = _(y), q = _(M), E = _(q);
  me(E, "", {}, { "font-weight": "var(--font-medium)" });
  var O = k(E, 2);
  let L;
  var C = k(q, 2);
  C.__click = i;
  var j = k(M, 2), A = _(j);
  me(A, "", {}, { "font-weight": "var(--font-medium)" });
  var z = k(A, 2), R = _(z), I = k(y, 2), B = _(I), D = _(B), X = _(D);
  me(X, "", {}, { "font-weight": "var(--font-medium)" });
  var Y = k(X, 2), Z = _(Y), se = k(D, 2), W = _(se);
  Ki(W, {
    get marginalEffects() {
      return ft.value.marginal_effects;
    },
    get distribution() {
      return ft.value.sequence_acts_histogram;
    },
    get classes() {
      return Le.value.label_indices;
    },
    get compareToBaseProbs() {
      return l(m);
    },
    marginTop: 32,
    marginRight: 88,
    marginLeft: 80,
    marginBottom: 40,
    get width() {
      return l(u).width;
    },
    get height() {
      return l(u).height;
    },
    xAxisLabel: "Activation value",
    yAxisLabel: "Predicted label",
    showColorLegend: !0
  });
  var P = k(B, 2), N = _(P), G = _(N);
  me(G, "", {}, { "font-weight": "var(--font-medium)" });
  var fe = k(G, 2), ne = _(fe), re = k(N, 2), U = _(re);
  Ui(U, {
    get cm() {
      return ft.value.cm;
    },
    get other() {
      return Pt.value.cm;
    },
    get showDifference() {
      return l(p);
    },
    legend: "vertical",
    get width() {
      return l(b).width;
    },
    get height() {
      return l(b).height;
    },
    marginTop: s,
    marginRight: v,
    marginBottom: c,
    marginLeft: d
  });
  var F = k(P, 2), te = _(F);
  ru(te, {
    get tokenColor() {
      return l(r);
    }
  });
  var ue = k(F, 2);
  {
    var Te = (K) => {
      var ye = ou(), Q = _(ye);
      fu(Q, {
        get tokenColor() {
          return l(r);
        },
        get featureId() {
          return an.value;
        }
      }), H(K, ye);
    };
    le(ue, (K) => {
      Nr.value && K(Te);
    });
  }
  $(
    (K, ye) => {
      L = me(O, "", L, { width: `${l(n) + 1}em` }), de(R, `${K ?? ""} (${ye ?? ""} instances)`), Ee(
        I,
        1,
        cf([
          "sae-main",
          Nr.value ? "sae-grid-inference" : "sae-grid-no-inference"
        ]),
        "svelte-il95ok"
      );
    },
    [
      () => Gn(ft.value.sequence_act_rate),
      () => It(ft.value.cm.n_sequences)
    ]
  ), ir(O, () => l(a), (K) => V(a, K)), on(Z, () => l(m), (K) => V(m, K)), Xe(se, "clientWidth", (K) => V(o, K)), Xe(se, "clientHeight", (K) => V(f, K)), on(ne, () => l(p), (K) => V(p, K)), Xe(re, "clientWidth", (K) => V(g, K)), Xe(re, "clientHeight", (K) => V(h, K)), H(e, w), we();
}
Lt(["click"]);
var cu = /* @__PURE__ */ oe('<div class="sae-widget-container svelte-zqdrxr"><div class="sae-tabs-container svelte-zqdrxr"><!></div> <div class="sae-tab-content svelte-zqdrxr"><!></div></div>');
function du(e, t) {
  pe(t, !0);
  let n = /* @__PURE__ */ ee("overview");
  function r(g) {
    V(n, g, !0);
  }
  function a(g) {
    an.value = g, V(n, "detail");
  }
  var i = cu();
  let f;
  var o = _(i), u = _(o);
  Mf(u, {
    get selectedTab() {
      return l(n);
    },
    changeTab: r
  });
  var s = k(o, 2), v = _(s);
  {
    var c = (g) => {
      As(g, {});
    }, d = (g, h) => {
      {
        var b = (p) => {
          Zs(p, { onClickFeature: a });
        }, m = (p) => {
          uu(p, {});
        };
        le(
          g,
          (p) => {
            l(n) === "table" ? p(b) : p(m, !1);
          },
          h
        );
      }
    };
    le(v, (g) => {
      l(n) === "overview" ? g(c) : g(d, !1);
    });
  }
  $(() => f = me(i, "", f, {
    height: `${Fi.value ?? ""}px`,
    "--text-xs": `${ce.xs ?? ""}px`,
    "--text-sm": `${ce.sm ?? ""}px`,
    "--text-base": `${ce.base ?? ""}px`,
    "--text-lg": `${ce.lg ?? ""}px`,
    "--text-xl": `${ce.xl ?? ""}px`
  })), H(e, i), we();
}
const vu = ({ model: e, el: t }) => {
  Tf(e), hs(t);
  let n = nf(du, { target: t });
  return () => af(n);
}, hu = { render: vu };
export {
  hu as default
};
