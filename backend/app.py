from local_analysis.sanitizer import sanitize
from semantic_analysis.gemini_client import analyze_security

def run_linter(user_prompt: str):
    print("\n=== SAFEGEN - Linter de Prompts ===\n")
    print(f"Prompt original:\n{user_prompt}\n")

    ############ ETAPA 1: ANÁLISE DE DADOS SENSÍVEIS ############ 
    print(">> Etapa 1: Verificando dados sensíveis (Phi-3 Mini)")
    sanitization = sanitize(user_prompt)

    if sanitization.get("error"):
        print(f"Aviso: {sanitization['error']}")

    if sanitization["sensitive_data"]:
        print("Dados sensíveis detectados. Prompt sanitizado.")
    else:
        print("Nenhum dado sensível encontrado.")

    sanitized = sanitization["sanitized_prompt"]

    ############### ETAPA 2: ANÁLISE SEMÂNTICA ###############
    print("\n>> Etapa 2: Analisando riscos de segurança (Gemini 2.5 Flash)")
    security = analyze_security(sanitized)

    if security.get("error"):
        print(f"Aviso: {security['error']}")

    if security["security_risk"]:
        print("Riscos de segurança identificados:")
        for issue in security["issues"]:
            print(f"  - {issue}")
        print(f"\nPrompt seguro sugerido:\n{security['safe_prompt']}")
    else:
        print("Nenhum risco de segurança identificado.")

    print("\n=== Resultado Final ===")
    return {
        "original_prompt": user_prompt,
        "sensitive_data": sanitization["sensitive_data"],
        "sanitized_prompt": sanitized,
        "security_risk": security["security_risk"],
        "issues": security["issues"],
        "safe_prompt": security["safe_prompt"]
    }

if __name__ == "__main__":
    prompt = input("Digite o prompt para análise: ")
    result = run_linter(prompt)