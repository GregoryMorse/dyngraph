# save this as app.py
from flask import Flask, send_file, make_response, Response

app = Flask(__name__)

def presortedness(l):
    direction, cursubseq, lastitem = None, 1, l[0]
    inversion, ascendingruns, longestsubseq = 0, 0, 0
    for item in l[1:]:
        newdirection = item < lastitem
        if direction is None: direction = newdirection
        if newdirection != direction:
            inversion += 1
            cursubseq = 2 if not newdirection else 1
        if newdirection and not direction: ascendingruns += 1
        if not newdirection and not direction: cursubseq += 1
        lastitem, direction = item, newdirection
        longestsubseq = max(longestsubseq, cursubseq)
    if direction == False: ascendingruns += 1
    return inversion, ascendingruns, longestsubseq
print(presortedness([4,3,5,8,7,6,9,9,10,11]))

def random_non_unique(n):
    return [np.random.choice(range(n)) for _ in range(n)]
import numpy as np
def staggerEveryK(l, k):
    for i in range(0, len(l), k):
        l.insert(i, l.pop())
    return l
def equalEveryK(n, k):
    return [x for x in range(n//k) for _ in range(k)] + [n//k]*(n % k)
datafuncs = [("Random Non Unique", random_non_unique), 
            ("Random Permutation", lambda n: np.random.permutation(range(n))),
            ("Ascending", lambda n: list(range(n))),
            ("Descencing", lambda n: list(reversed(range(n)))),
            ("All Equal", lambda n: [1]*n),
            ("Odds then Evens", lambda n: list(range(1, n, 2)) + list(range(0, n, 2))),
            ("Ascending then Equal Ascending", lambda n: list(range(0, n, 2)) + list(range(0, n-1, 2))),
            ("Evens then Odds", lambda n: list(range(0, n, 2)) + list(range(1, n, 2))),
            ("Ascending then Descending", lambda n: list(range(1, n, 2)) + list(reversed(range(0, n, 2)))),
            ("Descending then Ascending", lambda n: list(reversed(range(1, n, 2))) + list(range(0, n, 2))),
            ("Staggered by 5", lambda n: staggerEveryK(list(range(n)), 5)),
            ("Staggered by 10", lambda n: staggerEveryK(list(range(n)), 10)),
            ("Reverse Staggered by 5", lambda n: list(reversed(staggerEveryK(list(range(n)), 5)))),
            ("Reverse Staggered by 10", lambda n: list(reversed(staggerEveryK(list(range(n)), 10)))),
            ("Half Sorted Half Random Same Size", lambda n: list(range(0, n//2, 1)) + list(np.random.permutation(range(0, n-n//2, 1)))),
            ("Half Sorted Half Random Increasing", lambda n: list(range(0, n//2, 1)) + list(np.random.permutation(range(n//2, n, 1)))),
            ("Equal for 5 Ascending", lambda n: equalEveryK(n, 5)),
            ("Equal for 10 Ascending", lambda n: equalEveryK(n, 10)),
            ("Equal for 5 Descending", lambda n: list(reversed(equalEveryK(n, 5)))),
            ("Equal for 10 Descending", lambda n: list(reversed(equalEveryK(n, 10)))),
            ]
#listTransforms = [
#    lambda l, n: 
#]
print([len(set(f[1](1000))) for f in datafuncs])
sortfuncs = []
import timeit
xaxis = list(range(10000))
print([[timeit.timeit(f(datafuncs[0](n))) for n in xaxis] for f in sortfuncs])

@app.route("/")
def startpage():
    prolog = ("<html><head><title>Adaptive Sorting</title>" +
        "<script>function changeImage(chosen) {\n" +
        "newImg = document.getElementById('newImg');\n" +
#        "if (newImg == null) {" +
#        "newImg = document.createElement('img');\n" +
#        "newImg.id = 'newImg';"
#        "document.body.insertBefore(newImg, document.getElementById('data').nextSibling); }" +
        "newImg.src = '/picture/' + chosen;\n" + 
        "}\n" +
        "</script></head><body>")
    epilog = "</body></html>"
    body = "<select id='data' name='data' onchange='changeImage(this.options[this.selectedIndex].value)'>\n"
    for i, datasource in enumerate(datafuncs):
        body += "\t<option value='" + str(i) + "'>" + datasource[0] + "</option>\n"
    body += "</select><img id='newImg' src='/picture/0'/>"
    return prolog + body + epilog

#{"tensorFlowNeuralNetwork": {"neurons": 1000, "layers": 3, "learningThreshold": 0.5}}
@app.route("/")
def tensorFlowNeuralNetwork(): pass

@app.route('/picture/<int:id>')
def generateplot(id):
    import matplotlib.pyplot as plt
    import io
    fig, ax = plt.subplots()
    ax.bar(range(100), datafuncs[id][1](100))
    ax.set_title(datafuncs[id][0])
    ax.get_xaxis().set_visible(False)
    buf = io.BytesIO()
    fig.savefig(buf, format='svg')
    buf.seek(0)
    #fig.show()

    #response = make_response(buf)
    #response.headers.set('Content-Type', 'image/svg+xml')
    #response.direct_passthrough=True
    #return response
    return send_file(buf, mimetype="image/svg+xml")
    #return Response(buf, direct_passthrough=True, mimetype="image/svg+xml")

if __name__ == "__main__":
    app.run(debug=True)