---
trigger: tocar em autenticação, dados pessoais, pagamentos, ou segredos/credenciais
keywords: auth, autenticacao, login, senha, credencial, credenciais, segredo, segredos, token, jwt, oauth, sessao, cookie, permissao, autorizacao, pagamento, pagamentos, cartao, pix, cobranca, dados, pessoais, lgpd, gdpr, criptografia, hash
load-when: execução
applies-to: obrigatória se R ≥ 40; recomendada sempre que o gatilho ocorrer
priority: security (MÁXIMA — nunca sacrificada por estilo ou velocidade)
---

# security — segurança

Segurança não é uma fase final; é uma restrição em cada decisão. Esta instrução tem prioridade máxima.

**Proporcional ao risco real** (mapeado no questionário): qualquer sinal sensível — login, dados de pessoas — já levanta a base; um "cofre" (pagamentos, setor regulado) levanta mais. Nem todo projeto precisa de segurança ultra. Você já conhece as boas práticas — o papel do harness é **garantir que foram feitas, não reensinar**: valide cada uma, não deixe esquecer.

## Segredos (sempre que houver qualquer credencial)

- **`.env` é obrigatório** assim que existir qualquer credencial — em **qualquer nível**. **Todas** as credenciais vão nele; o `.gitignore` cobre o `.env`; o `.env.example` lista as chaves **sem valores**.
- **Nunca** hardcode, commite, logue ou exponha credencial, token, chave ou senha. Senha (de banco/serviço): use senha forte e **nunca a mostre**.
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

## Profundidade — proporcional ao risco

| Sinal de risco | Reforço (valide que foi feito) |
|---|---|
| Qualquer credencial no projeto | `.env` + segredos fora do repo (sempre) |
| Login / dados de pessoas | hash forte de senha; HTTPS; autorização negada por padrão; `memory/security.md` |
| "Cofre": pagamento / setor regulado | + separação dev/stage/prod; scan de deps; review de mudança sensível |
| Escala alta (Nível 4) | + threat model, `audits/`, testes de segurança, rotação de segredos |

## Registro

Toda decisão de segurança relevante vai para `memory/security.md` (ou `memory/decisions/`). Em dúvida sobre uma escolha sensível, **pare e confirme** com o usuário antes de prosseguir.
