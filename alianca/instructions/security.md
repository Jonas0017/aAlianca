---
trigger: tocar em autenticação, dados pessoais, pagamentos, ou segredos/credenciais
load-when: execução
applies-to: obrigatória se R ≥ 40; recomendada sempre que o gatilho ocorrer
priority: security (MÁXIMA — nunca sacrificada por estilo ou velocidade)
---

# security — segurança

Segurança não é uma fase final; é uma restrição em cada decisão. Esta instrução tem prioridade máxima.

## Segredos (vale em qualquer projeto, desde o nível 1)

- **Nunca** hardcode ou commite credencial, token, chave ou senha.
- `.gitignore` cobrindo segredos; `.env.example` com as chaves **sem valores**; valores reais só em `.env` local / secret manager.
- **Nunca logue** segredos nem dados pessoais.

## Superfícies sensíveis

Você já conhece as defesas de cada superfície — aplique-as. O que o harness **exige**, sempre:

- **Autenticação:** senha com hash forte e moderno (nunca em texto puro); sessão/token com expiração e transporte seguro.
- **Autorização negada por padrão** (least privilege): cheque permissão a cada acesso, não só na UI.
- **Nunca confie na entrada nem no cliente:** valide e normalize na borda (ver `bug-prevention`); parametrize queries; valide valores no servidor.
- **Dados pessoais:** minimize a coleta; cifre em trânsito (e em repouso, se sensível); registre categorias e base legal em `memory/security.md`.
- **Pagamentos:** nunca guarde cartão cru — use gateway/tokenização.

## Ambientes e configuração (a partir do Nível 2)

- **Separe dev / stage / prod.** Configuração e segredos por ambiente; nunca aponte o ambiente de desenvolvimento para dados de produção.
- Segredos vêm do ambiente (variável de ambiente / secret manager), nunca do código nem do repositório.
- `.env.example` documenta as chaves (sem valores); cada ambiente tem o seu `.env`/secret próprio, fora do versionamento.

## Dependências

- Lockfile versionado; **scan de vulnerabilidade** em dependências (nível ≥ 2); revise licenças.

## Por nível

| Nível | Reforço |
|---|---|
| 1 | segredos fora do repo; HTTPS; hash de senha |
| 2–3 | separação dev/stage/prod; scan de deps; `memory/security.md`; review de mudanças sensíveis |
| 4 | threat model, `audits/`, testes de segurança, rotação de segredos |

## Registro

Toda decisão de segurança relevante vai para `memory/security.md` (ou `memory/decisions/`). Em dúvida sobre uma escolha sensível, **pare e confirme** com o usuário antes de prosseguir.
