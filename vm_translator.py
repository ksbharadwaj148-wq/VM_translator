import sys
from pathlib import Path


class VMTranslator:

    def __init__(self, input_name):
        self.input_name = input_name
        self.output = []

        # Used for generating unique labels
        self.label_counter = 0

        # Current VM file name
        self.current_file = ""

        # Current function name
        self.current_function = ""

        # Used for generating unique return labels
        self.return_counter = 0

    # =========================================================
    # BASIC OUTPUT
    # =========================================================

    def write(self, code):

        for line in code:
            self.output.append(line)

    # =========================================================
    # UNIQUE LABEL
    # =========================================================

    def unique_label(self, prefix):

        label = f"{prefix}{self.label_counter}"
        self.label_counter += 1

        return label

    # =========================================================
    # LOAD VM FILE
    # =========================================================

    def load_file(self, filename):

        self.current_file = Path(filename).stem

        with open(filename, "r") as file:
            lines = file.readlines()

        return self.clean_lines(lines)

    # =========================================================
    # CLEAN VM FILE
    # =========================================================

    def clean_lines(self, lines):

        commands = []

        for line in lines:

            # Remove comments
            if "//" in line:
                line = line.split("//")[0]

            line = line.strip()

            if line:
                commands.append(line)

        return commands

    # =========================================================
    # PUSH
    # =========================================================

    def write_push(self, segment, index):

        index = int(index)

        # -----------------------------------------------------
        # constant
        # -----------------------------------------------------

        if segment == "constant":

            self.write([
                f"@{index}",
                "D=A",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ])

        # -----------------------------------------------------
        # local / argument / this / that
        # -----------------------------------------------------

        elif segment in ["local", "argument", "this", "that"]:

            base = {
                "local": "LCL",
                "argument": "ARG",
                "this": "THIS",
                "that": "THAT"
            }[segment]

            self.write([
                f"@{base}",
                "D=M",
                f"@{index}",
                "A=D+A",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ])

        # -----------------------------------------------------
        # temp
        # RAM[5] - RAM[12]
        # -----------------------------------------------------

        elif segment == "temp":

            address = 5 + index

            self.write([
                f"@{address}",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ])

        # -----------------------------------------------------
        # pointer
        #
        # pointer 0 -> THIS
        # pointer 1 -> THAT
        # -----------------------------------------------------

        elif segment == "pointer":

            if index == 0:
                address = "THIS"

            elif index == 1:
                address = "THAT"

            else:
                raise ValueError(
                    "pointer index must be 0 or 1"
                )

            self.write([
                f"@{address}",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ])

        # -----------------------------------------------------
        # static
        # -----------------------------------------------------

        elif segment == "static":

            symbol = f"{self.current_file}.{index}"

            self.write([
                f"@{symbol}",
                "D=M",
                "@SP",
                "A=M",
                "M=D",
                "@SP",
                "M=M+1"
            ])

        else:

            raise ValueError(
                f"Invalid push segment: {segment}"
            )

    # =========================================================
    # POP
    # =========================================================

    def write_pop(self, segment, index):

        index = int(index)

        # -----------------------------------------------------
        # local / argument / this / that
        # -----------------------------------------------------

        if segment in ["local", "argument", "this", "that"]:

            base = {
                "local": "LCL",
                "argument": "ARG",
                "this": "THIS",
                "that": "THAT"
            }[segment]

            # Calculate destination address
            self.write([
                f"@{base}",
                "D=M",
                f"@{index}",
                "D=D+A",
                "@R13",
                "M=D",

                "@SP",
                "AM=M-1",
                "D=M",

                "@R13",
                "A=M",
                "M=D"
            ])

        # -----------------------------------------------------
        # temp
        # -----------------------------------------------------

        elif segment == "temp":

            address = 5 + index

            self.write([
                "@SP",
                "AM=M-1",
                "D=M",
                f"@{address}",
                "M=D"
            ])

        # -----------------------------------------------------
        # pointer
        # -----------------------------------------------------

        elif segment == "pointer":

            if index == 0:
                address = "THIS"

            elif index == 1:
                address = "THAT"

            else:
                raise ValueError(
                    "pointer index must be 0 or 1"
                )

            self.write([
                "@SP",
                "AM=M-1",
                "D=M",
                f"@{address}",
                "M=D"
            ])

        # -----------------------------------------------------
        # static
        # -----------------------------------------------------

        elif segment == "static":

            symbol = f"{self.current_file}.{index}"

            self.write([
                "@SP",
                "AM=M-1",
                "D=M",
                f"@{symbol}",
                "M=D"
            ])

        # -----------------------------------------------------
        # constant cannot be popped
        # -----------------------------------------------------

        elif segment == "constant":

            raise ValueError(
                "Cannot pop to constant"
            )

        else:

            raise ValueError(
                f"Invalid pop segment: {segment}"
            )

    # =========================================================
    # ARITHMETIC
    # =========================================================

    def write_arithmetic(self, command):

        # -----------------------------------------------------
        # ADD
        # -----------------------------------------------------

        if command == "add":

            self.write([
                "@SP",
                "AM=M-1",
                "D=M",
                "A=A-1",
                "M=M+D"
            ])

        # -----------------------------------------------------
        # SUB
        # -----------------------------------------------------

        elif command == "sub":

            self.write([
                "@SP",
                "AM=M-1",
                "D=M",
                "A=A-1",
                "M=M-D"
            ])

        # -----------------------------------------------------
        # NEG
        # -----------------------------------------------------

        elif command == "neg":

            self.write([
                "@SP",
                "A=M-1",
                "M=-M"
            ])

        # -----------------------------------------------------
        # AND
        # -----------------------------------------------------

        elif command == "and":

            self.write([
                "@SP",
                "AM=M-1",
                "D=M",
                "A=A-1",
                "M=D&M"
            ])

        # -----------------------------------------------------
        # OR
        # -----------------------------------------------------

        elif command == "or":

            self.write([
                "@SP",
                "AM=M-1",
                "D=M",
                "A=A-1",
                "M=D|M"
            ])

        # -----------------------------------------------------
        # NOT
        # -----------------------------------------------------

        elif command == "not":

            self.write([
                "@SP",
                "A=M-1",
                "M=!M"
            ])

        # -----------------------------------------------------
        # EQ / GT / LT
        # -----------------------------------------------------

        elif command in ["eq", "gt", "lt"]:

            true_label = self.unique_label("TRUE")
            end_label = self.unique_label("END")

            jump_command = {
                "eq": "JEQ",
                "gt": "JGT",
                "lt": "JLT"
            }[command]

            self.write([
                "@SP",
                "AM=M-1",
                "D=M",

                "A=A-1",
                "D=M-D",

                f"@{true_label}",
                f"D;{jump_command}",

                "@SP",
                "A=M-1",
                "M=0",

                f"@{end_label}",
                "0;JMP",

                f"({true_label})",
                "@SP",
                "A=M-1",
                "M=-1",

                f"({end_label})"
            ])

        else:

            raise ValueError(
                f"Invalid arithmetic command: {command}"
            )

    # =========================================================
    # LABEL
    # =========================================================

    def write_label(self, label):

        if self.current_function:

            full_label = (
                f"{self.current_function}${label}"
            )

        else:

            full_label = label

        self.write([
            f"({full_label})"
        ])

    # =========================================================
    # GOTO
    # =========================================================

    def write_goto(self, label):

        if self.current_function:

            full_label = (
                f"{self.current_function}${label}"
            )

        else:

            full_label = label

        self.write([
            f"@{full_label}",
            "0;JMP"
        ])

    # =========================================================
    # IF-GOTO
    # =========================================================

    def write_if(self, label):

        if self.current_function:

            full_label = (
                f"{self.current_function}${label}"
            )

        else:

            full_label = label

        self.write([
            "@SP",
            "AM=M-1",
            "D=M",
            f"@{full_label}",
            "D;JNE"
        ])

    # =========================================================
    # FUNCTION
    # =========================================================

    def write_function(self, name, n_vars):

        n_vars = int(n_vars)

        self.current_function = name

        self.write([
            f"({name})"
        ])

        # Initialize local variables to 0
        for _ in range(n_vars):

            self.write([
                "@SP",
                "A=M",
                "M=0",
                "@SP",
                "M=M+1"
            ])

    # =========================================================
    # CALL
    # =========================================================

    def write_call(self, name, n_args):

        n_args = int(n_args)

        return_label = (
            f"{self.current_file}$ret.{self.return_counter}"
        )

        self.return_counter += 1

        # -----------------------------------------------------
        # Push return address
        # -----------------------------------------------------

        self.write([
            f"@{return_label}",
            "D=A",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1"
        ])

        # -----------------------------------------------------
        # Push LCL
        # -----------------------------------------------------

        self.write([
            "@LCL",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1"
        ])

        # -----------------------------------------------------
        # Push ARG
        # -----------------------------------------------------

        self.write([
            "@ARG",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1"
        ])

        # -----------------------------------------------------
        # Push THIS
        # -----------------------------------------------------

        self.write([
            "@THIS",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1"
        ])

        # -----------------------------------------------------
        # Push THAT
        # -----------------------------------------------------

        self.write([
            "@THAT",
            "D=M",
            "@SP",
            "A=M",
            "M=D",
            "@SP",
            "M=M+1"
        ])

        # -----------------------------------------------------
        # ARG = SP - 5 - nArgs
        # -----------------------------------------------------

        self.write([
            "@SP",
            "D=M",
            "@5",
            "D=D-A",
            f"@{n_args}",
            "D=D-A",
            "@ARG",
            "M=D"
        ])

        # -----------------------------------------------------
        # LCL = SP
        # -----------------------------------------------------

        self.write([
            "@SP",
            "D=M",
            "@LCL",
            "M=D"
        ])

        # -----------------------------------------------------
        # goto function
        # -----------------------------------------------------

        self.write([
            f"@{name}",
            "0;JMP",

            f"({return_label})"
        ])

    # =========================================================
    # RETURN
    # =========================================================

    def write_return(self):

        # FRAME = LCL
        # RET = *(FRAME - 5)

        self.write([
            "@LCL",
            "D=M",
            "@R13",
            "M=D",

            "@5",
            "A=D-A",
            "D=M",
            "@R14",
            "M=D"
        ])

        # -----------------------------------------------------
        # *ARG = pop()
        # -----------------------------------------------------

        self.write([
            "@SP",
            "AM=M-1",
            "D=M",
            "@ARG",
            "A=M",
            "M=D"
        ])

        # -----------------------------------------------------
        # SP = ARG + 1
        # -----------------------------------------------------

        self.write([
            "@ARG",
            "D=M+1",
            "@SP",
            "M=D"
        ])

        # -----------------------------------------------------
        # THAT = *(FRAME - 1)
        # THIS = *(FRAME - 2)
        # ARG  = *(FRAME - 3)
        # LCL  = *(FRAME - 4)
        # -----------------------------------------------------

        self.write([
            "@R13",
            "AM=M-1",
            "D=M",
            "@THAT",
            "M=D",

            "@R13",
            "AM=M-1",
            "D=M",
            "@THIS",
            "M=D",

            "@R13",
            "AM=M-1",
            "D=M",
            "@ARG",
            "M=D",

            "@R13",
            "AM=M-1",
            "D=M",
            "@LCL",
            "M=D"
        ])

        # -----------------------------------------------------
        # goto RET
        # -----------------------------------------------------

        self.write([
            "@R14",
            "A=M",
            "0;JMP"
        ])

    # =========================================================
    # BOOTSTRAP
    # =========================================================

    def write_bootstrap(self):

        self.write([
            "@256",
            "D=A",
            "@SP",
            "M=D"
        ])

        self.write_call(
            "Sys.init",
            0
        )

    # =========================================================
    # TRANSLATE COMMAND
    # =========================================================

    def translate_command(self, command):

        parts = command.split()

        if not parts:
            return

        command_type = parts[0]

        # -----------------------------------------------------
        # Arithmetic
        # -----------------------------------------------------

        if command_type in [
            "add",
            "sub",
            "neg",
            "eq",
            "gt",
            "lt",
            "and",
            "or",
            "not"
        ]:

            self.write_arithmetic(command_type)

        # -----------------------------------------------------
        # PUSH
        # -----------------------------------------------------

        elif command_type == "push":

            if len(parts) != 3:
                raise ValueError(
                    f"Invalid push command: {command}"
                )

            self.write_push(
                parts[1],
                parts[2]
            )

        # -----------------------------------------------------
        # POP
        # -----------------------------------------------------

        elif command_type == "pop":

            if len(parts) != 3:
                raise ValueError(
                    f"Invalid pop command: {command}"
                )

            self.write_pop(
                parts[1],
                parts[2]
            )

        # -----------------------------------------------------
        # LABEL
        # -----------------------------------------------------

        elif command_type == "label":

            self.write_label(parts[1])

        # -----------------------------------------------------
        # GOTO
        # -----------------------------------------------------

        elif command_type == "goto":

            self.write_goto(parts[1])

        # -----------------------------------------------------
        # IF-GOTO
        # -----------------------------------------------------

        elif command_type == "if-goto":

            self.write_if(parts[1])

        # -----------------------------------------------------
        # FUNCTION
        # -----------------------------------------------------

        elif command_type == "function":

            self.write_function(
                parts[1],
                parts[2]
            )

        # -----------------------------------------------------
        # CALL
        # -----------------------------------------------------

        elif command_type == "call":

            self.write_call(
                parts[1],
                parts[2]
            )

        # -----------------------------------------------------
        # RETURN
        # -----------------------------------------------------

        elif command_type == "return":

            self.write_return()

        else:

            raise ValueError(
                f"Unknown VM command: {command}"
            )

    # =========================================================
    # TRANSLATE FILE
    # =========================================================

    def translate_file(self, filename):

        commands = self.load_file(filename)

        for command in commands:

            # Add comment showing original VM command
            self.output.append(
                f"// {command}"
            )

            self.translate_command(command)

    # =========================================================
    # SAVE OUTPUT
    # =========================================================

    def save(self, output_file):

        with open(output_file, "w") as file:

            for line in self.output:

                file.write(line + "\n")


# =============================================================
# MAIN PROGRAM
# =============================================================

def main():

    if len(sys.argv) != 2:

        print("Usage:")
        print("python vm_translator.py <file.vm>")
        print()
        print("Example:")
        print("python vm_translator.py SimpleAdd\\SimpleAdd.vm")

        return

    input_path = Path(sys.argv[1])

    if not input_path.exists():

        print("ERROR: Input does not exist:")
        print(input_path)

        return

    # =========================================================
    # SINGLE VM FILE
    # =========================================================

    if input_path.is_file():

        if input_path.suffix.lower() != ".vm":

            print("ERROR: Input file must be .vm")

            return

        output_file = input_path.with_suffix(".asm")

        translator = VMTranslator(
            input_path.stem
        )

        print("Translating:")
        print(input_path)

        translator.translate_file(
            input_path
        )

        translator.save(
            output_file
        )

        print()
        print("Translation successful!")
        print("Output:")
        print(output_file)

    # =========================================================
    # DIRECTORY
    # =========================================================

    elif input_path.is_dir():

        vm_files = sorted(
            input_path.glob("*.vm")
        )

        if not vm_files:

            print("ERROR: No .vm files found")

            return

        output_file = (
            input_path /
            (input_path.name + ".asm")
        )

        translator = VMTranslator(
            input_path.name
        )

        print("Translating directory:")
        print(input_path)

        # Bootstrap
        print("Adding bootstrap code...")

        translator.write_bootstrap()

        # Translate every VM file
        for vm_file in vm_files:

            print(
                "Translating:",
                vm_file.name
            )

            translator.translate_file(
                vm_file
            )

        translator.save(
            output_file
        )

        print()
        print("Translation successful!")
        print("Output:")
        print(output_file)


if __name__ == "__main__":
    main()