from deap import base, creator, tools, algorithms
import pandas as pd
import numpy as np
from fpdf import FPDF
import subprocess
import os
import tkinter as tk
from tkinter import ttk


#parametri dell'ottimizzazione
Ntot = 100          #numero capienza database
N = 20              #numero farmaci utilizzati


def submit_and_close():
    global nome_cognome, misura_glicemia, misura_pressione_sistolica, misura_pressione_diastolica, ottimizza_costo, salute_fegato_reni_perc
    
    # Recupera i valori inseriti
    nome_cognome = nome_entry.get()
    misura_glicemia = int(diabete_entry.get())
    misura_pressione_sistolica = int(pressione_sistolica_entry.get())
    misura_pressione_diastolica = int(pressione_diastolica_entry.get())
    ottimizza_costo = bool(checkbox_var.get())
    salute_fegato_reni_perc = int(percentuale_var.get()) /100

    # Mostra i valori nella console o elabora ulteriormente
    print(f"Nome e cognome: {nome_cognome}")
    print(f"Diabete: {misura_glicemia}")
    print(f"Pressione diastolica: {misura_pressione_diastolica }")
    print(f"Pressione sistolica: {misura_pressione_sistolica}")
    print(f"Ottimizza costo selezionato: {ottimizza_costo}")
    print(f"Percentuale: {salute_fegato_reni_perc}%")

    # Chiude la finestra
    root.destroy()

# Creazione della finestra principale
root = tk.Tk()
root.title("Inserimento dati")
root.geometry("400x410")


# Etichetta e campi di testo per i dati

# Nome
tk.Label(root, text="Inserisci nome e cognome:").pack(pady=5)
nome_entry = ttk.Entry(root, width=30)
nome_entry.pack(pady=5)

# Diabete
tk.Label(root, text="Inserisci valore Diabete:").pack(pady=5)
diabete_entry = ttk.Entry(root, width=30)
diabete_entry.pack(pady=5)

# Pressione diastolica
tk.Label(root, text="Inserisci Pressione Diastolica:").pack(pady=5)
pressione_diastolica_entry = ttk.Entry(root, width=30)
pressione_diastolica_entry.pack(pady=5)

# Pressione sistolica
tk.Label(root, text="Inserisci Pressione Sistolica:").pack(pady=5)
pressione_sistolica_entry = ttk.Entry(root, width=30)
pressione_sistolica_entry.pack(pady=5)

# Casella di spunta
checkbox_var = tk.BooleanVar()
checkbox = ttk.Checkbutton(root, text="Ottimizza costo", variable=checkbox_var)
checkbox.pack(pady=5)

# Slider per la percentuale con freccette e inserimento manuale
tk.Label(root, text="Salute del fegato e dei reni:").pack(pady=5)
percentuale_var = tk.IntVar()
percentuale_var.set(100)  # Imposta il valore iniziale a 100
percentuale_spinbox = ttk.Spinbox(root, from_=0, to=100, textvariable=percentuale_var, width=10)
percentuale_spinbox.pack(pady=5)

# Bottone per inviare i dati e chiudere
submit_button = ttk.Button(root, text="Conferma", command=submit_and_close)
submit_button.pack(pady=10)

# Avvia il ciclo principale della finestra
root.mainloop()

if(misura_glicemia >= 90):                                                      #soglia di attivazione
    E_d_min = np.maximum(0, misura_glicemia - 80) / 25      # 80 è consideato nominale
else:
    E_d_min = 0

if (misura_pressione_sistolica >= 135 or  misura_pressione_diastolica >= 85):   #soglia di attivazione                                                               
    E_h_min = (np.maximum(misura_pressione_sistolica - 130, 0) + np.maximum(misura_pressione_diastolica - 80, 0)) / 28.3    #
else:
    E_h_min = 0

soglia_efficienza_minima = -0.5     #per non creare scompenso nelle efficienze

null_solution = False

if (E_h_min + E_d_min) != 0:
    alpha = E_d_min/(E_h_min + E_d_min)
    beta = E_h_min/(E_h_min + E_d_min)
else:
    null_solution = True


# vincolo di carica farmacologica max
k_max = (E_d_min + E_h_min)/3 * salute_fegato_reni_perc

# ottimizzazione di spesa massima

if ottimizza_costo :
   Ro = 0.005
else :
   Ro = 0



# Lettura del database dai file csv
incompatibility_matrix = pd.read_csv('incompatibility_matrix.csv', header=None, skiprows=1, usecols=range(1, N+1)).to_numpy(dtype=int)

drug_data = pd.read_csv('drug_data.csv', nrows=N)
X_i_Max = drug_data['X_i_Max'].to_numpy()       # Limite massimo di dosi
c_i = drug_data['c_i'].to_numpy()               # Costi
k_i = drug_data['k_i'].to_numpy()               # Cariche farmacologiche
ed_i = drug_data['ed_i'].to_numpy()             # Efficienza per diabete
sd_i = drug_data['sd_i'].to_numpy()             # Effetti collaterali per diabete
eh_i = drug_data['eh_i'].to_numpy()             # Efficienza per ipertensione
sh_i = drug_data['sh_i'].to_numpy()             # Effetti collaterali per ipertensione
nomi_farmaci = drug_data['DrugName'].to_numpy() # nomi farmaci     


# Crea lo spazio delle soluzioni
creator.create("FitnessMax", base.Fitness, weights=(1.0,))  # Massimizza l'efficienza
creator.create("Individual", list, fitness=creator.FitnessMax)
toolbox = base.Toolbox()

# Definizione di un individuo (soluzione)
#toolbox.register("attr_int", np.random.randint, 0, X_i_Max.max() + 1)
toolbox.register("attr_int", np.random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_int, n=N)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# Funzione obiettivo
def evaluate(individual):
    # Calcolo dell'efficienza totale
    efficiency = np.sum((alpha * (ed_i - sd_i ) + beta * (eh_i - sh_i) - Ro * c_i) * individual)
    # Penalità per i vincoli
    penalty = feasibility(individual)

    #print("\nIndividual: " + str(individual))
    return efficiency - penalty,  # Penalità sottratta dall'obiettivo

# Penalità per i vincoli
def feasibility(individual):
    penalty = 0

    #print("\ncarica: " + str(np.sum(k_i * individual)) + " - costo: " + str(np.sum(c_i * individual)))

    # Vincolo di carica farmacologica
    carica = np.sum(k_i * individual) 
    if carica > k_max:
        penalty += 1e6 * (carica - k_max)

    # # Vincolo di budget
    # if np.sum(c_i * individual) > budget:
    #     penalty += 1e2

    # Vincolo di efficienza minima
    efficiency_d = np.sum((ed_i - sd_i) * individual)
    if efficiency_d < soglia_efficienza_minima:
        penalty += 1e6 * (soglia_efficienza_minima - efficiency_d)
        
    efficiency_h = np.sum((eh_i - sh_i) * individual)
    if efficiency_h < soglia_efficienza_minima:
        penalty += 1e6 * (soglia_efficienza_minima - efficiency_h)

    # Vincolo di dosi massime
    penalty += np.sum(np.maximum(individual - X_i_Max, 0) * 1e5)

    # Vincolo di incompatibilità
    for i in range(N):
        for j in range(i + 1, N):
            if incompatibility_matrix[i, j] == 1 and (int(individual[i])>0 and int(individual[j])>0):
                penalty += 1e8
                
    return penalty
  
# Registro degli operatori genetici
toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxUniform, indpb=0.5)
toolbox.register("mutate", tools.mutUniformInt, low=0, up=X_i_Max.max(), indpb=0.2)
toolbox.register("select", tools.selTournament, tournsize=3)

# Algoritmo genetico
toolbox.register("map", map)
population = toolbox.population(n=200)

if null_solution:
    best_individual =  [0] * N
else:
    algorithms.eaSimple(population, toolbox, cxpb=0.7, mutpb=0.2, ngen=1000, verbose=True)
    best_individual = tools.selBest(population, k=1)[0]                                     # Migliore soluzione

# Migliore soluzione

print("\nMigliore soluzione:", best_individual)
print("Efficienza su diabete:", np.sum((ed_i - sd_i) * best_individual))
print("Efficienza su ipertensione:", np.sum((eh_i - sh_i) * best_individual))
print("Efficienza totale:", np.sum((ed_i - sd_i + eh_i - sh_i) * best_individual))
print("Carica totale:", np.sum(k_i * best_individual), " (target <=", k_max, ")" )
print("Costo totale:", np.sum(c_i * best_individual) )


print("\n\nPIANO TERAPEUTICO:")
for i in range(0,19):
    if best_individual[i] != 0:
        print(f"{best_individual[i]} {nomi_farmaci[i]}")

print("\n\n")


# generazione piano terapeutico in formato PDF
output_ricetta = "Il/La signor/a " + nome_cognome + " a cura delle seguenti patologie di diabete e ipertensione, dovrà seguire giornalmente il seguente piano terapeutico: \n\n"
for i in range(0,N):
    if best_individual[i] > 0:
        output_ricetta += "x" + str(best_individual[i]) + " - " + nomi_farmaci[i] + "\n"

pdf = FPDF()
pdf.add_page()

titolo = "Piano terapeutico"
pdf.set_font("Arial", style="B", size=16)  
pdf.cell(200, 10, txt=titolo, ln=True, align='C')  
pdf.ln(10) 

pdf.set_font("Arial", size=12)  
pdf.multi_cell(0, 10, txt=output_ricetta, align='L')  # Multi-cell per testo lungo

pdf.output("piano.pdf")


# apertura pdf
percorso_pdf = "piano.pdf"
adobe_path = r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe"

if os.path.exists(percorso_pdf) and os.path.exists(adobe_path):
    subprocess.Popen([adobe_path, percorso_pdf])
else:
    print("File PDF o Acrobat Reader non trovato!")
