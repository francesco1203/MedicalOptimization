#ATTENZIONE, PER USARE QUESTO CODICE DEV'ESSERE DISATTIVATA L'INTERFACCIA GRAFICA
#(Setta flag TestMode a true in GA.py)
import runpy



def test():
    diabete_testset = [80, 100, 130, 150]                                        
    pressione_testset = [(80, 120), (90, 130), (100, 140), (120, 160)]     
    fegatoreni_testset = [100, 60, 30, 10]    
    ottimizzacosto_testset = [False, True]                         

    for misura_diabete_test in diabete_testset:
        for misura_pressione_test  in pressione_testset:
            for misura_fegatoreni_test  in fegatoreni_testset:
                for ottimizza_costo_test  in ottimizzacosto_testset:

                    # nome_cognome = "test test"
                    # misura_glicemia = misura_diabete_test
                    # misura_pressione_sistolica = misura_pressione_test[0]
                    # misura_pressione_diastolica = misura_pressione_test[1]
                    # salute_fegato_reni_perc = misura_fegatoreni_test / 100
                    # ottimizza_costo = ottimizza_costo_test
                    # stampa_ricetta = False
                    # runpy.run_path("GA.py")


                    variabili = {
                        "nome_cognome": "test test",
                        "misura_glicemia": misura_diabete_test,
                        "misura_pressione_sistolica": misura_pressione_test[0],
                        "misura_pressione_diastolica": misura_pressione_test[1],
                        "salute_fegato_reni_perc": misura_fegatoreni_test / 100,
                        "ottimizza_costo": ottimizza_costo_test,
                        "stampa_ricetta": False,
                    }

                    # Esegui GA.py con le variabili nel contesto globale
                    runpy.run_path("GA.py", init_globals=variabili)

                


if __name__ == "__main__":
    test()
