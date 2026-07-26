# Runbook — Deploy presencial no HUB

Guia da instalação no host Docker do HUB (visita presencial). Sem acesso
remoto: chegue com tudo pronto e siga na ordem.

---

## Decisões fixas deste deploy
- **TLS:** o container termina o SSL (nginx do compose). Certificado fornecido pela infra.
- **Rede:** macvlan — o container tem IP próprio; portas 80/443 livres no host.
- **Auth:** exclusivamente via Active Directory (sem senha local em produção).
- **Banco:** Postgres institucional externo.

---

## A) Antes de ir (em casa) — checklist

- [ ] `docker compose build web` roda sem erro (JÁ VALIDADO ✅)
- [ ] Projeto pronto para levar (pendrive ou acesso ao git no host)
- [ ] `.env` pré-preenchido com o que já se sabe (deixar em branco só o que a infra dá no dia)
- [ ] Este runbook impresso ou salvo offline
- [ ] Valores da infra coletados por e-mail, se possível (ver seção B)

## B) Valores que a infra precisa entregar (colete antes ou pegue no dia)

| Item | Onde entra |
|---|---|
| `fullchain.pem` + `privkey.pem` | pasta `certs/` |
| FQDN do certificado (ex.: `elo.hub.local`) | `.env` ALLOWED_HOSTS/CSRF |
| IP do container + sub-rede + gateway + interface pai | `docker-compose.macvlan.yml` |
| (ou) nome da rede macvlan, se a infra a criou | `docker-compose.macvlan.yml` |
| AD: URI, conta de serviço (bind), base de busca, DNs dos grupos | `.env` AUTH_LDAP_*/LDAP_* |
| Postgres: host, porta, banco, usuário, senha, sslmode | `.env` DB_* |

---

## C) No host — passo a passo

### 1. Colocar o código no host
Via pendrive ou `git clone` (se houver rede). Entrar na pasta do projeto.

### 2. Colocar o certificado
```
certs/fullchain.pem   <- certificado + cadeia
certs/privkey.pem     <- chave privada
```

### 3. Preencher o `.env`
Editar e preencher os blocos DB_*, AUTH_LDAP_*/LDAP_* e os hosts:
```
DJANGO_ALLOWED_HOSTS=<FQDN>,<IP do container>
DJANGO_CSRF_TRUSTED_ORIGINS=https://<FQDN>
```

### 4. Preencher a rede no `docker-compose.macvlan.yml`
Substituir os 4 valores marcados com `<--` (IP, parent, subnet, gateway).

### 5. Subir
```bash
docker compose -f docker-compose.yml -f docker-compose.macvlan.yml up -d --build
```

### 6. Criar um superusuário de emergência (opcional, antes do AD)
Se quiser validar o app antes do AD, deixe `AUTH_LDAP_SERVER_URI` vazio,
suba, crie o superuser e teste; depois preencha o AD e reinicie.
```bash
docker compose exec web python manage.py createsuperuser
```

---

## D) Validação (na ordem)

**1. Containers de pé**
```bash
docker compose ps
docker compose logs -f web
```

**2. Banco (o migrate roda no start)**
Nos logs do `web`, confirmar que as migrações aplicaram sem erro de conexão.
Teste manual:
```bash
docker compose exec web python manage.py showmigrations
```

**3. LDAP / AD** (com AUTH_LDAP_SERVER_URI preenchido)
```bash
docker compose exec web python manage.py shell -c "from django.contrib.auth import authenticate; u=authenticate(username='SEU_LOGIN_AD', password='SUA_SENHA'); print(u, getattr(u,'is_staff',None))"
```
Esperado: imprime o usuário e `True` (se estiver no grupo de admins).

**4. HTTPS pelo FQDN** (de outra máquina na rede do HUB)
```bash
curl -I https://<FQDN>
```
Esperado: `HTTP/… 302` ou `200`, com o cadeado válido no navegador.

---

## E) Troubleshooting rápido

| Sintoma | Causa provável | Ação |
|---|---|---|
| Loop de redirect / "too many redirects" | header `X-Forwarded-Proto` | já tratado no nginx; conferir `DJANGO_SECURE_SSL=True` |
| `DisallowedHost` no log | FQDN/IP fora do ALLOWED_HOSTS | incluir FQDN e IP em `DJANGO_ALLOWED_HOSTS` |
| Erro de conexão no migrate | DB_HOST/porta/firewall | conferir alcance do IP do container até o Postgres (5432) |
| Login AD falha p/ todos | bind/base/filtro errados | conferir `AUTH_LDAP_BIND_*`, `LDAP_USER_SEARCH_BASE`, filtro |
| Login AD ok mas "só admin" barra | ninguém no grupo staff | preencher `LDAP_STAFF_GROUP_DN` e por a pessoa no grupo AD |
| Cert não confia | cadeia incompleta | usar `fullchain.pem` (cert + intermediárias), não só o cert |
| nginx não sobe / porta ocupada | ports herdados no macvlan | conferir `ports: !reset []` no override macvlan |

---

## F) Comandos úteis
```bash
docker compose logs -f nginx        # logs do proxy TLS
docker compose logs -f web          # logs do app
docker compose restart web          # aplicar mudança no .env
docker compose down                 # derrubar tudo
```
