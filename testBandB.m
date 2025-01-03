% Nome del file mlx
fileMlx = 'BranchAndBound.mlx'; 

% Verifica se il file esiste
if isfile(fileMlx)
    % Percorso completo del file mlx
    fullPath = fullfile(pwd, fileMlx);
    
    % Esegue il file mlx
    try
        % Definizione dei test set
        diabete_testset = [80, 100, 130, 150];
        pressione_testset = [80, 120; 90, 130; 100, 140; 120, 160];
        fegatoreni_testset = [100, 60, 30, 10];
        ottimizzacosto_testset = [false, true];

        % Loop nidificati
        for misura_diabete_test = diabete_testset
            for i = 1:size(pressione_testset, 1) 
                misura_pressione_test = pressione_testset(i, :);
                for misura_fegatoreni_test = fegatoreni_testset
                    for ottimizza_costo_test = ottimizzacosto_testset

                        misura_glicemia = misura_diabete_test, ...
                        misura_pressione_diastolica = misura_pressione_test(1)
                        misura_pressione_sistolica = misura_pressione_test(2)
                        salute_fegato_reni_perc = misura_fegatoreni_test / 100
                        ottimizza_costo = ottimizza_costo_test
                    
                        matlab.internal.liveeditor.executeAndSave(fullPath);
                    end
                end
            end
        end

        
        
    catch ME
        fprintf('Errore durante l esecuzione di %s: %s\n', fileMlx, ME.message);
    end
else
    fprintf('Il file %s non esiste nel percorso corrente.\n', fileMlx);
end
