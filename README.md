# 🐾 Veterinary Clinic Data Generator

**File:** `generate_vet_data.py`  
**Purpose:** Generates a **realistic dataset (CSV)** with **1,000 rows** simulating the **appointment history of a fictional veterinary clinic**.

---

## 📘 Overview

This script creates synthetic but **coherent** veterinary data for testing, analytics, or educational purposes.

It includes **clients, pets, veterinarians, services, and payments**, following logical constraints — such as owners having multiple pets and realistic service frequencies.

---

## 🧠 Key Features

- **1000 rows** of structured data in CSV format  
- **Consistent relationships**:
  - Owners (by CPF) may have **1 to 3 pets**
  - Each pet has an average of **~3 visits**
- **Realistic date distribution** up to `29/10/2025`
- **Automatic formatting**:
  - CPF → `000.000.000-00`
  - Phone → `(21) 9XXXX-XXXX`
  - CEP → `#####-###`
- **Veterinarians:** Dr. Lucas, Dra. Julia, Dra. Millena  
- **Payment methods:** Pix, Cash, Credit, Debit  
- **15 veterinary services** with realistic price ranges  
- **Automatic random medical observations**

---

## 📊 Data Structure

**CSV Columns:**

| Column | Description |
|--------|--------------|
| Data do Atendimento | Appointment date |
| Nome Completo | Pet owner’s full name |
| CPF | Owner’s Brazilian ID (unique identifier) |
| Número | Phone number |
| CEP | Postal code (RJ region) |
| Data de Nascimento (Dono) | Owner’s birth date |
| Nome do Pet | Pet name |
| Raça do Pet | Breed |
| Espécie do Pet | Species |
| Data de Nascimento (Pet) | Pet’s birth date |
| Sexo do Pet | Male / Female |
| Peso (kg) | Pet’s weight |
| Veterinário Responsável | Assigned vet |
| Serviços Realizados | Service type |
| Forma de Pagamento | Payment method |
| Valor do Serviço (R$) | Service price in BRL |
| Observações Médicas | Short medical comment |

---

## 📅 Appointment Date Distribution

| Period | Percentage | Count (approx.) |
|---------|-------------|-----------------|
| ≤ 12 days | 20% | 200 |
| 13–30 days | 30% | 300 |
| 31–179 days | 28% | 280 |
| 180–367 days | 22% | 220 |

---

## ⚙️ Requirements

Install dependencies before running:

```bash
pip install faker
```

## 🚀 Usage

1. Clone this repository or download the script.

2. Run the Python file:

```
python generate_vet_data.py
```

3. The output file will be created in the same directory:

```
veterinary_dataset.csv
```
