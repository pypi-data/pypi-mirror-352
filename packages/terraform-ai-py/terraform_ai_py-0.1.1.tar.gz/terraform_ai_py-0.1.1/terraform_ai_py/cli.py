import argparse
from ai import generate_terraform
import subprocess

def run_cli():
    parser = argparse.ArgumentParser(description="Gere código Terraform com IA")
    parser.add_argument("prompt", type=str, help="Descrição do recurso que deseja criar")
    parser.add_argument("--output", type=str, default="generated/main.tf", help="Arquivo de saída")

    args = parser.parse_args()
    
    result = generate_terraform(args.prompt)
    
    with open(args.output, "w") as f:
        f.write(result)
    
    print(f"Terraform gerado em: {args.output}\n")
    
    with open(args.output, "r") as f:
        content = f.read()
        print("Conteúdo do arquivo gerado:\n")
        print(content)

def validate_tf(path: str):
    print("Validando com Terraform...")
    subprocess.run(["terraform", "fmt", path])
    subprocess.run(["terraform", "validate"])

if __name__ == "__main__":
    run_cli()
