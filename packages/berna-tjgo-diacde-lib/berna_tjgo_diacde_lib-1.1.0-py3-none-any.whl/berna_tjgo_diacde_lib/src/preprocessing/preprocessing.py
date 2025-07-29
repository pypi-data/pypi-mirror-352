"""
Created on Sun Jul 21 09:54:07 2024

@authors:
    Antonio Pires
    Milton Ávila
    João Gabriel
    Wesley Oliveira

@license:
Este projeto está licenciado sob a Licença Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0). Você pode compartilhar, adaptar e construir sobre o material, desde que atribua crédito apropriado, não use o material para fins comerciais e distribua suas contribuições sob a mesma licença.
Para mais informações, consulte o arquivo [LICENSE](./LICENSE).
"""
from ..config import Packages
from . import _methods

def clear(
    txt: str | list[str],
    preset: list[str] = [],
    no_ponctuation: bool = False,
    no_loose_letters: bool = False,
    no_multiple_spaces: bool = False,
    # get_synonym_by_dict: bool = False,
    no_html: bool = False,
    no_email: bool = False,
    no_numbers: bool = False,
    no_stopwords: bool = False,
    only_latin: bool = False,
    lemmatize: bool = False,
    stemming: bool = False
) -> str | list:
    """
    Função para processar o texto de várias formas, removendo ou alterando caracteres,
    espaços, pontuação, entre outros, conforme os parâmetros fornecidos.

    Args:
        txt (str or list[str]): Texto ou lista de textos a serem processados.
        preset (list[str], opcional): Lista de métodos pré-definidos para aplicar.
        no_ponctuation (bool, opcional): Se True, remove pontuação.
        no_multiple_spaces (bool, opcional): Se True, remove espaços múltiplos.
        no_loose_letters (bool, opcional): Se True, remove letras soltas.
        only_latin (bool, opcional): Se True, limita o texto ao alfabeto latino.
        no_email (bool, opcional): Se True, remove endereços de e-mail.
        no_numbers (bool, opcional): Se True, remove números.
        no_stopwords (bool, opcional): Se True, remove palavras de parada.
        no_html (bool, opcional): Se True, remove tags HTML.
        lemmatize (bool, opcional): Se True, realiza lematização no texto.
        stemming (bool, opcional): Se True, realiza stemming no texto.

    Returns:
        str or list[str]: Texto processado ou lista de textos processados.
    """
    # Se o input for uma lista de strings, iteramos sobre ela
    if isinstance(txt, list):
        return [clear_single(
        t,
            preset, no_ponctuation, no_multiple_spaces, no_loose_letters, 
            only_latin, no_email, no_numbers, no_stopwords, no_html, 
            lemmatize, stemming
            # , get_synonym_by_dict
        ) for t in txt]
    
    # Caso contrário, tratamos o texto como uma string
    return clear_single(
        txt, preset, no_ponctuation, no_multiple_spaces, no_loose_letters, 
        only_latin, no_email, no_numbers, no_stopwords, no_html, 
        lemmatize, stemming
        # , get_synonym_by_dict
    )
    
def clear_single(
    txt: str,
    preset: list[str],
    no_ponctuation: bool,
    no_multiple_spaces: bool,
    no_loose_letters: bool,
    only_latin: bool,
    no_email: bool,
    no_numbers: bool,
    no_stopwords: bool,
    no_html: bool,
    lemmatize: bool,
    stemming: bool,
    # get_synonym_by_dict: bool
) -> str:
    
    if preset:
        for method in preset:
            method = getattr(Packages.PREP_METHODS, method)
            
            txt = method(txt)
        return txt
    
    else:
        txt = txt.lower()
        
        if no_email:
            txt = _methods.no_email(txt)
        if no_html:
            txt = _methods.no_html(txt)
        # if get_synonym_by_dict:
        #     txt = _methods.get_synonym_by_dict(txt)
        if no_ponctuation:
            txt = _methods.no_ponctuation(txt)
        if no_multiple_spaces:
            txt = _methods.no_multiple_spaces(txt)
        if no_loose_letters:
            txt = _methods.no_loose_letters(txt)
        if only_latin:
            txt = _methods.only_latin(txt)
        if no_numbers:
            txt = _methods.no_numbers(txt)
        if no_stopwords:
            txt = _methods.no_stopwords(txt)
        if lemmatize:
            txt = _methods.lemmatize(txt)
        if stemming:
            txt = _methods.stemming(txt)
        return txt

if __name__=="__main__":
    # Teste func 1
    print(clear(["<span>Eu sou o primeiro texto de antonio! pires, incluindo leis, resoluções, normas legais.</span>", "Essa é uma frase que não contém um email, joao@gmail.com."], no_html=True, no_email=True, no_ponctuation=True, only_latin=True))

    # Teste func 2
    print(_methods.lemmatize("Esse é um exemplo de um texto lematizado, com palavras reduzidas a sua raíz."))

    # Teste func 3
    print(_methods.stemming("Esse é um exemplo de um texto lematizado, com palavras reduzidas a sua raíz."))

    # Teste func 4
    print(_methods.no_ponctuation("Esse é um teste! e não devem haver pontuações nessa frase..."))
    
    # Teste func 5
    print(_methods.no_html("<script>Essa é uma frase sem palavras de css, </script>"))
    
    # Teste func 6
    print(_methods.no_stopwords("Esse é um exemplo de um texto sem stopwors, sem palavras de conjunção."))

    # # Teste func 7
    # print(_methods.get_synonym_by_dict("Método de sinonimos por dicionário: Eu sou o primeiro texto de antonio pires, incluindo leis, resoluções, normas legais."))
    
    # Teste func 8
    print(_methods.no_multiple_spaces("  Esse   é um teste!   e não devem haver espaços extras   nessa frase..  ."))
    
    # Teste func 9
    print(_methods.no_loose_letters("Esse é um exemplo de frase sem letras s soltas a i."))
    
    # Teste func 10
    print(_methods.only_latin("Essa é uma frase apenas com caracteres do alfabeto latin."))
    
    # Teste func 11
    print(_methods.no_email("Essa é uma frase que não contém um email, joao@gmail.com."))
    
    # Teste func 12
    print(_methods.no_numbers("Essa é um5a frase q2ue não contém números 123 4 22 3 135"))