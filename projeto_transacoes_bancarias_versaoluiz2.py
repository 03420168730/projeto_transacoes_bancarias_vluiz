# -----------------------
# depencies
# -----------------------
import json
import os
import uuid
import random
import sys
import unicodedata
from datetime import datetime
from collections import defaultdict, Counter

# -----------------------
# load settings
# -----------------------
sys.path.append('./data/')
from data import settings

# -----------------------
# SYSTEM functions 
# -----------------------
# não alterar nada das funções de system
def gera_transacao(categoria):
    return {
        "UUID": str(uuid.uuid4()),
        "valor": round(random.uniform(1.0, 1000.0), 2),  # Preço aleatório entre 1 e 1000
        "categoria": categoria
    }

def criar_transacoes(proporcao_categorias, num_transacoes=1,  categoria=None, seed=settings.seed):
    assert sum([proporcao_categorias[k] for k in proporcao_categorias])==1, '`proporcao_categorias` não soma 100%! Favor rever.'

    # garantir reprodutibilidade dos valores
    random.seed(seed)
    
    # Insere as transações para uma determinada categoria.
    if categoria:
        return [gera_transacao(categoria) for _ in range(0, num_transacoes)]
    
    # Calcula o número de transações por categoria com base na proporção
    numero_transacoes_por_categoria = {categoria: int(num_transacoes * proporcao) for categoria, proporcao in proporcao_categorias.items()}

    # Gera as transações
    transacoes = []
    for categoria, quantidade in numero_transacoes_por_categoria.items():
        for _ in range(quantidade):
            transacoes.append(gera_transacao(categoria))

    return transacoes

def salvar_json(transacoes, path2save, filename):
    # create path if not exist
    if not os.path.exists(path2save):
        os.makedirs(path2save)
    with open(os.path.join(path2save,filename), "w") as file:
        json.dump(transacoes, file, indent=4)
    print(f"Arquivo salvo em: {os.path.abspath(os.path.curdir)+'/'+path2save+'/'+filename}")

def criar_bd(num_transacoes:int = 10000, proporcao_categorias:list = settings.categorias_proporcao, path2save="./data", filename='transactions.json'):
    salvar_json(criar_transacoes(num_transacoes=num_transacoes,  proporcao_categorias=proporcao_categorias),
                path2save, filename
    )

def load_bd(filepath='./data/transactions.json'):
    with open(filepath, "r") as file:
        bd = json.load(file)
    return bd

def remover_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def tela_inicial():
    print("Bem-vindo Luiz!")
    print('conta: 0000031-0')
    print("\nEste programa permite gerenciar transações de sua conta pessoal.")
    print("\nEscolha uma das opções abaixo:")
    print("1. Visualizar relatórios")
    print("2. Cadastrar transações")
    print("3. Editar transações")
    print("4. Excluir transações")
    print("5. Consultar transação por ID")
    print("-" * 10)
    print("0. Sair")
    print('\n')

# -----------------------
# PROGRAM functions 
# -----------------------
def run():
    while True:
        try:
            tela_inicial()
            opcao = input("Escolha uma opção: ").strip()
            print('\n')
            if opcao == '1':
                visualizar_relatorios()
            elif opcao == '2':
                cadastrar_transacao()
            elif opcao == '3':
                editar_transacao_por_ID()
            elif opcao == '4':
                excluir_transacao()
            elif opcao == '5':
                consultar_transacao_por_ID()
            elif opcao == '0':
                print("Saindo do sistema. Até logo!")
                break
            else:
                print("Opção inválida. Por favor, tente novamente.\n") # enter para melhorar visualização
                input("Pressione Enter para continuar...\n") # enter para melhorar visualização
        except Exception as e:
            print(f"Erro: {e}. Por favor, tente novamente.")

def visualizar_relatorios():
    while True:
        try:
            print("\n--- Relatórios ---")
            print("1. Valor total das transações")
            print("2. Mostrar as 5 transações de maior valor (max)")
            print("3. Mostrar as 5 transações de menor valor (min)")
            print("4. Mostrar as 5 transações próximas da mediana (median)")
            print("5. Salvar todas as transações em relatório .txt")
            print("0. Voltar ao menu principal")
            print('\n')
            opcao = input("Escolha uma opção: ").strip()
            print('\n')
            if opcao == '1':
                calcular_total_transacoes()
            elif opcao == '2':
                mostrar_m5_transacoes('max')
            elif opcao == '3':
                mostrar_m5_transacoes('min')
            elif opcao == '4':
                mostrar_m5_transacoes('median')
            elif opcao == '5':
                data_consulta= datetime.now().strftime('%d/%m/%Y')
                texto = f"{'='*80}\nLISTA DE TRANSAÇÕES {' '*29}Dados consultados em {(data_consulta)}\n{'='*80}\n"
                for t in bd:
                    texto += f'UUID: {t["UUID"]} | Valor: R$ {str(t["valor"]).ljust(7)} | Categoria: {t["categoria"].capitalize()}\n'
                salvar_relatorio(texto, "todas_transacoes")
                input("Pressione Enter para voltar...")
            elif opcao == '0':
                break
            else:
                print("Opção inválida. Por favor, tente novamente.")
                input("Pressione Enter para voltar...") # usuário consegue visualizar que digitou algo errado, e só continua ao pressionar enter
        except Exception as e:
            print(f"Erro: {e}. Por favor, tente novamente.")

def salvar_relatorio(texto, nome_relatorio):
    try:
        opcao = input("Deseja salvar o relatório em arquivo? (s/n): ").strip().lower()

        if opcao != 's':
            print("Relatório **não foi salvo** em arquivo.")
            return  # sai da função sem salvar
        
        if not os.path.exists('./data'):
            os.makedirs('./data')
        caminho = f'./data/relatorio_{nome_relatorio}.txt'
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(texto)
        print(f'\nRelatório salvo em: {caminho}')
    except Exception as e:
        print(f'Erro ao salvar relatório: {e}')

def calcular_total_transacoes():
    try:
        # Valor total
        valor_total = sum(float(transacao['valor']) for transacao in bd)

        # Valor por categoria
        totais_por_categoria = defaultdict(float)
        categorias = []  # também usada para contagem depois

        for transacao in bd:
            categoria = transacao["categoria"]
            valor = float(transacao["valor"])
            totais_por_categoria[categoria] += valor
            categorias.append(categoria)

        # Quantidades por categoria
        total_qtd = len(bd)
        qtd_por_categoria = dict(Counter(categorias))

        # Média total
        media_total = valor_total / total_qtd if total_qtd else 0

        # Cabeçalho e linhas
        linhas_relatorio = []
        linhas_relatorio.append(f"{'Categoria':<15} {'Qtd':<15} {'Valor':<10} Média")
        linhas_relatorio.append("-" * 55)

        for categoria in totais_por_categoria:
            valor = totais_por_categoria[categoria]
            qtd = qtd_por_categoria.get(categoria, 0)
            media = valor / qtd if qtd else 0
            linhas_relatorio.append(
                f"{categoria.capitalize():<15} {qtd:<6} R$ {valor:>12,.2f}   R$ {media:>6,.2f}"
                .replace(",", "X").replace(".", ",").replace("X", ".")
            )

        linhas_relatorio.append("-" * 55)
        linhas_relatorio.append(
            f"{'Total Geral':<15} {total_qtd:<6} R$ {valor_total:>12,.2f}   R$ {media_total:>6,.2f}"
            .replace(",", "X").replace(".", ",").replace("X", ".")
        )

        conteudo_relatorio = '\n'.join(linhas_relatorio)

        nome_relatorio = "Total das transações"
        data_consulta = datetime.now().strftime('%d/%m/%Y')
        texto = (
            f"{'='*55}\n{nome_relatorio}\n{'='*55}\n"
            f"{conteudo_relatorio}\n"
            f"\n{'='*55}\nDados consultados em {data_consulta}"
        )

        # Impressão e salvamento
        print(f"\n{texto}\n")
        salvar_relatorio(texto, nome_relatorio)

    except Exception as e:
        print(f"Erro ao calcular o total: {e}")

    input("\nPressione Enter para voltar...")


def mostrar_m5_transacoes(m='max'):
    try:
        transacoes_ordenadas = sorted(bd, key=lambda x: x['valor'])
        
        if m == 'max':
            nome_relatorio = "Transações de maior valor"
            ultimas = transacoes_ordenadas[-5:][::-1]
        elif m == 'min':
            ultimas = transacoes_ordenadas[:5]
            nome_relatorio = "Transações de menor valor"
        elif m == 'median':
            nome_relatorio = "Transações próximas à mediana" #ajustado texto de media para mediana
            meio = len(transacoes_ordenadas) // 2
            if len(transacoes_ordenadas) % 2 == 0:
                mediana = (transacoes_ordenadas[meio - 1]['valor'] + transacoes_ordenadas[meio]['valor']) / 2
            else:
                mediana = transacoes_ordenadas[meio]['valor']

            print(f"Valor da mediana calculada: {mediana}")  # trecho adicionado para exibir o valor da mediana calculada
            transacoes_proximas_mediana = sorted(bd, key=lambda t: abs(t['valor'] - mediana))[:5]
            ultimas = transacoes_proximas_mediana
        else:
            print("Opção inválida para m.")
            return

        print(f"\n{'='*94}\n{nome_relatorio}\n{'='*94}\n")

        # inclusão das variáveis texto_arquivo e texto_tela para gerar os dados do arquivo txt
        texto_arquivo = '' 
        for i, transacao in enumerate(ultimas, 1):
            texto_tela = f"{i}. UUID: {transacao['UUID']} | Valor: R$ {transacao['valor']:.2f}  | Categoria: {transacao['categoria'].capitalize()}"
            texto_arquivo += (texto_tela+"\n")
            print(texto_tela)
                   
       # Salvar relatório consultado
        conteudo_relatorio = f"{'='*92}\n{nome_relatorio}\n{'='*92}\n{texto_arquivo}"
        data_consulta= datetime.now().strftime('%d/%m/%Y')
        conteudo_relatorio += '\n'*8 + f"Dados consultados em {(data_consulta)}\n{'='*92}"
        print('\n')
        salvar_relatorio(conteudo_relatorio, nome_relatorio)

    except Exception as e:
        print(f"Erro ao mostrar transações: {e}")
    input("\nPressione Enter para voltar...")
    
#def calcular_media(categoria=None):
#    try:
#        transacoes = [t for t in bd if t['categoria'] == categoria] if categoria else bd
#        if not transacoes:
#            print("Nenhuma transação encontrada.")
#            return None
#        media = sum(float(t['valor']) for t in transacoes) / len(transacoes)
#        print(f"Média: R$ {media:.2f}")
#        return media
#    except Exception as e:
#        print(f"Erro ao calcular média: {e}")
#        return None

def consultar_transacao_por_ID():
    while True:
        try:
            print("\n--- Consultar Transação por UUID ---")
            print("\nDigite 'voltar' para retornar ao menu anterior.")
            uuid_busca = input("\nInforme o UUID da transação: ").strip()
            if uuid_busca.lower() == 'voltar':
                return
            transacao = next((t for t in bd if t['UUID'] == uuid_busca.lower()), None)
            if not transacao:
                print("Transação não encontrada.")
                continue
            print("\nDados da transação informada:") # título tela consulta
            print(f"UUID: {transacao['UUID']} | Valor: R$ {transacao['valor']} | Categoria: {transacao['categoria']}\n")
            input("Pressione Enter para voltar...\n")
            return
        except Exception as e:
            print(f"Erro ao consultar transação: {e}")

def cadastrar_transacao():
    while True:
        try:
            print("\n--- Cadastrar Nova Transação ---")
            print("\nDigite 'voltar' para retornar ao menu anterior.")
            
            # VALOR
            valor = input("\nValor da transação: ").strip()
            print('\n')
            if remover_acentos(valor.lower()) == 'voltar':
                return
            valor =  valor.replace(",", ".")
            try:
                valor = float(valor)
                if valor <= 0:
                    print("Valor deve ser positivo.")
                    continue
            except ValueError:
                print("Valor inválido.")
                continue
            
            # CATEGORIA
            opcao_categ = settings.categorias_proporcao
            print("\nEscolha uma das categorias listadas abaixo ou digite 'voltar' para retornar")
            
            for categoria in opcao_categ.keys():
                print(f"- {categoria.capitalize()}")
            
            categoria = input("\nCategoria da transação:  ").strip()
            print('\n')
            if remover_acentos(categoria.lower()) == 'voltar':
                return

            # Remove acentos da categoria
            categoria_sem_acentos = remover_acentos(categoria.lower())
            
            # validação da categoria:
            if categoria_sem_acentos not in [remover_acentos(c.lower()) for c in opcao_categ.keys()]:
                print("Categoria inválida.")
                continue

            nova = {
                "UUID": str(uuid.uuid4()),
                "valor": round(valor, 2),
                "categoria": categoria_sem_acentos
            }

            bd.append(nova)
            
            # impressão na tela:
            salvar_json(bd, './data', 'transactions.json')
            print("\nTransação cadastrada:")
            
            for k, v in nova.items():
                print(k.capitalize(), str(v).capitalize().replace('.',','), sep=" ==> ")

            input("\nPressione Enter para voltar...\n")
            return

        except Exception as e:
            print(f"Erro ao cadastrar transação: {e}")

def editar_transacao_por_ID():
    while True:
        try:
            print("\n--- Editar Transação ---")
            print("\nPara editar, digite o UUID da transação.") 
            print("Digite 'voltar' para retornar ao menu anterior.")
            uuid_busca = input("\nUUID: ").strip()
            if remover_acentos(uuid_busca.lower()) == 'voltar':
                return

            transacao = next((t for t in bd if t['UUID'] == uuid_busca.lower()), None)  # fara a busca do UUID preenchido pelo usuario, em letras minusculas, e compara com o existente em bd
            if not transacao:
                print("\nTransação não encontrada.")
                continue

            print(f"Valor atual: R$ {transacao['valor']:.2f} | Categoria atual: {transacao['categoria']}")

            alterado = False

            # VALOR
            while True:
                novo_valor = input("\nDigite o novo valor (ou Enter para manter o atual): ").strip()
                if not novo_valor:
                    break
                
                novo_valor = novo_valor.replace(",", ".")
                try:
                    novo_valor_float = float(novo_valor)
                    if novo_valor_float > 0:
                        transacao['valor'] = round(novo_valor_float, 2)
                        alterado = True
                        print("\nValor alterado com sucesso")
                        break
                    else:
                        print("\nO valor deve ser maior que zero.")
                except ValueError:
                    print("\nValor inválido. Digite apenas números.")

            # CATEGORIA
            opcao_categ = settings.categorias_proporcao
            print('\nEscolha uma das categorias abaixo ou digite Enter para manter a categoria atual')
            
            for categoria in opcao_categ.keys():
                print(f"- {categoria.capitalize()}")
            
            while True:
                nova_categoria = input("\nNova categoria (ou Enter para manter a atual): ").strip()
                if not nova_categoria:
                    break  # mantém a atual e sai do loop

                # validação da categoria:    
                categoria_formatada = remover_acentos(nova_categoria.lower())
                categorias_validas = [remover_acentos(cat.lower()) for cat in opcao_categ.keys()]

                if categoria_formatada not in categorias_validas:
                    print("Categoria inválida. Tente novamente.")
                    continue  # volta para tentar de novo
                else:
                    transacao['categoria'] = categoria_formatada
                    alterado = True
                    print("\nCategoria alterada com sucesso.")
                    break  # categoria válida, sai do loop
                    
            # SALVAMENTO
            if alterado:
                print('\n')
                salvar_json(bd, './data', 'transactions.json')
                print("\nTransação atualizada:")
                for k, v in transacao.items():
                    print(k.capitalize(), str(v).capitalize().replace('.',','), sep=" ==> ")

            else:
                print("\nNenhuma alteração realizada.")

            input("\nPressione Enter para voltar...\n")
            return

        except Exception as e:
            print(f"\nErro ao editar: {e}")

def excluir_transacao():
    while True:
        try:
            print("\n--- Excluir Transação ---")
            print("\nPara excluir, digite o UUID da transação.")
            print("Digite 'voltar' para retornar ao menu anterior.")
            uuid_busca = input("\nUUID: ").strip()
            if uuid_busca.lower() == 'voltar':
                return
            idx = next((i for i, t in enumerate(bd) if t['UUID'] == uuid_busca.lower()), None) # deixa valores em minusculas antes de comparar
            if idx is None:
                print("Transação não encontrada.")
                continue
            print(f"Valor: R$ {bd[idx]['valor']} | Categoria: {bd[idx]['categoria']}")
            confirm = input("\nConfirma exclusão? (s/n): ").strip().lower()
            if confirm == 's':
                bd.pop(idx)
                print('\n')
                salvar_json(bd, './data', 'transactions.json')
                print("\nExcluída com sucesso.")
                input("\nPressione Enter para voltar...\n")
                return
            elif confirm in ['n', 'voltar']:
                print("\nExclusão cancelada.")
                input("\nPressione Enter para voltar...\n") # adicionada interação para apresentação da msg ao usuario
                return
            else:   # inclusão para tratar quando entrada diferent de 's' ou 'n'
                print("\nOpção inválida. Digite apenas 's' para confirmar ou 'n' para cancelar.")
        except Exception as e:
            print(f"Erro ao excluir: {e}")

# -----------------------
# MAIN SCRIPT
# -----------------------
if __name__ == "__main__":
    print(os.path.abspath('.'))
    if not os.path.exists('./data/transactions.json'):
        criar_bd()
    bd = load_bd()
    os.system('cls' if os.name == 'nt' else 'clear')
    run()
