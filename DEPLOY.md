# Deploy grátis — Vercel + Supabase

Guia das partes que **você** precisa fazer. Todo o código já está pronto
(`vercel.json`, `api/index.py`, WhiteNoise, endpoint de cron etc.).

Arquitetura:

- **Vercel (Hobby)** — hospeda o Django (serverless). Grátis, não expira.
- **Supabase (Free)** — banco PostgreSQL. Grátis, durável.
- **WhiteNoise** — serve os arquivos estáticos (CSS/JS) sem serviço externo.
- **Vercel Cron** — dispara `enviar_avisos` 1x/dia (essa query diária também
  mantém o banco do Supabase acordado).

> Segredos já gerados para você (use estes nas variáveis de ambiente):
>
> - `DJANGO_SECRET_KEY` = `v*ycd5g&@xwvoi#wzhd8c^1*v##cwzcock^lr#)+6a(nqlh5cs`
> - `CRON_SECRET` = `7vreY97Wv83uA7NpcHD577x03T8Yw-b9M5oLtIvtpEY`
>
> Trate-os como senhas. Se quiser trocar depois, gere novos com:
> `python elo/manage.py shell -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`

---

## 1) Criar o banco no Supabase

1. Crie uma conta em https://supabase.com e clique em **New project**.
2. Defina um nome, uma **Database Password** forte (guarde-a) e a região mais
   próxima (ex.: `South America (São Paulo)`).
3. Aguarde o provisionamento (~2 min).
4. Vá em **Project Settings → Database → Connection string** e escolha a aba
   **Connection pooling** (Supavisor).
   - **Mode:** `Transaction`
   - **Port:** `6543`
   - Copie a URI. Ela se parece com:
     ```
     postgresql://postgres.xxxxxxxx:[SUA-SENHA]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
     ```
5. Substitua `[SUA-SENHA]` pela senha do passo 2. **Essa string completa é a sua
   `DATABASE_URL`.**

> ⚠️ Importante: use a string do **POOLER (porta 6543, modo Transaction)**, não a
> conexão direta (5432). O Vercel é serverless e a conexão direta estoura o
> limite de conexões.

---

## 2) Rodar as migrações e criar o admin (uma vez, do seu PC)

Ainda no seu computador, apontando para o Supabase:

```powershell
# na raiz do projeto
$env:DATABASE_URL = "COLE_AQUI_A_DATABASE_URL_DO_SUPABASE"
$env:DJANGO_SECRET_KEY = "v*ycd5g&@xwvoi#wzhd8c^1*v##cwzcock^lr#)+6a(nqlh5cs"
$env:DJANGO_DEBUG = "False"

.venv\Scripts\python.exe elo\manage.py migrate
.venv\Scripts\python.exe elo\manage.py createsuperuser
```

Isso cria as tabelas no Supabase e o seu usuário administrador.

> Se quiser levar os dados que já existem no `db.sqlite3` local para o Supabase,
> me avise — dá para exportar/importar. Como só admins acessam o sistema,
> normalmente basta criar o superuser acima.

---

## 3) Subir o código para o GitHub

Os arquivos novos/alterados precisam estar no repositório:

```powershell
git add .
git commit -m "feat: configuração de deploy Vercel + Supabase"
git push
```

(O `.env` **não** vai junto — está no `.gitignore`, como deve ser.)

---

## 4) Conectar no Vercel

1. Crie conta em https://vercel.com (login com o GitHub).
2. **Add New → Project** e importe o repositório `ELO`.
3. Em **Framework Preset**, deixe **Other** (o `vercel.json` já configura tudo).
   Não é preciso mexer em Build/Output.
4. Antes de clicar em **Deploy**, abra **Environment Variables** e adicione
   (marque todas para *Production*, *Preview* e *Development*):

   | Nome | Valor |
   |------|-------|
   | `DATABASE_URL` | a string do pooler do Supabase (passo 1) |
   | `DJANGO_SECRET_KEY` | `v*ycd5g&@xwvoi#wzhd8c^1*v##cwzcock^lr#)+6a(nqlh5cs` |
   | `DJANGO_DEBUG` | `False` |
   | `DJANGO_ALLOWED_HOSTS` | `.vercel.app` (depois acrescente seu domínio) |
   | `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://SEU-PROJETO.vercel.app` |
   | `CRON_SECRET` | `7vreY97Wv83uA7NpcHD577x03T8Yw-b9M5oLtIvtpEY` |

5. Clique em **Deploy**.

> O nome do projeto (`SEU-PROJETO`) você só descobre depois do primeiro deploy.
> Se necessário, volte em **Settings → Environment Variables**, corrija
> `DJANGO_CSRF_TRUSTED_ORIGINS` com a URL real e faça **Redeploy**.

---

## 5) Conferir se funcionou

- Acesse `https://SEU-PROJETO.vercel.app/` → deve redirecionar para o login.
- Entre com o superuser criado no passo 2.
- O CSS/JS deve carregar normalmente (WhiteNoise).

### Testar o cron de avisos manualmente

```
https://SEU-PROJETO.vercel.app/cron/enviar-avisos?token=7vreY97Wv83uA7NpcHD577x03T8Yw-b9M5oLtIvtpEY
```

Deve responder um JSON `{"ok": true, "saida": "..."}`. O Vercel Cron chama esse
mesmo endpoint todo dia às 12:00 UTC (ver `vercel.json`), enviando o token pelo
header `Authorization` automaticamente.

> O Vercel Cron no plano Hobby roda **1x/dia** — exatamente o que o comando
> precisa (ele respeita o `intervalo_dias` da configuração de avisos).

---

## 6) (Opcional) Domínio próprio + Cloudflare

- No Vercel: **Settings → Domains → Add**. Aponte o DNS conforme instruído.
- Depois, adicione o domínio em `DJANGO_ALLOWED_HOSTS` e a URL `https://...` em
  `DJANGO_CSRF_TRUSTED_ORIGINS`, e faça Redeploy.

---

## Manutenção / durabilidade

- **Nada expira** nesse setup (diferente de Render/PythonAnywhere).
- O cron diário mantém o banco do Supabase acordado.
- **Backup do banco** (recomendado): periodicamente rode, no seu PC, um dump:
  ```powershell
  pg_dump "COLE_A_DATABASE_URL" > backup_elo.sql
  ```
  Guarde o arquivo em local seguro. Como o banco é pequeno, isso é rápido.
