class Parser:

    def __init__(self, lines):
        self.instructions = []

        for line in lines:
            line = line.strip()

            # Remove comments
            if "//" in line:
                line = line.split("//")[0].strip()

            # Ignore blank lines
            if line:
                self.instructions.append(line)

        self.current = -1

    def has_more_commands(self):
        return self.current + 1 < len(self.instructions)

    def advance(self):
        self.current += 1

    def current_command(self):
        return self.instructions[self.current]

    def command_type(self):

        command = self.current_command()

        if command.startswith("@"):
            return "A_COMMAND"

        elif command.startswith("(") and command.endswith(")"):
            return "L_COMMAND"

        else:
            return "C_COMMAND"

    def symbol(self):

        command = self.current_command()

        if self.command_type() == "A_COMMAND":
            return command[1:]

        elif self.command_type() == "L_COMMAND":
            return command[1:-1]

        else:
            raise ValueError("Symbol is not available for C-command")

    def dest(self):

        command = self.current_command()

        if "=" in command:
            return command.split("=")[0]

        return None

    def comp(self):

        command = self.current_command()

        if "=" in command:
            command = command.split("=")[1]

        if ";" in command:
            command = command.split(";")[0]

        return command

    def jump(self):

        command = self.current_command()

        if ";" in command:
            return command.split(";")[1]

        return None