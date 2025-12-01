import pygame

LARGURA_TELA = 830
ALTURA_TELA = 590
COR_FUNDO = (223, 176, 176)
COR_CABECALHO = (244, 221, 222)
COR_BORDA = (168, 163, 163)
COR_BORDA_LETRA = ('#494646')


class TelaGameOver:
    def __init__(self):
        self.fonte_titulo = pygame.font.SysFont("Arial", 64, bold=True)
        self.fonte_mensagem = pygame.font.SysFont("Arial", 45)
        self.fonte_botao = pygame.font.SysFont("Arial", 36)
        pygame.display.set_caption("Word Drop")
        
        # Cores
        self.cor_fundo = ('#ef7b7b')  # Vermelho claro
        self.cor_titulo = ('#000000') 
        self.cor_titulo_caixa = ('#f4ddde') 
        self.cor_mensagem = ('#000000')  # preto
        self.cor_borda_interna = ('#ffffff')
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

        #tela vermelha
        caixa_rect = pygame.Rect(20, 20, LARGURA_TELA-40, ALTURA_TELA -40)
        pygame.draw.rect(tela, (self.cor_fundo), caixa_rect)
        pygame.draw.rect(tela, (self.cor_borda_interna), caixa_rect,3)

        #caixa do titulo
        caixa_titulo = pygame.Rect(LARGURA_TELA/7, 100, 600, 100)
        pygame.draw.rect(tela, (self.cor_titulo_caixa), caixa_titulo)
        pygame.draw.rect(tela, (self.cor_botao_borda), caixa_titulo,3)

        # Título "VOCÊ PERDEU"
        titulo = self.fonte_titulo.render("VOCÊ PERDEU", True, self.cor_titulo)
        titulo_rect = titulo.get_rect(center=(LARGURA_TELA//2, 150))
        
        # Efeito de sombra no título
        titulo_sombra = self.fonte_titulo.render("VOCÊ PERDEU", True, (self.cor_fundo))
        tela.blit(titulo_sombra, (titulo_rect.x + 3, titulo_rect.y + 3))
        tela.blit(titulo, titulo_rect)
        
        # Mensagem "VOLTE AO MENU E TENTE NOVAMENTE!"
        mensagem1 = self.fonte_mensagem.render("VOLTE AO MENU E  ", True, self.cor_mensagem)
        mensagem2 = self.fonte_mensagem.render("TENTE NOVAMENTE!", True, self.cor_mensagem)
        mensagem1_rect = mensagem1.get_rect(center=(LARGURA_TELA//2, 250))
        mensagem2_rect = mensagem2.get_rect(center=((LARGURA_TELA//2)-5, 320))
        tela.blit(mensagem1, mensagem1_rect)
        tela.blit(mensagem2, mensagem2_rect)

        
        # Botão "MENU"
        botao_rect = pygame.Rect(LARGURA_TELA//2 - 100, 400, 200, 60)
        
        # Verifica se o mouse está sobre o botão
        mouse_pos = pygame.mouse.get_pos()
        esta_sobre_botao= botao_rect.collidepoint(mouse_pos)
        # cor_botao_atual = self.cor_botao_hover if botao_rect.collidepoint(mouse_pos) else self.cor_botao
        
        # Escolhe as cores baseado no hover
        if esta_sobre_botao:
            corB_fundo = self.cor_botao_hover
            corB_borda = self.cor_botao_borda_hover
            corB_texto = self.cor_texto_botao_hover
        else:
            corB_fundo = self.cor_botao
            corB_borda = self.cor_botao_borda
            corB_texto = self.cor_texto_botao

        # Desenha o botão
        pygame.draw.rect(tela, corB_fundo, botao_rect, border_radius=12)
        pygame.draw.rect(tela, corB_borda, botao_rect, 3, border_radius=12)  # Borda branca
        
        # Texto do botão
        texto_botao = self.fonte_botao.render("MENU", True, corB_texto)
        texto_rect = texto_botao.get_rect(center=botao_rect.center)
        tela.blit(texto_botao, texto_rect)
        
        return botao_rect  # Retorna o retângulo do botão para detectar cliques
    
    def processar_eventos(self, event, botao_rect):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if botao_rect.collidepoint(event.pos):
                return "MENU"
        return None
    
