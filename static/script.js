
"use strict";

// ========================================
// QUESTCALC - MAIN APPLICATION
// ========================================

// Mode buttons and views
const modeButtons = document.querySelectorAll(".mode");
const calculatorView = document.getElementById("calculator-view");
const solverView = document.getElementById("solver-view");
const systemsView = document.getElementById("systems-view");

// Inputs
const expressionInput = document.getElementById("expression");
const equationInput = document.getElementById("equation");
const equationOneInput = document.getElementById("equation-one");
const equationTwoInput = document.getElementById("equation-two");

// Buttons
const solveButton = document.getElementById("solve-button");
const solveSystemButton = document.getElementById("solve-system-button");
const clearButton = document.getElementById("clear-button");

// Results
const resultPanel = document.getElementById("result-panel");
const resultContent = document.getElementById("result-content");
const panelTitle = document.getElementById("panel-title");
const modeLabel = document.getElementById("mode-label");

// Calculator keypad
const keypad = document.getElementById("keypad");

let currentMode = "calculator";

// ========================================
// MODE MANAGEMENT
// ========================================

function setMode(mode) {
    currentMode = mode;

    modeButtons.forEach(function(button) {
        button.classList.toggle(
            "active",
            button.dataset.mode === mode
        );
    });

    if (calculatorView) {
        calculatorView.hidden = mode !== "calculator";
    }

    if (solverView) {
        solverView.hidden = mode !== "solver";
    }

    if (systemsView) {
        systemsView.hidden = mode !== "systems";
    }

    if (modeLabel) {
        if (mode === "calculator") {
            modeLabel.textContent = "STANDARD CALCULATOR";
        } else if (mode === "solver") {
            modeLabel.textContent = "STEP-BY-STEP MATH";
        } else {
            modeLabel.textContent = "MULTI-EQUATION SOLVER";
        }
    }

    if (panelTitle) {
        if (mode === "calculator") {
            panelTitle.textContent = "Calculator";
        } else if (mode === "solver") {
            panelTitle.textContent = "Equation Solver";
        } else {
            panelTitle.textContent = "Systems of Equations";
        }
    }

    if (solveButton) {
        const buttonText = solveButton.querySelector("span");

        if (buttonText) {
            buttonText.textContent =
                mode === "solver" ? "Solve Equation " : "Calculate Result ";
        }
    }

    hideResults();
}

modeButtons.forEach(function(button) {
    button.addEventListener("click", function() {
        setMode(button.dataset.mode);
    });
});

// ========================================
// RESULT DISPLAY
// ========================================

function showResults(title, content) {
    if (panelTitle) {
        panelTitle.textContent = title;
    }

    if (resultContent) {
        resultContent.replaceChildren();

        if (typeof content === "string") {
            resultContent.textContent = content;
        } else {
            resultContent.textContent = JSON.stringify(content, null, 2);
        }
    }

    if (resultPanel) {
        resultPanel.hidden = false;
    }
}

function hideResults() {
    if (resultPanel) {
        resultPanel.hidden = true;
    }

    if (resultContent) {
        resultContent.replaceChildren();
    }
}

function showError(message) {
    showResults("Something Went Wrong", message);
}

// ========================================
// FLASK API REQUESTS
// ========================================

async function apiRequest(endpoint, data) {
    const response = await fetch(endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    });

    let result;

    try {
        result = await response.json();
    } catch {
        throw new Error("The server returned an invalid response.");
    }

    if (!response.ok) {
        throw new Error(
            result.error ||
            result.message ||
            "The request failed. Please try again."
        );
    }

    if (result && result.error) {
        throw new Error(result.error);
    }

    return result;
}

// ========================================
// FORMAT SOLUTION STEPS
// ========================================


function displayResult(result, title) {
    
    if (result === null || result === undefined) {
        showError("No result was returned. Please try again.");
        return;
    }

    // Convert JSON strings into objects when necessary.
    if (typeof result === "string") {
        try {
            result = JSON.parse(result);
        } catch {
            showResults(title, result);
            return;
        }
    }

    const container = document.createElement("div");

    const answer = result.answer ?? result.result ?? result.solution;

    if (answer !== undefined) {
        const answerHeading = document.createElement("h3");
        answerHeading.textContent = "Your Answer";
        container.appendChild(answerHeading);

        const answerText = document.createElement("p");
        answerText.className = "answer";

        const boldAnswer = document.createElement("strong");
        boldAnswer.textContent =
            typeof answer === "object"
                ? JSON.stringify(answer)
                : String(answer);

        answerText.appendChild(boldAnswer);
        container.appendChild(answerText);
    }

    const steps = result.steps;

    if (Array.isArray(steps) && steps.length > 0) {
        const stepsHeading = document.createElement("h3");
        stepsHeading.textContent = "Step-by-Step Solution";
        container.appendChild(stepsHeading);

        const stepsList = document.createElement("ul");
        stepsList.className = "solution-steps";

        steps.forEach(function(step) {
            const item = document.createElement("li");

            item.textContent =
                typeof step === "string"
                    ? step
                    : JSON.stringify(step);

            stepsList.appendChild(item);
        });

        container.appendChild(stepsList);
    }

    if (answer === undefined && !Array.isArray(steps)) {
        const resultText = document.createElement("pre");
        resultText.textContent = JSON.stringify(result, null, 2);
        container.appendChild(resultText);
    }

    if (resultContent) {
        resultContent.replaceChildren(container);
    }

    if (resultPanel) {
        resultPanel.hidden = false;
    }

    if (panelTitle) {
        panelTitle.textContent = title;
    }
}


// ========================================
// CALCULATOR
// ========================================

async function calculateExpression() {
    const expression = expressionInput.value.trim();

    if (!expression) {
        showError("Enter a mathematical expression first.");
        return;
    }

    try {
        const result = await apiRequest("/api/calculate", {
            expression: expression
        });

        displayResult(result, "Calculator Result");
    } catch (error) {
        showError(error.message);
    }
}

// ========================================
// EQUATION SOLVER
// ========================================

async function solveEquation() {
    const equation = equationInput.value.trim();

    if (!equation) {
        showError("Enter an equation first.");
        return;
    }

    try {
        const result = await apiRequest("/api/solve", {
            equation: equation
        });

        displayResult(result, "Equation Solution");
    } catch (error) {
        showError(error.message);
    }
}

// ========================================
// SYSTEMS OF EQUATIONS
// ========================================

async function solveSystem() {
    const equation1 = equationOneInput.value.trim();
    const equation2 = equationTwoInput.value.trim();

    if (!equation1 || !equation2) {
        showError("Enter both equations before solving.");
        return;
    }

    try {
        const result = await apiRequest("/api/systems", {
            equation1: equation1,
            equation2: equation2
        });

        displayResult(result, "System Solution");
    } catch (error) {
        showError(error.message);
    }
}

// ========================================
// BUTTON EVENTS
// ========================================

if (solveButton) {
    solveButton.addEventListener("click", function() {
        if (currentMode === "solver") {
            solveEquation();
        } else {
            calculateExpression();
        }
    });
}

if (solveSystemButton) {
    solveSystemButton.addEventListener("click", solveSystem);
}

if (clearButton) {
    clearButton.addEventListener("click", function() {
        hideResults();

        if (currentMode === "calculator" && expressionInput) {
            expressionInput.value = "";
            expressionInput.focus();
        } else if (currentMode === "solver" && equationInput) {
            equationInput.value = "";
            equationInput.focus();
        } else if (currentMode === "systems") {
            if (equationOneInput) {
                equationOneInput.value = "";
            }

            if (equationTwoInput) {
                equationTwoInput.value = "";
            }

            if (equationOneInput) {
                equationOneInput.focus();
            }
        }
    });
}

// ========================================
// KEYBOARD SUPPORT
// ========================================

if (expressionInput) {
    expressionInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            calculateExpression();
        }
    });
}

if (equationInput) {
    equationInput.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            solveEquation();
        }
    });
}

if (equationOneInput || equationTwoInput) {
    [equationOneInput, equationTwoInput].forEach(function(input) {
        if (!input) {
            return;
        }

        input.addEventListener("keydown", function(event) {
            if (event.key === "Enter") {
                event.preventDefault();
                solveSystem();
            }
        });
    });
}

// ========================================
// CALCULATOR KEYPAD
// ========================================


const keypadButtons = [
    { label: "sin", value: "sin(" },
    { label: "cos", value: "cos(" },
    { label: "tan", value: "tan(" },
    { label: "√", value: "sqrt(" },

    { label: "log", value: "log(" },
    { label: "ln", value: "ln(" },
    { label: "π", value: "pi" },
    { label: "e", value: "e" },

    { label: "x²", value: "**2" },
    { label: "xʸ", value: "**" },
    { label: "(", value: "(" },
    { label: ")", value: ")" },

    { label: "C", value: "CLEAR", type: "utility" },
    { label: "÷", value: "/" },
    { label: "×", value: "*" },
    { label: "−", value: "-" },

    { label: "7", value: "7" },
    { label: "8", value: "8" },
    { label: "9", value: "9" },
    { label: "+", value: "+" },

    { label: "4", value: "4" },
    { label: "5", value: "5" },
    { label: "6", value: "6" },
    { label: "%", value: "%" },

    { label: "1", value: "1" },
    { label: "2", value: "2" },
    { label: "3", value: "3" },
    { label: ".", value: "." },

    { label: "0", value: "0" },

    { label: "=", value: "EQUALS", type: "equals" }
];


function insertAtCursor(input, value) {
    if (!input) {
        return;
    }

    const start = input.selectionStart ?? input.value.length;
    const end = input.selectionEnd ?? input.value.length;

    input.setRangeText(value, start, end, "end");
    input.focus();
}

function buildKeypad() {
    if (!keypad) {
        return;
    }

    keypad.replaceChildren();

    keypadButtons.forEach(function(buttonInfo) {
        const button = document.createElement("button");

        button.type = "button";
        button.textContent = buttonInfo.label;
        button.className = "keypad-button";

        if (buttonInfo.type === "utility") {
            button.classList.add("utility-button");
        }

        if (buttonInfo.type === "equals") {
            button.classList.add("equals-button");
        }

        button.addEventListener("click", function() {
            if (!expressionInput) {
                return;
            }

            if (buttonInfo.value === "CLEAR") {
                expressionInput.value = "";
                hideResults();
                expressionInput.focus();
                return;
            }

            if (buttonInfo.value === "EQUALS") {
                calculateExpression();
                return;
            }

            insertAtCursor(expressionInput, buttonInfo.value);
        });

        keypad.appendChild(button);
    });
}

// ========================================
// APP INITIALIZATION
// ========================================

buildKeypad();
setMode("calculator");
