"""
En simulering av legemer i rommet der
alle legeme påfører gravitasjonskraft
    -y
     |
     |
-x<--+--> x+
     |
     |
    +y
    tid er oppgitt i sekund.
    masse er oppgitt i kg
    distanse i oppgitt i m
"""
import pygame

# pygame setup
pygame.init() # type: ignore
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS_TARGET = 180
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gravity Demo")
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()
meters_per_screenwidth = 150E9*2
k_meters_per_pixel = meters_per_screenwidth/SCREEN_WIDTH # Fra 3.2, k i (3.1), zoom-faktoren
k_increment = k_meters_per_pixel*0.05
c_coordinate_at_origin = pygame.Vector2(0,0) # Fra 3.2, c i (3.1), koordinaten på planet vist på pixel (0,0)
mouse_drag_start = pygame.Vector2(-1,-1) # point where mouse starts to drag
user_is_dragging = False
object_size_pixels = 100
mb1, mb2, mb3 = 0,0,0
RUNNING = True
GAMMA = 7E-11
R_RELATIVE_TO_M=False # giddekje fiksa dette

class PhysObj:
    """
    Et fysisk objekt som påfører og påføres gravitasjonskraft
    """
    m=1
    s=pygame.Vector2(0,0)
    v=pygame.Vector2(0,0)
    a=pygame.Vector2(0,0)
    color=pygame.Color(255,0,0)
    def __init__(self, m, s, v, a, c=pygame.Color(255,0,0)):
        self.m=m
        self.s=s
        self.v=v
        self.a=a
        self.color=c
    def update_acceleration(self, all_objects):
        """
        Utfører metode for å kalkulere
        akselerasjon fra seksjon 2.3
        """
        gm = pygame.Vector2(0.0,0.0)
        for obj in all_objects:
            vec=obj.s-self.s
            length=vec.length()
            if length!=0:
                g_hat = vec/length
                gm=gm + ((g_hat*obj.m)/(length)/(length))
        self.a = gm*GAMMA

    def update_velocity(self, time_passed):
        """
        ...
        """
        self.v=self.v+self.a*time_passed

    def update_position(self, time_passed):
        """
        ...
        """
        self.s=self.s+self.v*time_passed

# Terra
objA = PhysObj(5972E21, # mass
               pygame.Vector2(147E9,0), # s
               pygame.Vector2(0,30E3), # v
               pygame.Vector2(0,0), # a
               pygame.Color(0,0,255)
               )
# Sol
objB = PhysObj(199E28, # m
               pygame.Vector2(0,0), # s
               pygame.Vector2(0,0), # v
               pygame.Vector2(0,0), # a
               pygame.Color(255,255,0)
               )
# Mars
objC = PhysObj(64E22, # m
               pygame.Vector2(-228E9,0), # s
               pygame.Vector2(0,-24E3), # v
               pygame.Vector2(0,0), # a
               pygame.Color(200,100,0)
               )
# Mercury
objD = PhysObj(33E22, # m
               pygame.Vector2(-60E9,0), # s
               pygame.Vector2(0,-47E3), # v
               pygame.Vector2(0,0), # a
               pygame.Color(200,200,200)
                )
#objA.m=1
#objB.m=1
objC.m=1
ALL_OBJECTS = [objA, objB, objC, objD]
dt=1/60
dt*=1E6

def add_object_with_vel(pos, color, mass, vel):
    """
    Legger et objekt til i ALL_OBJECTS
    """
    global ALL_OBJECTS
    new_obj=PhysObj(mass,
                    pos,
                    vel,
                    pygame.Vector2(0,0),
                    color
                    )
    ALL_OBJECTS.append(new_obj)

def add_object(pos, color, mass):
    """
    Legger et objekt til i ALL_OBJECTS
    """
    add_object_with_vel(pos, color, mass, pygame.Vector2(0,0))

def transform_window_to_plane(v):
    """
    finner koordinaten på planet ut i fra vinduskoordinat.
    """
    return k_meters_per_pixel*v+c_coordinate_at_origin
def transform_plane_to_window(v):
    """
    finner koordinaten i vinduet ut i fra koordinaten på planet.
    """
    return (v-c_coordinate_at_origin)/k_meters_per_pixel
def transform_plane_to_window_tuplet(v):
    """
    finner koordinaten i vinduet ut i fra koordinaten på planet.
    """
    t_v = (v-c_coordinate_at_origin)/k_meters_per_pixel
    return t_v.x, t_v.y

def draw_circle_in_plane(window, # pygame.screen ?
                         color, # pygame.Color
                         pos, # pygame.Vector2
                         rad, # uint
                         outline_thickness # uint
                         ):
    """
    Tegn en korrekt skalert sirkel.
    plane koordinater til vindu koordinater.
    """
    global k_meters_per_pixel
    if k_meters_per_pixel==0:
        k_meters_per_pixel = 0.01
    pygame.draw.circle(window, color,
                           transform_plane_to_window(pos),
                           int(rad/k_meters_per_pixel),
                           int(outline_thickness/k_meters_per_pixel))

def generate_color(input_mass):
    color_r=input_mass%255
    color_g=(input_mass+50)%255
    color_b=(input_mass+130)%255
    pygame_color=pygame.Color(color_r, color_g, color_b)
    return pygame_color

def handle_user_dragging():
    """
    håndterer draing osv. av rutenettet
    """
    global mouse_drag_start, c_coordinate_at_origin
    mx, my = pygame.mouse.get_pos()
    if mouse_drag_start != pygame.Vector2(-1,-1):
        c_coordinate_at_origin=c_coordinate_at_origin-(pygame.Vector2(mx,my)-mouse_drag_start)*k_meters_per_pixel
    mouse_drag_start.x = mx
    mouse_drag_start.y = my

def handle_input(event):
    """
    Kode for tastatur- og musrelaterte saker
    """
def handle_keydown(event):
    """
    Håndterer pygame.KEYDOWN
    """
    global object_size_pixels, user_is_dragging
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[pygame.K_s]:
        new_object_size_pixels=int(input("Ny størrelse på objekt(mengde pixel, uint): "))
        object_size_pixels=new_object_size_pixels
    if pressed_keys[pygame.K_SPACE]:
        mx, my = pygame.mouse.get_pos()
        if 0<=mx<SCREEN_WIDTH and 0<=my<SCREEN_HEIGHT:
            user_is_dragging=True
def handle_keyup(event):
    """
    Håndterer pygame.KEYUP
    """
    global object_size_pixels, user_is_dragging
    pressed_keys = pygame.key.get_pressed()
    if not pressed_keys[pygame.K_SPACE]:
        user_is_dragging=False
        mouse_drag_start.x=-1
        mouse_drag_start.y=-1
def handle_mousebuttondown(event):
    """
    Håndterer pygame.MOUSEBUTTONDOWN
    """
    global user_is_dragging, mb1, mb2, mb3
    mb1, mb2, mb3 = pygame.mouse.get_pressed(3)
    mx, my = pygame.mouse.get_pos()
    if mb1:
        input_mass=int(input("Mass: "))
        pygame_vec=pygame.Vector2(mx, my)
        add_object(transform_window_to_plane(pygame_vec), generate_color(input_mass), input_mass)
    if mb3:
        input_mass=int(input("Mass: "))
        input_velx=int(input("Velocity_x: "))
        input_vely=int(input("Velocity_y: "))
        pygame_vec=pygame.Vector2(mx, my)
        add_object_with_vel(transform_window_to_plane(pygame_vec), generate_color(input_mass), input_mass, pygame.Vector2(input_velx, input_vely))
    if mb2:
        user_is_dragging=True
def handle_mousebuttonup(event):
    """
    Håndterer pygame.MOUSEBUTTONUP
    """
    global mouse_drag_start, user_is_dragging, mb2
    if mb2:
        user_is_dragging=False
        mouse_drag_start.x=-1
        mouse_drag_start.y=-1

def handle_mousewheel(event):
    """
    Håndterer pygame.MOUSEWHEEL
    """
    global k_meters_per_pixel, k_increment
    if event.y < 0:
        k_meters_per_pixel+=k_increment
    else:
        k_meters_per_pixel-=k_increment
        k_meters_per_pixel=max(k_meters_per_pixel,0.001)
def update():
    """
    Kode for oppdatering av objekt osv.
    """
    global ALL_OBJECTS
    for _obj in ALL_OBJECTS:
        _obj.update_acceleration(ALL_OBJECTS)
    # fart og posisjon må kalkuleres etter akselerasjoner,
    # siden akselerasjonene er relaterte til objektenes posisjon.
    for _obj in ALL_OBJECTS:
        _obj.update_velocity(dt)
        _obj.update_position(dt)

def draw():
    """
    Kode for tegning
    """
    global font, screen, ALL_OBJECTS
    screen.fill(pygame.Color(0,0,0))
    for _obj in ALL_OBJECTS:
        draw_circle_in_plane(screen, _obj.color,
                           _obj.s,
                           int(_obj.m*7E-22) if R_RELATIVE_TO_M else object_size_pixels*k_meters_per_pixel,
                                0)
        draw_circle_in_plane(screen, pygame.Color(255,255,255),
                           _obj.s,
                           int((_obj.m/1E6)/k_meters_per_pixel) if R_RELATIVE_TO_M else object_size_pixels*k_meters_per_pixel,
                           max(1,k_meters_per_pixel))
    text = font.render(str(k_meters_per_pixel)+"m/pixel", True, (200,200,20))
    screen.blit(text, transform_plane_to_window(pygame.Vector2(0, 530)))

    # flip() the display to put your work on screen
    pygame.display.flip()

def handle_all_events():
    global RUNNING, event_handler, user_is_dragging
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            RUNNING = False

        event_handler=event_handlers.get(event.type)
        if event_handler:
            event_handler(event)

    if user_is_dragging:
        handle_user_dragging()

event_handlers={
    pygame.KEYDOWN:handle_keydown,
    pygame.KEYUP:handle_keyup,
    pygame.MOUSEBUTTONDOWN:handle_mousebuttondown,
    pygame.MOUSEBUTTONUP:handle_mousebuttonup,
    pygame.MOUSEWHEEL:handle_mousewheel,
    }

while RUNNING:

    handle_all_events()

    update()

    draw()

    clock.tick(FPS_TARGET)  # limits FPS to 60

pygame.quit()
