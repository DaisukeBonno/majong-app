from flask import Flask, render_template, request

app = Flask(__name__)

def calculate_score(scores):
    # プレイヤー番号付きでソート
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)

    # ウマ
    uma = [30, 10, -10, -30]

    results = [0] * 4

    i = 0
    while i < 4:
        same = [ranked[i]]
        j = i + 1

        # 同点グループを作る
        while j < 4 and ranked[i][1] == ranked[j][1]:
            same.append(ranked[j])
            j += 1

        # ウマ平均
        uma_sum = sum(uma[i:i+len(same)])
        uma_avg = uma_sum / len(same)

        # 各プレイヤーに適用
        for k, (idx, score) in enumerate(same):
            base = (score - 30000) / 1000 * 10
            results[idx] = int(base + uma_avg)

        i = j

    return results

@app.route("/", methods=["GET", "POST"])
def index():
    names = ["プレイヤー1", "プレイヤー2", "プレイヤー3", "プレイヤー4"]
    scores = [30000, 30000, 30000, 30000]
    results = [0, 0, 0, 0]

    if request.method == "POST":
        try:
            names = request.form.getlist("names")
            scores = list(map(int, request.form.getlist("scores")))
            results = calculate_score(scores)
        except:
            results = ["エラー"] * 4

    return render_template("index.html",
                           names=names,
                           scores=scores,
                           results=results)

if __name__ == "__main__":
    app.run(debug=True)