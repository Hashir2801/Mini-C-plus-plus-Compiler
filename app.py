from flask import Flask, request, render_template_string
from compiler_core import lexical_analyzer, syntax_analyzer, semantic_analyzer, symbol_table

app = Flask(__name__)

SAMPLE_CODE = """#include<iostream>
using namespace std;

int main()
{
    int num1 = 5;
    int num2 = 10;
    int sum = num1 + num2;

    cout << sum << endl;

    return 0;
}"""

HTML = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mini C++ Compiler</title>
<style>
*{box-sizing:border-box}
body{margin:0;font-family:Inter,Arial,sans-serif;background:#0f172a;color:#e5e7eb}
.top{background:#111827;border-bottom:1px solid #273449;padding:22px 28px}
.top h1{margin:0;font-size:32px}.top p{margin:7px 0 0;color:#94a3b8}
.wrap{max-width:1450px;margin:auto;padding:24px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.card{background:#1e293b;border:1px solid #334155;border-radius:18px;padding:20px}
h2,h3{margin-top:0}
textarea{width:100%;height:520px;background:#020617;color:#e5e7eb;border:1px solid #334155;border-radius:12px;padding:16px;font-family:Consolas,monospace;font-size:14px;resize:vertical}
.btns{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:14px}
button{border:0;border-radius:10px;padding:12px 10px;color:white;font-weight:700;cursor:pointer}
.lex{background:#2563eb}.syn{background:#7c3aed}.sem{background:#0891b2}.full{background:#16a34a}
.tabs{display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap}
.tab{background:#0f172a;border:1px solid #334155;color:#cbd5e1;padding:9px 13px;border-radius:9px;text-decoration:none}
.tab.active{background:#2563eb;color:white}
.panel{display:none}.panel.active{display:block}
.output{white-space:pre-wrap;background:#020617;border:1px solid #334155;border-radius:12px;padding:16px;min-height:260px;font-family:Consolas,monospace}
table{width:100%;border-collapse:collapse;background:#111827;border-radius:10px;overflow:hidden}
th,td{padding:10px;border-bottom:1px solid #263448;text-align:left}
th{background:#172033}
.badge{display:inline-block;padding:4px 8px;border-radius:999px;background:#263449;color:#bae6fd;font-size:12px}
.success{background:#12351f;border:1px solid #1d6a39;padding:12px;border-radius:10px;margin-bottom:12px}
.error{background:#4a2028;border:1px solid #8a3340;padding:12px;border-radius:10px;margin-bottom:12px}
.small{color:#94a3b8;font-size:13px}
@media(max-width:980px){.grid{grid-template-columns:1fr}.btns{grid-template-columns:1fr 1fr}}
</style>
</head>
<body>
<div class="top">
<h1>Mini C++ Compiler</h1>
<p>Lexical Analysis · Syntax Analysis · Semantic Analysis · Symbol Table</p>
</div>

<div class="wrap">
<div class="grid">
<div class="card">
<h2>Source Code</h2>
<form method="post">
<textarea name="code" spellcheck="false">{{ code }}</textarea>
<div class="btns">
<button class="lex" name="action" value="lexical">Lexical Analysis</button>
<button class="syn" name="action" value="syntax">Syntax Analysis</button>
<button class="sem" name="action" value="semantic">Semantic Analysis</button>
<button class="full" name="action" value="full">Run Full Compiler</button>
</div>
</form>
<p class="small">This educational compiler validates the supported C++ subset implemented in the project; it does not compile arbitrary C++ into machine code.</p>
</div>

<div class="card">
<div class="tabs">
<a class="tab {{ 'active' if active_tab=='tokens' else '' }}" href="#tokens">Tokens</a>
<a class="tab {{ 'active' if active_tab=='output' else '' }}" href="#output">Compiler Output</a>
<a class="tab {{ 'active' if active_tab=='symbols' else '' }}" href="#symbols">Symbol Table</a>
</div>

<div id="tokens" class="panel {{ 'active' if active_tab=='tokens' else '' }}">
<h3>Tokens <span class="badge">{{ tokens|length if tokens else 0 }}</span></h3>
{% if tokens %}
<table><thead><tr><th>Lexeme</th><th>Token Type</th></tr></thead><tbody>
{% for lexeme, token_type in tokens %}
<tr><td>{{ lexeme }}</td><td>{{ token_type }}</td></tr>
{% endfor %}
</tbody></table>
{% else %}
<div class="output">Run lexical analysis to view generated tokens.</div>
{% endif %}
</div>

<div id="output" class="panel {{ 'active' if active_tab=='output' else '' }}">
<h3>Compiler Output</h3>
{% if status == 'success' %}<div class="success">Analysis completed successfully.</div>{% elif status == 'error' %}<div class="error">The compiler found one or more issues.</div>{% endif %}
<div class="output">{{ output if output else 'Run syntax, semantic, or full compiler analysis to view results.' }}</div>
</div>

<div id="symbols" class="panel {{ 'active' if active_tab=='symbols' else '' }}">
<h3>Symbol Table</h3>
{% if symbols %}
<table><thead><tr><th>Name</th><th>Type</th><th>Value</th><th>Scope</th><th>Memory</th></tr></thead><tbody>
{% for item in symbols %}
<tr><td>{{ item.Name }}</td><td>{{ item.Type }}</td><td>{{ item.Value }}</td><td>{{ item.Scope }}</td><td>{{ item.Memory }}</td></tr>
{% endfor %}
</tbody></table>
{% else %}
<div class="output">Run semantic analysis or the full compiler to generate the symbol table.</div>
{% endif %}
</div>
</div>
</div>
</div>
</body>
</html>
"""

def format_result(title, lines, status_text):
    text = [title, "-" * 48]
    text.extend(lines)
    text.append("")
    text.append(status_text)
    return "\n".join(text)

@app.route("/", methods=["GET", "POST"])
def home():
    code = SAMPLE_CODE
    tokens = []
    symbols = []
    output = ""
    status = None
    active_tab = "output"

    if request.method == "POST":
        code = request.form.get("code", "").strip()
        action = request.form.get("action", "full")

        if not code:
            return render_template_string(
                HTML, code="", tokens=[], symbols=[], output="Please enter C++ source code.",
                status="error", active_tab="output"
            )

        if action == "lexical":
            tokens = lexical_analyzer(code)
            output = f"Lexical analysis completed. {len(tokens)} token(s) generated."
            status = "success"
            active_tab = "tokens"

        elif action == "syntax":
            ok, result = syntax_analyzer(code)
            output = format_result(
                "SYNTAX ANALYSIS RESULT",
                result,
                "Status: Valid Syntax" if ok else "Status: Invalid Syntax"
            )
            status = "success" if ok else "error"
            active_tab = "output"

        elif action == "semantic":
            syntax_ok, syntax_result = syntax_analyzer(code)
            if not syntax_ok:
                output = format_result(
                    "SEMANTIC ANALYSIS",
                    ["Semantic analysis cannot run because syntax has errors."] + syntax_result,
                    "Status: Semantic analysis stopped"
                )
                status = "error"
            else:
                ok, result = semantic_analyzer(code)
                symbols = list(symbol_table.table)
                output = format_result(
                    "SEMANTIC ANALYSIS RESULT",
                    result,
                    "Status: Semantic Correct" if ok else "Status: Semantic Error"
                )
                status = "success" if ok else "error"
            active_tab = "output"

        else:
            tokens = lexical_analyzer(code)
            syntax_ok, syntax_result = syntax_analyzer(code)
            text = [
                "MINI C++ COMPILER OUTPUT",
                "=" * 50,
                "",
                "1. LEXICAL ANALYSIS",
                "-" * 30,
                f"{len(tokens)} token(s) generated.",
                "",
                "2. SYNTAX ANALYSIS",
                "-" * 30,
                *syntax_result
            ]

            if not syntax_ok:
                text += ["", "Compilation stopped due to syntax errors."]
                output = "\n".join(text)
                status = "error"
            else:
                semantic_ok, semantic_result = semantic_analyzer(code)
                symbols = list(symbol_table.table)
                text += [
                    "",
                    "3. SEMANTIC ANALYSIS",
                    "-" * 30,
                    *semantic_result,
                    "",
                    "Final Result: Code compiled successfully."
                    if semantic_ok else
                    "Final Result: Code has semantic errors."
                ]
                output = "\n".join(text)
                status = "success" if semantic_ok else "error"

            active_tab = "output"

    return render_template_string(
        HTML,
        code=code,
        tokens=tokens,
        symbols=symbols,
        output=output,
        status=status,
        active_tab=active_tab
    )

if __name__ == "__main__":
    app.run(debug=True)