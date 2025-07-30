# Gestao de Stocks

**Sistema modular para gestao de armazens e mercadorias, com analise de margens, alertas e relatorios.**

Este pacote permite:
- Criar e gerir multiplos armazens com capacidade e localizacao
- Adicionar, remover e transferir mercadorias
- Calcular valores medios, margens de lucro e emitir alertas automaticos
- Gerar logs e visualizacoes graficas

---

## Instalacao

```bash
pip install ProjetoUmMADS
```

## Adicao de armazens
```python
armas =  []

armazem_A = Armazem("Armazem A", 1000, Lat=42.1, Lon=-8.6)
armazem_B = Armazem("Armazem B", 1500, Lat=42.1, Lon=-8.6)
armazem_C = Armazem("Armazem C", 2000, Lat=42.1, Lon=-8.6)
```

## Exemplos de erros e avisos
```python
armazem_D = Armazem("Armazem C", 260, Lat=42.1, Lon=-8.6)
```

## Adicao de dados
```python
armazem_A.adicionar_mercadoria("Arroz", 30, 1.2, 2.0)
armazem_A.adicionar_mercadoria("Feijao", 20, 1.5, 1.8)
armazem_B.adicionar_mercadoria("Acucar", 50, 1.0, 1.5)
armazem_C.adicionar_mercadoria("Sal", 40, 0.8, 1.0)
```

## Exemplos de erros e avisos
```python
armazem_C.adicionar_mercadoria("cafe", 50, 1.0, 1.5)
armazem_C.adicionar_mercadoria("cafe", -10, .8, 1.5)
```

## Remocao de mercadoria
```python
armazem_A.remover_mercadoria("Latas", 10)
```

## Transferencia entre armazens
```python
armazem_A.transferir_mercadoria(armazem_B, "Feijao", 10)
armazem_B.transferir_mercadoria(armazem_C, "Acucar", 20)

Armazem.listar_armazens()
```

## Criar armazem
```python
armazem_A = Armazem("A", 1000, 0, 0)
```

## Adicionar mercadoria para atingir 90%
```python
armazem_A.adicionar_mercadoria("Latas", 90, 1.5, 0.3)
```

## Verificar capacidade
```python
armazem_A.verificar_capacidade()
```

## Mostrar logs
```python
armazem_A.mostrar_logs()

armazem_A.custo_medio_produto("Latas")
```

## Adicionando mercadoria com preco de venda
```python
armazem_A.adicionar_mercadoria("Latas", 50, 2.0, 0.5)  # Preco de venda = 2.0
armazem_A.adicionar_mercadoria("Latas", 50, 3.0, 0.5)  # Preco de venda = 3.0
armazem_B.adicionar_mercadoria("Latas", 50, 3.0, 0.5)  # Preco de venda = 3.0
```

## Calcular o valor medio de venda
```python
armazem_A.valor_medio_venda_produto("Latas")
```

## Adicionando mercadorias com precos de custo e de venda
```python
armazem_A.adicionar_mercadoria("Latas", 10, 2.0, 0.5)  # Preco de custo = 2.0
armazem_A.stock["Latas"]["preco_venda"] = 3.0  # Preco de venda = 3.0

armazem_A.adicionar_mercadoria("Peras", 10, 1.0, 0.3)  # Preco de custo = 1.0
armazem_A.stock["Peras"]["preco_venda"] = 5.5  # Preco de venda = 5.5
```

## Listar produtos com maior margem de lucro
```python
armazem_A.listar_produtos_maior_margem()
```

## Adicionando mercadorias
```python
armazem_A.adicionar_mercadoria("Latas", 200, 2.0, 0.5)
armazem_B.adicionar_mercadoria("Peras", 200, 1.0, 0.3)
```

## Verificar alertas de capacidade
```python
armazem_A.alerta_quase_cheio()
armazem_A.alerta_quase_vazio()
```

## Remover mercadoria para verificar alerta de quase vazio
```python
armazem_B.remover_mercadoria("Peras", 300)
```

## Verificar alertas de capacidade novamente
```python
armazem_A.alerta_quase_cheio()
armazem_A.alerta_quase_vazio()
armazem_B.alerta_quase_cheio()
armazem_B.alerta_quase_vazio()

armazem_A.listar_produtos_maior_margem()
armazem_A.grafico_evolucao_margens()

Armazem.listar_armazens_mais_lucrativos()
```