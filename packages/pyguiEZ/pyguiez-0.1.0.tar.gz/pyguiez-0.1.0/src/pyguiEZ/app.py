import pygame

class App:
    def __init__(self, title="pyguiEZ App", size=(400, 300)):
        pygame.init()
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption(title)
        self.running = True
        self.widgets = []

    def add_widget(self, widget):
        self.widgets.append(widget)

    def run(self):
        while self.running:
            self.screen.fill((255, 255, 255))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                for widget in self.widgets:
                    widget.handle_event(event)

            for widget in self.widgets:
                widget.draw(self.screen)

            pygame.display.flip()

        pygame.quit()
