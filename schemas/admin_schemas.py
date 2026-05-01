from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UnidadeSchema(BaseModel):
    nome: str = Field(min_length=2, max_length=150)
    sigla: str = Field(min_length=2, max_length=20)
    cnpj: str = Field(min_length=14, max_length=18)
    email: EmailStr
    telefone: Optional[str] = None
    celular: Optional[str] = None
    rua: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    diretor_nome: Optional[str] = None
    diretor_cpf: Optional[str] = None
    diretor_email: Optional[EmailStr] = None
    diretor_telefone: Optional[str] = None
    tipo_unidade: Optional[str] = None
    capacidade_estudantes: Optional[int] = None
    status: Optional[str] = 'ativa'
    data_inicio_operacao: Optional[str] = None
    observacoes: Optional[str] = None


class UsuarioSchema(BaseModel):
    nome_completo: str = Field(min_length=2, max_length=150)
    cpf: str = Field(min_length=11, max_length=14)
    email: EmailStr
    matricula: str = Field(min_length=1, max_length=60)
    senha: str = Field(min_length=8)
    perfil_id: int
    unidade_id: Optional[int] = None
    departamento: Optional[str] = None
    status: Optional[str] = 'ativo'
    data_admissao: Optional[str] = None
    telefone: Optional[str] = None
