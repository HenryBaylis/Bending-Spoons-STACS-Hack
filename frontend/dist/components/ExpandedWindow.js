"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = ExpandedWindow;
var _jsxRuntime = require("react/jsx-runtime");
function ExpandedWindow(_ref) {
  var question = _ref.question,
    answer = _ref.answer,
    followUp = _ref.followUp,
    modes = _ref.modes,
    onDismiss = _ref.onDismiss;
  return /*#__PURE__*/(0, _jsxRuntime.jsxs)("div", {
    id: "question-section",
    className: "visible",
    children: [/*#__PURE__*/(0, _jsxRuntime.jsxs)("div", {
      style: {
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        marginBottom: 6
      },
      children: [/*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
        className: "label",
        style: {
          margin: 0
        },
        children: "Someone's asking you"
      }), modes && modes.length > 0 && /*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
        style: {
          display: "flex",
          gap: 4
        },
        children: modes.map(function (m) {
          return /*#__PURE__*/(0, _jsxRuntime.jsx)("span", {
            style: {
              fontSize: 10,
              background: "rgba(99,102,241,0.25)",
              border: "1px solid rgba(99,102,241,0.5)",
              borderRadius: 5,
              padding: "2px 7px",
              color: "rgba(180,180,255,0.9)",
              fontWeight: 600
            },
            children: m
          }, m);
        })
      })]
    }), /*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
      id: "transcript-text",
      children: question
    }), /*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
      className: "label",
      style: {
        marginBottom: 6
      },
      children: "Suggested response"
    }), /*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
      id: "answer-text",
      children: answer
    }), followUp && /*#__PURE__*/(0, _jsxRuntime.jsxs)("div", {
      style: {
        marginTop: 10,
        borderTop: "1px solid rgba(255,255,255,0.06)",
        paddingTop: 8
      },
      children: [/*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
        className: "label",
        style: {
          marginBottom: 4
        },
        children: "Possible follow-up"
      }), /*#__PURE__*/(0, _jsxRuntime.jsx)("div", {
        style: {
          fontSize: 13,
          color: "rgba(255,255,255,0.5)",
          lineHeight: 1.4,
          fontStyle: "italic"
        },
        children: followUp
      })]
    }), /*#__PURE__*/(0, _jsxRuntime.jsx)("button", {
      onClick: onDismiss,
      style: {
        marginTop: 12
      },
      children: "Dismiss"
    })]
  });
}