# Import da classe Berna
import berna_tjgo_diacde_lib as brn
# Import do módulo de Pré-processamento
from berna_tjgo_diacde_lib import preprocessing as prep

# Instância
calc1 = brn.Berna('Eu sou o primeiro texto de Antonio Pires', 'Eu sou o segundo texto de antonio pires', False)

# Teste valores de entrada
print(f'\nFrase 1: {calc1.vec_terms1}')
print(f'Frase 2: {calc1.vec_terms2}')
print(f'Preprocessamento: {calc1.pre_process}')

# Teste cálculos Similaridades 
print('\nCálculo de Similaridade')
print(f'Jaccard: {calc1.get_similaridade_jaccard()}')
print(f'Cosseno: {calc1.get_similaridade_cosseno()}')
# Resultados esperados:
# se Preprocess True: 66.6667 e 80.0
# se Preprocess False: 45.4545 e 62.5

preset = [
    'no_email',
    'no_multiple_spaces',
    'no_loose_letters',
    'only_latin',
    'no_numbers',
]

# Teste métodos módulo Pré Processamento
print('\nFrase sem pontuações: ' + prep.clear("Eu sou o primeiro texto de antonio pires, incluindo leis, resoluções, normas legais."))
print('Frase com sinonimos filtrados: ' + prep.clear("Eu sou o primeiro texto de antonio pires, incluindo leis, resoluções, normas legais.", preset=preset))

# Teste método estático
print(f'\nUtilizando text_para_vetor estaticamente: {brn.Berna.texto_para_vetor(None, "Eu sou o primeiro texto de antonio pires, incluindo leis, resoluções, normas legais.", True)}\n')

calc2 = brn.Berna('Texto de exemplo 1', 'Texto de exemplo 2', True)

print(calc2.get_similaridade_jaccard())
print(calc2.get_similaridade_cosseno())