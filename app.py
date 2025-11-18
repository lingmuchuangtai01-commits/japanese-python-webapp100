from flask import Flask, request, render_template_string, session
import io
import contextlib
import builtins

app = Flask(__name__)
app.secret_key = "nihongo-python-secret"


# --------------------------------
# 🔤 日本語 → Python 変換マップ
# --------------------------------
JP_TO_PY = {
    "表示": "print",
    "もし": "if",
    "でなければ": "else",
    "繰り返す": "for",
    "範囲": "range",
    "入力": "input",

    # 代入演算子（新規追加）
    "イコール": "=",

    "を足す": "+=",
    "を引く": "-=",
    "を掛ける": "*=",
    "を割る": "/=",
    "等しい": "==",
    "以上": ">=",
    "以下": "<=",
    "大きい": ">",
    "小さい": "<",

    "かつ": "and",
    "または": "or",
    "真": "True",
    "偽": "False",

    "終了": "break",
    "続ける": "continue",

    "関数": "def",
    "戻す": "return",

    "リスト": "list",
    "追加": "append",
    "削除": "remove",
    "長さ": "len",

    "インポート": "import",
    "時間": "time",
    "待つ": "sleep",

    "ランダム": "random",
    "から選ぶ": "choice",

    "辞書": "dict",
    "キー": "keys",
    "値": "values",
}


# --------------------------------
# 🧪 実用例（全コマンド対応）
# --------------------------------
EXAMPLE_MAP = {
    "表示": '表示("こんにちは") → 結果：こんにちは',
    "もし": 'もし x イコール 5: → 結果：条件が真なら中が実行',
    "でなければ": 'でなければ: → 結果：条件が偽なら中が実行',
    "繰り返す": '繰り返す i 範囲(3): → 結果：0 1 2 が順番に出る',
    "範囲": '範囲(0, 3) → 結果：[0,1,2]',
    "入力": '名前 イコール 入力("名前：") → 結果：入力された文字',
    "イコール": 'x イコール 10 → 結果：x に 10 が入る',
    "を足す": 'x を足す 1 → 結果：x に 1 加算',
    "を引く": 'x を引く 1 → 結果：x から 1 減算',
    "を掛ける": 'x を掛ける 2 → 結果：x が 2倍',
    "を割る": 'x を割る 2 → 結果：x が 半分',
    "等しい": 'もし x 等しい 10: → 結果：x が10なら実行',
    "以上": 'もし x 以上 5: → 結果：x >= 5 なら実行',
    "以下": 'もし x 以下 5: → 結果：x <= 5 なら実行',
    "大きい": 'もし x 大きい 5: → 結果：x > 5 なら実行',
    "小さい": 'もし x 小さい 5: → 結果：x < 5 なら実行',
    "かつ": 'もし a かつ b: → 結果：両方真なら実行',
    "または": 'もし a または b: → 結果：どちらか真なら実行',
    "真": 'flag イコール 真 → 結果：True が入る',
    "偽": 'flag イコール 偽 → 結果：False が入る',
    "終了": '終了 → 結果：ループを抜ける',
    "続ける": '続ける → 結果：次の繰り返しへ進む',
    "関数": '関数 あいさつ(): → 結果：関数が定義される',
    "戻す": '戻す x → 結果：関数の戻り値になる',
    "リスト": 'nums イコール リスト([1,2,3]) → 結果：[1,2,3]',
    "追加": 'nums.追加(4) → 結果：[1,2,3,4]',
    "削除": 'nums.削除(2) → 結果：[1,3]',
    "長さ": '長さ([1,2,3]) → 結果：3',
    "インポート": 'インポート random → 結果：randomが使える',
    "時間": 'インポート 時間 → 結果：time が使える',
    "待つ": '待つ(1) → 結果：1秒待つ',
    "ランダム": 'ランダム.から選ぶ([1,2,3]) → 結果：どれか1つ',
    "から選ぶ": 'ランダム.から選ぶ([1,2,3]) → 結果：どれか1つ',
    "辞書": 'd イコール 辞書({"a":1}) → 結果：{"a":1}',
    "キー": 'd.キー() → 結果：キー一覧',
    "値": 'd.値() → 結果：値一覧',
}

def example(jp):
    return EXAMPLE_MAP.get(jp, "（例なし）")


# --------------------------------
# 🔄 日本語 → Python コード変換
# --------------------------------
def translate(jp_code: str) -> str:
    py_code = jp_code
    for jp, py in JP_TO_PY.items():
        py_code = py_code.replace(jp, py)
    return py_code


# --------------------------------
# ⚠ やさしい日本語エラーメッセージ
# --------------------------------
ERROR_MESSAGES = {
    "SyntaxError": "文の書き方が間違っています。\n（例：「かっこ」や「：」を忘れていませんか？）",
    "NameError": "使おうとした名前が見つかりません。\n（例：「変数」をまだ作っていませんか？）",
    "TypeError": "データの種類が合っていません。\n（例：「文字」と「数」を混ぜていませんか？）",
    "ZeroDivisionError": "0で割ることはできません。",
    "IndentationError": "インデント（字下げ）が正しくありません。",
    "AttributeError": "その命令はその対象に使えません。",
    "ValueError": "値が正しくありません。",
    "IndexError": "番号が大きすぎます。",
    "KeyError": "そのキーが辞書にありません。",
    "RuntimeError": "実行中に問題が起きました。",
    "ImportError": "読み込むものが見つかりません。",
}


def translate_error_to_japanese(e: Exception) -> str:
    t = type(e).__name__
    if t in ERROR_MESSAGES:
        return f"{ERROR_MESSAGES[t]}\n\n（詳細: {e}）"
    return f"不明なエラーが発生しました: {t}\n{e}"


# --------------------------------
# ▶ 日本語Python 実行（input対応）
# --------------------------------
def run_japanese_code(jp_code, inputs=None):
    try:
        py_code = translate(jp_code)
        output = io.StringIO()

        input_list = inputs or []
        input_iter = iter(input_list)

        def fake_input(prompt=""):
            try:
                return next(input_iter)
            except StopIteration:
                raise EOFError("入力が足りませんでした。")

        # input をすり替え
        original_input = builtins.input
        builtins.input = fake_input

        with contextlib.redirect_stdout(output):
            exec(py_code, {})

        builtins.input = original_input
        return output.getvalue()

    except Exception as e:
        builtins.input = original_input
        return f"⚠ エラー:\n{translate_error_to_japanese(e)}"


# --------------------------------
# 🔥 Flask ルート
# --------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    code = session.get("saved_code", "")
    inputs = session.get("saved_inputs", "")
    result = ""

    if request.method == "POST":
        code = request.form["code"]
        inputs = request.form.get("inputs", "")
        session["saved_code"] = code
        session["saved_inputs"] = inputs
        result = run_japanese_code(code, inputs.splitlines())

    return render_template_string(HTML_MAIN, code=code, inputs=inputs, result=result)


@app.route("/table")
def table():
    rows = "".join(
        f"""
        <tr>
            <td>{jp}</td>
            <td>{py}</td>
            <td>{example(jp)}</td>
            <td><button onclick="copyText('{jp}')">📋 コピー</button></td>
        </tr>
        """
        for jp, py in JP_TO_PY.items()
    )
    return render_template_string(HTML_TABLE, rows=rows)


# --------------------------------
# 🖥 HTML（実行ページ）
# --------------------------------
HTML_MAIN = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>日本語Python 実行ページ</title>
<style>
  body {
    font-family: 'Arial', sans-serif;
    background-color: #f0f0f0;
    margin: 0;
    padding: 0;
    display: flex;
    justify-content: center;
  }
  .container {
    width: 90%;
    max-width: 400px;
    background: #fff;
    margin-top: 30px;
    padding: 15px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }
  textarea {
    width: 100%;
    height: 200px;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 8px;
  }
  textarea[name="inputs"] {
    height: 120px;
  }
  button {
    width: 100%;
    padding: 12px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 8px;
  }
  pre {
    background: #222;
    color: #0f0;
    padding: 8px;
    border-radius: 5px;
  }
</style>
</head>
<body>
  <div class="container">
    <h1>🐍 日本語Python 実行ページ</h1>
    <a href="/table">👉 対応表を見る</a>
    <form method="post">
      <textarea name="code">{{ code }}</textarea>
      <textarea name="inputs">{{ inputs }}</textarea>
      <button type="submit">▶ 実行</button>
    </form>
    <h3>結果</h3>
    <pre>{{ result }}</pre>
  </div>
</body>
</html>
"""


# --------------------------------
# 📘 対応表ページ
# --------------------------------
HTML_TABLE = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>対応表</title>
<style>
body {
  font-family: 'Arial';
  background: #f5f6fa;
  text-align: center;
}
table {
  width: 95%;
  margin: 20px auto;
  background: white;
  border-collapse: collapse;
}
th, td {
  padding: 10px;
  border-bottom: 1px solid #ddd;
}
th {
  background: #4CAF50;
  color: white;
}
</style>
<script>
function copyText(t){
  navigator.clipboard.writeText(t);
  alert("コピーしました: " + t);
}
</script>
</head>
<body>
<h1>📘 日本語 → Python 対応表</h1>
<a href="/">← 戻る</a>
<table>
<tr><th>日本語</th><th>Python</th><th>実用例</th><th>操作</th></tr>
{{ rows | safe }}
</table>
</body>
</html>
"""


# --------------------------------
# 🚀 起動
# --------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
