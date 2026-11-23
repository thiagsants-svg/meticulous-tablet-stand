# Guia para o agente (Claude Code ou outro)

Este repositório gera, por código, um suporte de tablet que pendura na espresso **Meticulous**. Quem clonou quer adaptar o suporte às medidas e à impressora **dele**. Responda na língua da pessoa. Os comentários do código estão em português.

## Antes de gerar, pergunte e confirme
1. **Lado**: esquerdo (`gerar_suporte.py`) ou direito, na frente da tela e do botão (`gerar_suporte_dir.py`).
2. **Tablet**: modelo, largura × altura × espessura, se usa **capa** (a espessura com capa é a que vale), se fica **em pé ou deitado**, e onde fica a porta USB.
3. **Máquina**, medida com paquímetro:
   - profundidade do topo onde o gancho pega (`coluna=`, referência 50,6);
   - no lado direito, o botão: topo e base abaixo do topo da máquina e quanto ele sai da face (`BOTAO_TOPO/BASE/SAI` em `gerar_suporte_dir.py`, referência 65,07 / 113,08 / 34,13).
4. **Altura**: quanto a base do tablet fica abaixo do topo da máquina (`base=`; 190 com o tablet em pé, 142 deitado). Mostre quanto o topo do tablet passa da máquina.
5. **Impressora, material e bico**. As folgas abaixo foram medidas em PETG numa Anycubic Kobra S1 com bico 0,4. Outra impressora pode pedir um cupom de teste antes.

## Geometria e convenções (leia antes de mexer)
- O perfil é desenhado no plano **XY**, com **X = profundidade** (frente → máquina) e **Y = altura**, e extrudado em **Z = largura**.
- O tablet encosta numa linha a 10° da vertical: `f(y) = 15.3 + inc*(y-4)`.
- O vão do degrau é a espessura / cos 10° + 0,5 (`vao=`).
- **Duas peças**: o **quadro** (imprime deitado, com o perfil na mesa) e a **régua** (imprime deitada sobre o piso). Elas se unem por um **rabo de andorinha de 20°**:
  - a língua fica no quadro e o canal na régua;
  - o canal é fechado numa ponta, que serve de **batente**.
- **Lado direito**:
  - A régua é a do lado esquerdo **espelhada em Z** (`z → 35 − z`).
  - **No lado direito o quadro fica junto à cabeça e a régua vai para FORA da máquina.** Comentários antigos em `gerar_suporte_dir.py` e `gerar_regua_deitado.py` dizem "fora/dentro" trocado. `ext_fora` em `gerar_regua_deitado.py` foi parar em cima do grupo, por isso aquela régua não deu certo.
  - O quadro direito faz uma janela em volta do botão. `conferir()` imprime a folga mínima até o botão, que nunca pode ser 0.
- **Compensação de caimento** (a régua cede com o peso):
  - `inclina=` dobra o piso a partir do bloco do encaixe;
  - `gerar_regua_reta.py` gira a régua inteira em volta de um pivô logo depois do bloco e mantém o canal e o topo do bloco onde o quadro espera (a régua parece reta).
- **Saídas**: as funções `G.regua(..., com_canal=False, passa_cabo=False, ext_fora=...)` e `G.canal_regua()` são reutilizadas pelas variantes.

## Folgas que já foram testadas (PETG, Kobra S1, bico 0,4)
| Item | Resultado |
|---|---|
| Rabo de andorinha 0,30 por lado no curso + 0,15 nos últimos 8 mm | frouxo |
| 0,20 / 0,10 | ainda frouxo |
| **0,10 no curso / 0,00 nos últimos 8 mm, camada 0,08** | **firme** (use este) |
| Gancho: medida + 0,25 por lado (`folga_col=`) | encaixou na máquina |
| Caimento com o tablet em pé (149 de largura, ~470 g), encaixe frouxo | 3° sem compensação; 2,5° deixou 1° |
| Régua reta de 3,5° com o encaixe firme | −2° (passou); o encaixe firme cede só ~1,5° |

Trate tudo o que não está nesta tabela como **sem teste** e diga isso à pessoa.

## Scripts
| Script | O que faz |
|---|---|
| `gerar_suporte.py` | lado esquerdo e funções comuns: `vao= labio= folga= justo= coluna= folga_col=` |
| `gerar_suporte_dir.py` | lado direito: `base= furo= ponte= n_furos= inclina= folga_curso= folga_fim=` |
| `reguas_marcadas.py` | réguas com o ângulo gravado na frente: `graus=2.5,5` |
| `gerar_regua_deitado.py` | régua longa para o tablet deitado (ver o aviso de fora/dentro acima) |
| `gerar_deitado_v2.py` | quadro mais alto (`base=142`) + régua; `marca=0`, `so=regua` |
| `gerar_regua_reta.py` | régua reta com o ângulo no encaixe: `graus=` |
| `gerar_regua_adaptador.py` | régua com túnel por baixo para o adaptador USB-C de 90° (versão anterior, mais funda) |
| `gerar_regua_cabo_tras.py` | régua com vão para o adaptador USB-C de 90° e o cabo saindo por trás: `graus= porta=30,100 folga_frente= folga_topo= colar= a_plugue=` |
| `gerar_3mf.py` | monta o 3MF da Kobra S1 com o perfil de `fatiador/`: `lado= ver= so= sup=1 x:chave=valor` |
| `fatiar.py` | fatia pela linha de comando do Anycubic Slicer Next (caminho do .exe no topo) e resume tempo, gramas e tipos de linha |
| `previa*.py` | imagens de conferência (`previa.py` compara com o STL original, que não está no repositório: coloque-o em `origem/` se tiver) |

## Como trabalhar aqui
- Rode com `python -I script.py chave=valor`. Os parâmetros entram por `chave=valor`.
- Depois de gerar, **confira**:
  - `is_watertight` das malhas;
  - a interferência entre quadro e régua, montada e deslizando (`gerar_regua_deitado.montagem`);
  - cortes transversais em matplotlib com o tablet desenhado por cima.
- Ao exportar uma peça girada, limpe a malha no manifold3d (`gerar_regua_adaptador.limpa`). Gravado em float32, o STL juntava vértices e criava faces de área zero.
- Mudar só a régua (o canal) deixa reaproveitar o quadro já impresso. Prefira isso quando der.
- Para outra impressora, entregue STL e diga as configurações: camada 0,08 para a régua (o canal fica mais fiel), sem aba, suporte só onde o script indicar.
