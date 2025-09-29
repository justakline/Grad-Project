import pygame




def run_pygame(model, width=800, height=800, agent_radius=3):
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Mesa Agents in Pygame")
    clock = pygame.time.Clock()

    scale_x = width / model.highway.x_max
    scale_y = height / model.highway.y_max

    # Load font for rendering text
    font = pygame.font.SysFont("Arial", 12)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update model
        model.step()

        # Draw
        screen.fill((0, 0, 0))  # black background
        for i, a in enumerate(model.agents):

            px = int(a.pos[0] * scale_x)
            py = height - int(a.pos[1] * scale_y)



            # Draw agent
            pygame.draw.circle(screen, (255,255,255), (px, py), agent_radius)

            # Draw text with (x,y) above agent
            # coord_text = f"({int(px)}, {int(py)})"
            # text_surface = font.render(coord_text, True, (255, 255, 255))
            # text_rect = text_surface.get_rect(center=(px, py - agent_radius - 8))
            # screen.blit(text_surface, text_rect)

            if(i == 0):
                print(f"({px}, {py})")

        pygame.display.flip()
        clock.tick(60)  # limit FPS

    pygame.quit()


# ------------------------------
# Run
# ------------------------------

