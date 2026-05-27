import os
import random
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILE = ROOT_DIR / ".env"

def load_dotenv(dotenv_path: Path) -> None:
    if not dotenv_path.exists():
        return
    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)

load_dotenv(DEFAULT_ENV_FILE)

host = os.getenv("PGHOST", "localhost")
port = int(os.getenv("PGPORT", "5432"))
user = os.getenv("PGUSER", "postgres")
password = os.getenv("PGPASSWORD", "")
database = os.getenv("PGDATABASE", "saadi_db")

print(f"Connecting to database {database} on {host}:{port} as {user}...")
conn = psycopg2.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    dbname=database
)
conn.autocommit = False

try:
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # 1. Ensure the 2 units exist
        schools = [
            {
                "nome": "Escola Municipal Centro",
                "sigla": "EMC",
                "cnpj": "00.000.000/0001-00",
                "email": "contato@emc.saadi.local",
                "telefone": "(11) 5555-0101",
                "cidade": "São Paulo",
                "estado": "SP",
                "status": "ativa"
            },
            {
                "nome": "Escola Estadual Norte",
                "sigla": "EEN",
                "cnpj": "00.000.000/0002-00",
                "email": "contato@een.saadi.local",
                "telefone": "(11) 5555-0202",
                "cidade": "São Paulo",
                "estado": "SP",
                "status": "ativa"
            }
        ]
        
        unit_ids = []
        for school in schools:
            cur.execute("SELECT id FROM unidades WHERE cnpj = %s", (school["cnpj"],))
            row = cur.fetchone()
            if row:
                unit_ids.append(row["id"])
                print(f"School '{school['nome']}' already exists with ID {row['id']}.")
            else:
                cur.execute(
                    """
                    INSERT INTO unidades (nome, sigla, cnpj, email, telefone, cidade, estado, status)
                    VALUES (%(nome)s, %(sigla)s, %(cnpj)s, %(email)s, %(telefone)s, %(cidade)s, %(estado)s, %(status)s)
                    RETURNING id
                    """,
                    school
                )
                new_id = cur.fetchone()["id"]
                unit_ids.append(new_id)
                print(f"Created school '{school['nome']}' with ID {new_id}.")
        
        # 2. Get available categories
        cur.execute("SELECT id, nome FROM categorias_neurodiversidade WHERE ativa = TRUE")
        categories = cur.fetchall()
        if not categories:
            raise ValueError("No active neurodiversity categories found in the database. Run seed first.")
        
        print(f"Found {len(categories)} active categories.")
        
        # 3. Clean existing students and related records with correct foreign key constraint ordering
        for uid in unit_ids:
            # Delete metas from plans belonging to students of this unit
            cur.execute(
                """
                DELETE FROM plano_metas 
                WHERE plano_id IN (
                    SELECT id FROM planos_acompanhamento 
                    WHERE aluno_id IN (SELECT id FROM alunos WHERE unidade_id = %s)
                )
                """,
                (uid,)
            )
            # Delete plans
            cur.execute("DELETE FROM planos_acompanhamento WHERE aluno_id IN (SELECT id FROM alunos WHERE unidade_id = %s)", (uid,))
            # Delete reports
            cur.execute("DELETE FROM relatorios WHERE aluno_id IN (SELECT id FROM alunos WHERE unidade_id = %s)", (uid,))
            # Delete encaminhamentos
            cur.execute("DELETE FROM encaminhamentos WHERE aluno_id IN (SELECT id FROM alunos WHERE unidade_id = %s)", (uid,))
            # Delete triagens
            cur.execute("DELETE FROM triagens WHERE aluno_id IN (SELECT id FROM alunos WHERE unidade_id = %s)", (uid,))
            # Delete laudos
            cur.execute("DELETE FROM laudos WHERE aluno_id IN (SELECT id FROM alunos WHERE unidade_id = %s)", (uid,))
            # Delete categories
            cur.execute("DELETE FROM aluno_categorias WHERE aluno_id IN (SELECT id FROM alunos WHERE unidade_id = %s)", (uid,))
            # Delete students
            cur.execute("DELETE FROM alunos WHERE unidade_id = %s", (uid,))
            print(f"Cleared existing student data and related foreign records for school ID {uid}.")

        # 4. Generate 20 students per school
        n_students = 20
        first_names = ["Lucas", "Gabriel", "Matheus", "Pedro", "Enzo", "João", "Guilherme", "Gustavo", "Felipe", "Rafael", 
                       "Sofia", "Julia", "Alice", "Manuela", "Isabella", "Laura", "Luiza", "Valentina", "Giovanna", "Maria"]
        last_names = ["Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Gomes", "Ribeiro",
                      "Martins", "Carvalho", "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa", "Rocha", "Dias"]
        
        series = ["1º Ano A", "2º Ano B", "3º Ano A", "4º Ano B", "5º Ano A", "6º Ano B", "7º Ano A", "8º Ano B", "9º Ano A"]
        
        for index, uid in enumerate(unit_ids):
            school_tag = "Centro" if index == 0 else "Norte"
            print(f"\nPopulating {n_students} students for {school_tag} (School ID {uid})...")
            
            for i in range(1, n_students + 1):
                # Pick unique details
                nome = f"{random.choice(first_names)} {random.choice(last_names)} ({school_tag} #{i})"
                cpf = f"{random.randint(100, 999)}.{random.randint(100, 999)}.{random.randint(100, 999)}-{random.randint(10, 99)}"
                data_nascimento = f"{random.randint(2010, 2018)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
                responsavel = f"{random.choice(first_names)} {random.choice(last_names)}"
                telefone = f"(11) 9{random.randint(8000, 9999)}-{random.randint(1000, 9999)}"
                serie = random.choice(series)
                nivel_suporte = random.choice([1, 2, 3])
                
                # Insert Aluno
                cur.execute(
                    """
                    INSERT INTO alunos (unidade_id, nome_completo, cpf, data_nascimento, endereco, responsavel_nome, responsavel_telefone, serie_turma, nivel_suporte, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (uid, nome, cpf, data_nascimento, f"Rua das Flores, {random.randint(1, 500)}", responsavel, telefone, serie, nivel_suporte, "ativo")
                )
                aluno_id = cur.fetchone()["id"]
                
                # Assign specialty/category (neurodiversity)
                # Ensure each student gets at least one active category, rotating through all of them
                cat = categories[(i - 1) % len(categories)]
                cur.execute(
                    """
                    INSERT INTO aluno_categorias (aluno_id, categoria_id)
                    VALUES (%s, %s)
                    """,
                    (aluno_id, cat["id"])
                )
                
                # Add laudo
                cur.execute(
                    """
                    INSERT INTO laudos (aluno_id, descricao, profissional_responsavel, data_emissao)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (aluno_id, f"Laudo de diagnóstico para {cat['nome']}", "Dr. Roberto Neurologista", data_nascimento)
                )

                # Add a triagem for some students to populate dashboard
                if i % 2 == 0:
                    status_triagem = random.choice(['aguardando_entrevista', 'em_avaliacao', 'concluida', 'alta_prioridade'])
                    cur.execute(
                        """
                        INSERT INTO triagens (aluno_id, psicopedagogo_id, data_registro, tipo_registro, status, queixa_principal)
                        VALUES (%s, (SELECT id FROM usuarios WHERE perfil_id = (SELECT id FROM perfis WHERE nome = 'psicopedagogo') LIMIT 1), '2026-05-20', 'triagem', %s, %s)
                        """,
                        (aluno_id, status_triagem, f"Queixa de dificuldades de aprendizagem relacionada a {cat['nome']}")
                    )

                # Add plano for some students
                if i % 3 == 0:
                    cur.execute(
                        """
                        INSERT INTO planos_acompanhamento (aluno_id, psicopedagogo_id, titulo, objetivo_geral, estrategias, status, data_inicio)
                        VALUES (%s, (SELECT id FROM usuarios WHERE perfil_id = (SELECT id FROM perfis WHERE nome = 'psicopedagogo') LIMIT 1), %s, %s, %s, %s, '2026-05-01')
                        """,
                        (aluno_id, f"Plano de Acompanhamento - {cat['nome']}", f"Objetivos específicos para {cat['nome']}", "Estratégias de inclusão e apoio pedagógico", "ativo")
                    )

                print(f" -> Created student {i}/20: {nome} with specialty: {cat['nome']}")

    conn.commit()
    print("\n[SUCCESS] Successfully populated 40 students across the 2 schools with distinct specialties and support levels.")
except Exception as e:
    conn.rollback()
    print(f"\n[ERROR] Transaction rolled back due to error: {e}")
finally:
    conn.close()
