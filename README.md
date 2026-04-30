# gerar_molduras_a_partir_de_feicoes
Aplicação de processing tools do Qgis para emissão de molduras a partir de cada feição da camada.

# 🧭 Moldura por Feição (QGIS Processing Tool)

Ferramenta de geoprocessamento para geração automática de molduras cartográficas por feição, respeitando escala, dimensão do layout e divisão automática em múltiplas folhas.

---

## 🎯 Objetivo

Automatizar a geração de molduras para plantas técnicas (ex: loteamentos, servidões, imóveis), eliminando o processo manual de:

* Ajuste de escala
* Enquadramento da feição
* Divisão em múltiplas folhas
* Criação de grids

---

## ⚙️ Funcionamento Geral

A ferramenta:

1. Lê cada feição da camada de entrada
2. Calcula sua extensão (bounding box)
3. Converte a escala e dimensões do layout (cm) para unidades reais (metros)
4. Define um grid de molduras compatível com a escala
5. Aplica sobreposição (opcional)
6. Centraliza o conjunto de molduras na feição
7. Gera uma ou múltiplas molduras por feição
8. Mantém os atributos originais + adiciona campos de controle

---

## 🔄 Fluxo do Algoritmo

```
Entrada (camada de polígonos)
        ↓
Cálculo do bounding box por feição
        ↓
Conversão escala + dimensão (cm → metros)
        ↓
Definição do tamanho da moldura (ground_w / ground_h)
        ↓
Cálculo do grid (cols x rows)
        ↓
Aplicação de sobreposição (opcional)
        ↓
Centralização do grid na feição
        ↓
Geração das molduras (retângulos)
        ↓
Filtro por interseção
        ↓
Saída final (camada de molduras)
```

---

## 📥 Inputs (Parâmetros)

| Parâmetro                  | Tipo             | Descrição                              |
| -------------------------- | ---------------- | -------------------------------------- |
| Camada de entrada          | Vetor (Polígono) | Feições que serão enquadradas          |
| Escala                     | Decimal          | Escala cartográfica (ex: 1000, 750.5)  |
| Largura do mapa (cm)       | Decimal          | Largura da área útil do mapa no layout |
| Altura do mapa (cm)        | Decimal          | Altura da área útil do mapa no layout  |
| Usar sobreposição          | Booleano         | Ativa sobreposição entre molduras      |
| Percentual de sobreposição | Decimal          | Ex: 0.1 = 10%                          |

---

## 📤 Output

Camada vetorial (polígonos) contendo as molduras geradas.

### 📊 Atributos da saída:

* ✔ Todos os atributos da camada de entrada
* ✔ Campos adicionais:

| Campo        | Descrição                 |
| ------------ | ------------------------- |
| id_feat      | ID da feição original     |
| folha        | Número da folha           |
| total_folhas | Total de folhas da feição |
| col          | Coluna no grid            |
| row          | Linha no grid             |

---

## 🧠 Lógica Técnica

### 📐 Conversão de escala

```
ground_width  = (largura_cm / 100) * escala
ground_height = (altura_cm / 100) * escala
```

---

### 🔁 Sobreposição

Quando ativada:

```
step = tamanho_moldura - (tamanho_moldura * percentual)
```

Resultado:

* Molduras se sobrepõem
* Evita cortes ruins na feição

---

### 🎯 Centralização

A moldura é centralizada com base em:

* `pointOnSurface()` da geometria
* Dimensão total do grid

Resultado:

* Melhor enquadramento
* Layout mais equilibrado

---

## 🚀 Casos de Uso

* Loteamentos urbanos
* Faixas de servidão (linhas de transmissão)
* Imóveis rurais
* APPs e áreas ambientais
* Plantas técnicas para cartório
* Geração de Atlas no QGIS

---

## ⚠️ Boas Práticas

* Use projeções em metros (ex: UTM)
* Evite escala zero ou negativa
* Recomenda-se sobreposição entre 5% e 20%
* Certifique-se que o tamanho do layout no QGIS corresponde aos parâmetros usados

---

## 🔥 Limitações

* Não considera rotação da feição (ainda)
* Não gera layout automaticamente (pode ser integrado)
* Não ajusta escala dinamicamente por feição

---

## 🚧 Próximas Melhorias (Sugestões)

* Rotação automática da moldura
* Geração automática de Layout + Atlas
* Exportação direta para PDF
* Numeração inteligente de folhas (ex: 01/05)
* Ajuste automático de escala por feição

---

## 🧩 Integração Recomendada

Essa ferramenta foi projetada para ser usada com:

* QGIS Layout Manager
* Atlas (Data-driven pages)
* Exportação em lote de PDFs

---

## 💡 Resumo

Essa ferramenta transforma um processo manual demorado em:

👉 1 clique → molduras prontas
👉 Escala respeitada
👉 Feição centralizada
👉 Pronto para produção

---

## 👨‍💻 Autor

Desenvolvido para automação de processos de geoprocessamento aplicados à regularização fundiária e produção cartográfica.

---
