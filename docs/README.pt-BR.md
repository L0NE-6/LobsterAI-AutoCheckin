# 🦞 LobsterAI AutoCheckin

**Check-in diário do LobsterAI com extração de credenciais do cliente desktop, login por SMS, várias contas, renovação de token e notificações opcionais.**

[简体中文](../README.md) | [English](README.en.md) | [繁體中文](README.zh-Hant.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Português (BR)](README.pt-BR.md)

> A documentação chinesa completa está em [../README.md](../README.md).

## Visão geral

O LobsterAI AutoCheckin recebe a recompensa diária de uma ou várias contas do LobsterAI. O fluxo lê o slot e o context, envia o check-in e lê o context novamente para verificar o resultado. A execução distingue sucesso, conta já verificada, atividade não oferecida pelo serviço e falha de requisição.

O repositório inclui três scripts: `lobsterai_checkin.py` para o check-in diário, `lobsterai_login.py` para extrair credenciais do cliente desktop e `lobsterai_sms.py` para o login opcional por SMS com Playwright. O check-in e a extração desktop precisam apenas de `requests`; o Playwright é específico do auxiliar de SMS.

## Recursos principais

- Executa a sequência `slot → context → check_in → context`.
- Suporta várias contas por `LOBSTERAI_TOKEN`.
- Renova o AT com o RT quando faltam menos de sete dias para expirar.
- Persiste tokens rotacionados em `lb_refresh_tokens.json`.
- Diferencia conta já verificada e atividade indisponível.
- Obtém a versão do cliente na API oficial de atualização e permite substituição manual.
- Envia notificações opcionais pelo PushPlus e mascara credenciais nos logs normais.

## Preparação das credenciais

Cada conta usa `uid:AT:RT`. Uma entrada somente com AT funciona até expirar, mas não se renova automaticamente.

### Extração do cliente desktop

Instale e entre no cliente desktop do LobsterAI e execute:

```bash
python lobsterai_login.py
python lobsterai_login.py --export
```

No Windows, a ferramenta lê `%APPDATA%/LobsterAI/lobsterai.sqlite` e obtém `accessToken` e `refreshToken` de `kv.auth_tokens`. Com `--export`, imprime apenas a linha `uid:AT:RT` pronta para uso.

### Login por SMS

```bash
pip install playwright
playwright install chromium
python lobsterai_sms.py
python lobsterai_sms.py 138xxxxxxxx
python lobsterai_sms.py --headless 138xxxxxxxx
```

Conclua o slider e informe o código SMS conforme a página. O auxiliar converte o login em `uid:AT:RT`. O telefone de exemplo serve apenas para demonstrar o comando.

## Configuração mínima no Qinglong

1. Envie `lobsterai_checkin.py`.
2. Instale a dependência com `pip3 install requests`.
3. Adicione a variável de ambiente:

```text
LOBSTERAI_TOKEN=UID_VALUE:AT_VALUE:RT_VALUE
```

4. Crie a tarefa agendada:

```bash
task lobsterai_checkin.py
```

Cron sugerido:

```cron
0 9 * * *
```

Separe várias contas por quebras de linha ou `@`. Adicione `PUSHPLUS_TOKEN` somente se quiser notificações.

## Configuração mínima no GitHub Actions

Adicione estes Secrets em **Settings → Secrets and variables → Actions**:

| Secret | Obrigatório | Finalidade |
| :--- | :---: | :--- |
| `LOBSTERAI_TOKEN` | sim | Uma ou mais entradas `uid:AT:RT` |
| `PUSHPLUS_TOKEN` | opcional | Token de notificação PushPlus |

Execute **Actions → LobsterAI Daily → Run workflow** uma vez. A agenda incluída usa UTC `0 1 * * *`, equivalente a 09:00 no horário de Pequim. Se um fork mantiver workflows agendados desativados, habilite o workflow na página Actions.

O workflow salva `lb_refresh_tokens.json` somente em repositório privado. Repositórios públicos pulam esse commit para não registrar o RT rotacionado no histórico público. Em repositório público, o Secret deve continuar válido a cada execução.

## Variáveis de ambiente principais

| Variável | Obrigatória | Descrição |
| :--- | :---: | :--- |
| `LOBSTERAI_TOKEN` | sim | Credenciais de várias contas no formato `uid:AT:RT` |
| `PUSHPLUS_TOKEN` | opcional | Token PushPlus para o resumo da execução |

## Opções de linha de comando

| Opção de check-in | Efeito |
| :--- | :--- |
| nenhuma | Executa todas as contas |
| `--only UID` | Executa somente o UID informado |
| `--version VERSION` | Força a versão do cliente |
| `--auths PATH` | Usa um diretório auth local quando a variável de ambiente não existe |
| `--base URL` | Substitui a URL base da API |

| Opção de login | Efeito |
| :--- | :--- |
| `--export` | Imprime apenas `uid:AT:RT` |
| `--manual` | Permite colar credenciais manualmente |
| `--headless` | Executa o navegador de SMS sem interface visível |

## Semântica de verificação

Depois de enviar o check-in, o script lê novamente o context da conta. O sucesso depende do estado atualizado de `claimedToday`, não apenas de HTTP 200. A falha de uma conta não interrompe as demais. `lb_refresh_tokens.json` contém credenciais reais e não deve ser enviado a um repositório público.

## Privacidade

As credenciais vêm apenas de variáveis de ambiente, Secrets ou armazenamento local do cliente. Não publique o banco de dados, AT/RT exportados, código SMS, `lb_refresh_tokens.json` ou logs sem máscara. Revise a saída antes de anexá-la a uma Issue, pois identificadores de conta ainda podem aparecer.

## Limites de uso e redistribuição

O repositório oficial, os scripts, as instruções de implantação e as Releases permanecem gratuitos e públicos. Sem autorização escrita explícita do autor, não empacote este projeto como recurso pago, serviço de implantação paga ou serviço de atualização paga; não remova a atribuição para alegar autoria original; não se passe pelo autor; e não use a identidade, o nome, o avatar ou os QR codes de pagamento do autor para sugerir endosso oficial. Também não republique o projeto em contas, grupos, canais ou plataformas pagas sem relação com ele para ganhar seguidores, desviar tráfego ou revender. Em caso de violação, o autor pode solicitar a remoção e pode pausar atualizações, arquivar ou excluir o repositório. Consulte as regras completas em [NOTICE.md](../NOTICE.md).

## Links

- [Releases](https://github.com/L0NE-6/LobsterAI-AutoCheckin/releases)
- [Issues](https://github.com/L0NE-6/LobsterAI-AutoCheckin/issues)
- [README em chinês](../README.md)
- [Histórico de alterações](../CHANGELOG.md)

## Aviso

Este projeto é destinado a aprendizado pessoal e automação. Respeite os termos do LobsterAI, NetEase Youdao e serviços relacionados. O uso é por sua conta e risco.
