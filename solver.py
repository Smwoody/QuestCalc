
import re

import sympy as sp


x = sp.Symbol("x")


def format_expression(expression):
    """Format a mathematical expression for display."""
    return str(sp.simplify(expression)).replace("**", "^")


def format_equation(left, right):
    """Format both sides of an equation."""
    return (
        f"{format_expression(left)} = "
        f"{format_expression(right)}"
    )


def error_result(message):
    """Return a consistent result for invalid equations."""
    return {
        "answer": message,
        "steps": [message]
    }


def solve_equation(equation):
    """Solve linear and quadratic equations with basic explanations."""

    if not isinstance(equation, str) or not equation.strip():
        return error_result("Please enter an equation.")

    equation = equation.strip().replace("X", "x")

    if equation.count("=") != 1:
        return error_result(
            "Enter an equation with exactly one equals sign."
        )

    # Only accept basic arithmetic and the variable x.
    if not re.fullmatch(r"[0-9x+\-*/().=\s^]*", equation):
        return error_result(
            "Use numbers, x, parentheses, and basic math operators only."
        )

    left_text, right_text = equation.split("=")

    if not left_text.strip() or not right_text.strip():
        return error_result(
            "Enter an expression on both sides of the equals sign."
        )

    try:
        left = sp.sympify(
            left_text.replace("^", "**"),
            locals={"x": x}
        )
        right = sp.sympify(
            right_text.replace("^", "**"),
            locals={"x": x}
        )

        # Reject undefined or infinite arithmetic results.
        invalid_values = (sp.zoo, sp.oo, -sp.oo, sp.nan)

        if any(
            expr.has(*invalid_values)
            for expr in (left, right)
        ):
            return error_result(
                "Division by zero or undefined arithmetic detected."
            )

        difference = sp.expand(left - right)
        polynomial = sp.Poly(difference, x)

    except (
        sp.SympifyError,
        sp.PolynomialError,
        TypeError,
        ValueError,
        ZeroDivisionError,
    ):
        return error_result(
            "Unable to solve this equation. Check your input."
        )

    steps = [
        "Original equation: " + format_equation(left, right)
    ]

    # Handle identities and contradictions first.
    if sp.simplify(difference) == 0:
        steps.append(
            "Both sides simplify to the same expression."
        )
        steps.append(
            "The equation is true for every allowed value of x."
        )
        return {
            "answer": "Infinitely many solutions",
            "steps": steps
        }

    if not difference.has(x):
        steps.append(
            "The variable terms cancel, leaving "
            + format_expression(difference)
            + " = 0."
        )
        steps.append(
            "This statement is false, so there is no solution."
        )
        return {
            "answer": "No solution",
            "steps": steps
        }

    degree = polynomial.degree()

    
    # Linear equations.
    if degree == 1:
        coefficient = polynomial.coeff_monomial(x)
        constant = polynomial.coeff_monomial(1)

        solution = sp.simplify(-constant / coefficient)

        steps.append(
            "Combine like terms and collect the variable terms: "
            + format_equation(
                coefficient * x,
                -constant
            )
        )

        if constant != 0:
            steps.append(
                "The constant term is "
                + format_expression(constant)
                + ". Move it to the right side to get "
                + format_expression(-constant)
                + "."
            )

        if coefficient != 1:
            steps.append(
                "Divide both sides by "
                + format_expression(coefficient)
                + ": x = "
                + format_expression(solution)
                + "."
            )
        else:
            steps.append(
                "The coefficient of x is 1, so x = "
                + format_expression(solution)
                + "."
            )

        steps.append(
            "Final answer: x = "
            + format_expression(solution)
        )

        return {
            "answer": "x = " + format_expression(solution),
            "steps": steps
        }


    
    # Quadratic equations.
    if degree == 2:
        a = polynomial.coeff_monomial(x**2)
        b = polynomial.coeff_monomial(x)
        c = polynomial.coeff_monomial(1)

        steps.append(
            "Write the equation in standard form: "
            + format_equation(difference, 0)
        )

        steps.append(
            "Identify the coefficients: a = "
            + format_expression(a)
            + ", b = "
            + format_expression(b)
            + ", c = "
            + format_expression(c)
            + "."
        )

        discriminant = sp.simplify(b**2 - 4*a*c)
        factored = sp.factor(difference)

        if factored != difference:
            steps.append(
                "Factor the quadratic: "
                + format_expression(factored)
                + " = 0."
            )

            factors = sp.Mul.make_args(factored)

            for factor in factors:
                if factor.has(x):
                    steps.append(
                        "Set a factor equal to zero: "
                        + format_expression(factor)
                        + " = 0."
                    )

            steps.append(
                "Solve each factor equation to find the roots."
            )
        else:
            steps.append(
                "Use the quadratic formula: "
                "x = (-b ± sqrt(b^2 - 4ac)) / (2a)."
            )

        steps.append(
            "Calculate the discriminant: D = "
            + format_expression(discriminant)
            + "."
        )

        if discriminant > 0:
            steps.append(
                "The discriminant is positive, so there are "
                "two distinct real solutions."
            )
        elif discriminant == 0:
            steps.append(
                "The discriminant is zero, so there is "
                "one repeated real solution."
            )
        else:
            steps.append(
                "The discriminant is negative, so there are "
                "two complex solutions and no real solutions."
            )

        solutions = sp.solve(difference, x)

        answer = ", ".join(
            "x = " + format_expression(solution)
            for solution in solutions
        )

        steps.append("Final answer: " + answer)

        return {
            "answer": answer,
            "steps": steps
        }

    # Higher-degree polynomial equations.
    try:
        solutions = sp.solve(difference, x)

        if solutions:
            answer = ", ".join(
                "x = " + format_expression(solution)
                for solution in solutions
            )
        else:
            answer = "No solution found"

        steps.append(
            "This equation is higher than degree two. "
            "Detailed steps for this equation type are not "
            "yet supported."
        )
        steps.append("Result: " + answer)

        return {
            "answer": answer,
            "steps": steps
        }

    except Exception:
        return error_result(
            "QuestCalc could not solve this equation."
        )



def solve_system(equations):
    """Solve a system of two equations in x and y."""

    if not isinstance(equations, (list, tuple)):
        return {
            "answer": "Enter two equations.",
            "steps": ["Provide two equations as a list."]
        }

    if len(equations) != 2:
        return {
            "answer": "Enter exactly two equations.",
            "steps": ["A system must contain two equations."]
        }

    x_symbol = sp.Symbol("x")
    y_symbol = sp.Symbol("y")
    variables = (x_symbol, y_symbol)
    parsed_equations = []

    try:
        for equation in equations:
            if not isinstance(equation, str) or equation.count("=") != 1:
                return {
                    "answer": "Invalid equation format.",
                    "steps": [
                        "Each equation must contain exactly one equals sign."
                    ]
                }

            left_text, right_text = equation.split("=")

            allowed = r"[0-9xyXY+\-*/().=\s^]*"

            if not re.fullmatch(allowed, equation):
                return {
                    "answer": "Unsupported characters.",
                    "steps": [
                        "Use x, y, numbers, and basic operators."
                    ]
                }

            left = sp.sympify(
                left_text.replace("^", "**"),
                locals={"x": x_symbol, "y": y_symbol}
            )

            right = sp.sympify(
                right_text.replace("^", "**"),
                locals={"x": x_symbol, "y": y_symbol}
            )

            difference = sp.expand(left - right)

            if difference.has(sp.zoo, sp.nan, sp.oo, -sp.oo):
                return {
                    "answer": "Invalid equation.",
                    "steps": ["Check for division by zero."]
                }

            parsed_equations.append(difference)

        steps = [
            "Original system:",
            equations[0].strip(),
            equations[1].strip()
        ]

        # Confirm both equations are linear.
        for equation in parsed_equations:
            try:
                polynomial = sp.Poly(equation, x_symbol, y_symbol)
            except sp.PolynomialError:
                return {
                    "answer": "Unsupported equation type.",
                    "steps": steps + [
                        "This version supports linear systems only."
                    ]
                }

            if polynomial.total_degree() > 1:
                return {
                    "answer": "Unsupported equation type.",
                    "steps": steps + [
                        "This version supports linear systems only."
                    ]
                }

        a1 = sp.expand(parsed_equations[0]).coeff(x_symbol)
        b1 = sp.expand(parsed_equations[0]).coeff(y_symbol)
        c1 = sp.simplify(-parsed_equations[0].subs({
            x_symbol: 0,
            y_symbol: 0
        }))

        a2 = sp.expand(parsed_equations[1]).coeff(x_symbol)
        b2 = sp.expand(parsed_equations[1]).coeff(y_symbol)
        c2 = sp.simplify(-parsed_equations[1].subs({
            x_symbol: 0,
            y_symbol: 0
        }))

        steps.append(
            "Write both equations in standard form: "
            "ax + by = c."
        )

        steps.append(
            format_expression(a1) + "x + "
            + format_expression(b1) + "y = "
            + format_expression(c1)
        )

        steps.append(
            format_expression(a2) + "x + "
            + format_expression(b2) + "y = "
            + format_expression(c2)
        )

        # Use elimination to solve the system.
        determinant = sp.simplify(a1 * b2 - a2 * b1)

        if determinant == 0:
            solutions = sp.solve(
                parsed_equations,
                variables,
                dict=True
            )

            if solutions:
                solution = solutions[0]

                if x_symbol in solution and y_symbol in solution:
                    x_answer = sp.simplify(solution[x_symbol])
                    y_answer = sp.simplify(solution[y_symbol])

                    answer = (
                        "x = " + format_expression(x_answer)
                        + ", y = " + format_expression(y_answer)
                    )

                    steps.append(
                        "The equations do not have a unique intersection."
                    )
                    steps.append("Final answer: " + answer)

                    return {
                        "answer": answer,
                        "steps": steps
                    }

            if sp.simplify(
                a1 * c2 - a2 * c1
            ) != 0 or sp.simplify(
                b1 * c2 - b2 * c1
            ) != 0:
                return {
                    "answer": "No solution",
                    "steps": steps + [
                        "The equations describe parallel lines.",
                        "Parallel lines do not intersect, so there is no solution."
                    ]
                }

            return {
                "answer": "Infinitely many solutions",
                "steps": steps + [
                    "The equations represent the same line.",
                    "Every point on that line satisfies both equations."
                ]
            }

        # Eliminate y by multiplying the equations.
        multiplier1 = b2
        multiplier2 = -b1

        if multiplier1 != 0 and multiplier2 != 0:
            steps.append(
                "Multiply the first equation by "
                + format_expression(multiplier1)
                + " and the second equation by "
                + format_expression(multiplier2)
                + " so the y coefficients cancel."
            )

            new_a1 = sp.simplify(a1 * multiplier1)
            new_c1 = sp.simplify(c1 * multiplier1)
            new_a2 = sp.simplify(a2 * multiplier2)
            new_c2 = sp.simplify(c2 * multiplier2)

            steps.append(
                format_expression(new_a1) + "x + "
                + format_expression(b1 * multiplier1) + "y = "
                + format_expression(new_c1)
            )

            steps.append(
                format_expression(new_a2) + "x + "
                + format_expression(b2 * multiplier2) + "y = "
                + format_expression(new_c2)
            )

            combined_x = sp.simplify(new_a1 + new_a2)
            combined_y = sp.simplify(
                b1 * multiplier1 + b2 * multiplier2
            )
            combined_c = sp.simplify(new_c1 + new_c2)

            steps.append(
                "Add the equations to eliminate y: "
                + format_expression(combined_x) + "x = "
                + format_expression(combined_c)
            )

            if combined_x != 0:
                x_answer = sp.simplify(combined_c / combined_x)

                steps.append(
                    "Divide both sides by "
                    + format_expression(combined_x)
                    + ": x = " + format_expression(x_answer)
                )
            else:
                x_answer = sp.simplify(
                    solutions[0][x_symbol]
                ) if (solutions := sp.solve(
                    parsed_equations, variables, dict=True
                )) else sp.S.Zero
        else:
            x_answer = sp.solve(
                parsed_equations,
                x_symbol,
                dict=True
            )

            if not x_answer:
                return {
                    "answer": "Unable to solve this system.",
                    "steps": steps + [
                        "Try checking the equations."
                    ]
                }

            x_answer = sp.simplify(x_answer[0][x_symbol])

        # Substitute x back into an original equation to find y.
        if b1 != 0:
            y_answer = sp.simplify((c1 - a1 * x_answer) / b1)
            substitution_equation = 1
        elif b2 != 0:
            y_answer = sp.simplify((c2 - a2 * x_answer) / b2)
            substitution_equation = 2
        else:
            return {
                "answer": "Unable to solve this system.",
                "steps": steps + [
                    "Could not isolate y from either equation."
                ]
            }

        steps.append(
            "Substitute x = " + format_expression(x_answer)
            + " into equation " + str(substitution_equation)
            + " to find y."
        )

        steps.append(
            "y = " + format_expression(y_answer)
        )

        # Verify the solution in both original equations.
        verification1 = sp.simplify(
            parsed_equations[0].subs({
                x_symbol: x_answer,
                y_symbol: y_answer
            })
        )

        verification2 = sp.simplify(
            parsed_equations[1].subs({
                x_symbol: x_answer,
                y_symbol: y_answer
            })
        )

        if verification1 != 0 or verification2 != 0:
            return {
                "answer": "Unable to verify the solution.",
                "steps": steps + [
                    "The proposed values did not satisfy both equations."
                ]
            }

        steps.append(
            "Check both equations. The solution satisfies each one."
        )

        answer = (
            "x = " + format_expression(x_answer)
            + ", y = " + format_expression(y_answer)
        )

        steps.append("Final answer: " + answer)

        return {
            "answer": answer,
            "steps": steps
        }

    except (
        sp.SympifyError,
        sp.PolynomialError,
        TypeError,
        ValueError,
        ZeroDivisionError,
        KeyError,
        IndexError
    ):
        return {
            "answer": "Unable to solve this system.",
            "steps": ["Check the equations and try again."]
        }
