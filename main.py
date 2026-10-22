
import json
import os

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp 
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.graphics import Color, RoundedRectangle

from calculator import calculate
from solver import solve_equation, solve_system


BLACK = (0.035, 0.043, 0.039, 1)
CARD = (0.075, 0.090, 0.080, 1)
GREEN = (0.22, 0.91, 0.37, 1)
DARK_GREEN = (0.08, 0.28, 0.14, 1)
WHITE = (0.94, 0.97, 0.94, 1)
MUTED = (0.60, 0.69, 0.62, 1)
ERROR = (1, 0.36, 0.36, 1)

Window.clearcolor = BLACK



class QuestCalcApp(App):
    def build(self):
        self.history = []
        self.current_mode = "Calculator"

        self.load_history()

        root = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(12),
            size_hint=(1, 1)
        )
        root.bind(size=self.update_background)

        with root.canvas.before:
            Color(*BLACK)
            self.background_rect = RoundedRectangle(
                pos=root.pos,
                size=root.size,
                radius=[0]
            )

        header = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(54),
            spacing=dp(10)
        )

        title = Label(
            text="[b]QUEST[/b][color=33E85D]CALC[/color]",
            markup=True,
            font_size=sp(25),
            color=WHITE,
            halign="left",
            valign="middle"
        )
        title.bind(size=title.setter("text_size"))

        header.add_widget(title)

        history_button = self.make_button(
            "History",
            DARK_GREEN,
            height=44
        )
        history_button.size_hint_x = None
        history_button.width = dp(90)
        history_button.bind(on_release=self.show_history)
        header.add_widget(history_button)

        root.add_widget(header)

        self.mode_label = Label(
            text="CALCULATOR",
            size_hint_y=None,
            height=dp(24),
            font_size=sp(12),
            color=GREEN,
            halign="left"
        )
        self.mode_label.bind(
            size=self.mode_label.setter("text_size")
        )
        root.add_widget(self.mode_label)

        self.active_input = None

        self.display = TextInput(
            hint_text="Enter a math expression",
            multiline=False,
            size_hint_y=None,
            height=dp(70),
            font_size=sp(26),
            foreground_color=WHITE,
            background_color=CARD,
            cursor_color=GREEN,
            padding=[dp(14), dp(20), dp(14), dp(12)]
        )
        root.add_widget(self.display)
        self.display.bind(
            focus=lambda instance, focused: (
                setattr(self, "active_input", instance)
                if focused else None
            )
        )
        self.second_display = TextInput(
            hint_text="Enter the second equation",
            multiline=False,
            size_hint_y=None,
            height=dp(55),
            font_size=sp(20),
            foreground_color=WHITE,
            background_color=CARD,
            cursor_color=GREEN,
            padding=[dp(14), dp(14), dp(14), dp(10)],
            opacity=0,
            disabled=True,
            size_hint_x=1
        )
        root.add_widget(self.second_display)
        self.second_display.bind(
            focus=lambda instance, focused: (
                setattr(self, "active_input", instance)
                if focused else None
            )
        )
        self.result_label = Label(
            text="Your answer will appear here",
            size_hint_y=None,
            height=dp(48),
            font_size=sp(17),
            color=GREEN,
            halign="left",
            valign="middle"
        )
        self.result_label.bind(
            size=self.result_label.setter("text_size")
        )
        root.add_widget(self.result_label)

        mode_row = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(44),
            spacing=dp(8)
        )

        calculator_mode = self.make_button(
            "Calculator",
            DARK_GREEN
        )
        calculator_mode.bind(
            on_release=lambda button: self.set_mode("Calculator")
        )

        solver_mode = self.make_button(
            "Equation Solver",
            DARK_GREEN
        )
        solver_mode.bind(
            on_release=lambda button: self.set_mode("Solver")
        )
        systems_mode = self.make_button(
            "Systems",
            DARK_GREEN
        )
        systems_mode.bind(
            on_release=lambda button: self.set_mode("Systems of Equations")
        )

        mode_row.add_widget(calculator_mode)
        mode_row.add_widget(solver_mode)
        mode_row.add_widget(systems_mode)
        root.add_widget(mode_row)

        
        self.keypad = GridLayout(
            cols=4,
            spacing=dp(8),
            size_hint_y=None
        )

        keys = [
            "7", "8", "9", "÷",
            "4", "5", "6", "×",
            "1", "2", "3", "−",
            "C", "0", ".", "+",
            "(", ")", "^", "⌫", 
            "x", "=", "%", "√", 
            "½", "a/b", "x²", "xʸ", 
            "π", "sin", "cos", "tan",
            "log", "ln", "!"
        ]

        for key in keys:
            button = self.make_button(
                key,
                DARK_GREEN if key in ["x", "=", "%"] else CARD,
                text_color=GREEN if key in ["x", "=", "%"] else WHITE,
                height=52
            )

            button.bind(
                on_release=lambda instance, value=key: self.press_key(value)
            )

            self.keypad.add_widget(button)

        self.keypad.bind(
            minimum_height=self.keypad.setter("height")
        )

        keypad_scroll = ScrollView(
            size_hint=(1, 1),
            do_scroll_x=False,
            do_scroll_y=True
        )

        keypad_scroll.add_widget(self.keypad)
        root.add_widget(keypad_scroll)


        self.solve_button = self.make_button(
            "CALCULATE",
            GREEN,
            text_color=BLACK,
            height=54
        )
        self.solve_button.bind(
            on_release=self.solve_current
        )
        root.add_widget(self.solve_button)

        return root

    def update_background(self, widget, size):
        self.background_rect.pos = widget.pos
        self.background_rect.size = size

    def make_button(
        self,
        text,
        background,
        text_color=WHITE,
        height=48
    ):
        button = Button(
            text=text,
            size_hint_y=None,
            height=dp(height),
            background_normal="",
            background_color=background,
            color=text_color,
            font_size=sp(17),
            bold=True
        )
        
        return button

    
    def set_mode(self, mode):
        self.current_mode = mode
        self.mode_label.text = mode.upper()

        if mode == "Calculator":
            self.solve_button.text = "CALCULATE"
            self.display.hint_text = "Example: 12*5"
            self.second_display.opacity = 0
            self.second_display.disabled = True

        elif mode == "Solver":
            self.solve_button.text = "SOLVE EQUATION"
            self.display.hint_text = "Example: 2*x + 5 = 15"
            self.second_display.opacity = 0
            self.second_display.disabled = True

        elif mode == "Systems of Equations":
            self.solve_button.text = "SOLVE SYSTEM"
            self.display.hint_text = "First equation, e.g. x + y = 10"
            self.second_display.opacity = 1
            self.second_display.disabled = False
            self.second_display.hint_text = "Second equation, e.g. x - y = 2"

        self.result_label.text = "Ready"

    
    def press_key(self, key):
        active_input = self.active_input

        if active_input is None:
            active_input = self.display

        text = active_input.text
        cursor = active_input.cursor[0]

        if key == "C":
            active_input.text = ""
            active_input.cursor = (0, 0)
            self.result_label.text = "Cleared"
            return

        if key == "⌫":
            if cursor > 0:
                active_input.text = (
                    text[:cursor - 1] + text[cursor:]
                )
                active_input.cursor = (cursor - 1, active_input.cursor[1])
            return

        replacements = {
    "÷": "/",
    "×": "*",
    "−": "-",
    "X": "x",
    "√": "sqrt(",
    "½": "(1/2)",
    "a/b": "(/)",
    "x²": "**2",
    "xʸ": "**",
    "π": "pi",
    "sin": "sin(",
    "cos": "cos(",
    "tan": "tan(",
    "log": "log(",
    "ln": "ln("
}

        if key == "=" and self.current_mode == "Calculator":
            self.solve_current()
            return

        character = replacements.get(key, key)

        active_input.text = (
            text[:cursor] + character + text[cursor:]
        )
        active_input.cursor = (cursor + len(character), active_input.cursor[1])

    def solve_current(self, *args):
        if self.current_mode == "Systems of Equations":
            first_equation = self.display.text.strip()
            second_equation = self.second_display.text.strip()

            if not first_equation or not second_equation:
                self.result_label.text = "Enter both equations"
                return

            result = solve_system([
                first_equation,
                second_equation
            ])

        elif self.current_mode == "Solver":
            expression = self.display.text.strip()

            if not expression:
                self.result_label.text = "Enter an equation first"
                return

            result = solve_equation(expression)

        else:
            expression = self.display.text.strip()

            if not expression:
                self.result_label.text = "Enter a calculation first"
                return

            try:
                answer = calculate(expression)
                self.result_label.text = str(answer)
                self.add_history(expression, str(answer))
            except Exception as error:
                self.result_label.text = "Error: " + str(error)

            return

        answer = result.get("answer", "Unable to solve")
        steps = result.get("steps", [])

        self.result_label.text = answer

        if self.current_mode == "Systems of Equations":
            history_expression = (
                self.display.text.strip()
                + " ; "
                + self.second_display.text.strip()
            )
        else:
            history_expression = self.display.text.strip()

        self.add_history(history_expression, answer)
        self.show_solution_steps(history_expression, answer, steps)

    def solve_system_current(self, first_equation, second_equation):
        result = solve_system([
            first_equation,
            second_equation
        ])

        answer = result["answer"]
        steps = result.get("steps", [])

        self.add_history(
            first_equation + " ; " + second_equation,
            answer
        )

        self.show_solution_steps(history_expression, answer, steps)
    
    def show_solution_steps(self, expression, answer, steps):
        content = BoxLayout(
            orientation="vertical",
            padding=dp(16),
            spacing=dp(10)
        )

        heading = Label(
            text="STEP-BY-STEP SOLUTION",
            size_hint_y=None,
            height=dp(35),
            color=GREEN,
            font_size=sp(16),
            bold=True
        )
        content.add_widget(heading)

        equation_label = Label(
            text=f"Equation: {expression}",
            size_hint_y=None,
            height=dp(45),
            color=WHITE,
            font_size=sp(16),
            halign="left",
            valign="middle"
        )
        equation_label.bind(
            size=equation_label.setter("text_size")
        )
        content.add_widget(equation_label)

        answer_label = Label(
            text=f"Final answer: {answer}",
            size_hint_y=None,
            height=dp(50),
            color=GREEN,
            font_size=sp(20),
            bold=True,
            halign="left",
            valign="middle"
        )
        answer_label.bind(
            size=answer_label.setter("text_size")
        )
        content.add_widget(answer_label)

        scroll = ScrollView()

        steps_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(10),
            padding=[0, dp(8), 0, dp(8)]
        )
        steps_layout.bind(
            minimum_height=steps_layout.setter("height")
        )

        if steps:
            for index, step in enumerate(steps, start=1):
                step_label = Label(
                    text=f"Step {index}: {step}",
                    size_hint_y=None,
                    height=dp(60),
                    color=WHITE,
                    font_size=sp(15),
                    halign="left",
                    valign="middle"
                )
                step_label.bind(
                    size=step_label.setter("text_size")
                )
                steps_layout.add_widget(step_label)
        else:
            no_steps = Label(
                text="No individual steps were provided.",
                size_hint_y=None,
                height=dp(50),
                color=MUTED
            )
            steps_layout.add_widget(no_steps)

        scroll.add_widget(steps_layout)
        content.add_widget(scroll)

        close_button = self.make_button(
            "Close",
            DARK_GREEN,
            height=48
        )
        content.add_widget(close_button)

        popup = Popup(
            title="QuestCalc | Solution",
            content=content,
            size_hint=(0.92, 0.82),
            background_color=CARD,
            title_color=GREEN,
            separator_color=GREEN
        )

        close_button.bind(
            on_release=popup.dismiss
        )

        popup.open()


    def load_history(self):
        history_path = os.path.join(
            self.user_data_dir,
            "history.json"
        )

        try:
            with open(history_path, "r", encoding="utf-8") as file:
                self.history = json.load(file)

        except (FileNotFoundError, json.JSONDecodeError):
            self.history = []

    def save_history(self):
        history_path = os.path.join(
            self.user_data_dir,
            "history.json"
        )

        try:
            with open(history_path, "w", encoding="utf-8") as file:
                json.dump(self.history, file, indent=4)

        except OSError as error:
            print(f"Could not save history: {error}")

    def add_history(self, expression, answer):
        record = {
            "expression": expression,
            "answer": answer
        }

        self.history.insert(0, record)
        self.history = self.history[:20]

        self.save_history()


    def show_history(self, instance):
        content = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8)
        )

        scroll = ScrollView()

        history_layout = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=dp(8)
        )
        history_layout.bind(
            minimum_height=history_layout.setter("height")
        )

        if not self.history:
            empty_label = Label(
                text="No calculations yet.",
                size_hint_y=None,
                height=dp(50),
                color=MUTED
            )
            history_layout.add_widget(empty_label)

        else:
            for record in self.history:
                expression = record.get("expression", "")
                answer = record.get("answer", "")

                record_button = Button(
                    text=f"{expression} = {answer}",
                    size_hint_y=None,
                    height=dp(52),
                    background_normal="",
                    background_color=CARD,
                    color=WHITE,
                    font_size=sp(14)
                )

                record_button.bind(
                    on_release=lambda button, value=expression:
                    self.restore_history_expression(value, popup)
                )

                history_layout.add_widget(record_button)

        scroll.add_widget(history_layout)
        content.add_widget(scroll)

        close_button = self.make_button(
            "Close",
            DARK_GREEN,
            height=44
        )
        content.add_widget(close_button)

        popup = Popup(
            title="Calculation History",
            content=content,
            size_hint=(0.9, 0.8),
            background_color=CARD,
            title_color=GREEN,
            separator_color=GREEN
        )

        close_button.bind(
            on_release=popup.dismiss
        )

        popup.open()

    def restore_history_expression(self, expression, popup):
        self.display.text = expression
        popup.dismiss()


if __name__ == "__main__":
    QuestCalcApp().run()
