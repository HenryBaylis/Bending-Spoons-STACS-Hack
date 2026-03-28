"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = App;
var _react = require("react");
var _FillForm = _interopRequireDefault(require("./components/FillForm"));
var _MockWindow = _interopRequireDefault(require("./components/MockWindow"));
var _ExpandedWindow = _interopRequireDefault(require("./components/ExpandedWindow"));
var _jsxRuntime = require("react/jsx-runtime");
function _interopRequireDefault(e) { return e && e.__esModule ? e : { "default": e }; }
function _slicedToArray(r, e) { return _arrayWithHoles(r) || _iterableToArrayLimit(r, e) || _unsupportedIterableToArray(r, e) || _nonIterableRest(); }
function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function _unsupportedIterableToArray(r, a) { if (r) { if ("string" == typeof r) return _arrayLikeToArray(r, a); var t = {}.toString.call(r).slice(8, -1); return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? _arrayLikeToArray(r, a) : void 0; } }
function _arrayLikeToArray(r, a) { (null == a || a > r.length) && (a = r.length); for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e]; return n; }
function _iterableToArrayLimit(r, l) { var t = null == r ? null : "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t["return"] && (u = t["return"](), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }
function _arrayWithHoles(r) { if (Array.isArray(r)) return r; }
function App() {
  var _useState = (0, _react.useState)("form"),
    _useState2 = _slicedToArray(_useState, 2),
    stage = _useState2[0],
    setStage = _useState2[1]; // 'form' | 'mock' | 'expanded'
  var _useState3 = (0, _react.useState)(""),
    _useState4 = _slicedToArray(_useState3, 2),
    question = _useState4[0],
    setQuestion = _useState4[1];
  var _useState5 = (0, _react.useState)(""),
    _useState6 = _slicedToArray(_useState5, 2),
    answer = _useState6[0],
    setAnswer = _useState6[1];
  var _useState7 = (0, _react.useState)(null),
    _useState8 = _slicedToArray(_useState7, 2),
    followUp = _useState8[0],
    setFollowUp = _useState8[1];
  var containerRef = (0, _react.useRef)(null);
  var handleClose = function handleClose() {
    var _window$api;
    return (_window$api = window.api) === null || _window$api === void 0 ? void 0 : _window$api.closeWindow();
  };
  (0, _react.useEffect)(function () {
    if (stage === "form") return;
    var el = containerRef.current;
    if (!el) return;
    var observer = new ResizeObserver(function () {
      var _window$api2;
      (_window$api2 = window.api) === null || _window$api2 === void 0 || _window$api2.resizeWindow(el.offsetHeight);
    });
    observer.observe(el);
    return function () {
      return observer.disconnect();
    };
  }, [stage]);
  (0, _react.useEffect)(function () {
    var _window$api3, _window$api4, _window$api5;
    (_window$api3 = window.api) === null || _window$api3 === void 0 || _window$api3.onQuestion(function (data) {
      setQuestion(data.transcript);
      setAnswer(data.answer);
      setFollowUp(data.follow_up || null);
      setStage("expanded");
    });
    (_window$api4 = window.api) === null || _window$api4 === void 0 || _window$api4.onDismiss(function () {
      return setStage("mock");
    });
    (_window$api5 = window.api) === null || _window$api5 === void 0 || _window$api5.onStopMeeting(function () {
      return setStage("form");
    });
  }, []);
  var handleStart = function handleStart(profile) {
    window.api.startMeeting(profile);
    setStage("mock");
  };
  if (stage === "form") {
    return /*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
      ref: containerRef,
      children: /*#__PURE__*/(0, _jsxRuntime.jsx)(_FillForm["default"], {
        onSubmit: handleStart,
        onClose: handleClose
      })
    });
  }
  return /*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
    ref: containerRef,
    children: /*#__PURE__*/(0, _jsxRuntime.jsx)(_MockWindow["default"], {
      onClose: handleClose,
      children: stage === "expanded" && /*#__PURE__*/(0, _jsxRuntime.jsx)(_ExpandedWindow["default"], {
        question: question,
        answer: answer,
        followUp: followUp,
        onDismiss: function onDismiss() {
          var _window$api6;
          setStage("mock");
          (_window$api6 = window.api) === null || _window$api6 === void 0 || _window$api6.dismiss();
        }
      })
    })
  });
}