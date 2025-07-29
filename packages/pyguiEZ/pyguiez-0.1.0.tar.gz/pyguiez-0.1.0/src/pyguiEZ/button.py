import pygame

class Button:
    def __init__(self, app, text, pos=(10, 50), size=(120, 40), command=None):
        self.text = text
        self.rect = pygame.Rect(pos, size)
        self.command = command
        self.font = pygame.font.SysFont(None, 24)
        app.add_widget(self)

    def draw(self, surface):
        pygame.draw.rect(surface, (180, 180, 180), self.rect)
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and self.command:
                self.command()
