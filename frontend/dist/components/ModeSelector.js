"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = ModeSelector;
var _jsxRuntime = require("react/jsx-runtime");
function _toConsumableArray(r) { return _arrayWithoutHoles(r) || _iterableToArray(r) || _unsupportedIterableToArray(r) || _nonIterableSpread(); }
function _nonIterableSpread() { throw new TypeError("Invalid attempt to spread non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function _unsupportedIterableToArray(r, a) { if (r) { if ("string" == typeof r) return _arrayLikeToArray(r, a); var t = {}.toString.call(r).slice(8, -1); return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? _arrayLikeToArray(r, a) : void 0; } }
function _iterableToArray(r) { if ("undefined" != typeof Symbol && null != r[Symbol.iterator] || null != r["@@iterator"]) return Array.from(r); }
function _arrayWithoutHoles(r) { if (Array.isArray(r)) return _arrayLikeToArray(r); }
function _arrayLikeToArray(r, a) { (null == a || a > r.length) && (a = r.length); for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e]; return n; }
var MODES = ["Assertiveness", "Promise Maker", "Debate", "AFK"];
function ModeSelector(_ref) {
  var modes = _ref.modes,
    onChange = _ref.onChange;
  var toggle = function toggle(m) {
    if (modes.includes(m)) {
      onChange(modes.filter(function (x) {
        return x !== m;
      }));
    } else {
      onChange([].concat(_toConsumableArray(modes), [m]));
    }
  };
  return /*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
    style: {
      display: "flex",
      gap: 6,
      marginBottom: 12
    },
    children: MODES.map(function (m) {
      var active = modes.includes(m);
      return /*#__PURE__*/(0, _jsxRuntime.jsx)("button", {
        onClick: function onClick() {
          return toggle(m);
        },
        style: {
          flex: 1,
          background: active ? "rgba(99,102,241,0.35)" : "rgba(255,255,255,0.06)",
          border: active ? "1px solid rgba(99,102,241,0.7)" : "1px solid rgba(255,255,255,0.1)",
          color: active ? "#fff" : "rgba(255,255,255,0.45)",
          borderRadius: 7,
          fontSize: 10,
          padding: "3px 0",
          cursor: "pointer",
          fontWeight: active ? 600 : 400,
          transition: "all 0.15s"
        },
        children: m
      }, m);
    })
  });
}