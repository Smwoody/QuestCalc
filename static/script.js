const modeButtons = document.querySelectorAll(".mode");
const calculatorView = document.getElementById("calculator-view");
const solverView = document.getElementById("solver-view");
const systemsView = document.getElementById("systems-view");
const expressionInput = document.getElementById("expression");
const equationInput = document.getElementById("equation");
const equationOneInput = document.getElementById("equation-one");
const equationTwoInput = document.getElementById("equation-two");
const solveButton = document.getElementById("solve-button");
const clearButton = document.getElementById("clear-button");
const resultPanel = document.getElementById("result-panel");
const resultContent = document.getElementById("result-content");
const panelTitle = document.getElementById("panel-title");
const modeLabel = document.getElementById("mode-label");

let currentMode = "calculator";

function setMode(mode) {
    currentMode = mode;

    modeButtons.forEach(function(button) {
        button.classList.toggle(
            "active",
            button.dataset.mode === mode
        );
    });

    calculatorView.hidden = mode !== "calculator";
    solverView.hidden = mode !== "solver";
    systemsView.hidden = mode !== "systems";

    if (mode === "calculator") {
        panelTitle.textContent = "Calculator";
        modeLabel.textContent = "STANDARD CALCULATOR";
        solveButton.firstChild.textContent = "Calculate Result ";
    } else if (mode === "solver") {
        panelTitle.textContent = "Equation Solver";
        modeLabel.textContent = "STEP-BY-STEP MATH";
        solveButton.firstChild.textContent = "Solve Equation ";
    } else {
        panelTitle.textContent = "Systems of Equations";
        modeLabel.textContent = "MULTI-EQUATION SOLVER";
        solveButton.firstChild.textContent = "Solve System ";
    }

    hideResult();
}

function hideResult() {
    resultPanel.hidden = true;
    resultContent.replaceChildren();
}

function showError(message) {
    hideResult();

    const paragraph = document.createElement("p");
    paragraph.className = "error";
    paragraph.textContent = message;

    resultContent.appendChild(paragraph);
    resultPanel.hidden = false;
}

function showResult(data) {
    hideResult();

    if (data.error) {
        showError(data.error);
        return;
    }

    const result = data.result;

    if (typeof result === "string" ||
        typeof result === "number") {
        const heading = document.createElement("h3");
        heading.textContent = String(result);
        resultContent.appendChild(heading);
    } else if (Array.isArray(result)) {
        result.forEach(function(item) {
            const paragraph = document.createElement("p");
            paragraph.textContent = typeof item === "string"
                ? item
                : JSON.stringify(item);
            resultContent.appendChild(paragraph);
        });
    } else if (result && typeof result === "object") {
        Object.entries(result).forEach(function(entry) {
            const paragraph = document.createElement("p");
            const label = document.createElement("strong");

            label.textContent = entry[0] + ": ";
            paragraph.appendChild(label);

            const value = entry[1];
            paragraph.appendChild(
                document.createTextNode(
                    typeof value === "string"
                        ? value
                        : JSON.stringify(value)
                )
            );

            resultContent.appendChild(paragraph);
        });
    } else {
        const paragraph = document.createElement("p");
        paragraph.textContent = String(result);
        resultContent.appendChild(paragraph);
    }

    resultPanel.hidden = false;
}

async function sendRequest(url, payload) {
    solveButton.disabled = true;
    solveButton.firstChild.textContent = "Working... ";

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok && !data.error) {
            showError("Something went wrong. Please try again.");
            return;
        }

        showResult(data);
    } catch (error) {
        showError(
            "Could not connect to QuestCalc. Make sure the Flask server is running."
        );
    } finally {
        solveButton.disabled = false;

        if (currentMode === "calculator") {
            solveButton.firstChild.textContent = "Calculate Result ";
        } else if (currentMode === "solver") {
            solveButton.firstChild.textContent = "Solve Equation ";
        } else {
            solveButton.firstChild.textContent = "Solve System ";
        }
    }
}

async function calculateExpression() {
    const expression = expressionInput.value.trim();

    if (!expression) {
        showError("Enter a mathematical expression first.");
        return;
    }

    await sendRequest("/api/calculate", {
        expression: expression,
        degrees: true
    });
}

async function solveEquation() {
    const equation = equationInput.value.trim();

    if (!equation) {
        showError("Enter an equation first.");
        return;
    }

    await sendRequest("/api/solve", {
        equation: equation
    });
}

async function solveSystem() {
    const equations = [
        equationOneInput.value.trim(),
        equationTwoInput.value.trim()
    ];

    if (equations.some(function(equation) {
        return equation.length === 0;
    })) {
        showError("Enter both equations first.");
        return;
    }

    await sendRequest("/api/systems", {
        equations: equations
    });
}

modeButtons.forEach(function(button) {
    button.addEventListener("click", function() {
        setMode(button.dataset.mode);
    });
});

solveButton.addEventListener("click", function() {
    if (currentMode === "calculator") {
        calculateExpression();
    } else if (currentMode === "solver") {
        solveEquation();
    } else {
        solveSystem();
    }
});

clearButton.addEventListener("click", function() {
    expressionInput.value = "";
    equationInput.value = "";
    equationOneInput.value = "";
    equationTwoInput.value = "";
    hideResult();
});

document.querySelectorAll("[data-insert]").forEach(function(button) {
    button.addEventListener("click", function() {
        const insertion = button.dataset.insert;
        const input = expressionInput;
        const start = input.selectionStart;
        const end = input.selectionEnd;

        input.setRangeText(insertion, start, end, "end");
        input.focus();
    });
});

document.querySelectorAll("[data-action]").forEach(function(button) {
    button.addEventListener("click", function() {
        if (button.dataset.action === "equals") {
            calculateExpression();
        }

        if (button.dataset.action === "backspace") {
            const input = expressionInput;
            const start = input.selectionStart;
            const end = input.selectionEnd;

            if (start !== end) {
                input.setRangeText("", start, end, "end");
            } else if (start > 0) {
                input.setRangeText("", start - 1, start, "end");
            }

            input.focus();
        }
    });
});

expressionInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        calculateExpression();
    }
});

equationInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        solveEquation();
    }
});

equationOneInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        solveSystem();
    }
});

equationTwoInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        solveSystem();
    }
});

setMode("calculator");