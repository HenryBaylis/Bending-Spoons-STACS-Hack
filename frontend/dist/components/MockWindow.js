"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = MockWindow;
var _jsxRuntime = require("react/jsx-runtime");
function MockWindow(_ref) {
  var onClose = _ref.onClose,
    children = _ref.children;
  return /*#__PURE__*/(0, _jsxRuntime.jsxs)("div", {
    id: "card",
    style: {
      position: "relative"
    },
    children: [/*#__PURE__*/(0, _jsxRuntime.jsx)("button", {
      onClick: onClose,
      style: {
        position: "absolute",
        top: 4,
        right: 4
      },
      children: "\u2715"
    }), /*#__PURE__*/(0, _jsxRuntime.jsxs)("div", {
      id: "live-section",
      children: [/*#__PURE__*/(0, _jsxRuntime.jsxs)("div", {
        className: "label",
        children: [/*#__PURE__*/(0, _jsxRuntime.jsx)("span", {
          className: "dot"
        }), "Live"]
      }), /*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
        id: "live-text",
        children: "\u2014"
      })]
    }), /*#__PURE__*/(0, _jsxRuntime.jsxs)("div", {
      id: "mention-section",
      style: {
        display: "none",
        marginBottom: 10,
        borderLeft: "2px solid rgba(250,204,21,0.5)",
        paddingLeft: 8
      },
      children: [/*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
        className: "label",
        children: "Mentioned"
      }), /*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
        id: "mention-text",
        style: {
          fontSize: 12,
          color: "rgba(255,255,255,0.6)",
          lineHeight: 1.4
        }
      })]
    }), /*#__PURE__*/(0, _jsxRuntime.jsxs)("div", {
      id: "summary-section",
      children: [/*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
        className: "label",
        children: "Last summary"
      }), /*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
        id: "summary-text",
        children: "\u2014"
      })]
    }), children]
  });
}