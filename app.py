from flask import Flask, render_template, request, session

app = Flask(__name__)
app.secret_key = "mahjong-secret"

def calculate_score(scores):
    base_points = [(s - 30000) / 1000 for s in scores]

    sorted_scores = sorted([(s, i) for i, s in enumerate(scores)], reverse=True)

    ranks = [0]*4
    for r, (_, i) in enumerate(sorted_scores):
        ranks[i] = r

    uma_table = [30, 10, -10, -30]
    results = [0]*4

    from collections import defaultdict
    groups = defaultdict(list)

    for i, s in enumerate(scores):
        groups[s].append(i)

    for players in groups.values():
        if len(players) == 1:
            i = players[0]
            uma = uma_table[ranks[i]]
            oka = 20 if ranks[i] == 0 else 0
            results[i] = base_points[i] + uma + oka
        else:
            total_uma = sum(uma_table[ranks[i]] for i in players)
            avg_uma = total_uma / len(players)

            for i in players:
                oka = 20 if ranks[i] == 0 else 0
                results[i] = base_points[i] + avg_uma + oka

    return [round(r) for r in results]

@app.route("/", methods=["GET", "POST"])
def index():
    if "history" not in session:
        session["history"] = []

    history = session["history"]

    names = ["プレイヤー1", "プレイヤー2", "プレイヤー3", "プレイヤー4"]
    scores = [25000]*4
    results = [0]*4

    if request.method == "POST":
        names = request.form.getlist("name")
        scores = list(map(int, request.form.getlist("score")))

        results = calculate_score(scores)

        history.append(results)
        session["history"] = history

    totals = [0]*4
    for game in history:
        for i in range(4):
            totals[i] += game[i]

    round_num = len(history) + 1

    return render_template("index.html",
                           names=names,
                           scores=scores,
                           results=results,
                           totals=totals,
                           history=history,
                           round_num=round_num)

@app.route("/reset")
def reset():
    session.clear()
    return "<h2>リセットしました</h2><a href='/'>戻る</a>"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")