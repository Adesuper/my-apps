import{r as i,j as t}from"./index-CWTewShq.js";const b="https://cdn.jsdelivr.net/pyodide/v0.26.4/full/",w=`
importScripts("${b}pyodide.js");
let py = null;
self.onmessage = async (e) => {
  const { code, tests } = e.data;
  try {
    if (!py) py = await loadPyodide({ indexURL: "${b}" });
    let out = "";
    py.setStdout({ batched: (s) => { out += s + "\\n"; } });
    py.setStderr({ batched: (s) => { out += s + "\\n"; } });
    const ns = py.globals.get("dict")();
    let error = null;
    try { await py.runPythonAsync(code, { globals: ns }); }
    catch (err) { error = String(err.message || err).split("\\n").filter(Boolean).slice(-1)[0]; }
    const results = [];
    if (!error) for (const t of tests || []) {
      try { await py.runPythonAsync(t.code, { globals: ns }); results.push({ label: t.label, ok: true }); }
      catch (err) { results.push({ label: t.label, ok: false }); }
    }
    ns.destroy();
    self.postMessage({ out, error, results });
  } catch (err) {
    self.postMessage({ out: "", error: "Could not start Python: " + (err.message || err), results: [] });
  }
};`;let d=null;function O(){return d||(d=new Worker(URL.createObjectURL(new Blob([w],{type:"text/javascript"})))),d}function N(r,p=[],a=2e4){return new Promise(o=>{const l=O(),s=setTimeout(()=>{l.terminate(),d=null,o({out:"",error:"Your program ran for too long. Is there a loop that never stops?",results:[]})},a);l.onmessage=c=>{clearTimeout(s),o(c.data)},l.postMessage({code:r,tests:p})})}function R({ch:r,onSolved:p}){const a="mcc-code-"+r.id,[o,l]=i.useState(()=>{try{return localStorage.getItem(a)||r.starter}catch{return r.starter}}),[s,c]=i.useState(null),[m,g]=i.useState(!1),[x,j]=i.useState(!0);function y(e){l(e);try{localStorage.setItem(a,e)}catch{}}function k(e){if(e.key!=="Tab")return;e.preventDefault();const n=e.currentTarget,u=n.selectionStart,h=n.selectionEnd;y(o.slice(0,u)+"    "+o.slice(h)),requestAnimationFrame(()=>{n.selectionStart=n.selectionEnd=u+4})}async function v(){g(!0);const e=await N(o,r.tests||[]);c(e),g(!1),j(!1);const n=r.expectOutput==null||e.out.trim().replace(/\s+\n/g,`
`)===r.expectOutput.trim(),u=e.results.every(h=>h.ok);!e.error&&n&&u&&p()}const f=s&&r.expectOutput!=null?s.out.trim().replace(/\s+\n/g,`
`)===r.expectOutput.trim():null,S=s&&!s.error&&f!==!1&&s.results.every(e=>e.ok);return t.jsxs("div",{children:[t.jsx("textarea",{className:"code",spellCheck:!1,value:o,onChange:e=>y(e.target.value),onKeyDown:k,"aria-label":"Python code"}),t.jsxs("div",{className:"row",children:[t.jsx("button",{className:"btn primary big",onClick:v,disabled:m,children:m?x?"Starting Python…":"Running…":"▶ Run my code"}),t.jsx("button",{className:"btn",onClick:()=>{y(r.starter),c(null)},children:"Start over"})]}),m&&x&&t.jsx("p",{className:"muted",children:"The first run downloads Python (about 10 seconds). After that it's quick."}),s&&t.jsxs(t.Fragment,{children:[t.jsx("h3",{style:{marginTop:14},children:"Output"}),t.jsxs("pre",{className:"out",children:[s.out||(s.error?"":"(nothing printed)"),s.error?`
⚠ ${s.error}`:""]}),r.expectOutput!=null&&!s.error&&(f?t.jsx("div",{className:"ok",children:"✓ The output is exactly right."}):t.jsxs("div",{className:"err",children:["The output isn't what we expected yet. Expected:",t.jsx("pre",{className:"out",style:{marginBottom:0},children:r.expectOutput})]})),s.results.length>0&&t.jsxs("div",{className:"card",style:{marginTop:8},children:[t.jsx("h3",{children:"Checks"}),s.results.map(e=>t.jsxs("div",{children:[e.ok?"✅":"❌"," ",e.label]},e.label))]}),S&&t.jsx("div",{className:"ok",children:"🎉 Challenge complete! Great programming."})]})]})}export{R as default};
