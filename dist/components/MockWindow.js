"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = MockWindow;
function MockWindow(_ref) {
  var onClose = _ref.onClose,
    children = _ref.children;
  return /*#__PURE__*/React.createElement("div", {
    id: "card",
    style: {
      position: "relative"
    }
  }, /*#__PURE__*/React.createElement("button", {
    onClick: onClose,
    style: {
      position: "absolute",
      top: 4,
      right: 4
    }
  }, "\u2715"), /*#__PURE__*/React.createElement("div", {
    id: "live-section"
  }, /*#__PURE__*/React.createElement("div", {
    className: "label"
  }, /*#__PURE__*/React.createElement("span", {
    className: "dot"
  }), "Live"), /*#__PURE__*/React.createElement("div", {
    id: "live-text"
  }, "\u2014")), /*#__PURE__*/React.createElement("div", {
    id: "mention-section",
    style: {
      display: "none",
      marginBottom: 10,
      borderLeft: "2px solid rgba(250,204,21,0.5)",
      paddingLeft: 8
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "label"
  }, "Mentioned"), /*#__PURE__*/React.createElement("div", {
    id: "mention-text",
    style: {
      fontSize: 12,
      color: "rgba(255,255,255,0.6)",
      lineHeight: 1.4
    }
  })), /*#__PURE__*/React.createElement("div", {
    id: "summary-section"
  }, /*#__PURE__*/React.createElement("div", {
    className: "label"
  }, "Last summary"), /*#__PURE__*/React.createElement("div", {
    id: "summary-text"
  }, "\u2014")), children);
}