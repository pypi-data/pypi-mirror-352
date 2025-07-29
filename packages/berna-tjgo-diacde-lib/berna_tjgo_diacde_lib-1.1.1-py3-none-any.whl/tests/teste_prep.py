from berna_tjgo_diacde_lib import preprocessing as prep

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
