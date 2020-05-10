module.exports = {
  "plugins": [
    "html"
  ],
  env: {
    browser: true,
    es6: true,
    commonjs: true,
    jquery: true
  },
  extends: [
    'airbnb-base',
  ],
  globals: {
    Atomics: 'readonly',
    SharedArrayBuffer: 'readonly',
  },
  parserOptions: {
    ecmaVersion: 2018,
  },
  rules: {
    // Indent
    "indent": [2, "tab"],
    "no-tabs": ["error", {"allowIndentationTabs": true}],

    "space-before-function-paren": 0,

    "no-restricted-syntax" : 0,

    "no-var": 0,

    // remove react errors
    "react/jsx-indent-props" : 0,
    "react/jsx-indent" : 0,

    "no-undef" : 0,

    "no-console" : 0,
    "no-debugger" :0
  },
};