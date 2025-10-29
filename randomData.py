"""
generate_vet_data.py

Gera um CSV com 1000 registros de histórico de atendimentos para uma clínica veterinária fictícia.
Regras implementadas (resumo):
- Clientes (CPF) podem ter mais de 1 pet.
- Média de repetição de registros por pet ~ 3x (1000 registros / ~330 pets).
- Datas de consulta até 29/10/2025 (base date), com distribuição:
    * 200 registros (20%) dentro de <=12 dias
    * 300 registros (30%) dentro de 13-30 dias
    * 280 registros (28%) dentro de 31-179 dias  --> total 78% <=179 dias
    * 220 registros (22%) entre 180-367 dias
- Campos: Data do Atendimento, Nome Completo, CPF, Número (celular), CEP, Data de Nascimento (dono),
         Nome do Pet, Raça do Pet, Espécie do Pet, Data Nasc Pet, Sexo do Pet, Peso(kg), Veterinário,
         Serviço, Forma de Pagamento, Valor do Serviço (R$), Observações Médicas
- Formatos: CPF "000.000.000-00", telefone "(21) 9XXXX-XXXX", CEP "#####-###"
- Gera dados consistentes (mesmo CPF = mesmo dono, donos têm 1..3 pets, pet datas coerentes)
"""

import csv
import random
from datetime import datetime, timedelta
from faker import Faker

faker = Faker("pt_BR")
random.seed(42)
Faker.seed(42)

BASE_DATE = datetime(2025, 10, 29)  # não ultrapassar esta data
TOTAL_ROWS = 1000

# Configuração de clientes/pets para obter média de repetição ~3
NUM_PETS = 330        # número de pets distintos (ajusta a média de repetição)
NUM_CLIENTS = 250     # número de clientes (cada cliente 1..3 pets)

# Species, breeds exemplos (simplificado)
SPECIES_BREEDS = {
    "Cachorro": ["SRD", "Labrador", "Poodle", "Shih Tzu", "Bulldog", "Golden Retriever", "Pinscher"],
    "Gato": ["SRD", "Siamês", "Persa", "Maine Coon", "Sphynx", "Ragdoll"],
    "Coelho": ["SRD", "Netherland Dwarf", "Lop"],
    "Pássaro": ["Calopsita", "Canário", "Papagaio", "Periquito"],
    "Hamster": ["Sírio", "Anão russo"]
}
SPECIES = list(SPECIES_BREEDS.keys())

VETS = ["Dr. Lucas", "Dra. Julia", "Dra. Millena"]
PAYMENT_METHODS = ["Pix", "Dinheiro", "Crédito", "Débito"]

SERVICES = {
    "Consulta veterinária": (100, 200),
    "Vacinação": (80, 180),
    "Castração": (250, 800),
    "Exame de sangue": (100, 250),
    "Ultrassonografia": (180, 400),
    "Raio-X": (150, 300),
    "Limpeza dental": (200, 500),
    "Banho e tosa": (60, 150),
    "Internação diária": (100, 250),
    "Emergência 24h": (200, 400),
    "Exame de fezes": (60, 120),
    "Microchipagem": (80, 150),
    "Consulta com especialista": (180, 350),
    "Eutanásia": (200, 500)
}

# Gera CEPs do estado do RJ (prefixos aproximados: 20000-28999)
def random_rj_cep():
    prefix = random.randint(20000, 28999)
    suffix = random.randint(0, 999)
    return f"{prefix:05d}-{suffix:03d}"

# Gera CPF formatado usando faker (faker.cpf() gera sem máscara? ele já gera com pontos e traço)
def format_cpf(cpf_raw):
    # se vier sem máscara, aplicar máscara
    s = ''.join(filter(str.isdigit, str(cpf_raw)))
    if len(s) != 11:
        # fallback: gerar aleatório
        s = faker.cpf().replace('.', '').replace('-', '')
    return f"{s[0:3]}.{s[3:6]}.{s[6:9]}-{s[9:11]}"

def random_phone():
    # Preferência por DDD 21 (Rio). Format "(21) 9XXXX-XXXX"
    ddd = "21"
    first = random.choice([9])  # celular 9...
    rest = random.randint(1000, 9999)
    mid = random.randint(6000, 9999)
    # formato (21) 9XXXX-XXXX
    return f"({ddd}) {first}{mid:04d}-{rest:04d}"

# Gera data de nascimento do dono: maior que 16 anos, maioria 25-45
def owner_birthdate():
    # probabilidades: 70% entre 25-45, 15% 16-24, 15% 46-70
    p = random.random()
    if p < 0.70:
        age = random.randint(25, 45)
    elif p < 0.85:
        age = random.randint(16, 24)
    else:
        age = random.randint(46, 70)
    birth = BASE_DATE - timedelta(days=age*365 + random.randint(0, 364))
    return birth.date()

# Gera pet birthdate coerente com species and consultation date
def pet_birthdate_for_species(species, consult_date):
    # approximated lifespans and typical age distributions
    if species == "Cachorro":
        min_age_days = 30  # at least 1 month
        max_age_years = 15
    elif species == "Gato":
        min_age_days = 30
        max_age_years = 18
    elif species == "Coelho":
        min_age_days = 30
        max_age_years = 8
    elif species == "Pássaro":
        min_age_days = 30
        max_age_years = 20
    elif species == "Hamster":
        min_age_days = 30
        max_age_years = 3
    else:
        min_age_days = 30
        max_age_years = 10

    # choose an age in days from 1 month up to max_age_years, but ensure not negative
    max_days = max_age_years * 365
    age_days = random.randint(min_age_days, max_days)
    birth = consult_date - timedelta(days=age_days)
    return birth.date()

# Peso por espécie (kg) — formatado com vírgula como exemplo "4,37"
def random_weight_for_species(species):
    if species == "Cachorro":
        # wide range
        w = random.uniform(1.0, 40.0)
    elif species == "Gato":
        w = random.uniform(2.0, 8.0)
    elif species == "Coelho":
        w = random.uniform(1.0, 6.0)
    elif species == "Pássaro":
        w = random.uniform(0.02, 2.0)
    elif species == "Hamster":
        w = random.uniform(0.03, 0.3)
    else:
        w = random.uniform(1.0, 20.0)
    # format with 2 decimals and comma decimal separator
    return f"{w:0.2f}".replace('.', ',')

# Decide serviço e valor conforme tabela
def pick_service_and_value():
    service = random.choice(list(SERVICES.keys()))
    low, high = SERVICES[service]
    value = round(random.uniform(low, high), 2)
    # format value with 2 decimals (using comma decimal to match BR if you want)
    return service, f"{value:0.2f}".replace('.', ',')

# Gera um comentário médico curto
def random_observation():
    phrases = [
        "Paciente estável, sem sinais vitais alterados.",
        "Recomendada medicação antibiótica por 7 dias.",
        "Vacinação atualizada, sem reações.",
        "Necessário retorno para avaliação em 15 dias.",
        "Sinais de melhoria após tratamento.",
        "Realizar exames laboratoriais complementares.",
        "Peso abaixo do ideal, sugerir dieta.",
        "Ferida cicatrizando, curativo semanal.",
        "Sedação leve para procedimento indicado.",
        "Encaminhado para especialista."
    ]
    return random.choice(phrases)

# --- Construção dos clientes e pets ---
clients = []
client_cpf_set = set()

# Gerar clientes únicos com CPF, nome, telefone, cep, birthdate
for _ in range(NUM_CLIENTS):
    # garantir cpf único
    cpf_raw = faker.cpf()  # já formatado por faker, ex: '170.061.267-03'
    while cpf_raw in client_cpf_set:
        cpf_raw = faker.cpf()
    client_cpf_set.add(cpf_raw)
    name = faker.name().lower().title()  # capitalize each word
    phone = random_phone()
    cep = random_rj_cep()
    dob = owner_birthdate()
    clients.append({
        "cpf": format_cpf(cpf_raw),
        "name": name,
        "phone": phone,
        "cep": cep,
        "dob": dob
    })

# Gerar pets list tied to clients: assign pets to clients until NUM_PETS total
pets = []
client_index = 0
while len(pets) < NUM_PETS:
    client = clients[client_index % len(clients)]
    # número de pets por cliente 1..3 (probabilidade maior 1-2)
    n_pets_for_client = random.choices([1,2,3], weights=[0.6,0.3,0.1])[0]
    for p in range(n_pets_for_client):
        if len(pets) >= NUM_PETS:
            break
        species = random.choice(SPECIES)
        breed = random.choice(SPECIES_BREEDS[species])
        pet_name = faker.first_name().title()
        sex = random.choice(["Macho", "Fêmea"])
        # store pet but birthdate set later per consultation to allow reasonable ages per consult
        pets.append({
            "owner_cpf": client["cpf"],
            "owner_name": client["name"],
            "owner_phone": client["phone"],
            "owner_cep": client["cep"],
            "owner_dob": client["dob"],
            "pet_name": pet_name,
            "species": species,
            "breed": breed,
            "sex": sex
        })
    client_index += 1

# --- Montar distribuição de datas de consulta ---
rows = []

# distribution counts
count_within_12 = int(0.20 * TOTAL_ROWS)    # 20%
count_13_30 = int(0.30 * TOTAL_ROWS)        # 30%
count_31_179 = int(0.28 * TOTAL_ROWS)       # 28%  (so total 78% <=179 days)
count_180_367 = TOTAL_ROWS - (count_within_12 + count_13_30 + count_31_179)

date_offsets = []
date_offsets += [random.randint(1, 12) for _ in range(count_within_12)]
date_offsets += [random.randint(13, 30) for _ in range(count_13_30)]
date_offsets += [random.randint(31, 179) for _ in range(count_31_179)]
date_offsets += [random.randint(180, 367) for _ in range(count_180_367)]

# shuffle offsets to mix
random.shuffle(date_offsets)

# Now pick pet indices for each consult (allow repeats) - sampling pets uniformly
for offset in date_offsets:
    consult_date = BASE_DATE - timedelta(days=offset)
    # choose a pet (thus client info derived)
    pet = random.choice(pets)
    # pet birthdate coherent with species and consult date
    pet_dob = pet_birthdate_for_species(pet["species"], consult_date)
    # weight
    weight = random_weight_for_species(pet["species"])
    # veterinarian
    vet = random.choice(VETS)
    # service and price
    service, price = pick_service_and_value()
    payment = random.choice(PAYMENT_METHODS)
    observation = random_observation()
    row = {
        "Data do Atendimento": consult_date.strftime("%d/%m/%Y"),
        "Nome Completo": pet["owner_name"],
        "CPF": pet["owner_cpf"],
        "Número": pet["owner_phone"],
        "CEP": pet["owner_cep"],
        "Data de Nascimento (Dono)": pet["owner_dob"].strftime("%d/%m/%Y"),
        "Nome do Pet": pet["pet_name"],
        "Raça do Pet": pet["breed"],
        "Espécie do Pet": pet["species"],
        "Data de Nascimento (Pet)": pet_dob.strftime("%d/%m/%Y"),
        "Sexo do Pet": pet["sex"],
        "Peso (kg)": weight,
        "Veterinário Responsável": vet,
        "Serviços Realizados": service,
        "Forma de Pagamento": payment,
        "Valor do Serviço (R$)": price,
        "Observações Médicas": observation
    }
    rows.append(row)

# If we have not reached TOTAL_ROWS because of rounding, ensure length
while len(rows) < TOTAL_ROWS:
    # duplicate random existing row with slight variation (new consult date within 1..12 days)
    orig = random.choice(rows)
    new_offset = random.randint(1, 12)
    consult_date = BASE_DATE - timedelta(days=new_offset)
    new_row = orig.copy()
    new_row["Data do Atendimento"] = consult_date.strftime("%d/%m/%Y")
    new_row["Valor do Serviço (R$)"] = pick_service_and_value()[1]
    new_row["Observações Médicas"] = random_observation()
    rows.append(new_row)

# Shuffle final rows
random.shuffle(rows)

# --- Escrever CSV ---
output_file = "veterinary_dataset.csv"
fieldnames = [
    "Data do Atendimento", "Nome Completo", "CPF", "Número", "CEP", "Data de Nascimento (Dono)",
    "Nome do Pet", "Raça do Pet", "Espécie do Pet", "Data de Nascimento (Pet)", "Sexo do Pet",
    "Peso (kg)", "Veterinário Responsável", "Serviços Realizados", "Forma de Pagamento",
    "Valor do Serviço (R$)", "Observações Médicas"
]

with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for r in rows[:TOTAL_ROWS]:
        writer.writerow(r)

print(f"✅ Dataset gerado: {output_file} ({len(rows[:TOTAL_ROWS])} linhas)")
