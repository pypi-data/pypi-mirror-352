import argparse
import os
from pathlib import Path
from colorama import Fore, Style, init

init(autoreset=True)

def remove_yaml_comments(yaml_text):
    cleaned_lines = []

    for line in yaml_text.splitlines():
        stripped = line.strip()

        if stripped.startswith("#"):
            continue

        quote_open = False
        new_line = ""
        for i, char in enumerate(line):
            if char in "\"'":
                quote_open = not quote_open
            if char == '#' and not quote_open:
                new_line = line[:i].rstrip()
                break
        else:
            new_line = line

        cleaned_lines.append(new_line)

    return "\n".join(cleaned_lines)


def process_file(filepath: Path, output_base: Path):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    cleaned = remove_yaml_comments(content)

    relative_path = filepath.relative_to(filepath.parents[0])
    output_path = output_base / relative_path
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleaned)

    print(f"{Fore.GREEN}Nettoyé : {output_path}")


def process_path(input_path: Path, output_path: Path):
    if input_path.is_file() and input_path.suffix in ['.yaml', '.yml']:
        process_file(input_path, output_path)
    elif input_path.is_dir():
        for root, _, files in os.walk(input_path):
            for file in files:
                if file.endswith(('.yml', '.yaml')):
                    full_path = Path(root) / file
                    process_file(full_path, output_path)
    else:
        print(f"{Fore.RED}Chemin invalide ou pas un fichier YAML : {input_path}")


def main():
    parser = argparse.ArgumentParser(description="Nettoyeur de commentaires YAML.")
    parser.add_argument("input", help="Fichier ou dossier source")
    parser.add_argument("-o", "--output", help="Dossier de sortie (par défaut: ./cleaned)", default="cleaned")

    args = parser.parse_args()
    input_path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()

    process_path(input_path, output_path)
