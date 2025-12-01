from tela_game_over import TelaGameOver
from tela_game_win import TelaVitoria
from tela_menu import TelaMenu

import pygame
import random
import sys


# --------------------------- Configuração ---------------------------
LARGURA_TELA = 830
ALTURA_TELA = 590
COR_FUNDO = (223, 176, 176)
COR_CABECALHO = (244, 221, 222)
COR_BORDA = (168, 163, 163)
COR_BORDA_LETRA = ('#494646')

COR_TEXTO = (0, 0, 0)
CORES_TEXTO = ["#6be433", '#ff5757', '#8c52ff', '#ffdf55',
               '#4244f4', '#eb31ef', '#30df96', '#2cbddd',
               '#ff9221', '#f64283', '#35af63', '#7f24af']

COR_PALAVRA_COMPLETA = (100, 220, 100)
COR_LETRA_FIXA = (220, 220, 220)
COR_LETRA_ATUAL = (255, 200, 60)
COR_LETRA_ERRADA = (220, 100, 100)

MARGEM_ESQUERDA = 18
LARGURA_COLUNA = 120
ESPACAMENTO = 40

GRID_COLS = 5
GRID_ROWS = 6

CELL_PADDING = 4

FPS = 60

# --------------------------- Gerenciador de Palavras ---------------------------


class GerenciadorPalavras:
    def __init__(self, palavras_ativas=None):
        if palavras_ativas is None:
            palavras_ativas = ['bravo', 'clima', 'festa', 'hotel']
        palavras_ativas = [p.lower() for p in palavras_ativas if len(p) == 5]
        self.palavras = palavras_ativas
        self.cor_palavras = {}
        self.completadas = {p: False for p in self.palavras}

        # Sistema de liberação progressiva
        self.liberadas = {p: set([1]) for p in self.palavras}

        # Rastrear progresso de cada palavra
        self.progresso = {p: 0 for p in self.palavras}
        self.letras_colocadas = {p: {} for p in self.palavras}

    def get_letras_permitidas(self):
        """Retorna todas as letras que podem ser sorteadas no momento"""
        letras_permitidas = []

        for palavra in self.palavras:
            if self.completadas[palavra]:
                continue

            for pos in self.liberadas[palavra]:
                letra = palavra[pos - 1]
                if pos not in self.letras_colocadas[palavra]:
                    letras_permitidas.append((letra, palavra, pos))

        return letras_permitidas

    def liberar_posicao_apos_letra(self, letra, palavra_origem, pos_origem):
        """Libera posições baseado no progresso"""
        letra = letra.lower()

        # Registra a letra colocada
        self.letras_colocadas[palavra_origem][pos_origem] = letra

        # Atualiza o progresso máximo desta palavra
        if pos_origem > self.progresso[palavra_origem]:
            self.progresso[palavra_origem] = pos_origem

        # Encontra o progresso MÁXIMO entre todas as palavras
        progresso_maximo_global = max(self.progresso.values())

        # PARA CADA PALAVRA: determina quais posições devem estar liberadas
        for palavra in self.palavras:
            if self.completadas[palavra]:
                continue

            novas_posicoes_liberadas = set()
            novas_posicoes_liberadas.add(1)

            # Libera até progresso_maximo_global + 1
            limite_para_esta_palavra = min(progresso_maximo_global + 1, 5)

            for pos in range(2, limite_para_esta_palavra + 1):
                if palavra == palavra_origem or self.progresso[palavra] >= pos - 1:
                    novas_posicoes_liberadas.add(pos)

            self.liberadas[palavra] = novas_posicoes_liberadas

    def encontrar_palavra_posicao_para_letra(self, letra, coluna):
        """Encontra qual palavra e posição corresponde a esta letra na coluna dada"""
        letra = letra.lower()
        posicao_alvo = coluna

        for palavra in self.palavras:
            if (not self.completadas[palavra] and
                posicao_alvo in self.liberadas[palavra] and
                palavra[posicao_alvo - 1] == letra and
                    posicao_alvo not in self.letras_colocadas[palavra]):
                return (palavra, posicao_alvo)

        return (None, None)

    def verificar_palavra_formada(self, letras_linha):
        """Verifica se a sequência de 5 letras corresponde a alguma palavra ativa"""
        s = ''.join(letras_linha).lower()
        for p in self.palavras:
            if s == p and not self.completadas[p]:
                # posicoes_preenchidas = set(self.letras_colocadas[p].keys())
                # if posicoes_preenchidas == set(range(1, 6)):
                return p
        return None

    def marcar_palavra_completa(self, palavra):
        """Marca uma palavra como completa"""
        self.completadas[palavra] = True
        self.liberadas[palavra] = set()

# --------------------------- Gerenciador de Letras ---------------------------


class LetraCaindo:
    def __init__(self, char, palavra_origem, pos_origem, col, row_px, velocidade=80, cor=COR_LETRA_ATUAL):
        self.char = char
        self.palavra_origem = palavra_origem
        self.pos_origem = pos_origem
        self.col = col
        self.y = row_px
        self.vel = velocidade
        self.fixa = False
        self.cor = cor


class GerenciadorLetras:
    def __init__(self, x, y, largura, altura, gerenciador_palavras):
        self.x = x
        self.y = y
        self.largura = largura+3
        self.altura = altura+3
        self.gp: GerenciadorPalavras = gerenciador_palavras
        self.num_palavras = len(self.gp.palavras)

        self.cell_w = largura // GRID_COLS
        self.cell_h = altura // GRID_ROWS

        self.grid = [[None for _ in range(GRID_COLS)]
                     for _ in range(self.num_palavras)]
        self.grid_cores = [[None for _ in range(GRID_COLS)]
                           for _ in range(self.num_palavras)]
        self.atual = None
        self.tempo_anterior = pygame.time.get_ticks()
        self.pausado = False
        self.palavra_em_pausa = None
        self.pausa_inicio = None
        self.ultima_linha_valida = GRID_ROWS - 1

        self.sequencia_de_letras = []
        self.proximo_indice_letra = 0
        self.gerar_seuquencia_de_letras()

        self.gerar_nova_letra()

    def gerar_seuquencia_de_letras(self):
        self.num_palavras = len(self.gp.palavras)
        random.shuffle(self.gp.palavras)

        cores = [CORES_TEXTO[i] for i in range(self.num_palavras)]

        for palavra, cor in zip(self.gp.palavras, cores):
            self.gp.cor_palavras[palavra] = cor

        positions = [[False for _ in range(GRID_COLS)]
                     for _ in range(self.num_palavras+1)]
        positions[0] = [True] * GRID_COLS

        for i in range(self.num_palavras):
            # somente as letras da palavra i
            valides = [idx for idx, p in enumerate(positions[i]) if p]

            pos = random.choice(valides)

            self.sequencia_de_letras.append(
                (self.gp.palavras[i][pos], i, pos, cores[i]))
            positions[i][pos] = False
            positions[i+1][pos] = True

            while any(positions[i]):
                valides = [
                    (k, l)
                    for k in range(i, min(i+4, self.num_palavras)) for l in range(GRID_COLS)
                    if positions[k][l]
                ]
                if valides:
                    k, l = random.choice(valides)
                    self.sequencia_de_letras.append(
                        (self.gp.palavras[k][l], k, l, cores[k]))
                    positions[k][l] = False
                    positions[k+1][l] = True

    def gerar_nova_letra(self):
        """Gera uma nova letra baseada nas letras permitidas - SEM RESTRIÇÕES de coluna"""

        letra, palavra_origem, pos_origem, cor = self.sequencia_de_letras[
            self.proximo_indice_letra % (GRID_COLS*len(self.gp.palavras))]
        self.proximo_indice_letra += 1
        # SEM RESTRIÇÕES - começa em qualquer coluna
        # start_x_col = random.randint(0, GRID_COLS - 1)
        # começar pela coluna 2
        start_x_col = 2
        self.atual = LetraCaindo(
            letra, palavra_origem, pos_origem, start_x_col, self.y + 10, cor=cor)

    def mover_letra_esquerda(self):
        """Move para esquerda - SEM RESTRIÇÕES"""
        if not self.atual or self.pausado:
            return
        if self.atual.col > 0:
            self.atual.col -= 1

    def mover_letra_direita(self):
        """Move para direita - SEM RESTRIÇÕES"""
        if not self.atual or self.pausado:
            return
        if self.atual.col < GRID_COLS - 1:
            self.atual.col += 1

    def get_letras_linha_inferior(self):
        """Retorna lista de letras na última linha"""
        linha = []
        r = self.ultima_linha_valida
        for c in range(GRID_COLS):
            val = self.grid[r][c]
            if val is None:
                return []
            linha.append(val)
        return linha

    def pausar_por_palavra(self, palavra):
        self.pausado = True
        self.palavra_em_pausa = palavra
        self.pausa_inicio = pygame.time.get_ticks()

    def update(self, tempo_atual_ms):
        all_completas = all(self.gp.completadas.values())
        any_0 = any(self.grid[0])
        check = not self.atual and not all_completas and not any_0
        if self.pausado:
            if pygame.time.get_ticks() - self.pausa_inicio >= 1000:
                self.pausado = False
                self.palavra_em_pausa = None
                self.pausa_inicio = None
            return

        dt = (tempo_atual_ms - self.tempo_anterior) / 1000.0
        self.tempo_anterior = tempo_atual_ms

        if check and not self.atual and not self.pausado:
            self.gerar_nova_letra()
            return

        if all_completas or any_0:
            return

        # Movimento da letra atual - SEM RESTRIÇÕES
        self.atual.y += self.atual.vel * dt

        # Verifica colisão com o fundo
        bottom_y = self.y + self.altura - self.cell_h/2
        if self.atual.y >= bottom_y:
            self.fixar_atual_na_coluna(self.atual.col)
            return

        # Verifica colisão com outras letras
        row = int((self.atual.y - self.y) // self.cell_h)
        if row >= GRID_ROWS - 1:
            self.fixar_atual_na_coluna(self.atual.col)
            return
        if self.grid[row+1][self.atual.col] is not None:
            self.fixar_atual_na_coluna(self.atual.col)
            return

    def fixar_atual_na_coluna(self, col):
        """Fixa a letra atual na coluna especificada - SEM VERIFICAÇÕES"""
        if not self.atual:
            return

        # Encontra a primeira linha livre de baixo pra cima
        for r in range(GRID_ROWS-1, -1, -1):
            if self.grid[r][col] is None:
                self.grid[r][col] = self.atual.char
                self.grid_cores[r][col] = self.atual.cor

                # Informa ao gerenciador sobre a letra fixada
                coluna_humana = col + 1
                palavra, posicao = self.gp.encontrar_palavra_posicao_para_letra(
                    self.atual.char, coluna_humana
                )

                if palavra and posicao:
                    self.gp.liberar_posicao_apos_letra(
                        self.atual.char, palavra, posicao)

                break

        self.atual = None

    def remover_linha(self, row):
        """Remove a linha especificada e desloca tudo para baixo"""
        for r in range(row, 0, -1):
            for c in range(GRID_COLS):
                self.grid[r][c] = self.grid[r - 1][c]
                self.grid_cores[r][c] = self.grid_cores[r - 1][c]

        # Limpa a primeira linha
        for c in range(GRID_COLS):
            self.grid[0][c] = None
            self.grid_cores[0][c] = None

    def remover_linha_inferior(self):
        """Remove a última linha e desloca tudo para baixo"""
        self.remover_linha(self.ultima_linha_valida)

    def desenhar(self, tela):
        """Desenha o grid e as letras"""
        font = pygame.font.SysFont("Arial", 40, bold=True)

        # Função auxiliar para desenhar texto com borda grossa
        def desenhar_texto_com_borda(surface, texto, fonte, cor_texto, cor_borda, grossura, posicao):
            """Desenha texto com borda grossa de forma prática"""
            texto_surf = fonte.render(texto, True, cor_texto)
            texto_borda_surf = fonte.render(texto, True, cor_borda)
            texto_rect = texto_surf.get_rect(center=posicao)

            # Gera offsets automaticamente para borda grossa
            offsets = []
            for dx in range(-grossura, grossura + 1):
                for dy in range(-grossura, grossura + 1):
                    if dx != 0 or dy != 0:
                        offsets.append((dx, dy))

            # Desenha a borda
            for dx, dy in offsets:
                surface.blit(texto_borda_surf,
                             (texto_rect.x + dx, texto_rect.y + dy))

            # Desenha o texto principal
            surface.blit(texto_surf, texto_rect)
            return texto_rect

        # Desenha células do grid
        for c in range(GRID_COLS):
            for r in range(GRID_ROWS):
                rect = pygame.Rect(
                    self.x + c * self.cell_w + CELL_PADDING,
                    self.y + r * self.cell_h + CELL_PADDING,
                    self.cell_w - 2*CELL_PADDING,
                    self.cell_h - 2*CELL_PADDING,
                )
                val = self.grid[r][c]
                if val is not None:
                    pygame.draw.rect(tela, (COR_CABECALHO), rect)
                    # borda da caixa letra:
                    pygame.draw.rect(tela, (COR_BORDA),
                                     rect, 4)  # Borda de 2px

                    # Usa a função auxiliar para desenhar com borda grossa
                    desenhar_texto_com_borda(
                        tela, val.upper(), font,
                        # Cor do texto
                        self.grid_cores[r][c] or COR_LETRA_FIXA,
                        (255, 255, 255),  # Cor da borda (preta)
                        2,  # Grossura da borda
                        rect.center  # Posição
                    )

                else:
                    pygame.draw.rect(tela, ('#ddc1c2'), rect)

        # Desenha letra atual
        if self.atual:
            c = self.atual.col
            rect = pygame.Rect(
                self.x + c * self.cell_w + CELL_PADDING,
                int(self.atual.y) + CELL_PADDING,
                self.cell_w - 2*CELL_PADDING,
                self.cell_h - 2*CELL_PADDING,
            )
            font2 = pygame.font.SysFont("Arial", 45, bold=True)
            texto = font2.render(self.atual.char.upper(),
                                 True, self.atual.cor)
            pygame.draw.rect(tela, (COR_CABECALHO), rect)

            # coloca borda em volta da caixa de letra
            pygame.draw.rect(tela, (COR_BORDA), rect, 4)

            # Letra atual com borda mais grossa
            desenhar_texto_com_borda(
                tela, self.atual.char.upper(), font2,
                self.atual.cor,  # Cor do texto
                (255, 255, 255),  # Cor da borda (preta mais escura)
                2,  # Grossura maior para letra atual
                rect.center
            )

#--------------------------- Menu ---------------------------

# class TelaMenu:


# --------------------------- Main game ---------------------------


class WordDropGame:
    def __init__(self, palavras):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
        pygame.display.set_caption("Word Drop")
        self.relogio = pygame.time.Clock()
        self.fonte_titulo = pygame.font.SysFont("Arial", 40, bold=True)
        self.fonte_palavras = pygame.font.SysFont("Arial", 30, bold=True)
        self.fonte_debug = pygame.font.SysFont("Arial", 25)

        self.gerenciador_palavras = GerenciadorPalavras(palavras)

        #tela de jogo
        self.tela_menu = TelaMenu() 
        self.tela_game_over = TelaGameOver()
        self.tela_vitoria = TelaVitoria()
        self.tela_atual = "MENU"  # "JOGO", "GAME_OVER", "VITORIA"
        self.botao_play_rect = None
        self.botao_exit_rect = None


        # Área de jogo
        self.x_area_jogo = 380
        self.y_area_jogo = 30
        self.largura_area_jogo = 430
        self.altura_area_jogo = 540
        self.gerenciador_letras = None

    def iniciar_jogo(self, palavras):
        self.gerenciador_palavras = GerenciadorPalavras(palavras)
        self.gerenciador_letras = GerenciadorLetras(
            self.x_area_jogo, self.y_area_jogo,
            self.largura_area_jogo, self.altura_area_jogo,
            self.gerenciador_palavras
        )
        self.tela_atual = "JOGO"

    def desenhar_interface(self):
        self.tela.fill(COR_FUNDO)

        # Função auxiliar para texto com borda (igual à anterior)
        def desenhar_texto_com_borda(surface, texto, fonte, cor_texto, cor_borda, grossura, posicao):
            texto_surf = fonte.render(texto, True, cor_texto)
            texto_borda_surf = fonte.render(texto, True, cor_borda)
            texto_rect = texto_surf.get_rect(center=posicao)

            offsets = []
            for dx in range(-grossura, grossura + 1):
                for dy in range(-grossura, grossura + 1):
                    if dx != 0 or dy != 0:
                        offsets.append((dx, dy))

            for dx, dy in offsets:
                surface.blit(texto_borda_surf,
                             (texto_rect.x + dx, texto_rect.y + dy))

            surface.blit(texto_surf, texto_rect)
            return texto_rect

        # Título
        titulo_surf = pygame.Surface((330, 90))
        titulo_surf.fill(COR_CABECALHO)
        pygame.draw.rect(titulo_surf, COR_BORDA, (0, 0, 330, 90), 4)

        texto = self.fonte_titulo.render("WORD DROP", True, COR_TEXTO)
        texto_rect = texto.get_rect(center=(165, 45))
        titulo_surf.blit(texto, texto_rect)
        self.tela.blit(titulo_surf, (18, 30))

        # Lista de palavras com status
        # Lista de palavras centralizada
        num_cols = 2
        num_palavras = len(self.gerenciador_palavras.palavras)
        largura_total = num_cols * \
            (LARGURA_COLUNA + 5) + (num_cols - 1) * ESPACAMENTO

        # calcula posição X centralizada na tela
        x_base = (LARGURA_TELA - (2*largura_total)) // 8
        y_base = 150

        for i, palavra in enumerate(self.gerenciador_palavras.palavras):
            coluna = i % num_cols
            linha = i // num_cols

            x = x_base + coluna * (LARGURA_COLUNA + ESPACAMENTO + 5)
            y = y_base + linha * 70

            # Cores
            if self.gerenciador_palavras.completadas[palavra]:
                cor_fundo = COR_PALAVRA_COMPLETA
                cor_texto = COR_TEXTO
            else:
                cor_fundo = COR_CABECALHO
                cor_texto = self.gerenciador_palavras.cor_palavras[palavra]

            rect_palavra = pygame.Rect(x, y, LARGURA_COLUNA + 20, 45)
            pygame.draw.rect(self.tela, cor_fundo, rect_palavra)
            pygame.draw.rect(self.tela, COR_BORDA, rect_palavra, 3)

            # texto = self.fonte_palavras.render(palavra.upper(), True, cor_texto)
            # texto_rect = texto.get_rect(center=rect_palavra.center)
            # self.tela.blit(texto, texto_rect)

            # Palavra da lista com borda
            desenhar_texto_com_borda(
                self.tela, palavra.upper(), self.fonte_palavras,
                cor_texto, (255, 255, 255), 1, rect_palavra.center
            )

        # Área de jogo
        area_rect = pygame.Rect(self.x_area_jogo-2, self.y_area_jogo - 2,
                                self.largura_area_jogo + 4, self.altura_area_jogo + 4)
        pygame.draw.rect(self.tela, COR_CABECALHO, area_rect)
        pygame.draw.rect(self.tela, COR_BORDA, area_rect, 3)

        # Grade
        largura_quadrado = self.largura_area_jogo // GRID_COLS
        altura_quadrado = self.altura_area_jogo // GRID_ROWS
        for coluna in range(GRID_COLS):
            for linha in range(GRID_ROWS):
                quadrado_rect = pygame.Rect(
                    self.x_area_jogo + coluna * largura_quadrado,
                    self.y_area_jogo + linha * altura_quadrado,
                    largura_quadrado, altura_quadrado
                )
                pygame.draw.rect(self.tela, COR_BORDA, quadrado_rect, 1)

        # Desenha letras
        self.gerenciador_letras.desenhar(self.tela)

    def verificar_derrota(self):
        return any(self.gerenciador_letras.grid[0])

    def verificar_vitoria(self):
        return all(self.gerenciador_palavras.completadas.values())

    def verificar_palavras_formadas(self):
        letras_linha_inferior = self.gerenciador_letras.get_letras_linha_inferior()

        if len(letras_linha_inferior) == GRID_COLS:
            palavra_formada = self.gerenciador_palavras.verificar_palavra_formada(
                letras_linha_inferior)
            if palavra_formada is not None:
                self.gerenciador_palavras.marcar_palavra_completa(
                    palavra_formada)
                self.gerenciador_letras.pausar_por_palavra(palavra_formada)
                self.gerenciador_letras.remover_linha_inferior()
                return True
            else:
                # Não é palavra válida - nunca será removida
                self.gerenciador_letras.ultima_linha_valida -= 1
        return False

    def run(self):
        running = True
        palavras_jogo = ['bravo', 'clima', 'festa', 'hotel',
                      'fluir', 'poder', 'quero', 'tango',
                      'renda', 'zebra', 'grupo', 'lucro']
        while running:
            tempo_atual = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # elif event.type == pygame.KEYDOWN:
                #     if event.key == pygame.K_ESCAPE:
                #         running = False

                 # Se está no JOGO, processa controles
                if self.tela_atual == "MENU":
                    if self.botao_play_rect and self.botao_exit_rect:
                        resultado = self.tela_menu.processar_eventos(event, self.botao_play_rect, self.botao_exit_rect)
                        if resultado == "PLAY":
                            print("Iniciando jogo...")
                            self.iniciar_jogo(palavras_jogo)
                        elif resultado == "EXIT":
                            running = False
                 
                elif self.tela_atual == "JOGO":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.tela_atual = "MENU"  # Volta ao menu com ESC  
                        elif event.key == pygame.K_LEFT and not self.gerenciador_letras.pausado:
                            self.gerenciador_letras.mover_letra_esquerda()
                        elif event.key == pygame.K_RIGHT and not self.gerenciador_letras.pausado:
                            self.gerenciador_letras.mover_letra_direita()
                        elif event.key == pygame.K_DOWN:
                            # Acelera a queda da letra atual
                            if self.gerenciador_letras.atual and not self.gerenciador_letras.pausado:
                                self.gerenciador_letras.atual.y += 20
                        elif event.key == pygame.K_r:
                            self.gerenciador_palavras = GerenciadorPalavras(
                                self.gerenciador_palavras.palavras)
                            self.gerenciador_letras.gp = self.gerenciador_palavras

                # Se está em tela de fim de jogo, processa eventos do botão
                elif self.tela_atual in ["GAME_OVER", "VITORIA"] and self.botao_rect:
                    resultado = None
                    if self.tela_atual == "GAME_OVER":
                        resultado = self.tela_game_over.processar_eventos(event, self.botao_rect)

                    elif self.tela_atual == "VITORIA":
                        resultado = self.tela_vitoria.processar_eventos(event, self.botao_rect)

                    if resultado == "MENU":
                        self.tela_atual = "MENU"  # Ou volta para o menu
                        # self.iniciar_jogo(novas_palavras)


            # Atualiza lógica do jogo apenas se estiver jogando
            if self.tela_atual == "JOGO" and self.gerenciador_letras:
                self.gerenciador_letras.update(tempo_atual)

                # Verifica formação de palavras
                if not self.gerenciador_letras.pausado:
                    self.verificar_palavras_formadas()

                 # Verifica condições de fim de jogo
                if self.verificar_derrota():
                    self.tela_atual = "GAME_OVER"
                elif self.verificar_vitoria():
                    self.tela_atual = "VITORIA"

            
            # Desenha a tela apropriada
            if self.tela_atual == "MENU":
                self.botao_play_rect, self.botao_exit_rect = self.tela_menu.desenhar(self.tela)
            elif self.tela_atual == "JOGO":
                self.desenhar_interface()
            elif self.tela_atual == "GAME_OVER":
                self.botao_rect = self.tela_game_over.desenhar(self.tela)
            elif self.tela_atual == "VITORIA":
                self.botao_rect = self.tela_vitoria.desenhar(self.tela)
                
            pygame.display.flip()
            self.relogio.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == '__main__':

    # palavras com cinco letras e não repetidas
    novas_palavras = ['bravo', 'clima', 'festa', 'hotel',
                      'fluir', 'poder', 'quero', 'tango',
                      'renda', 'zebra', 'grupo', 'lucro']
    game = WordDropGame(novas_palavras)
    game.run()
