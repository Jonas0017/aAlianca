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

## Autenticação e autorização

- Senhas: **hash forte** (argon2/bcrypt), nunca texto puro nem MD5/SHA1.
- Sessões/tokens: expiração, rotação, transporte seguro (HTTPS), `httpOnly`/`secure` em cookies.
- **Autorização por padrão negada** (least privilege): verifique permissão em cada acesso, não só na UI. RBAC quando há papéis.

## Entrada e injeção

- **Queries parametrizadas** sempre (anti-SQLi). Nunca concatene input em query/comando.
- Escape/sanitize saída para prevenir XSS; valide e normalize todo input (ver `bug-prevention`).
- Cuidado com deserialização, upload de arquivo e SSRF.

## Dados pessoais (LGPD/GDPR)

- **Minimização:** colete só o necessário.
- Criptografia em trânsito (TLS) e, para dado sensível, em repouso.
- Suporte a consentimento e ao direito de exclusão/portabilidade.
- Documente categorias de dados e base legal em `memory/security.md`.

## Pagamentos

- **Nunca** armazene dados de cartão crus — use gateway/tokenização (PCI-DSS).
- Valide valores e idempotência no servidor, nunca confie no cliente.

## Dependências

- Lockfile versionado; **scan de vulnerabilidade** em dependências (nível ≥ 2); revise licenças.

## Por nível

| Nível | Reforço |
|---|---|
| 1 | segredos fora do repo; HTTPS; hash de senha |
| 2–3 | scan de deps; `memory/security.md`; review de mudanças sensíveis |
| 4 | threat model, `audits/`, testes de segurança, rotação de segredos |

## Registro

Toda decisão de segurança relevante vai para `memory/security.md` (ou `memory/decisions/`). Em dúvida sobre uma escolha sensível, **pare e confirme** com o usuário antes de prosseguir.
