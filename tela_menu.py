import pygame

LARGURA_TELA = 830
ALTURA_TELA = 590
COR_FUNDO = (223, 176, 176)
COR_CABECALHO = (244, 221, 222)
COR_BORDA = (168, 163, 163)
COR_BORDA_LETRA = ('#494646')


class TelaMenu:
    def __init__(self):
        self.fonte_titulo = pygame.font.SysFont("Arial", 75, bold=True)
        self.fonte_mensagem = pygame.font.SysFont("Arial", 50)
        self.fonte_botao = pygame.font.SysFont("Arial", 36)
        pygame.display.set_caption("Word Drop")
        
        # Cores
        self.cor_fundo = ('#f4d8d9')  # 
        self.cor_titulo = ('#000000') 
        self.cor_titulo_caixa = ('#f4ddde') 
        self.cor_mensagem = ('#000000')  # preto
        self.cor_borda_interna = ('#8f8b8b')
        self.cor_fundo_externo = ('#dfb0b0')

        self.cor_botao = ('#dfb0b0')  # rosa escuro
        self.cor_texto_botao = ('#000000')
        self.cor_botao_borda = ('#b26969')

        #botao hover
        self.cor_botao_hover = ('#b26969')  
        self.cor_texto_botao_hover = ('#f4ddde') 
        self.cor_botao_borda_hover = ('#f4ddde')
        
    def desenhar(self, tela):
        # Fundo 
        tela.fill(self.cor_fundo_externo)

        #tela verde
        caixa_rect = pygame.Rect(20, 20, LARGURA_TELA-40, ALTURA_TELA -40)
        pygame.draw.rect(tela, (self.cor_fundo), caixa_rect)
        pygame.draw.rect(tela, (self.cor_borda_interna), caixa_rect,3)

        #caixa do titulo
        caixa_titulo = pygame.Rect(LARGURA_TELA/7, 100, 600, 100)
        pygame.draw.rect(tela, (self.cor_titulo_caixa), caixa_titulo)
        pygame.draw.rect(tela, (self.cor_botao_borda), caixa_titulo,6)

        # Título "VOCÊ PERDEU"
        titulo = self.fonte_titulo.render("WORD DROP", True, self.cor_titulo)
        titulo_rect = titulo.get_rect(center=(LARGURA_TELA//2, 150))
        tela.blit(titulo, titulo_rect)
        
         # Botão "PLAY"
        botao_play_rect = pygame.Rect(LARGURA_TELA//2 - 130, 260, 260, 80)
        # Verifica se o mouse está sobre o botão
        mouse_pos = pygame.mouse.get_pos()
        esta_sobre_play= botao_play_rect.collidepoint(mouse_pos)
        
        # Escolhe as cores baseado no hover play
        if esta_sobre_play:
            cor_play_fundo = self.cor_botao_hover
            cor_play_borda = self.cor_botao_borda_hover
            cor_play_texto = self.cor_texto_botao_hover
        else:
            cor_play_fundo = self.cor_botao
            cor_play_borda = self.cor_botao_borda
            cor_play_texto = self.cor_texto_botao

        # Desenha o botão play
        pygame.draw.rect(tela, cor_play_fundo, botao_play_rect, border_radius=12)
        pygame.draw.rect(tela, cor_play_borda, botao_play_rect, 3, border_radius=12)  # Borda branca
        
        # Texto do botão play
        texto_play = self.fonte_botao.render("PLAY", True, cor_play_texto)
        texto_play_rect = texto_play.get_rect(center=botao_play_rect.center)
        tela.blit(texto_play, texto_play_rect)
        
        
        # Botão "EXIT"
        botao_exit_rect = pygame.Rect(LARGURA_TELA//2 - 110, 380, 220, 70)
        
        # Verifica se o mouse está sobre o botão exit
        mouse_pos = pygame.mouse.get_pos()
        esta_sobre_exit= botao_exit_rect.collidepoint(mouse_pos)
        
        # Escolhe as cores baseado no hover exit
        if esta_sobre_exit:
            cor_exit_fundo = self.cor_botao_hover
            cor_exit_borda = self.cor_botao_borda_hover
            cor_exit_texto = self.cor_texto_botao_hover
        else:
            cor_exit_fundo = self.cor_botao
            cor_exit_borda = self.cor_botao_borda
            cor_exit_texto = self.cor_texto_botao

        # Desenha o botão
        pygame.draw.rect(tela, cor_exit_fundo, botao_exit_rect, border_radius=12)
        pygame.draw.rect(tela, cor_exit_borda, botao_exit_rect, 3, border_radius=12)  # Borda branca
        
        # Texto do botão
        texto_exit = self.fonte_botao.render("EXIT", True, cor_exit_texto)
        texto_exit_rect = texto_exit.get_rect(center=botao_exit_rect.center)
        tela.blit(texto_exit, texto_exit_rect)
        
        return botao_play_rect,botao_exit_rect   # Retorna o retângulo do botão para detectar cliques
    
    def processar_eventos(self, event, botao_play_rect, botao_exit_rect):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if botao_play_rect.collidepoint(event.pos):
                return "PLAY"
            elif botao_exit_rect.collidepoint(event.pos):
                return "EXIT"
        return None

   
