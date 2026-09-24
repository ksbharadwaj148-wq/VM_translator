import sys
from pathlib import Path

from parser import Parser
from code import dest, comp, jump
from symbol_table import SymbolTable


def clean_lines(lines):
    result = []

    for line in lines:

        # Remove comments
        if "//" in line:
            line = line.split("//")[0]

        line = line.strip()

        if line:
            result.append(line)

    return result


def first_pass(lines, symbol_table):

    parser = Parser(lines)

    rom_address = 0

    while parser.has_more_commands():

        parser.advance()

        command_type = parser.command_type()

        if command_type == "L_COMMAND":

            symbol = parser.symbol()

            if symbol_table.contains(symbol):
                raise ValueError(
                    f"Duplicate label: {symbol}"
                )

            symbol_table.add(symbol, rom_address)

        else:
            rom_address += 1


def second_pass(lines, symbol_table):

    parser = Parser(lines)

    output = []

    next_variable_address = 16

    while parser.has_more_commands():

        parser.advance()

        command_type = parser.command_type()

        # --------------------------------
        # A-INSTRUCTION
        # --------------------------------

        if command_type == "A_COMMAND":

            symbol = parser.symbol()

            # Numeric address
            if symbol.isdigit():

                address = int(symbol)

            # Symbolic address
            else:

                if not symbol_table.contains(symbol):

                    symbol_table.add(
                        symbol,
                        next_variable_address
                    )

                    next_variable_address += 1

                address = symbol_table.get_address(symbol)

            if address < 0 or address > 32767:
                raise ValueError(
                    f"Address out of range: {address}"
                )

            binary = format(address, "016b")

            output.append(binary)

        # --------------------------------
        # L-INSTRUCTION
        # --------------------------------

        elif command_type == "L_COMMAND":

            # Labels do not generate machine code
            continue

        # --------------------------------
        # C-INSTRUCTION
        # --------------------------------

        elif command_type == "C_COMMAND":

            dest_part = parser.dest()
            comp_part = parser.comp()
            jump_part = parser.jump()

            binary = (
                "111"
                + comp(comp_part)
                + dest(dest_part)
                + jump(jump_part)
            )

            output.append(binary)

    return output


def assemble(input_file, output_file):

    print(f"Reading: {input_file}")

    with open(input_file, "r") as file:
        lines = file.readlines()

    symbol_table = SymbolTable()

    # -------------------------------
    # PASS 1
    # -------------------------------

    print("Pass 1: Finding labels...")

    first_pass(lines, symbol_table)

    # -------------------------------
    # PASS 2
    # -------------------------------

    print("Pass 2: Generating binary...")

    machine_code = second_pass(
        lines,
        symbol_table
    )

    # -------------------------------
    # WRITE OUTPUT
    # -------------------------------

    with open(output_file, "w") as file:

        for instruction in machine_code:
            file.write(instruction + "\n")

    print()
    print("Assembly successful!")
    print(f"Output: {output_file}")
    print(f"Instructions: {len(machine_code)}")


def main():

    if len(sys.argv) != 2:

        print("Usage:")
        print("python assembler.py Add.asm")
        return

    input_file = Path(sys.argv[1])

    if not input_file.exists():

        print("ERROR: File does not exist")
        print(input_file)
        return

    output_file = input_file.with_suffix(".hack")

    try:
        assemble(
            input_file,
            output_file
        )

    except Exception as error:

        print()
        print("ASSEMBLER ERROR:")
        print(error)


if __name__ == "__main__":
    main()