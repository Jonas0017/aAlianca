# stack — ferramentas e ambiente do desenvolvimento da Aliança

> Comandos concretos e fatos de ambiente deste repo. O backbone (`testing`, `code-quality`) e os benchmarks leem daqui.

## Kernel
- Testes do kernel: `python alianca/kernel/selftest.py` (58 PASS).
- Verificação do repo (3º portão): `alianca/kernel/verify.cmd`.
- Índice roteador: `python alianca/kernel/compile.py` gera `router.index.json` (grafo `pulls`).

## Ambiente desta máquina (Windows)
- **O Ollama corrompe a saída com flash attention ligado nesta máquina** (Ollama 0.30.6, `AppData/Local/Programs/Ollama`): duplica tokens (`if if`, `isalnumalnum()`) e trunca código no meio (`()`). Afeta **todos** os modelos (`qwen2.5-coder:7b`, `llama3`) → é bug de runtime/GPU, não do modelo.
  - **Correção permanente (já aplicada):** variável de usuário `OLLAMA_FLASH_ATTENTION=0`. Se o app de bandeja estiver aberto, reiniciar pra pegar. Reinstalar **não** resolve (a mesma versão religa o recurso).
  - **Rodar servidor em teste:** `OLLAMA_FLASH_ATTENTION=0 ollama serve &` (processos com `&` no Bash tool persistem entre chamadas na sessão). Antes de confiar em qualquer benchmark local, checar token duplicado com a regex `\b(\w{2,})\s+\1\b`.
