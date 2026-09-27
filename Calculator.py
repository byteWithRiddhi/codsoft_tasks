import tkinter as tk
import math

class Calculator:

    def __init__(self, root):
        self.root = root

        self.root.title("Calculator")
        self.root.geometry("420x700")
        self.root.minsize(380, 600)
        self.root.configure(bg="#202124")

        self.expression = ""
        self.result_displayed = False

        self.bg_color = "#202124"
        self.display_color = "#202124"
        self.number_color = "#303134"
        self.operator_color = "#3c4043"
        self.function_color = "#5f6368"
        self.equal_color = "#8ab4f8"
        self.text_color = "#ffffff"
        self.secondary_text = "#9aa0a6"

        self.create_display()
        self.create_buttons()

        self.root.bind("<Key>", self.keyboard_input)

    def create_display(self):

        display_frame = tk.Frame(
            self.root,
            bg=self.display_color
        )

        display_frame.pack(
            fill="both",
            expand=False,
            padx=15,
            pady=(20, 5)
        )

        self.expression_label = tk.Label(
            display_frame,
            text="",
            anchor="e",
            bg=self.display_color,
            fg=self.secondary_text,
            font=("Arial", 14)
        )

        self.expression_label.pack(
            fill="x",
            padx=10,
            pady=(10, 0)
        )

        self.display = tk.Label(
            display_frame,
            text="0",
            anchor="e",
            bg=self.display_color,
            fg=self.text_color,
            font=("Arial", 34, "bold")
        )

        self.display.pack(
            fill="x",
            padx=10,
            pady=(5, 15)
        )

    def create_buttons(self):

        button_frame = tk.Frame(
            self.root,
            bg=self.bg_color
        )

        button_frame.pack(
            fill="both",
            expand=True,
            padx=12,
            pady=10
        )

        for row in range(7):
            button_frame.rowconfigure(row, weight=1)

        for col in range(5):
            button_frame.columnconfigure(col, weight=1)

        buttons = [

            ("AC", 0, 0, self.clear, self.function_color),
            ("⌫", 0, 1, self.backspace, self.function_color),
            ("(", 0, 2, lambda: self.add_to_expression("("), self.function_color),
            (")", 0, 3, lambda: self.add_to_expression(")"), self.function_color),
            ("÷", 0, 4, lambda: self.add_to_expression("/"), self.operator_color),

            ("sin", 1, 0, lambda: self.scientific_function("sin"), self.function_color),
            ("cos", 1, 1, lambda: self.scientific_function("cos"), self.function_color),
            ("tan", 1, 2, lambda: self.scientific_function("tan"), self.function_color),
            ("√", 1, 3, lambda: self.scientific_function("sqrt"), self.function_color),
            ("×", 1, 4, lambda: self.add_to_expression("*"), self.operator_color),

            ("x²", 2, 0, self.square, self.function_color),
            ("1/x", 2, 1, self.reciprocal, self.function_color),
            ("log", 2, 2, lambda: self.scientific_function("log"), self.function_color),
            ("ln", 2, 3, lambda: self.scientific_function("ln"), self.function_color),
            ("−", 2, 4, lambda: self.add_to_expression("-"), self.operator_color),

            ("7", 3, 0, lambda: self.add_to_expression("7"), self.number_color),
            ("8", 3, 1, lambda: self.add_to_expression("8"), self.number_color),
            ("9", 3, 2, lambda: self.add_to_expression("9"), self.number_color),
            ("%", 3, 3, self.percent, self.function_color),
            ("+", 3, 4, lambda: self.add_to_expression("+"), self.operator_color),

            ("4", 4, 0, lambda: self.add_to_expression("4"), self.number_color),
            ("5", 4, 1, lambda: self.add_to_expression("5"), self.number_color),
            ("6", 4, 2, lambda: self.add_to_expression("6"), self.number_color),
            ("π", 4, 3, lambda: self.add_to_expression("pi"), self.function_color),
            ("=", 4, 4, self.calculate, self.equal_color),

            ("1", 5, 0, lambda: self.add_to_expression("1"), self.number_color),
            ("2", 5, 1, lambda: self.add_to_expression("2"), self.number_color),
            ("3", 5, 2, lambda: self.add_to_expression("3"), self.number_color),
            ("e", 5, 3, lambda: self.add_to_expression("e"), self.function_color),
            (".", 5, 4, lambda: self.add_to_expression("."), self.number_color),

            ("0", 6, 0, lambda: self.add_to_expression("0"), self.number_color),
            ("00", 6, 1, lambda: self.add_to_expression("00"), self.number_color),
            ("±", 6, 2, self.toggle_sign, self.function_color),
            ("Ans", 6, 3, self.add_answer, self.function_color),
            ("=", 6, 4, self.calculate, self.equal_color),
        ]

        for text, row, col, command, color in buttons:

            button = tk.Button(
                button_frame,
                text=text,
                command=command,
                bg=color,
                fg=self.text_color,
                activebackground="#6b7075",
                activeforeground="#ffffff",
                font=("Arial", 13, "bold"),
                relief="flat",
                bd=0,
                cursor="hand2"
            )

            button.grid(
                row=row,
                column=col,
                padx=4,
                pady=4,
                sticky="nsew"
            )

    def add_to_expression(self, value):

        if self.result_displayed:
            if value in "+-*/":
                self.expression = self.display.cget("text")
            else:
                self.expression = ""

            self.result_displayed = False

        self.expression += value
        self.update_display()

    def update_display(self):

        display_expression = self.expression

        display_expression = display_expression.replace(
            "*", "×"
        )

        display_expression = display_expression.replace(
            "/", "÷"
        )

        self.expression_label.config(
            text=display_expression
        )

        if self.expression:
            self.display.config(
                text=self.expression
            )
        else:
            self.display.config(
                text="0"
            )

    def clear(self):

        self.expression = ""
        self.result_displayed = False

        self.expression_label.config(text="")
        self.display.config(text="0")

    def backspace(self):

        if self.result_displayed:
            self.clear()
            return

        self.expression = self.expression[:-1]
        self.update_display()

    def calculate(self):

        if not self.expression:
            return

        try:

            expression = self.expression

            expression = expression.replace(
                "pi", str(math.pi)
            )

            expression = expression.replace(
                "e", str(math.e)
            )

            result = eval(
                expression,
                {
                    "__builtins__": {},
                    "abs": abs
                }
            )

            if isinstance(result, float) and result.is_integer():
                result = int(result)

            self.expression_label.config(
                text=self.expression.replace("*", "×").replace("/", "÷")
            )

            self.display.config(
                text=str(result)
            )

            self.last_answer = result
            self.result_displayed = True

        except ZeroDivisionError:

            self.display.config(
                text="Cannot divide by zero"
            )

            self.result_displayed = True

        except Exception:

            self.display.config(
                text="Invalid expression"
            )

            self.result_displayed = True

    def scientific_function(self, function):

        if not self.expression:
            return

        try:

            expression = self.expression

            expression = expression.replace(
                "pi", str(math.pi)
            )

            expression = expression.replace(
                "e", str(math.e)
            )

            value = eval(
                expression,
                {"__builtins__": {}}
            )

            # Trigonometric functions use degrees
            if function == "sin":
                result = math.sin(math.radians(value))

            elif function == "cos":
                result = math.cos(math.radians(value))

            elif function == "tan":
                result = math.tan(math.radians(value))

            elif function == "sqrt":
                result = math.sqrt(value)

            elif function == "log":
                result = math.log10(value)

            elif function == "ln":
                result = math.log(value)

            else:
                return

            if isinstance(result, float) and result.is_integer():
                result = int(result)

            self.expression_label.config(
                text=f"{function}({self.expression})"
            )

            self.display.config(
                text=str(result)
            )

            self.last_answer = result
            self.result_displayed = True

        except ValueError:

            self.display.config(
                text="Math error"
            )

            self.result_displayed = True

        except Exception:

            self.display.config(
                text="Invalid expression"
            )

            self.result_displayed = True

    def square(self):

        if not self.expression:
            return

        try:

            value = eval(
                self.expression.replace("pi", str(math.pi)),
                {"__builtins__": {}}
            )

            result = value ** 2

            if result.is_integer():
                result = int(result)

            self.expression_label.config(
                text=f"({self.expression})²"
            )

            self.display.config(
                text=str(result)
            )

            self.last_answer = result
            self.result_displayed = True

        except Exception:

            self.display.config(
                text="Invalid expression"
            )

            self.result_displayed = True

    def reciprocal(self):

        if not self.expression:
            return

        try:

            value = eval(
                self.expression.replace("pi", str(math.pi)),
                {"__builtins__": {}}
            )

            if value == 0:
                raise ZeroDivisionError

            result = 1 / value

            self.expression_label.config(
                text=f"1/({self.expression})"
            )

            self.display.config(
                text=f"{result:.10g}"
            )

            self.last_answer = result
            self.result_displayed = True

        except ZeroDivisionError:

            self.display.config(
                text="Cannot divide by zero"
            )

            self.result_displayed = True

        except Exception:

            self.display.config(
                text="Invalid expression"
            )

            self.result_displayed = True

    def percent(self):

        if not self.expression:
            return

        try:

            value = eval(
                self.expression.replace("pi", str(math.pi)),
                {"__builtins__": {}}
            )

            result = value / 100

            self.expression_label.config(
                text=f"{self.expression}%"
            )

            self.display.config(
                text=str(result)
            )

            self.last_answer = result
            self.result_displayed = True

        except Exception:

            self.display.config(
                text="Invalid expression"
            )

            self.result_displayed = True

    def toggle_sign(self):

        if not self.expression:
            return

        try:

            value = eval(
                self.expression.replace("pi", str(math.pi)),
                {"__builtins__": {}}
            )

            result = -value

            if isinstance(result, float) and result.is_integer():
                result = int(result)

            self.expression = str(result)
            self.update_display()

        except Exception:

            self.display.config(
                text="Invalid expression"
            )

    def add_answer(self):

        if hasattr(self, "last_answer"):

            if self.result_displayed:
                self.expression = ""

            self.expression += str(self.last_answer)

            self.result_displayed = False

            self.update_display()

    def keyboard_input(self, event):

        key = event.keysym
        char = event.char

        if char in "0123456789.+-*/()":
            self.add_to_expression(char)

        elif key in ("Return", "KP_Enter"):
            self.calculate()

        elif key == "BackSpace":
            self.backspace()

        elif key == "Escape":
            self.clear()

if __name__ == "__main__":

    root = tk.Tk()
    calculator = Calculator(root)
    root.mainloop()
