
from flask import Flask, render_template, request, jsonify
from calculator import calculate
from solver import solve_equation, solve_system

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    data = request.get_json(silent=True) or {}
    expression = str(data.get("expression", "")).strip()
    degrees = bool(data.get("degrees", True))

    if not expression:
        return jsonify({"error": "Enter a mathematical expression."}), 400

    if len(expression) > 500:
        return jsonify({"error": "Expression is too long."}), 400

    try:
        result = calculate(expression, degrees=degrees)
        return jsonify({"result": str(result)})
    except Exception:
        return jsonify({"error": "Unable to calculate this expression."}), 400


@app.route("/api/solve", methods=["POST"])
def api_solve():
    data = request.get_json(silent=True) or {}
    equation = str(data.get("equation", "")).strip()

    if not equation:
        return jsonify({"error": "Enter an equation to solve."}), 400

    if len(equation) > 500:
        return jsonify({"error": "Equation is too long."}), 400

    try:
        result = solve_equation(equation)
        return jsonify({"result": result})
    except Exception:
        return jsonify({"error": "Unable to solve this equation."}), 400


@app.route("/api/systems", methods=["POST"])
def api_systems():
    data = request.get_json(silent=True) or {}
    equations = data.get("equations", [])

    if not isinstance(equations, list) or not 2 <= len(equations) <= 5:
        return jsonify({
            "error": "Enter between 2 and 5 equations."
        }), 400

    equations = [str(eq).strip() for eq in equations]

    if any(not eq or len(eq) > 500 for eq in equations):
        return jsonify({
            "error": "Each equation must contain 1–500 characters."
        }), 400

    try:
        result = solve_system(equations)
        return jsonify({"result": result})
    except Exception:
        return jsonify({
            "error": "Unable to solve this system."
        }), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5003)
