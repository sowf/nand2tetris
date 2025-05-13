import argparse

# A instruction: 0vvvvvvvvvvvvvvv
# C instruction: 1xxaccccccdddjjj


DEST_BITS = {
    "": "000",      # No destination
    "M": "001",     # Memory
    "D": "010",     # D register
    "MD": "011",    # Memory and D register
    "A": "100",     # A register
    "AM": "101",    # A register and Memory
    "AD": "110",    # A register and D register
    "AMD": "111",   # A register, Memory, and D
}

COMP_BITS = {
    "0": "0101010",    # 0
    "1": "0111111",    # 1
    "-1": "0111010",   # -1
    "D": "0001100",    # D
    "A": "0110000",    # A
    "M": "1110000",    # M
    "!D": "0001101",   # not D
    "!A": "0110001",   # not A
    "!M": "1110001",   # not M
    "-D": "0001111",   # -D
    "-A": "0110011",   # -A
    "-M": "1110011",   # -M
    "D+1": "0011111",  # D+1
    "A+1": "0110111",  # A+1
    "M+1": "1110111",  # M+1
    "D-1": "0001110",  # D-1
    "A-1": "0110010",  # A-1
    "M-1": "1110010",  # M-1
    "D+A": "0000010",  # D+A
    "D+M": "1000010",  # D+M
    "D-A": "0010011",  # D-A
    "D-M": "1010011",  # D-M
    "A-D": "0000111",  # A-D
    "M-D": "1000111",  # M-D
    "D&A": "0000000",  # D AND A
    "D&M": "1000000",  # D AND M
    "D|A": "0010101",  # D OR A
    "D|M": "1010101",  # D OR M
}

JUMP_BITS = {
    "": "000",      # No jump
    "JGT": "001",   # Jump if greater than zero
    "JEQ": "010",   # Jump if equal to zero
    "JGE": "011",   # Jump if greater than or equal to zero
    "JLT": "100",   # Jump if less than zero
    "JNE": "101",   # Jump if not equal to zero
    "JLE": "110",   # Jump if less than or equal to zero
    "JMP": "111"    # Jump unconditionally
}


class Interpreter:
    def __init__(self, input_file_path, output_file_path) -> None:
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.input = None
        self.output = None
    
    @staticmethod
    def convert_to_15bit_binary_string(number: int) -> str:
        if not 0 <= number <= 32767:
            raise ValueError(f"Number {number} cannot be represented in 15 bits address")
        return f"{number:015b}"

    @staticmethod
    def parse_c_instruction(line) -> tuple[str, str, str]:
        comp, dest, jump = "", "", ""

        if ";" in line:
            instruction_part, jump = line.split(";", 1)
        else:
            instruction_part = line

        if "=" in instruction_part:
            dest, comp = instruction_part.split("=", 1)
        else:
            comp = instruction_part

        return comp, dest, jump

    def read(self):
        with open(self.input_file_path, 'r') as f:
            self.input = f.readlines()

    def prepare(self):
        symbol_table = {
            "SP": 0, 
            "LCL": 1, 
            "ARG": 2, 
            "THIS": 3, 
            "THAT": 4,
            "R0": 0, 
            "R1": 1, 
            "R2": 2, 
            "R3": 3, 
            "R4": 4, 
            "R5": 5, 
            "R6": 6, 
            "R7": 7,
            "R8": 8, 
            "R9": 9, 
            "R10": 10, 
            "R11": 11, 
            "R12": 12, 
            "R13": 13, 
            "R14": 14, 
            "R15": 15,
            "SCREEN": 16384, 
            "KBD": 24576
        }
        cleaned_lines = []

        # First pass
        line_count = 0
        for line in self.input:
            if "//" in line:
                line = line.split("//")[0]

            line = line.strip()

            if len(line) == 0:
                continue
            
            if line.startswith("(") and line.endswith(")"):
                label = line[1:-1]
                symbol_table[label] = line_count
            else:
                cleaned_lines.append(line)
                line_count += 1

        # Second pass
        variable_address = 16
        result = []
        for line in cleaned_lines:
            if line.startswith("@"):
                symbol = line[1:]
                if not symbol.isdigit() and symbol not in symbol_table:
                    symbol_table[symbol] = variable_address
                    variable_address += 1
                if not symbol.isdigit():
                    line = f"@{symbol_table[symbol]}"
            result.append(line)

        self.input = result

    def convert(self):
        print(self.input)
        self.output = []
        for line in self.input:
            if line.startswith("@"):
                address = int(line[1:])
                instruction = f"0{self.convert_to_15bit_binary_string(address)}"
            else:
                instruction = "111"
                comp, dest, jump = self.parse_c_instruction(line)
                instruction += COMP_BITS[comp]
                instruction += DEST_BITS[dest]
                instruction += JUMP_BITS[jump]

            self.output.append(instruction)
        print(self.output)
    
    def write(self):
        with open(self.output_file_path, 'w') as f:
            for line in self.output:
                print(line, file=f)

    def run(self):
        self.read()
        self.prepare()
        self.convert()
        self.write()


def main():
    parser = argparse.ArgumentParser(description="Interpret asm to binary")
    parser.add_argument("--input", required=True, help="Input ASM file path")
    parser.add_argument("--output", required=True, help="Output binary file path")

    args = parser.parse_args()
    interpreter = Interpreter(args.input, args.output)
    interpreter.run()


if __name__ == "__main__":
    main()
