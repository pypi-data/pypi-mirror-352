# 📦 Gestão de Stocks

**Sistema modular para gestão de armazéns e mercadorias, com análise de margens, alertas e relatórios.**

Este pacote permite:
- Criar e gerir múltiplos armazéns com capacidade e localização
- Adicionar, remover e transferir mercadorias
- Calcular valores médios, margens de lucro e emitir alertas automáticos
- Gerar logs e visualizações gráficas

---

## 📦 Instalação

```bash
pip install ProjetoUmMADS==0.0.1
```

## Adição de armazéns
armas =  []

armazem_A = Armazem("Armazém A", 1000, Lat=42.1, Lon=-8.6)
armazem_B = Armazem("Armazém B", 1500, Lat=42.1, Lon=-8.6)
armazem_C = Armazem("Armazém C", 2000, Lat=42.1, Lon=-8.6)

## Exemplos de erros e avisos
armazem_D = Armazem("Armazém C", 260, Lat=42.1, Lon=-8.6)

## Adição de dados
armazem_A.adicionar_mercadoria("Arroz", 30, 1.2, 2.0)
armazem_A.adicionar_mercadoria("Feijão", 20, 1.5, 1.8)
armazem_B.adicionar_mercadoria("Açúcar", 50, 1.0, 1.5)
armazem_C.adicionar_mercadoria("Sal", 40, 0.8, 1.0)

## Exemplos de erros e avisos
armazem_C.adicionar_mercadoria("café", 50, 1.0, 1.5)
armazem_C.adicionar_mercadoria("café", -10, .8, 1.5)

## Remoção de mercadoria
armazem_A.remover_mercadoria("Latas", 10)

## Transferência entre armazéns
armazem_A.transferir_mercadoria(armazem_B, "Feijão", 10)
armazem_B.transferir_mercadoria(armazem_C, "Açúcar", 20)

Armazem.listar_armazens()

## Criar armazém
armazem_A = Armazem("A", 1000, 0, 0)

## Adicionar mercadoria para atingir 90%
armazem_A.adicionar_mercadoria("Latas", 90, 1.5, 0.3)

## Verificar capacidade
armazem_A.verificar_capacidade()

## Mostrar logs
armazem_A.mostrar_logs()

armazem_A.custo_medio_produto("Latas")

## Adicionando mercadoria com preço de venda
armazem_A.adicionar_mercadoria("Latas", 50, 2.0, 0.5)  # Preço de venda = 2.0€
armazem_A.adicionar_mercadoria("Latas", 50, 3.0, 0.5)  # Preço de venda = 3.0€
armazem_B.adicionar_mercadoria("Latas", 50, 3.0, 0.5)  # Preço de venda = 3.0€

## Calcular o valor médio de venda
armazem_A.valor_medio_venda_produto("Latas")

## Adicionando mercadorias com preços de custo e de venda
armazem_A.adicionar_mercadoria("Latas", 10, 2.0, 0.5)  # Preço de custo = 2.0€
armazem_A.stock["Latas"]["preço_venda"] = 3.0  # Preço de venda = 3.0€

armazem_A.adicionar_mercadoria("Peras", 10, 1.0, 0.3)  # Preço de custo = 1.0€
armazem_A.stock["Peras"]["preço_venda"] = 5.5  # Preço de venda = 5.5€

## Listar produtos com maior margem de lucro
armazem_A.listar_produtos_maior_margem()

## Adicionando mercadorias
armazem_A.adicionar_mercadoria("Latas", 200, 2.0, 0.5)  # 40 unidades
armazem_B.adicionar_mercadoria("Peras", 200, 1.0, 0.3)  # 30 unidades

## Verificar alertas de capacidade
armazem_A.alerta_quase_cheio()
armazem_A.alerta_quase_vazio()

## Remover mercadoria para verificar alerta de quase vazio
armazem_B.remover_mercadoria("Peras", 300)

## Verificar alertas de capacidade novamente
armazem_A.alerta_quase_cheio()
armazem_A.alerta_quase_vazio()
armazem_B.alerta_quase_cheio()
armazem_B.alerta_quase_vazio()

armazem_A.listar_produtos_maior_margem()
armazem_A.grafico_evolucao_margens()

Armazem.listar_armazens_mais_lucrativos()