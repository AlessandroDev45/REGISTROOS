# Gestão de Login e Fluxo de Autenticação

Este documento detalha o processo de login e como o controle de acesso é aplicado após a autenticação do usuário.

## Fluxo de Login Comum para Todos os Tipos de Usuário

1.  **Acesso à Página de Login**: Todos os usuários, independentemente do seu nível, acessam a mesma página de login (`/login`).

2.  **Credenciais**: Eles inserem seu email e senha.

3.  **Autenticação no Backend**: O frontend envia essas credenciais para o endpoint `/token` no backend.

4.  **Validação pelo Backend** (em `RegistroOS/registrooficial/backend/routes/auth.py`):
    -   O backend verifica se o email existe no banco de dados.
    -   Se existir, ele valida se a senha fornecida corresponde à senha hash armazenada.
    -   Se a senha estiver correta, ele verifica se a conta do usuário está aprovada (`is_approved = True`). Se não estiver, o login é negado com a mensagem "Conta de usuário não aprovada".
    -   Se tudo estiver correto, o backend gera um token JWT (JSON Web Token) contendo o ID do usuário e seu `privilege_level`, e o envia de volta ao frontend.

5.  **Armazenamento no Frontend**: O frontend armazena o token em `localStorage.setItem('accessToken', token)`. Ele também armazena as informações do usuário (como `id`, `nome_completo`, `setor`, `privilege_level`) em `localStorage.setItem('user', JSON.stringify(user))`.

6.  **Redirecionamento**: Após um login bem-sucedido, todos os usuários são redirecionados para uma página inicial, como o Dashboard (`/dashboard`).

---

## Diferenças no Acesso à Área de Desenvolvimento (`/desenvolvimento`) Após o Login

A principal diferença entre os tipos de usuário reside no que acontece quando eles tentam acessar uma página de desenvolvimento específica, como `.../mecanica/desenvolvimento.tsx`.

### 1. Colaborador do Laboratório
- **Exemplo**: `privilege_level = 'USER'`, `setor = 'laboratorio-ensaios-eletricos'`
- **Login**: Ele usa suas credenciais. Após o login, o objeto `user` no `AuthContext` terá `privilege_level: 'USER'` e `setor: 'laboratorio-ensaios-eletricos'`.

- **Acesso à Área de Desenvolvimento do Laboratório (`.../laboratorio-ensaios-eletricos/desenvolvimento`)**:
    - O sistema chamará `checkAccess('laboratorio-ensaios-eletricos')`.
    - O backend verificará:
        - `user_privilege` é `'USER'`.
        - `user_sector` (`laboratorio-ensaios-eletricos`) é igual ao `requested_sector` (`laboratorio-ensaios-eletricos`).
    - **Resultado**: **Acesso permitido**. Ele verá a página de desenvolvimento do seu próprio setor.

- **Acesso à Área de Desenvolvimento de Mecânica (`.../mecanica/desenvolvimento`)**:
    - O sistema chamará `checkAccess('mecanica')`.
    - O backend verificará que `user_sector` (`laboratorio-ensaios-eletricos`) é **diferente** do `requested_sector` (`mecanica`).
    - **Resultado**: **Acesso negado**. Ele será redirecionado para uma página de "Acesso Negado" ou de volta para o dashboard.

### 2. Colaborador da Mecânica
- **Exemplo**: `privilege_level = 'USER'`, `setor = 'mecanica'`
- **Login**: Usa suas credenciais. Após o login, `privilege_level: 'USER'` e `setor: 'mecanica'`.

- **Acesso à Área de Desenvolvimento da Mecânica (`.../mecanica/desenvolvimento`)**:
    - `checkAccess('mecanica')` é chamado.
    - O backend confirma que `user_sector` (`mecanica`) é igual ao `requested_sector` (`mecanica`).
    - **Resultado**: **Acesso permitido**.

- **Acesso à Área de Desenvolvimento do Laboratório (`.../laboratorio-ensaios-eletricos/desenvolvimento`)**:
    - `checkAccess('laboratorio-ensaios-eletricos')` é chamado.
    - O backend verifica que `user_sector` (`mecanica`) é **diferente** do `requested_sector`.
    - **Resultado**: **Acesso negado**.

### 3. Administrador
- **Exemplo**: `privilege_level = 'ADMIN'`
- **Login**: Usa suas credenciais de administrador. Após o login, `privilege_level: 'ADMIN'`. O `setor` associado à conta do administrador não restringe seu acesso.

- **Acesso à Área de Desenvolvimento de Qualquer Setor**:
    - O sistema chama `checkAccess` para qualquer setor (ex: `mecanica`).
    - O backend verifica que `user_privilege` é `'ADMIN'`.
    - **Resultado**: **Acesso permitido para qualquer setor**. A lógica no backend (`user_utils.py`) concede acesso irrestrito a `ADMIN` e `GESTAO`.
    - No frontend, como `isAdmin` no `AuthContext` é `true`, o sistema pode exibir um `SectorSelector`, permitindo que o administrador visualize e gerencie apontamentos de qualquer setor.

### Resumo da Lógica de Acesso no Backend (`check_development_access`)

O trecho de código a seguir, localizado em `RegistroOS/registrooficial/backend/utils/user_utils.py`, resume a regra de negócio:

```python
# Em RegistroOS/registrooficial/backend/utils/user_utils.py

if user_privilege in ['ADMIN', 'GESTAO']: # Acesso a TODOS os setores
    return True 
if user_privilege in ['SUPERVISOR', 'PCP', 'USER']: # Acesso apenas ao próprio setor
    return user_sector == requested_sector.lower()