#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script used to analyze results, getting best and worst results for each dataset.
Also finds best, median and worst balancing method, feature selection method,
number of selected features and classifier for each dataset.

@author: Henrique de Almeida Machado da Silveira

October 29th, 2017
"""

import csv
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

# Adapted from https://matplotlib.org/examples/pylab_examples/barchart_demo.html
def plot_best_worst_results(dataset_names, best_results, worst_results):
    best = [x["G-Mean"] for x in best_results]
    worst = [x["G-Mean"] for x in worst_results]

    n_groups = len(dataset_names)
    
    plt.figure(figsize=(18,15))
    
    index = np.arange(n_groups)
    bar_width = 0.2
    
    opacity = 0.4
    error_config = {'ecolor': '0.3'}
    
    plt.bar(index, best, bar_width,
                     alpha=opacity,
                     color='b',
                     error_kw=error_config,
                     label='Melhores resultados')
    
    plt.bar(index + bar_width, worst, bar_width,
                     alpha=opacity,
                     color='r',
                     error_kw=error_config,
                     label='Piores resultados')
    
    plt.xlabel('Conjunto de dados')
    plt.ylabel('G-Mean')
    plt.title('Melhores e piores resultados para cada conjunto de dados')
    plt.xticks(index + bar_width / 2, dataset_names)
    plt.yticks(np.arange(0.0, 1.01, 0.05))
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('analysis/results.png')
    plt.close()

def create_dict(data_frame, column, values):
    data_dict = {}
    data_dict[values[0]] = data_frame.loc[data_frame[column] == values[0], "G-Mean"].mean()
    data_dict[values[1]] = data_frame.loc[data_frame[column] == values[1], "G-Mean"].mean()
    data_dict[values[2]] = data_frame.loc[data_frame[column] == values[2], "G-Mean"].mean()
    
    return data_dict

def compute_diff_dict(data_dict, max_key, min_key):
    return compute_diff(data_dict[max_key], data_dict[min_key])

def compute_diff(a, b):
    diff =  abs(a - b) / ((a + b)/2) * 100
    return np.around(diff, decimals = 4)

def analyze_info(data_frame, column, values):
    data_dict = create_dict(data_frame, column, values)
    
    sorted_data_dict = sorted(data_dict, key=data_dict.get)
    max_data = sorted_data_dict[2]
    med_data = sorted_data_dict[1]
    min_data = sorted_data_dict[0]
        
    diff_max_med = compute_diff_dict(data_dict = data_dict,
                                     max_key = max_data,
                                     min_key = med_data)
    
    diff_max_min = compute_diff_dict(data_dict = data_dict,
                                     max_key = max_data,
                                     min_key = min_data)
    
    return {"max_data" : max_data,
            "med_data" : med_data,
            "min_data" : min_data,
            "diff_max_med" : diff_max_med,
            "diff_max_min" : diff_max_min}

def main():
    
    filenames = glob("results/*.csv")
    dataset_names = [os.path.splitext(os.path.basename(x))[0] for x in filenames]
    
    if len(filenames) == 0:
        raise FileNotFoundError("No results files found in the target directory!")
        
    best_results = []
    worst_results = []
    median_results = []
    mean_results = []
    first_quartile_results = []
    third_quartile_results = []
    
    with open("analysis/analysis.csv", "w") as analysis_file:
        wr1 = csv.writer(analysis_file,
                        delimiter = ",",
                        quoting=csv.QUOTE_NONNUMERIC)
        
        wr1.writerow(["Dataset",
                     "Melhor Algoritmo de seleção de atributos",
                     "Mediana Algoritmo de seleção de atributos",
                     "Pior Algoritmo de seleção de atributos",
                     "Diff Melhor Mediana %",
                     "Diff Melhor Pior %",
                     "Melhor Número de atributos selecionados",
                     "Mediana Número de atributos selecionados",
                     "Pior Número de atributos selecionados",
                     "Diff Melhor Mediana %",
                     "Diff Melhor Pior %",
                     "Melhor Método de Balanceamento",
                     "Mediana Método de Balanceamento",
                     "Pior Método de Balanceamento",
                     "Diff Melhor Mediana %",
                     "Diff Melhor Pior %",
                     "Melhor Classificador",
                     "Mediana Classificador",
                     "Pior Classificador",
                     "Diff Melhor Mediana %",
                     "Diff Melhor Pior %"])

        for i, filename in enumerate(filenames):
        
            results = pd.read_csv(filename)
            results["G-Mean"] = np.around(results["G-Mean"], decimals = 4)
            results = results.sort_values(by = "G-Mean")
            worst_results.append(results.iloc[0])
            best_results.append(results.iloc[-1])
            median_results.append(results["G-Mean"].median())
            mean_results.append(results["G-Mean"].mean())
            first_quartile_results.append(results["G-Mean"].quantile(0.25))
            third_quartile_results.append(results["G-Mean"].quantile(0.75))
        
            ft_slct_dict = analyze_info(data_frame = results,
                                   column = "Algoritmo de seleção de atributos",
                                   values = ["ReliefF", "SDAE", "FCBF"])
            
            num_ft_slct_dict = analyze_info(data_frame = results,
                               column = "Número de atributos selecionados",
                                       values = [10, 50, 100])
            
            blc_dict = analyze_info(data_frame = results,
                                       column = "Método de Balanceamento",
                                       values = ["SMOTE", "SMOTETomek", "NearMiss"])
            
            clf_dict = analyze_info(data_frame = results,
                                       column = "Classificador",
                                       values = ["MLP", "CNN", "DecisionTree"])
            
            wr1.writerow([dataset_names[i],
                         ft_slct_dict["max_data"],
                         ft_slct_dict["med_data"],
                         ft_slct_dict["min_data"],
                         ft_slct_dict["diff_max_med"],
                         ft_slct_dict["diff_max_min"],
                         num_ft_slct_dict["max_data"],
                         num_ft_slct_dict["med_data"],
                         num_ft_slct_dict["min_data"],
                         num_ft_slct_dict["diff_max_med"],
                         num_ft_slct_dict["diff_max_min"],
                         blc_dict["max_data"],
                         blc_dict["med_data"],
                         blc_dict["min_data"],
                         blc_dict["diff_max_med"],
                         blc_dict["diff_max_min"],
                         clf_dict["max_data"],
                         clf_dict["med_data"],
                         clf_dict["min_data"],
                         clf_dict["diff_max_med"],
                         clf_dict["diff_max_min"]])
    
    with open("analysis/bestworst.csv", "w") as bestworst_file:
        wr2 = csv.writer(bestworst_file,
                        delimiter = ",",
                        quoting=csv.QUOTE_NONNUMERIC)
        
        wr2.writerow(["Dataset",
                      "Tipo",
                      "Resultado",
                      "Algoritmo de seleção de atributos",
                      "Número de atributos selecionados",
                      "Método de Balanceamento",
                      "Classificador",
                      "Diferença % para pior",
                      "Diferença % para 1º Quartil",
                      "Diferença % para Mediana",
                      "Diferença % para Média",
                      "Diferença % para 3º Quartil"])

        for i, filename in enumerate(filenames):
            best = best_results[i]
            worst = worst_results[i]
            wr2.writerow([dataset_names[i],
                          "Melhor resultado",
                          best["G-Mean"],
                          best["Algoritmo de seleção de atributos"],
                          best["Número de atributos selecionados"],
                          best["Método de Balanceamento"],
                          best["Classificador"],
                          compute_diff(best["G-Mean"], worst["G-Mean"]),
                          compute_diff(best["G-Mean"], first_quartile_results[i]),
                          compute_diff(best["G-Mean"], median_results[i]),
                          compute_diff(best["G-Mean"], mean_results[i]),
                          compute_diff(best["G-Mean"], third_quartile_results[i])])
            wr2.writerow([dataset_names[i],
                          "Pior resultado",
                          worst["G-Mean"],
                          worst["Algoritmo de seleção de atributos"],
                          worst["Número de atributos selecionados"],
                          worst["Método de Balanceamento"],
                          worst["Classificador"],
                          "-",
                          "-",
                          "-",
                          "-",
                          "-"])

    plot_best_worst_results(dataset_names, best_results, worst_results)

if __name__ == "__main__":
    main()
    