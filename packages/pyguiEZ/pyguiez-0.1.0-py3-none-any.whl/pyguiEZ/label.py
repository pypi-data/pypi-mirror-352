import pygame

class Label:
    def __init__(self, app, text, pos=(10, 10), font_size=24):
        self.text = text
        self.font = pygame.font.SysFont(None, font_size)
        self.pos = pos
        app.add_widget(self)

    def set_text(self, new_text):
        self.text = new_text

    def draw(self, surface):
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        surface.blit(text_surf, self.pos)

    def handle_event(self, event):
        pass
