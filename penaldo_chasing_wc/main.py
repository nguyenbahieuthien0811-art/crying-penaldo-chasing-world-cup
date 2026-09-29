# main.py

### Imports ###
import os
import math
import random
import pygame as pg

### Data ###

# Window
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60
WINDOW_TITLE = "Ronaldo Chases the World Cup"

# Physics
GRAVITY = 0.45
FLAP_STRENGTH = -7.5

# World scrolling
SCROLL_SPEED = 3.0

# Obstacles
GAP_SIZE = 170
SPAWN_INTERVAL = 1500
CONE_WIDTH = 60

# Player
PLAYER_WIDTH = 125

# Trophy
TROPHY_WIDTH = 90
TROPHY_X = 335

# Ground
GROUND_HEIGHT = 100
GROUND_Y = SCREEN_HEIGHT - GROUND_HEIGHT

# Asset filenames
RONALDO_FILE = "ronaldo.png"
TROPHY_FILE = "trophy.png"
CONE_FILE = "cone.png"
BACKGROUND_FILE = "background.png"

# Colors
SKY_BLUE = (135, 206, 235)

WHITE = (255, 255, 255)
BLACK = (25, 25, 25)

GREEN = (45, 160, 70)
LIGHT_GREEN = (70, 185, 80)

ORANGE = (240, 120, 30)
GOLD = (255, 215, 0)

pg.init()

screen = pg.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pg.display.set_caption(
    WINDOW_TITLE
)

clock = pg.time.Clock()


#* Fonts

FONT_LARGE = pg.font.Font(
    None,
    54
)

FONT_MEDIUM = pg.font.Font(
    None,
    32
)

FONT_SMALL = pg.font.Font(
    None,
    22
)


#* Asset paths

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

ASSET_DIR = os.path.join(
    BASE_DIR,
    "assets"
)


#* Load image function

def load_image(
    filename,
    width,
    fallback_color,
    fallback_shape="rect"
):
    """
    Load an image from the assets folder.

    If the image is missing, use a simple fallback shape.
    """

    path = os.path.join(
        ASSET_DIR,
        filename
    )

    try:

        image = pg.image.load(
            path
        ).convert_alpha()

        # Keep original aspect ratio
        original_width = image.get_width()
        original_height = image.get_height()

        scale = width / original_width

        new_width = int(
            original_width * scale
        )

        new_height = int(
            original_height * scale
        )

        image = pg.transform.smoothscale(
            image,
            (
                new_width,
                new_height
            )
        )

        return image

    except (FileNotFoundError, pg.error):

        print(
            "WARNING: Could not load:",
            path
        )

        print(
            "Using fallback shape instead."
        )

        height = width

        image = pg.Surface(
            (
                width,
                height
            ),
            pg.SRCALPHA
        )

        if fallback_shape == "circle":

            pg.draw.circle(
                image,
                fallback_color,
                (
                    width // 2,
                    height // 2
                ),
                width // 2
            )

        elif fallback_shape == "triangle":

            points = [
                (width // 2, 0),
                (0, height),
                (width, height)
            ]

            pg.draw.polygon(
                image,
                fallback_color,
                points
            )

        else:

            pg.draw.rect(
                image,
                fallback_color,
                (
                    0,
                    0,
                    width,
                    height
                )
            )

        return image


# ============================================================
# LOAD ASSETS
# ============================================================

ronaldo_image = load_image(
    RONALDO_FILE,
    PLAYER_WIDTH,
    (30, 80, 220),
    "circle"
)

trophy_image = load_image(
    TROPHY_FILE,
    TROPHY_WIDTH,
    GOLD,
    "rect"
)

cone_image = load_image(
    CONE_FILE,
    CONE_WIDTH,
    ORANGE,
    "triangle"
)

background_image = load_image(
    BACKGROUND_FILE,
    SCREEN_WIDTH,
    SKY_BLUE,
    "rect"
)

# Fill the complete window
background_image = pg.transform.smoothscale(
    background_image,
    (
        SCREEN_WIDTH,
        SCREEN_HEIGHT
    )
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def draw_centered_text(
    text,
    font,
    color,
    y
):
    """Draw text horizontally centered."""

    surface = font.render(
        text,
        True,
        color
    )

    x = (
        SCREEN_WIDTH -
        surface.get_width()
    ) // 2

    screen.blit(
        surface,
        (
            x,
            y
        )
    )


def draw_background(
    ground_offset
):
    """Draw the background image and football pitch."""

    # --------------------------------------------------------
    # Background image
    # --------------------------------------------------------

    screen.blit(
        background_image,
        (0, 0)
    )

    # --------------------------------------------------------
    # Football pitch
    # --------------------------------------------------------

    pg.draw.rect(
        screen,
        GREEN,
        (
            0,
            GROUND_Y,
            SCREEN_WIDTH,
            GROUND_HEIGHT
        )
    )

    # --------------------------------------------------------
    # Scrolling grass stripes
    # --------------------------------------------------------

    stripe_width = 40

    for x in range(
        -stripe_width,
        SCREEN_WIDTH + stripe_width,
        stripe_width
    ):

        actual_x = (
            x -
            int(ground_offset)
        )

        pg.draw.rect(
            screen,
            LIGHT_GREEN,
            (
                actual_x,
                GROUND_Y,
                stripe_width // 2,
                GROUND_HEIGHT
            )
        )

    # --------------------------------------------------------
    # White line at top of pitch
    # --------------------------------------------------------

    pg.draw.rect(
        screen,
        WHITE,
        (
            0,
            GROUND_Y,
            SCREEN_WIDTH,
            4
        )
    )


# ============================================================
# PLAYER CLASS
# ============================================================

class Player:

    def __init__(self):

        self.image = ronaldo_image

        # Ronaldo stays at a fixed X position
        self.x = 80

        self.y = SCREEN_HEIGHT // 2

        self.velocity = 0

        self.rect = self.image.get_rect()

    def reset(self):

        self.y = SCREEN_HEIGHT // 2

        self.velocity = 0

    def flap(self):

        self.velocity = FLAP_STRENGTH

    def update(self):

        # Gravity
        self.velocity += GRAVITY

        # Move vertically
        self.y += self.velocity

        # Update rectangle
        self.rect = self.image.get_rect(
            center=(
                int(self.x),
                int(self.y)
            )
        )

    def draw(self):

        screen.blit(
            self.image,
            self.rect
        )

    def get_hitbox(self):

        # Smaller hitbox makes collision feel fair
        return self.rect.inflate(
            -16,
            -14
        )


# ============================================================
# CONE PAIR CLASS
# ============================================================

class ConePair:

    def __init__(self, x):

        self.x = x

        min_gap_y = 130
        max_gap_y = GROUND_Y - GAP_SIZE - 30

        self.gap_y = random.randint(min_gap_y, max_gap_y)
        self.passed = False

        # Heights needed to fully cover the space above and below the gap
        top_height = max(self.gap_y, 1)
        bottom_height = max(GROUND_Y - (self.gap_y + GAP_SIZE), 1)

        # Stretch the cone image so it always touches the screen edge
        stretched_top = pg.transform.scale(cone_image, (CONE_WIDTH, top_height))
        self.top_image = pg.transform.rotate(stretched_top, 180)

        self.bottom_image = pg.transform.scale(cone_image, (CONE_WIDTH, bottom_height))

        self.top_rect = self.top_image.get_rect()
        self.top_rect.midbottom = (int(self.x + CONE_WIDTH / 2), self.gap_y)

        self.bottom_rect = self.bottom_image.get_rect()
        self.bottom_rect.midtop = (int(self.x + CONE_WIDTH / 2), self.gap_y + GAP_SIZE)

    def update(self):

        self.x -= SCROLL_SPEED

        self.top_rect.midbottom = (int(self.x + CONE_WIDTH / 2), self.gap_y)
        self.bottom_rect.midtop = (int(self.x + CONE_WIDTH / 2), self.gap_y + GAP_SIZE)

    def draw(self):

        screen.blit(self.top_image, self.top_rect)
        screen.blit(self.bottom_image, self.bottom_rect)

    def collides_with(self, player_hitbox):

        return (
            player_hitbox.colliderect(self.top_rect)
            or player_hitbox.colliderect(self.bottom_rect)
        )

    def is_off_screen(self):

        return self.x + CONE_WIDTH < 0

    def should_score(self, player_x):

        if not self.passed:
            if self.x + CONE_WIDTH < player_x:
                self.passed = True
                return True

        return False


# ============================================================
# TROPHY CLASS
# ============================================================

class Trophy:

    def __init__(self):

        self.image = trophy_image

        # Trophy stays far ahead
        self.x = TROPHY_X

        self.base_y = (
            SCREEN_HEIGHT // 2
        )

        self.y = self.base_y

        self.time = 0

    def reset(self):

        self.time = 0

        self.y = self.base_y

    def update(
        self,
        next_gap_y
    ):

        self.time += 1

        # Smooth floating animation
        bob = (
            math.sin(
                self.time * 0.045
            ) * 25
        )

        # Follow the next gap slightly
        target_y = (
            next_gap_y +
            GAP_SIZE / 2
        )

        self.base_y += (
            target_y -
            self.base_y
        ) * 0.015

        self.y = (
            self.base_y +
            bob
        )

        # Never moves horizontally toward Ronaldo
        self.x = TROPHY_X

    def draw(self):

        rect = self.image.get_rect(
            center=(
                int(self.x),
                int(self.y)
            )
        )

        screen.blit(
            self.image,
            rect
        )


# ============================================================
# CREATE / RESET GAME
# ============================================================

def create_game():

    player = Player()

    trophy = Trophy()

    cones = []

    score = 0

    last_spawn_time = (
        pg.time.get_ticks()
    )

    ground_offset = 0

    return (
        player,
        trophy,
        cones,
        score,
        last_spawn_time,
        ground_offset
    )


# ============================================================
# FIND NEXT GAP
# ============================================================

def get_next_gap_y(
    cones
):

    player_x = 80

    closest_gap = (
        SCREEN_HEIGHT // 2
    )

    closest_distance = 999999

    for cone in cones:

        if cone.x >= player_x:

            distance = (
                cone.x -
                player_x
            )

            if (
                distance <
                closest_distance
            ):

                closest_distance = distance

                closest_gap = (
                    cone.gap_y
                )

    return closest_gap


# ============================================================
# SCORE DISPLAY
# ============================================================

def draw_score(
    score
):

    # Shadow
    shadow = FONT_LARGE.render(
        str(score),
        True,
        BLACK
    )

    # Main score
    text = FONT_LARGE.render(
        str(score),
        True,
        WHITE
    )

    x = (
        SCREEN_WIDTH -
        text.get_width()
    ) // 2

    screen.blit(
        shadow,
        (
            x + 2,
            8
        )
    )

    screen.blit(
        text,
        (
            x,
            6
        )
    )


# ============================================================
# START SCREEN
# ============================================================

def draw_start_screen(
    player,
    bob_time
):

    draw_background(0)

    # --------------------------------------------------------
    # Ronaldo bobbing
    # --------------------------------------------------------

    bob_y = (
        SCREEN_HEIGHT // 2 -
        40
    )

    bob_y += (
        math.sin(
            bob_time * 0.004
        ) * 15
    )

    player.rect = (
        player.image.get_rect(
            center=(
                SCREEN_WIDTH // 2,
                int(bob_y)
            )
        )
    )

    screen.blit(
        player.image,
        player.rect
    )

    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    draw_centered_text(
        "RONALDO",
        FONT_LARGE,
        WHITE,
        65
    )

    draw_centered_text(
        "Chases the World Cup",
        FONT_MEDIUM,
        GOLD,
        120
    )

    # --------------------------------------------------------
    # Trophy
    # --------------------------------------------------------

    trophy_rect = (
        trophy_image.get_rect(
            center=(
                SCREEN_WIDTH // 2 + 95,
                int(bob_y)
            )
        )
    )

    screen.blit(
        trophy_image,
        trophy_rect
    )

    # --------------------------------------------------------
    # Start instruction box
    # --------------------------------------------------------

    instruction_width = 330
    instruction_height = 50

    instruction_x = (
        SCREEN_WIDTH -
        instruction_width
    ) // 2

    instruction_y = 500

    instruction_surface = pg.Surface(
        (
            instruction_width,
            instruction_height
        ),
        pg.SRCALPHA
    )

    instruction_surface.fill(
        (255, 255, 255, 190)
    )

    screen.blit(
        instruction_surface,
        (
            instruction_x,
            instruction_y
        )
    )

    draw_centered_text(
        "SPACE or CLICK to start",
        FONT_SMALL,
        BLACK,
        515
    )


# ============================================================
# GAME OVER SCREEN
# ============================================================

def draw_game_over(
    score
):

    # --------------------------------------------------------
    # Dark overlay
    # --------------------------------------------------------

    overlay = pg.Surface(
        (
            SCREEN_WIDTH,
            SCREEN_HEIGHT
        ),
        pg.SRCALPHA
    )

    overlay.fill(
        (0, 0, 0, 100)
    )

    screen.blit(
        overlay,
        (0, 0)
    )

    # --------------------------------------------------------
    # Game-over card
    # --------------------------------------------------------

    card_width = 330
    card_height = 280

    card_x = (
        SCREEN_WIDTH -
        card_width
    ) // 2

    card_y = 145

    # Card shadow
    shadow_rect = pg.Rect(
        card_x + 5,
        card_y + 7,
        card_width,
        card_height
    )

    pg.draw.rect(
        screen,
        (20, 20, 20),
        shadow_rect,
        border_radius=18
    )

    # Main card
    card_rect = pg.Rect(
        card_x,
        card_y,
        card_width,
        card_height
    )

    pg.draw.rect(
        screen,
        (245, 245, 245),
        card_rect,
        border_radius=18
    )

    # Gold line at top
    pg.draw.rect(
        screen,
        GOLD,
        (
            card_x,
            card_y,
            card_width,
            8
        ),
        border_radius=18
    )

    # --------------------------------------------------------
    # GAME OVER
    # --------------------------------------------------------

    title_font = pg.font.Font(
        None,
        52
    )

    title = title_font.render(
        "GAME OVER",
        True,
        (35, 35, 35)
    )

    title_x = (
        SCREEN_WIDTH -
        title.get_width()
    ) // 2

    screen.blit(
        title,
        (
            title_x,
            card_y + 35
        )
    )

    # --------------------------------------------------------
    # Trophy
    # --------------------------------------------------------

    trophy_size = 55

    game_over_trophy = (
        pg.transform.smoothscale(
            trophy_image,
            (
                trophy_size,
                trophy_size
            )
        )
    )

    trophy_rect = (
        game_over_trophy.get_rect(
            center=(
                SCREEN_WIDTH // 2,
                card_y + 105
            )
        )
    )

    screen.blit(
        game_over_trophy,
        trophy_rect
    )

    # --------------------------------------------------------
    # Final score
    # --------------------------------------------------------

    score_font = pg.font.Font(
        None,
        38
    )

    score_text = score_font.render(
        "Score: " + str(score),
        True,
        (35, 35, 35)
    )

    score_x = (
        SCREEN_WIDTH -
        score_text.get_width()
    ) // 2

    screen.blit(
        score_text,
        (
            score_x,
            card_y + 145
        )
    )

    # --------------------------------------------------------
    # Restart instruction
    # --------------------------------------------------------

    instruction_font = pg.font.Font(
        None,
        24
    )

    instruction = (
        instruction_font.render(
            "SPACE or CLICK to play again",
            True,
            (80, 80, 80)
        )
    )

    instruction_x = (
        SCREEN_WIDTH -
        instruction.get_width()
    ) // 2

    screen.blit(
        instruction,
        (
            instruction_x,
            card_y + 210
        )
    )


# ============================================================
# MAIN GAME LOOP
# ============================================================

def main():

    # Current game state
    game_state = "start"

    # Create game objects
    (
        player,
        trophy,
        cones,
        score,
        last_spawn_time,
        ground_offset
    ) = create_game()

    running = True

    start_bob_time = 0

    # ========================================================
    # MAIN LOOP
    # ========================================================

    while running:

        clock.tick(FPS)

        # ====================================================
        # EVENTS
        # ====================================================

        for event in pg.event.get():

            # ------------------------------------------------
            # Close window
            # ------------------------------------------------

            if event.type == pg.QUIT:

                running = False

            # ------------------------------------------------
            # Keyboard
            # ------------------------------------------------

            if event.type == pg.KEYDOWN:

                if event.key == pg.K_SPACE:

                    # Start
                    if game_state == "start":

                        (
                            player,
                            trophy,
                            cones,
                            score,
                            last_spawn_time,
                            ground_offset
                        ) = create_game()

                        game_state = "playing"

                        player.flap()

                    # Flap
                    elif game_state == "playing":

                        player.flap()

                    # Restart
                    elif game_state == "game_over":

                        (
                            player,
                            trophy,
                            cones,
                            score,
                            last_spawn_time,
                            ground_offset
                        ) = create_game()

                        game_state = "playing"

                        player.flap()

            # ------------------------------------------------
            # Mouse
            # ------------------------------------------------

            if event.type == pg.MOUSEBUTTONDOWN:

                if event.button == 1:

                    # Start
                    if game_state == "start":

                        (
                            player,
                            trophy,
                            cones,
                            score,
                            last_spawn_time,
                            ground_offset
                        ) = create_game()

                        game_state = "playing"

                        player.flap()

                    # Flap
                    elif game_state == "playing":

                        player.flap()

                    # Restart
                    elif game_state == "game_over":

                        (
                            player,
                            trophy,
                            cones,
                            score,
                            last_spawn_time,
                            ground_offset
                        ) = create_game()

                        game_state = "playing"

                        player.flap()

        # ====================================================
        # START STATE
        # ====================================================

        if game_state == "start":

            start_bob_time += (
                1000 / FPS
            )

            draw_start_screen(
                player,
                start_bob_time
            )

        # ====================================================
        # PLAYING STATE
        # ====================================================

        elif game_state == "playing":

            # ------------------------------------------------
            # Scroll ground
            # ------------------------------------------------

            ground_offset += (
                SCROLL_SPEED
            )

            if ground_offset >= 40:

                ground_offset -= 40

            # ------------------------------------------------
            # Update player
            # ------------------------------------------------

            player.update()

            # ------------------------------------------------
            # Spawn cones
            # ------------------------------------------------

            current_time = (
                pg.time.get_ticks()
            )

            if (
                current_time -
                last_spawn_time >=
                SPAWN_INTERVAL
            ):

                cones.append(
                    ConePair(
                        SCREEN_WIDTH + 20
                    )
                )

                last_spawn_time = (
                    current_time
                )

            # ------------------------------------------------
            # Update cones
            # ------------------------------------------------

            for cone in cones:

                cone.update()

            # Remove off-screen cones
            cones = [
                cone
                for cone in cones
                if not cone.is_off_screen()
            ]

            # ------------------------------------------------
            # Update trophy
            # ------------------------------------------------

            next_gap_y = (
                get_next_gap_y(
                    cones
                )
            )

            trophy.update(
                next_gap_y
            )

            # ------------------------------------------------
            # Collision
            # ------------------------------------------------

            player_hitbox = (
                player.get_hitbox()
            )

            # Top of screen
            if player_hitbox.top <= 0:

                game_state = "game_over"

            # Ground
            if (
                player_hitbox.bottom >=
                GROUND_Y
            ):

                game_state = "game_over"

            # Cones
            for cone in cones:

                if cone.collides_with(
                    player_hitbox
                ):

                    game_state = "game_over"

                    break

            # ------------------------------------------------
            # Score
            # ------------------------------------------------

            for cone in cones:

                if cone.should_score(
                    player.x
                ):

                    score += 1

            # ------------------------------------------------
            # Draw gameplay
            # ------------------------------------------------

            draw_background(
                ground_offset
            )

            for cone in cones:

                cone.draw()

            trophy.draw()

            player.draw()

            draw_score(
                score
            )

        # ====================================================
        # GAME OVER STATE
        # ====================================================

        elif game_state == "game_over":

            # Draw frozen gameplay
            draw_background(
                ground_offset
            )

            for cone in cones:

                cone.draw()

            trophy.draw()

            player.draw()

            draw_score(
                score
            )

            # Draw improved game-over UI
            draw_game_over(
                score
            )

        # ====================================================
        # DISPLAY
        # ====================================================

        pg.display.flip()

    # ========================================================
    # CLEAN EXIT
    # ========================================================

    pg.quit()


# ============================================================
# PROGRAM ENTRY
# ============================================================

if __name__ == "__main__":

    main()