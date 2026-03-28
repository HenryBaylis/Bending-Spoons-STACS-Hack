"use strict";

function _typeof(o) { "@babel/helpers - typeof"; return _typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, _typeof(o); }
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = App;
var _react = _interopRequireWildcard(require("react"));
function _interopRequireWildcard(e, t) { if ("function" == typeof WeakMap) var r = new WeakMap(), n = new WeakMap(); return (_interopRequireWildcard = function _interopRequireWildcard(e, t) { if (!t && e && e.__esModule) return e; var o, i, f = { __proto__: null, "default": e }; if (null === e || "object" != _typeof(e) && "function" != typeof e) return f; if (o = t ? n : r) { if (o.has(e)) return o.get(e); o.set(e, f); } for (var _t in e) "default" !== _t && {}.hasOwnProperty.call(e, _t) && ((i = (o = Object.defineProperty) && Object.getOwnPropertyDescriptor(e, _t)) && (i.get || i.set) ? o(f, _t, i) : f[_t] = e[_t]); return f; })(e, t); }
function _slicedToArray(r, e) { return _arrayWithHoles(r) || _iterableToArrayLimit(r, e) || _unsupportedIterableToArray(r, e) || _nonIterableRest(); }
function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function _unsupportedIterableToArray(r, a) { if (r) { if ("string" == typeof r) return _arrayLikeToArray(r, a); var t = {}.toString.call(r).slice(8, -1); return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? _arrayLikeToArray(r, a) : void 0; } }
function _arrayLikeToArray(r, a) { (null == a || a > r.length) && (a = r.length); for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e]; return n; }
function _iterableToArrayLimit(r, l) { var t = null == r ? null : "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t["return"] && (u = t["return"](), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }
function _arrayWithHoles(r) { if (Array.isArray(r)) return r; }
var _window$require = window.require("electron"),
  ipcRenderer = _window$require.ipcRenderer; // Use contextBridge in production for safety

function App() {
  var _useState = (0, _react.useState)("—"),
    _useState2 = _slicedToArray(_useState, 2),
    liveText = _useState2[0],
    setLiveText = _useState2[1];
  var _useState3 = (0, _react.useState)("—"),
    _useState4 = _slicedToArray(_useState3, 2),
    summaryText = _useState4[0],
    setSummaryText = _useState4[1];
  var _useState5 = (0, _react.useState)({
      transcript: "",
      answer: ""
    }),
    _useState6 = _slicedToArray(_useState5, 2),
    question = _useState6[0],
    setQuestion = _useState6[1];
  var _useState7 = (0, _react.useState)(false),
    _useState8 = _slicedToArray(_useState7, 2),
    questionVisible = _useState8[0],
    setQuestionVisible = _useState8[1];
  (0, _react.useEffect)(function () {
    ipcRenderer.on("transcript", function (_, data) {
      return setLiveText(data.text);
    });
    ipcRenderer.on("summary", function (_, data) {
      return setSummaryText(data.text);
    });
    ipcRenderer.on("question", function (_, data) {
      setQuestion({
        transcript: data.transcript,
        answer: data.answer
      });
      setQuestionVisible(true);
    });
    ipcRenderer.on("dismiss", function () {
      return setQuestionVisible(false);
    });
    return function () {
      ipcRenderer.removeAllListeners("transcript");
      ipcRenderer.removeAllListeners("summary");
      ipcRenderer.removeAllListeners("question");
      ipcRenderer.removeAllListeners("dismiss");
    };
  }, []);
  var dismiss = function dismiss() {
    setQuestionVisible(false);
    ipcRenderer.send("dismiss");
  };
  return /*#__PURE__*/_react["default"].createElement("div", {
    id: "card"
  }, /*#__PURE__*/_react["default"].createElement("div", {
    id: "live-section"
  }, /*#__PURE__*/_react["default"].createElement("div", {
    className: "label"
  }, /*#__PURE__*/_react["default"].createElement("span", {
    className: "dot"
  }), " Live"), /*#__PURE__*/_react["default"].createElement("div", {
    id: "live-text"
  }, liveText)), /*#__PURE__*/_react["default"].createElement("div", {
    id: "summary-section"
  }, /*#__PURE__*/_react["default"].createElement("div", {
    className: "label"
  }, "Last summary"), /*#__PURE__*/_react["default"].createElement("div", {
    id: "summary-text"
  }, summaryText)), questionVisible && /*#__PURE__*/_react["default"].createElement("div", {
    id: "question-section",
    className: "visible"
  }, /*#__PURE__*/_react["default"].createElement("div", {
    className: "label"
  }, "Someone's asking you"), /*#__PURE__*/_react["default"].createElement("div", {
    id: "transcript-text"
  }, "\"", question.transcript, "\""), /*#__PURE__*/_react["default"].createElement("div", {
    className: "label",
    style: {
      marginBottom: "6px"
    }
  }, "Suggested response"), /*#__PURE__*/_react["default"].createElement("div", {
    id: "answer-text"
  }, question.answer), /*#__PURE__*/_react["default"].createElement("button", {
    onClick: dismiss
  }, "Dismiss")));
}