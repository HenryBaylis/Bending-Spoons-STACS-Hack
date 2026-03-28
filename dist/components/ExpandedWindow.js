"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = ExpandedWindow;
function ExpandedWindow(_ref) {
  var question = _ref.question,
    answer = _ref.answer,
    followUp = _ref.followUp,
    onDismiss = _ref.onDismiss;
  return /*#__PURE__*/React.createElement("div", {
    id: "question-section",
    className: "visible"
  }, /*#__PURE__*/React.createElement("div", {
    className: "label"
  }, "Someone's asking you"), /*#__PURE__*/React.createElement("div", {
    id: "transcript-text"
  }, question), /*#__PURE__*/React.createElement("div", {
    className: "label",
    style: {
      marginBottom: 6
    }
  }, "Suggested response"), /*#__PURE__*/React.createElement("div", {
    id: "answer-text"
  }, answer), followUp && /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 10,
      borderTop: "1px solid rgba(255,255,255,0.06)",
      paddingTop: 8
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "label",
    style: {
      marginBottom: 4
    }
  }, "Possible follow-up"), /*#__PURE__*/React.createElement("div", {
    style: {
      fontSize: 13,
      color: "rgba(255,255,255,0.5)",
      lineHeight: 1.4,
      fontStyle: "italic"
    }
  }, followUp)), /*#__PURE__*/React.createElement("button", {
    onClick: onDismiss,
    style: {
      marginTop: 12
    }
  }, "Dismiss"));
}