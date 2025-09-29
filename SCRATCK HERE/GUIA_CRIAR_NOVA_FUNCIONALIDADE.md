# 🆕 GUIA SIMPLES: Como Criar uma Nova Funcionalidade Completa

## 🎯 EXEMPLO: Vamos criar "FORNECEDORES" do zero

### 🗄️ PASSO 1: CRIAR TABELA NA DATABASE

**Arquivo:** `RegistroOS/registrooficial/backend/app/database_models.py`

**ADICIONE no final do arquivo:**
```python
class Fornecedor(Base):
    __tablename__ = "fornecedores"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    cnpj = Column(String)
    telefone = Column(String)
    email = Column(String)
    endereco = Column(Text)
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.now)
    data_ultima_atualizacao = Column(DateTime, default=datetime.now)
```

---

### 📋 PASSO 2: CRIAR SCHEMAS (VALIDAÇÃO)

**Arquivo:** `RegistroOS/registrooficial/backend/app/schemas.py`

**ADICIONE no final do arquivo:**
```python
# ============================================================================
# SCHEMAS PARA FORNECEDORES
# ============================================================================

class FornecedorBase(BaseModel):
    nome: str = Field(..., description="Nome do fornecedor")
    cnpj: Optional[str] = Field(None, description="CNPJ do fornecedor")
    telefone: Optional[str] = Field(None, description="Telefone do fornecedor")
    email: Optional[str] = Field(None, description="Email do fornecedor")
    endereco: Optional[str] = Field(None, description="Endereço do fornecedor")

class FornecedorCreate(FornecedorBase):
    pass

class FornecedorUpdate(FornecedorBase):
    nome: Optional[str] = Field(None, description="Nome do fornecedor")

class FornecedorResponse(FornecedorBase):
    id: int
    ativo: bool
    data_criacao: Optional[datetime]
    data_ultima_atualizacao: Optional[datetime]

    class Config:
        from_attributes = True
```

---

### 🔧 PASSO 3: CRIAR ENDPOINTS NO BACKEND

**Arquivo:** `RegistroOS/registrooficial/backend/routes/admin_config_routes.py`

**ADICIONE no final do arquivo (antes da última linha):**
```python
# ============================================================================
# ENDPOINTS PARA FORNECEDORES
# ============================================================================

@router.get("/fornecedores", response_model=List[dict])
async def listar_fornecedores(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Listar todos os fornecedores ativos"""
    try:
        fornecedores = db.query(Fornecedor).filter(Fornecedor.ativo == True).all()
        
        result = []
        for fornecedor in fornecedores:
            item = {
                "id": fornecedor.id,
                "nome": fornecedor.nome,
                "cnpj": fornecedor.cnpj,
                "telefone": fornecedor.telefone,
                "email": fornecedor.email,
                "endereco": fornecedor.endereco,
                "ativo": fornecedor.ativo
            }
            result.append(item)
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao listar fornecedores: {str(e)}"
        )

@router.post("/fornecedores", response_model=FornecedorResponse)
async def criar_fornecedor(
    fornecedor_data: FornecedorCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Criar novo fornecedor"""
    try:
        novo_fornecedor = Fornecedor(
            nome=fornecedor_data.nome,
            cnpj=fornecedor_data.cnpj,
            telefone=fornecedor_data.telefone,
            email=fornecedor_data.email,
            endereco=fornecedor_data.endereco,
            ativo=True,
            data_criacao=datetime.now(),
            data_ultima_atualizacao=datetime.now()
        )
        
        db.add(novo_fornecedor)
        db.commit()
        db.refresh(novo_fornecedor)
        
        return FornecedorResponse.model_validate(novo_fornecedor)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar fornecedor: {str(e)}"
        )

@router.put("/fornecedores/{fornecedor_id}", response_model=FornecedorResponse)
async def atualizar_fornecedor(
    fornecedor_id: int,
    fornecedor_data: FornecedorUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Atualizar fornecedor"""
    try:
        fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
        
        if not fornecedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fornecedor com ID {fornecedor_id} não encontrado"
            )
        
        # Atualizar campos
        if fornecedor_data.nome is not None:
            setattr(fornecedor, 'nome', fornecedor_data.nome)
        if fornecedor_data.cnpj is not None:
            setattr(fornecedor, 'cnpj', fornecedor_data.cnpj)
        if fornecedor_data.telefone is not None:
            setattr(fornecedor, 'telefone', fornecedor_data.telefone)
        if fornecedor_data.email is not None:
            setattr(fornecedor, 'email', fornecedor_data.email)
        if fornecedor_data.endereco is not None:
            setattr(fornecedor, 'endereco', fornecedor_data.endereco)
        
        setattr(fornecedor, 'data_ultima_atualizacao', datetime.now())
        
        db.commit()
        db.refresh(fornecedor)
        
        return FornecedorResponse.model_validate(fornecedor)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao atualizar fornecedor: {str(e)}"
        )

@router.delete("/fornecedores/{fornecedor_id}")
async def deletar_fornecedor(
    fornecedor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Deletar fornecedor (soft delete)"""
    try:
        fornecedor = db.query(Fornecedor).filter(Fornecedor.id == fornecedor_id).first()
        
        if not fornecedor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Fornecedor com ID {fornecedor_id} não encontrado"
            )
        
        # Soft delete
        setattr(fornecedor, 'ativo', False)
        setattr(fornecedor, 'data_ultima_atualizacao', datetime.now())
        
        db.commit()
        
        return {"message": f"Fornecedor '{fornecedor.nome}' desativado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar fornecedor: {str(e)}"
        )
```

**IMPORTANTE:** Adicione também o import no topo do arquivo:
```python
from app.database_models import Fornecedor  # ← ADICIONAR ESTA LINHA
```

---

### 🎨 PASSO 4: CRIAR SERVIÇO NO FRONTEND

**Arquivo:** `RegistroOS/registrooficial/frontend/src/services/adminApi.ts`

**ADICIONE a interface:**
```typescript
export interface Fornecedor {
  id: number;
  nome: string;
  cnpj?: string;
  telefone?: string;
  email?: string;
  endereco?: string;
  ativo: boolean;
}
```

**ADICIONE o serviço:**
```typescript
export const fornecedorService = {
  getFornecedores: () => api.get<Fornecedor[]>('/admin/fornecedores'),
  createFornecedor: (data: Omit<Fornecedor, 'id' | 'ativo'>) => 
    api.post<Fornecedor>('/admin/fornecedores', data),
  updateFornecedor: (id: number, data: Partial<Fornecedor>) => 
    api.put<Fornecedor>(`/admin/fornecedores/${id}`, data),
  deleteFornecedor: (id: number) => 
    api.delete(`/admin/fornecedores/${id}`)
};
```

---

### 📝 PASSO 5: CRIAR FORMULÁRIO

**Criar arquivo:** `RegistroOS/registrooficial/frontend/src/features/admin/components/config/FornecedorForm.tsx`

```tsx
import React, { useState, useEffect } from 'react';
import { Fornecedor } from '../../../../services/adminApi';

interface FornecedorFormProps {
    fornecedor?: Fornecedor;
    onSubmit: (data: any, isEdit: boolean) => void;
    onCancel: () => void;
}

export const FornecedorForm: React.FC<FornecedorFormProps> = ({
    fornecedor,
    onSubmit,
    onCancel
}) => {
    const [formData, setFormData] = useState({
        nome: '',
        cnpj: '',
        telefone: '',
        email: '',
        endereco: ''
    });

    const isEdit = !!fornecedor;

    useEffect(() => {
        if (fornecedor) {
            setFormData({
                nome: fornecedor.nome || '',
                cnpj: fornecedor.cnpj || '',
                telefone: fornecedor.telefone || '',
                email: fornecedor.email || '',
                endereco: fornecedor.endereco || ''
            });
        }
    }, [fornecedor]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit(formData, isEdit);
    };

    return (
        <div className="mt-6">
            <div className="p-6 bg-white rounded-lg shadow-md">
                <h2 className="text-2xl font-semibold text-gray-700 mb-6">
                    {isEdit ? 'Editar Fornecedor' : 'Adicionar Novo Fornecedor'}
                </h2>

                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Nome */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Nome do Fornecedor *
                        </label>
                        <input
                            type="text"
                            name="nome"
                            value={formData.nome}
                            onChange={handleInputChange}
                            required
                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                            placeholder="Ex: Fornecedor ABC Ltda"
                        />
                    </div>

                    {/* CNPJ */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            CNPJ
                        </label>
                        <input
                            type="text"
                            name="cnpj"
                            value={formData.cnpj}
                            onChange={handleInputChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                            placeholder="Ex: 12.345.678/0001-90"
                        />
                    </div>

                    {/* Telefone */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Telefone
                        </label>
                        <input
                            type="text"
                            name="telefone"
                            value={formData.telefone}
                            onChange={handleInputChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                            placeholder="Ex: (11) 99999-9999"
                        />
                    </div>

                    {/* Email */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Email
                        </label>
                        <input
                            type="email"
                            name="email"
                            value={formData.email}
                            onChange={handleInputChange}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                            placeholder="Ex: contato@fornecedor.com"
                        />
                    </div>

                    {/* Endereço */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Endereço
                        </label>
                        <textarea
                            name="endereco"
                            value={formData.endereco}
                            onChange={handleInputChange}
                            rows={3}
                            className="w-full px-3 py-2 border border-gray-300 rounded-md"
                            placeholder="Endereço completo do fornecedor"
                        />
                    </div>

                    {/* Botões */}
                    <div className="flex justify-end space-x-4">
                        <button
                            type="button"
                            onClick={onCancel}
                            className="px-4 py-2 text-gray-600 bg-gray-200 rounded-md hover:bg-gray-300"
                        >
                            Cancelar
                        </button>
                        <button
                            type="submit"
                            className="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700"
                        >
                            {isEdit ? 'Atualizar' : 'Criar'} Fornecedor
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};
```

---

## 🚀 RESUMO PARA CRIAR NOVA FUNCIONALIDADE

1. **DATABASE** → Criar nova classe/tabela
2. **SCHEMAS** → Criar validações (Base, Create, Update, Response)
3. **BACKEND** → Criar todos os endpoints (GET, POST, PUT, DELETE)
4. **FRONTEND** → Criar interface e serviço
5. **FORMULÁRIO** → Criar componente de formulário
6. **LISTA** → Criar componente de listagem
7. **INTEGRAÇÃO** → Adicionar na página principal

**PRONTO!** Agora você tem uma funcionalidade completa de Fornecedores! 🎉


# 📋 GUIA PASSO A PASSO: Como Adicionar Campos

## 🎯 EXEMPLO PRÁTICO: Vamos adicionar o campo "TELEFONE" no Departamento

### 🗄️ PASSO 1: ADICIONAR CAMPO NA DATABASE

**1.1** Abra o VS Code
**1.2** No painel esquerdo, clique na pasta `RegistroOS`
**1.3** Clique em `registrooficial`
**1.4** Clique em `backend`
**1.5** Clique em `app`
**1.6** Clique no arquivo `database_models.py`

**1.7** Pressione `Ctrl + F` para abrir a busca
**1.8** Digite: `class Departamento`
**1.9** Pressione `Enter` - vai levar você para a linha 318

**1.10** Você vai ver este código:
```python
class Departamento(Base):
    __tablename__ = "tipo_departamentos"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nome_tipo = Column(String, nullable=False)
    descricao = Column(Text)
    ativo = Column(Boolean)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
```

**1.11** Clique no FINAL da linha `descricao = Column(Text)`
**1.12** Pressione `Enter` para criar uma nova linha
**1.13** Digite exatamente: `    telefone = Column(String)`

**1.14** Agora deve ficar assim:
```python
class Departamento(Base):
    __tablename__ = "tipo_departamentos"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    nome_tipo = Column(String, nullable=False)
    descricao = Column(Text)
    telefone = Column(String)  # ← NOVA LINHA
    ativo = Column(Boolean)
    data_criacao = Column(DateTime)
    data_ultima_atualizacao = Column(DateTime)
```

**1.15** Pressione `Ctrl + S` para salvar

---

### 📋 PASSO 2: ATUALIZAR OS SCHEMAS (VALIDAÇÃO)

**2.1** No VS Code, clique no arquivo `schemas.py` (na mesma pasta `app`)

**2.2** Pressione `Ctrl + F` para buscar
**2.3** Digite: `class DepartamentoBase`
**2.4** Pressione `Enter` - vai levar você para a linha 15

**2.5** Você vai ver este código:

```python
class DepartamentoBase(BaseModel):
    nome: str = Field(..., description="Nome do departamento")
    descricao: Optional[str] = Field(None, description="Descrição do departamento")
```

**2.6** Clique no FINAL da linha `descricao: Optional[str] = Field(None, description="Descrição do departamento")`
**2.7** Pressione `Enter` para criar uma nova linha
**2.8** Digite exatamente: `    telefone: Optional[str] = Field(None, description="Telefone do departamento")`

**2.9** Agora deve ficar assim:

```python
class DepartamentoBase(BaseModel):
    nome: str = Field(..., description="Nome do departamento")
    descricao: Optional[str] = Field(None, description="Descrição do departamento")
    telefone: Optional[str] = Field(None, description="Telefone do departamento")  # ← NOVA LINHA
```

**2.10** Pressione `Ctrl + S` para salvar

---

### 🔧 PASSO 3: ATUALIZAR O BACKEND (ENDPOINT)

**3.1** No VS Code, clique no arquivo `admin_config_routes.py` (na pasta `routes`)

**3.2** Pressione `Ctrl + F` para buscar
**3.3** Digite: `listar_departamentos`
**3.4** Pressione `Enter` - vai levar você para a linha 298

**3.5** Role para baixo até encontrar este código:

```python
item = {
    "id": dept.id,
    "nome": dept.nome_tipo,
    "nome_tipo": dept.nome_tipo,
    "descricao": dept.descricao,
    "ativo": dept.ativo
}
```

**3.6** Clique no FINAL da linha `"descricao": dept.descricao,`
**3.7** Pressione `Enter` para criar uma nova linha
**3.8** Digite exatamente: `                "telefone": dept.telefone,`

**3.9** Agora deve ficar assim:

```python
item = {
    "id": dept.id,
    "nome": dept.nome_tipo,
    "nome_tipo": dept.nome_tipo,
    "descricao": dept.descricao,
    "telefone": dept.telefone,  # ← NOVA LINHA
    "ativo": dept.ativo
}
```

**3.10** Pressione `Ctrl + F` novamente
**3.11** Digite: `criar_departamento`
**3.12** Pressione `Enter` até encontrar a linha 1600

**3.13** Role para baixo até encontrar este código:

```python
novo_departamento = Departamento(
    nome_tipo=departamento_data.nome,
    descricao=departamento_data.descricao,
    ativo=True,
    data_criacao=datetime.now(),
    data_ultima_atualizacao=datetime.now()
)
```

**3.14** Clique no FINAL da linha `descricao=departamento_data.descricao,`
**3.15** Pressione `Enter` para criar uma nova linha
**3.16** Digite exatamente: `    telefone=departamento_data.telefone,`

**3.17** Agora deve ficar assim:

```python
novo_departamento = Departamento(
    nome_tipo=departamento_data.nome,
    descricao=departamento_data.descricao,
    telefone=departamento_data.telefone,  # ← NOVA LINHA
    ativo=True,
    data_criacao=datetime.now(),
    data_ultima_atualizacao=datetime.now()
)
```

**3.18** Pressione `Ctrl + S` para salvar

---

### 🎨 PASSO 4: ATUALIZAR O FRONTEND (INTERFACE)

**4.1** No VS Code, no painel esquerdo, clique na pasta `frontend`
**4.2** Clique em `src`
**4.3** Clique em `services`
**4.4** Clique no arquivo `adminApi.ts`

**4.5** Pressione `Ctrl + F` para buscar
**4.6** Digite: `interface Departamento`
**4.7** Pressione `Enter` - vai levar você para a linha 8

**4.8** Você vai ver este código:

```typescript
export interface Departamento {
  id: number;
  nome: string;
  nome_tipo: string;
  descricao?: string;
  ativo: boolean;
}
```

**4.9** Clique no FINAL da linha `descricao?: string;`
**4.10** Pressione `Enter` para criar uma nova linha
**4.11** Digite exatamente: `  telefone?: string;`

**4.12** Agora deve ficar assim:

```typescript
export interface Departamento {
  id: number;
  nome: string;
  nome_tipo: string;
  descricao?: string;
  telefone?: string;  // ← NOVA LINHA
  ativo: boolean;
}
```

**4.13** Pressione `Ctrl + S` para salvar

---

### 📝 PASSO 5: ATUALIZAR O FORMULÁRIO

**5.1** No VS Code, navegue para: `frontend` → `src` → `features` → `admin` → `components` → `config`
**5.2** Clique no arquivo `DepartamentoForm.tsx`

**5.3** Pressione `Ctrl + F` para buscar
**5.4** Digite: `useState({`
**5.5** Pressione `Enter` - vai levar você para a linha 20

**5.6** Você vai ver este código:

```typescript
const [formData, setFormData] = useState({
    nome: '',
    descricao: ''
});
```

**5.7** Clique no FINAL da linha `descricao: ''`
**5.8** Digite: `,` (vírgula)
**5.9** Pressione `Enter` para criar uma nova linha
**5.10** Digite exatamente: `    telefone: ''`

**5.11** Agora deve ficar assim:

```typescript
const [formData, setFormData] = useState({
    nome: '',
    descricao: '',
    telefone: ''  // ← NOVA LINHA
});
```

**5.12** Pressione `Ctrl + F` novamente
**5.13** Digite: `placeholder="Descrição`
**5.14** Pressione `Enter` - vai levar você para o campo de descrição

**5.15** Role para baixo até encontrar o `</div>` que fecha o campo descrição
**5.16** Clique DEPOIS do `</div>`
**5.17** Pressione `Enter` duas vezes para criar espaço
**5.18** Cole este código completo:

```jsx
{/* Campo Telefone */}
<div>
    <label htmlFor="telefone" className="block text-sm font-medium text-gray-700 mb-2">
        Telefone
    </label>
    <input
        type="text"
        id="telefone"
        name="telefone"
        value={formData.telefone}
        onChange={handleInputChange}
        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        placeholder="Ex: (11) 99999-9999"
    />
</div>
```

**5.19** Pressione `Ctrl + S` para salvar

---

### 📊 PASSO 6: ATUALIZAR A LISTA (TABELA)

**6.1** No VS Code, clique no arquivo `DepartamentoList.tsx` (na mesma pasta)

**6.2** Pressione `Ctrl + F` para buscar
**6.3** Digite: `<th>Descrição</th>`
**6.4** Pressione `Enter` - vai levar você para o cabeçalho da tabela

**6.5** Você vai ver este código:

```jsx
<thead className="bg-gray-50">
    <tr>
        <th>Nome</th>
        <th>Descrição</th>
        <th>Ativo</th>
        <th>Ações</th>
    </tr>
</thead>
```

**6.6** Clique no FINAL da linha `<th>Descrição</th>`
**6.7** Pressione `Enter` para criar uma nova linha
**6.8** Digite exatamente: `        <th>Telefone</th>`

**6.9** Agora deve ficar assim:

```jsx
<thead className="bg-gray-50">
    <tr>
        <th>Nome</th>
        <th>Descrição</th>
        <th>Telefone</th>  {/* ← NOVA COLUNA */}
        <th>Ativo</th>
        <th>Ações</th>
    </tr>
</thead>
```

**6.10** Pressione `Ctrl + F` novamente
**6.11** Digite: `{dept.descricao || '-'}`
**6.12** Pressione `Enter` - vai levar você para o corpo da tabela

**6.13** Você vai ver este código:

```jsx
<td>{dept.nome}</td>
<td>{dept.descricao || '-'}</td>
<td>{dept.ativo ? 'Sim' : 'Não'}</td>
```

**6.14** Clique no FINAL da linha `<td>{dept.descricao || '-'}</td>`
**6.15** Pressione `Enter` para criar uma nova linha
**6.16** Digite exatamente: `            <td>{dept.telefone || '-'}</td>`

**6.17** Agora deve ficar assim:

```jsx
<td>{dept.nome}</td>
<td>{dept.descricao || '-'}</td>
<td>{dept.telefone || '-'}</td>  {/* ← NOVA CÉLULA */}
<td>{dept.ativo ? 'Sim' : 'Não'}</td>
```

**6.18** Pressione `Ctrl + S` para salvar

---

## 🎉 PRONTO! CAMPO TELEFONE ADICIONADO!

### ✅ O QUE VOCÊ FEZ:
1. ✅ Adicionou campo na database
2. ✅ Adicionou validação no schema
3. ✅ Atualizou endpoints do backend
4. ✅ Atualizou interface do frontend
5. ✅ Adicionou campo no formulário
6. ✅ Adicionou coluna na tabela

### 🧪 COMO TESTAR:
1. Abra o navegador
2. Vá para a página de Departamentos
3. Clique em "Adicionar Novo"
4. Preencha o campo Telefone
5. Salve e veja se aparece na lista

---

## 📁 RESUMO DOS ARQUIVOS ALTERADOS:
- `database_models.py` - Linha 318
- `schemas.py` - Linha 15
- `admin_config_routes.py` - Linhas 298 e 1600
- `adminApi.ts` - Linha 8
- `DepartamentoForm.tsx` - Linhas 20 e 80
- `DepartamentoList.tsx` - Linhas 45 e 60

**AGORA VOCÊ SABE ADICIONAR QUALQUER CAMPO EM QUALQUER LUGAR!** 🚀

# 💡 DICAS E TRUQUES IMPORTANTES

## 🎯 REGRAS DE OURO

### ✅ SEMPRE FAÇA ASSIM:
1. **Teste cada passo** antes de ir para o próximo
2. **Copie código que já funciona** e adapte
3. **Use nomes consistentes** em todos os arquivos
4. **Siga a ordem**: Database → Backend → Frontend

### ❌ NUNCA FAÇA ASSIM:
1. Não mude muita coisa de uma vez
2. Não invente nomes diferentes para a mesma coisa
3. Não esqueça de adicionar imports
4. Não teste só no final

---

## 🔧 TIPOS DE CAMPOS MAIS USADOS

### 📝 CAMPOS DE TEXTO
```python
# Database
nome = Column(String, nullable=False)  # Obrigatório
descricao = Column(Text)               # Opcional, texto longo

# Schema
nome: str = Field(..., description="Nome obrigatório")
descricao: Optional[str] = Field(None, description="Descrição opcional")

# Frontend
<input type="text" />
<textarea />
```

### 🔢 CAMPOS NUMÉRICOS
```python
# Database
preco = Column(Float)
quantidade = Column(Integer)

# Schema
preco: Optional[float] = Field(None, description="Preço")
quantidade: Optional[int] = Field(None, description="Quantidade")

# Frontend
<input type="number" />
```

### 📅 CAMPOS DE DATA
```python
# Database
data_vencimento = Column(DateTime)

# Schema
data_vencimento: Optional[datetime] = Field(None, description="Data de vencimento")

# Frontend
<input type="date" />
<input type="datetime-local" />
```

### ✅ CAMPOS VERDADEIRO/FALSO
```python
# Database
ativo = Column(Boolean, default=True)

# Schema
ativo: bool = Field(True, description="Status ativo")

# Frontend
<input type="checkbox" />
```

### 📋 CAMPOS DE SELEÇÃO
```python
# Database
status = Column(String)  # Ex: "PENDENTE", "APROVADO", "REJEITADO"

# Schema
status: str = Field(..., description="Status do item")

# Frontend
<select>
    <option value="PENDENTE">Pendente</option>
    <option value="APROVADO">Aprovado</option>
    <option value="REJEITADO">Rejeitado</option>
</select>
```

---

## 🔗 COMO LIGAR TABELAS (RELACIONAMENTOS)

### 👥 EXEMPLO: Usuário pertence a um Departamento

**Database:**
```python
class Usuario(Base):
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    id_departamento = Column(Integer, ForeignKey("tipo_departamentos.id"))  # ← CHAVE ESTRANGEIRA
    
    # Relacionamento
    departamento_obj = relationship("Departamento", foreign_keys=[id_departamento])
```

**Schema:**
```python
class UsuarioBase(BaseModel):
    nome: str
    id_departamento: Optional[int] = Field(None, description="ID do departamento")
```

**Frontend:**
```tsx
// Buscar departamentos para o select
const [departamentos, setDepartamentos] = useState([]);

useEffect(() => {
    departamentoService.getDepartamentos().then(response => {
        setDepartamentos(response.data);
    });
}, []);

// Select no formulário
<select name="id_departamento">
    <option value="">Selecione um departamento</option>
    {departamentos.map(dept => (
        <option key={dept.id} value={dept.id}>
            {dept.nome}
        </option>
    ))}
</select>
```

---

## 🚨 ERROS MAIS COMUNS E COMO RESOLVER

### ❌ ERRO: "Column 'campo' cannot be null"
**Problema:** Campo obrigatório não foi preenchido
**Solução:** Adicione `nullable=False` na database OU torne opcional com `Optional[str]`

### ❌ ERRO: "Field required"
**Problema:** Schema exige campo que não foi enviado
**Solução:** Use `Optional[str]` no schema ou `Field(None)`

### ❌ ERRO: "404 Not Found"
**Problema:** Endpoint não existe ou URL errada
**Solução:** Verifique se o endpoint foi criado no backend e se a URL está correta

### ❌ ERRO: "500 Internal Server Error"
**Problema:** Erro no código do backend
**Solução:** Olhe o console do backend para ver o erro detalhado

### ❌ ERRO: "Cannot read property 'nome' of undefined"
**Problema:** Frontend tentando acessar campo que não existe
**Solução:** Verifique se o backend está retornando o campo correto

---

## 🎨 PADRÕES DE CÓDIGO

### 📁 NOMES DE ARQUIVOS
```
Database: TipoMaquina (PascalCase)
Endpoint: /tipos-maquina (kebab-case)
Arquivo: TipoMaquinaForm.tsx (PascalCase)
Variável: tiposMaquina (camelCase)
```

### 🔧 ESTRUTURA DE ENDPOINT
```python
@router.get("/nome-da-rota")  # ← URL sempre em kebab-case
async def nome_da_funcao(    # ← Função sempre em snake_case
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(verificar_admin)
):
    """Descrição do que faz"""
    try:
        # Código aqui
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao fazer algo: {str(e)}"
        )
```

### 🎨 ESTRUTURA DE COMPONENTE REACT
```tsx
interface MinhaProps {
    dados?: TipoDados;
    onSubmit: (data: any) => void;
}

export const MeuComponente: React.FC<MinhaProps> = ({ dados, onSubmit }) => {
    const [estado, setEstado] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit(estado);
    };

    return (
        <div>
            {/* JSX aqui */}
        </div>
    );
};
```

---

## 🔍 COMO DEBUGAR PROBLEMAS

### 1. **PROBLEMA NO BACKEND**
```python
# Adicione prints para debugar
print(f"🔧 [DEBUG] Dados recebidos: {dados}")
print(f"🔧 [DEBUG] Resultado da query: {resultado}")
```

### 2. **PROBLEMA NO FRONTEND**
```tsx
// Adicione console.log para debugar
console.log('🎨 [DEBUG] Dados do formulário:', formData);
console.log('🎨 [DEBUG] Resposta da API:', response);
```

### 3. **PROBLEMA NA DATABASE**
- Verifique se a tabela existe
- Verifique se os campos existem
- Verifique se os tipos estão corretos

---

## 🚀 CHECKLIST ANTES DE TESTAR

### ✅ BACKEND
- [ ] Modelo criado na database
- [ ] Schema criado
- [ ] Endpoint criado
- [ ] Import adicionado
- [ ] Função de validação OK

### ✅ FRONTEND
- [ ] Interface TypeScript criada
- [ ] Serviço criado
- [ ] Componente de formulário criado
- [ ] Componente de lista criado
- [ ] Estados inicializados

### ✅ INTEGRAÇÃO
- [ ] URLs corretas
- [ ] Nomes de campos consistentes
- [ ] Validações funcionando
- [ ] Mensagens de erro claras

**PRONTO!** Com essas dicas você vai conseguir criar qualquer funcionalidade! 🎉
