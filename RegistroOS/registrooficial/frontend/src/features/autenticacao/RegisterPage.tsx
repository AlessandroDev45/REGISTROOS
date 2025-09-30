import React, { useState } from 'react';
import api from '../../services/api';
import { Link, useNavigate } from 'react-router-dom';
import { useCachedSetores } from '../../hooks/useCachedSetores'; // Import the new hook
import { StyledInput, SelectField } from '../../components/UIComponents';

const RegisterPage: React.FC = () => {
    const { setoresMotores, setoresTransformadores, loading: setoresLoading } = useCachedSetores(); // Use the hook
    const [formData, setFormData] = useState({
        primeiro_nome: '',
        sobrenome: '',
        email: '',
        password: '',
        nome_usuario: '', // Novo campo
        matricula: '',
        cargo: '', // Novo campo
        departamento: 'MOTORES', // Valor inicial para departamento
        setor_de_trabalho: '', // Será preenchido após a seleção do departamento
        trabalha_producao: false
    });
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value, type, checked } = e.target;
        setFormData({ ...formData, [name]: type === 'checkbox' ? checked : value });
    };

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        try {
            await api.post('/register', formData);
            alert('✅ Cadastro realizado com sucesso!\n\n📋 Próximos passos:\n• Sua conta foi criada e aguarda aprovação\n• Um supervisor do seu setor analisará sua solicitação\n• Você receberá acesso assim que aprovado\n• Use as mesmas credenciais do DSS Data Engenharia para fazer login');
            navigate('/login');
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Erro ao registrar.');
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-gray-50">
            <div className="p-8 bg-white rounded-lg shadow-md w-full max-w-2xl">
                <h2 className="text-2xl font-bold text-center mb-6">Cadastro de Novo Colaborador</h2>

                {/* Instruções importantes */}
                <div className="mb-6 p-4 bg-blue-50 border-l-4 border-blue-400 rounded-r-lg">
                    <div className="flex">
                        <div className="flex-shrink-0">
                            <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                            </svg>
                        </div>
                        <div className="ml-3">
                            <h3 className="text-sm font-medium text-blue-800">Instruções Importantes</h3>
                            <div className="mt-2 text-sm text-blue-700">
                                <ul className="list-disc list-inside space-y-1">
                                    <li><strong>Usuário e Senha:</strong> Use as mesmas credenciais que você utiliza para acessar o sistema DSS Data Engenharia para consultas.</li>
                                    <li><strong>Trabalha na Produção:</strong> Se você atua diretamente na produção (chão de fábrica), marque esta opção. Algumas funcionalidades do sistema são específicas para colaboradores da produção.</li>
                                    <li><strong>Aprovação:</strong> Após o cadastro, sua conta precisará ser aprovada por um supervisor do seu setor antes de poder acessar o sistema.</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <form onSubmit={handleRegister}>
                    {/* Campos de Input */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <StyledInput name="primeiro_nome" placeholder="Primeiro Nome" value={formData.primeiro_nome} onChange={handleChange} required />
                        <StyledInput name="sobrenome" placeholder="Sobrenome" value={formData.sobrenome} onChange={handleChange} required />
                        
                        <StyledInput name="nome_usuario" placeholder="Nome de Guerra" value={formData.nome_usuario} onChange={handleChange} required />
                        <StyledInput name="email" type="email" placeholder="Email" value={formData.email} onChange={handleChange} required />
                        
                        <StyledInput name="password" type="password" placeholder="Senha" value={formData.password} onChange={handleChange} required />
                        <StyledInput name="matricula" placeholder="Matrícula (no formato ex: 000335)" value={formData.matricula} onChange={handleChange} />

                        <StyledInput name="cargo" placeholder="Cargo" value={formData.cargo} onChange={handleChange} />
                    </div>

                    {/* Seleção de Departamento */}
                    <SelectField
                        name="departamento"
                        value={formData.departamento}
                        onChange={(e) => setFormData({ ...formData, departamento: e.target.value, setor_de_trabalho: '' })}
                        label="Departamento"
                        required
                    >
                        <option value="MOTORES">MOTORES</option>
                        <option value="TRANSFORMADORES">TRANSFORMADORES</option>
                    </SelectField>
                    
                    {/* Seleção de Setor com Dropdown */}
                    <SelectField
                        name="setor_de_trabalho"
                        value={formData.setor_de_trabalho}
                        onChange={(e) => setFormData({ ...formData, setor_de_trabalho: e.target.value })}
                        label="Setor de Trabalho"
                        required
                        disabled={!formData.departamento || setoresLoading} // Disable if no department or loading
                    >
                        <option value="">
                            {setoresLoading ? 'Carregando setores...' : 'Selecione um setor'}
                        </option>
                        {(() => {
                            const filteredSetores = formData.departamento === 'MOTORES' ? setoresMotores : setoresTransformadores;
                            return filteredSetores.map(setor => (
                                <option key={setor.id} value={setor.nome}>{setor.nome}</option>
                            ));
                        })()}
                    </SelectField>

                    {/* Checkbox para trabalho na produção */}
                    <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <label className="flex items-start">
                            <input
                                type="checkbox"
                                name="trabalha_producao"
                                checked={formData.trabalha_producao}
                                onChange={handleChange}
                                className="mr-3 mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                            <div>
                                <span className="text-sm font-medium text-gray-700">Trabalho na Produção (Chão de Fábrica)</span>
                                <p className="text-xs text-gray-600 mt-1">
                                    Marque esta opção se você atua diretamente na produção. Isso habilitará funcionalidades específicas como apontamentos de produção, controle de OS e outras ferramentas essenciais para o chão de fábrica.
                                </p>
                            </div>
                        </label>
                    </div>

                    {error && <p className="text-red-500 text-center mb-4">{error}</p>}
                    <button type="submit" className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700">
                        Cadastrar
                    </button>
                </form>
                <p className="text-center mt-4">
                    Já tem uma conta? <Link to="/login" className="text-blue-600 hover:underline">Faça o login</Link>
                </p>
            </div>
        </div>
    );
};

export default RegisterPage;
