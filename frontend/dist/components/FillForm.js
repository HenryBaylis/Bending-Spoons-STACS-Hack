"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = FillForm;
var _react = require("react");
var _jsxRuntime = require("react/jsx-runtime");
function _slicedToArray(r, e) { return _arrayWithHoles(r) || _iterableToArrayLimit(r, e) || _unsupportedIterableToArray(r, e) || _nonIterableRest(); }
function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function _unsupportedIterableToArray(r, a) { if (r) { if ("string" == typeof r) return _arrayLikeToArray(r, a); var t = {}.toString.call(r).slice(8, -1); return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? _arrayLikeToArray(r, a) : void 0; } }
function _arrayLikeToArray(r, a) { (null == a || a > r.length) && (a = r.length); for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e]; return n; }
function _iterableToArrayLimit(r, l) { var t = null == r ? null : "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t["return"] && (u = t["return"](), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }
function _arrayWithHoles(r) { if (Array.isArray(r)) return r; }
function FillForm(_ref) {
  var onSubmit = _ref.onSubmit;
  var _useState = (0, _react.useState)(""),
    _useState2 = _slicedToArray(_useState, 2),
    name = _useState2[0],
    setName = _useState2[1];
  var _useState3 = (0, _react.useState)(""),
    _useState4 = _slicedToArray(_useState3, 2),
    role = _useState4[0],
    setRole = _useState4[1];
  var _useState5 = (0, _react.useState)(null),
    _useState6 = _slicedToArray(_useState5, 2),
    contextFile = _useState6[0],
    setContextFile = _useState6[1];
  var _useState7 = (0, _react.useState)(false),
    _useState8 = _slicedToArray(_useState7, 2),
    submitted = _useState8[0],
    setSubmitted = _useState8[1];
  var handleFile = function handleFile(e) {
    var file = e.target.files[0];
    if (file) setContextFile(file.path);
  };
  var handleSubmit = function handleSubmit() {
    setSubmitted(true);
    if (!name.trim() || !role.trim()) return;
    onSubmit({
      name: name,
      role: role,
      contextFile: contextFile
    });
  };
  return /*#__PURE__*/(0, _jsxRuntime.jsxs)("div", {
    children: [/*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
      className: "label",
      children: "Setup"
    }), /*#__PURE__*/(0, _jsxRuntime.jsxs)("div", {
      style: {
        marginBottom: 8
      },
      children: [/*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
        className: "label",
        children: "Name"
      }), /*#__PURE__*/(0, _jsxRuntime.jsx)("input", {
        name: "nameInput",
        value: name,
        onChange: function onChange(e) {
          return setName(e.target.value);
        },
        style: {
          WebkitAppRegion: "no-drag",
          background: "rgba(255,255,255,0.08)",
          border: "1px solid rgba(255,255,255,0.12)",
          borderRadius: 6,
          color: "#fff",
          fontSize: 12,
          padding: "4px 8px",
          width: "100%"
        }
      }), submitted && !name.trim() && /*#__PURE__*/(0, _jsxRuntime.jsx)("span", {
        style: {
          color: "#f87171",
          fontSize: 11
        },
        children: "Required"
      })]
    }), /*#__PURE__*/(0, _jsxRuntime.jsxs)("div", {
      style: {
        marginBottom: 8
      },
      children: [/*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
        className: "label",
        children: "Role"
      }), /*#__PURE__*/(0, _jsxRuntime.jsx)("input", {
        name: "roleInput",
        value: role,
        onChange: function onChange(e) {
          return setRole(e.target.value);
        },
        style: {
          WebkitAppRegion: "no-drag",
          background: "rgba(255,255,255,0.08)",
          border: "1px solid rgba(255,255,255,0.12)",
          borderRadius: 6,
          color: "#fff",
          fontSize: 12,
          padding: "4px 8px",
          width: "100%"
        }
      }), submitted && !role.trim() && /*#__PURE__*/(0, _jsxRuntime.jsx)("span", {
        style: {
          color: "#f87171",
          fontSize: 11
        },
        children: "Required"
      })]
    }), /*#__PURE__*/(0, _jsxRuntime.jsxs)("div", {
      style: {
        marginBottom: 8
      },
      children: [/*#__PURE__*/(0, _jsxRuntime.jsxs)("div", {
        className: "label",
        children: ["Context File ", /*#__PURE__*/(0, _jsxRuntime.jsx)("span", {
          style: {
            textTransform: 'none',
            opacity: 0.5
          },
          children: "(optional \u2014 .txt, .md, .pdf)"
        })]
      }), /*#__PURE__*/(0, _jsxRuntime.jsx)("input", {
        type: "file",
        accept: ".txt,.md,.pdf",
        onChange: handleFile,
        style: {
          WebkitAppRegion: "no-drag",
          color: "rgba(255,255,255,0.6)",
          fontSize: 11,
          width: "100%"
        }
      }), contextFile && /*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
        style: {
          fontSize: 10,
          color: "rgba(255,255,255,0.4)",
          marginTop: 2
        },
        children: contextFile
      })]
    }), /*#__PURE__*/(0, _jsxRuntime.jsx)("button", {
      className: "btn-primary",
      onClick: handleSubmit,
      children: "Start"
    })]
  });
}