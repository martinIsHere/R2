"""
En simulering av elektriske felt. Tegner feltene og
viser feltlinjer.
    -y
     |
     |
-x<--+--> x+
     |
     |
    +y
    tid er oppgitt i sekund.
    masse er oppgitt i kilogram
    distanse oppgitt i meter
    ladning oppgitt i coulomb
"""
import pygame

# pygame setup
pygame.init() # type: ignore
#-#-variable declarations
SCREEN_WIDTH = 1480
SCREEN_HEIGHT = 750
FPS_TARGET = 180
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Elektriske felt demo")
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()
meters_per_screenwidth = 1E3
DEFAULT_K_METERS_PER_PIXEL = meters_per_screenwidth/SCREEN_WIDTH
k_meters_per_pixel = DEFAULT_K_METERS_PER_PIXEL # Fra 3.2, k i (3.1), zoom-faktoren
k_increment = k_meters_per_pixel*0.05
c_coordinate_at_origin = pygame.Vector2(0,0) # Fra 3.2, c i (3.1), koordinaten på planet vist på pixel (0,0)
mouse_drag_start = pygame.Vector2(-1,-1) # point where mouse starts to drag
user_is_dragging = False
object_size_pixels = 10
mb1, mb2, mb3 = 0,0,0
RUNNING = True
GAMMA = 7E-11
COULOMB_CONSTANT_K_E = 8.99E9
dt = 1 # seconds per tick
dt *= 1E4
electrical_field_sim_timestep = 8 # seconds per tick
electrical_field_sim_timestep *= 1E3
PIXELS_BETWEEN_GRID_NODES = 80
R_RELATIVE_TO_M = False # giddekje fiksa dette
GRAVITY_ACTIVATED = False

#-#-class definitions
class PhysObj:
    """
    Et fysisk objekt som påfører og påføres gravitasjonskraft
    """
    m = 1 # masse
    q = 1 # ladning
    s = pygame.Vector2(0, 0) # posisjon
    v = pygame.Vector2(0, 0) # hastighet
    a = pygame.Vector2(0, 0) # akselerasjon
    color=pygame.Color(255, 0, 0) # farge
    immovable = False
    def __init__(self, m, q, s, v, a, c=pygame.Color(255, 0, 0)):
        self.m = m
        self.q = q
        self.s = s
        self.v = v
        self.a = a
        self.color = c

    def __calculateGravitationalForce(self, all_objects):
        """
        Bruker fysikkformler oppgitt i Ergo Fysikk 2
        """
        g_accelerationVec = pygame.Vector2(0.0, 0.0)
        for obj in all_objects:
            vec = obj.s-self.s
            length = vec.length()
            if length != 0:
                g_hat = vec/length # direction of g_accelerationVec
                g_accelerationVec = g_accelerationVec + ((g_hat*obj.m)/(length)/(length))
        G_forceVec = g_accelerationVec*GAMMA*self.m
        return G_forceVec

    def __calculateElectricalForce(self, all_objects): 
        """
        Bruker fysikkformler oppgitt i Ergo Fysikk 2
        Coulombs lov
        """
        E_sumForceVec = pygame.Vector2(0.0, 0.0)
        for obj in all_objects:
            vec = self.s-obj.s # obj -> self (opposite of gravitational *vec* direction)
            length = vec.length()
            if length != 0:
                E_hat = vec/length # direction of E_sumForceVec
                E_sumForceVec = (E_sumForceVec +
                        ((E_hat*obj.q*self.q)/(length)/(length)))
        E_sumForceVec *= COULOMB_CONSTANT_K_E
        return E_sumForceVec

    def get_updated_acceleration(self, all_objects, includeGravity=True):
        """
        Bruker fysikkformler oppgitt i Ergo Fysikk 2
        """
        if self.immovable:
            return pygame.Vector2(0.0, 0.0)
        if includeGravity:
            G_sumForceVec = self.__calculateGravitationalForce(all_objects) # gravity
        else:
            G_sumForceVec = pygame.Vector2(0.0, 0.0)
        E_sumForceVec = self.__calculateElectricalForce(all_objects) # electrical field
        totalSum_forceVec = G_sumForceVec + E_sumForceVec
        a_accelerationVec = totalSum_forceVec / self.m
        return a_accelerationVec

    def update_acceleration(self, all_objects, includeGravity=True):
        """
        Bruker fysikkformler oppgitt i Ergo Fysikk 2
        """
        self.a = self.get_updated_acceleration(all_objects, includeGravity)

    def update_velocity(self, time_passed):
        """
        ...
        """
        if self.immovable:
            return
        self.v=self.v+self.a*time_passed

    def update_position(self, time_passed):
        """
        ...
        """
        if self.immovable:
            return
        self.s=self.s+self.v*time_passed

#-#- variable definitions declarations
# et ladet partikkel
objA = PhysObj(
    100, # m i kg
    0.0000001, # q i C
    pygame.Vector2(0,0), # s
    pygame.Vector2(0,0), # v
    pygame.Vector2(0,0), # a
    pygame.Color(255,255,0)
)

ALL_OBJECTS = [objA]

#-#-function definitions
#-#-sim functions definitions
def add_object_with_vel(pos, color, mass, charge, vel, immovable=False):
    """
    Legger et objekt til i ALL_OBJECTS
    """
    global ALL_OBJECTS
    new_obj=PhysObj(
        mass,
        charge,
        pos,
        vel,
        pygame.Vector2(0,0),
        color
    )
    new_obj.immovable = immovable
    ALL_OBJECTS.append(new_obj)

def add_object(pos, color, mass, charge, immovable=False):
    """
    Legger et objekt til i ALL_OBJECTS
    """
    add_object_with_vel(pos, color, mass, charge, pygame.Vector2(0,0), immovable)

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

def draw_circle_in_plane(
                         window, # pygame.screen ?
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

def remove_closest_object(pos, objects):
    if len(objects) == 0:
        return objects
    winPos = transform_window_to_plane(pos)
    closestObj = objects[0]
    indexClosestObj = 0
    closestDist = -1
    index = 0
    for obj in objects:
        currentDist = (obj.s - winPos).length()
        if closestDist == -1 or currentDist < closestDist:
            closestDist = currentDist
            indexClosestObj = index
        index+=1
    objects.pop(indexClosestObj)
    return objects

def handle_input(event):
    """
    Kode for tastatur- og musrelaterte saker
    """
def handle_keydown(event):
    """
    Håndterer pygame.KEYDOWN
    """
    global object_size_pixels, user_is_dragging, ALL_OBJECTS
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[pygame.K_s]:
        new_object_size_pixels=int(input("Ny størrelse på objekt(mengde pixel, uint): "))
        object_size_pixels=new_object_size_pixels
    if pressed_keys[pygame.K_SPACE]:
        mx, my = pygame.mouse.get_pos()
        if 0<=mx<SCREEN_WIDTH and 0<=my<SCREEN_HEIGHT:
            user_is_dragging=True

    if pressed_keys[pygame.K_e]:
        mx, my = pygame.mouse.get_pos()
        input_mass=100000
        input_charge=-0.000000001
        pygame_vec=pygame.Vector2(mx, my)
        add_object(transform_window_to_plane(pygame_vec), generate_color(input_mass), input_mass, input_charge)
    if pressed_keys[pygame.K_p]:
        mx, my = pygame.mouse.get_pos()
        input_mass=100000
        input_charge=0.000000001
        pygame_vec=pygame.Vector2(mx, my)
        add_object(transform_window_to_plane(pygame_vec), generate_color(input_mass), input_mass, input_charge)
    if pressed_keys[pygame.K_1]:
        mx, my = pygame.mouse.get_pos()
        input_mass=999999999999999
        input_charge=2
        pygame_vec=pygame.Vector2(mx, my)
        add_object(transform_window_to_plane(pygame_vec), generate_color(input_mass), input_mass, input_charge)
    if pressed_keys[pygame.K_2]:
        mx, my = pygame.mouse.get_pos()
        input_mass=999999999999999
        input_charge=4
        pygame_vec=pygame.Vector2(mx, my)
        add_object(transform_window_to_plane(pygame_vec), generate_color(input_mass), input_mass, input_charge)
    if pressed_keys[pygame.K_3]:
        mx, my = pygame.mouse.get_pos()
        input_mass=999999999999999
        input_charge=-2
        pygame_vec=pygame.Vector2(mx, my)
        add_object(transform_window_to_plane(pygame_vec), generate_color(input_mass), input_mass, input_charge)
    if pressed_keys[pygame.K_4]:
        mx, my = pygame.mouse.get_pos()
        input_mass=9999999999999999
        input_charge=-4
        pygame_vec=pygame.Vector2(mx, my)
        add_object(transform_window_to_plane(pygame_vec), generate_color(input_mass), input_mass, input_charge)
    if pressed_keys[pygame.K_5]:
        mx, my = pygame.mouse.get_pos()
        input_mass=1
        input_charge=1
        pygame_vec=pygame.Vector2(mx, my)
        add_object(transform_window_to_plane(pygame_vec), generate_color(input_mass), input_mass, input_charge, True)
    if pressed_keys[pygame.K_6]:
        mx, my = pygame.mouse.get_pos()
        input_mass=1
        input_charge=5
        pygame_vec=pygame.Vector2(mx, my)
        add_object(transform_window_to_plane(pygame_vec), generate_color(input_mass), input_mass, input_charge, True)
    if pressed_keys[pygame.K_7]:
        mx, my = pygame.mouse.get_pos()
        input_mass=1
        input_charge=-1
        pygame_vec=pygame.Vector2(mx, my)
        add_object(transform_window_to_plane(pygame_vec), generate_color(input_mass), input_mass, input_charge, True)
    if pressed_keys[pygame.K_7]:
        mx, my = pygame.mouse.get_pos()
        input_mass=1
        input_charge=-5
        pygame_vec=pygame.Vector2(mx, my)
        add_object(transform_window_to_plane(pygame_vec), generate_color(input_mass), input_mass, input_charge, True)
    if pressed_keys[pygame.K_q]:
        mx, my = pygame.mouse.get_pos()
        input_mass=1
        input_charge=float(input("Charge: "))
        pygame_vec=pygame.Vector2(mx, my)
        add_object(transform_window_to_plane(pygame_vec), generate_color(input_mass), input_mass, input_charge, True)
    if pressed_keys[pygame.K_r]:
        ALL_OBJECTS.clear()
    if pressed_keys[pygame.K_t]:
        if len(ALL_OBJECTS) != 0:
            ALL_OBJECTS.pop()
        print(len(ALL_OBJECTS))
    if pressed_keys[pygame.K_y]:
        mx, my = pygame.mouse.get_pos()
        pos = pygame.Vector2(mx, my)
        ALL_OBJECTS = remove_closest_object(pos, ALL_OBJECTS)

def handle_keyup(event):
    """
    Håndterer pygame.KEYUP
    """
    global object_size_pixels, user_is_dragging
    pressed_keys = pygame.key.get_pressed()
    if not pressed_keys[pygame.K_SPACE]:
        mx, my = pygame.mouse.get_pos()
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
        input_charge=float(input("Charge: "))
        pygame_vec=pygame.Vector2(mx, my)
        add_object(transform_window_to_plane(pygame_vec), generate_color(input_mass), input_mass, input_charge)
    if mb3:
        input_mass=9999999999999999999
        input_charge=float(input("Charge: "))
        pygame_vec=pygame.Vector2(mx, my)
        add_object(transform_window_to_plane(pygame_vec), generate_color(input_mass), input_mass, input_charge)
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
#-#- misc div utility functions definitions
def roundToClosestMultiple(base, numToBeRounded):
   const_coefficient = int( numToBeRounded / base )
   return base * const_coefficient

def createColorFromList(input_list):
    return pygame.Color(input_list[0], input_list[1], input_list[2])

def correctLineByInterpolation(
        start, # start position
        end # end position
        ):
    pass

def isOutOfBounds(pos): # returns true if out of bounds
    global SCREEN_WIDTH, SCREEN_HEIGHT
    if pos.x > SCREEN_WIDTH or pos.x < 0:
        return True
    if pos.x > SCREEN_HEIGHT or pos.x < 0:
        return True
    return False

def correctColorValueBoundaries(color):
    corrected_color = color
    if ( corrected_color.r > 255 ): corrected_color.r = 255
    if ( corrected_color.g > 255 ): corrected_color.g = 255
    if ( corrected_color.b > 255 ): corrected_color.b = 255
    if ( corrected_color.r < 0 ): corrected_color.r = 0
    if ( corrected_color.g < 0 ): corrected_color.g = 0
    if ( corrected_color.b < 0 ): corrected_color.b = 0
    return corrected_color

def shortestDistToObjects(pos, objects):
    d = -1
    for obj in objects:
        d1 = (obj.s - pos).length()
        if d < 0 or d > d1:
            d = d1
    return d

#-#-electrical fields charges functions
def traceSampleChargePath(
    window,      # pygame window

    pos,         # pygame.Vector2
                 # start position of tracing
    charge,      # number
                 # sample charge
    all_objects, # array of PhysObj
                 # contains all objects in scene
    timestep,    # number

    maxTimeDepth # number
    ):
    """
    Tegner linjer som skal representere elektriskladde partikler
    sine veier. Kan brukes til å lage diagram av elektriske
    felt.
    """
    # constants/macros
    MIN_DISTANCE = 4.0 # meters
    MAX_SPEED = 0.008 # meters per second
    MASS = 1
    TARGET_COLOR = pygame.Color(0, 255, 255)
    INIT_COLOR = pygame.Color(255, 0, 0)
    TARGET_THICKNESS = 1
    INIT_THICKNESS = 10
    # variables
    maxTime = maxTimeDepth # seconds
    const_maxAmountOfTicks = maxTime / timestep + 1
    const_position_vec = pos # 2D vector
                             # simulated charge position
    const_particle_charge = charge # C
    particle = PhysObj(
            MASS,
            const_particle_charge,
            const_position_vec, # pos
            pygame.Vector2(0.0, 0.0), # vel
            pygame.Vector2(0.0, 0.0), # acc
            pygame.Color(0,0,255) # UNUSED
            )
    const_timestep = timestep
        # seconds per tick
    totalTimePassed = 0
    temp_start_pos = particle.s
    temp_end_pos = temp_start_pos
    distToNearestParticle = shortestDistToObjects(temp_start_pos, all_objects)
    thickness = INIT_THICKNESS
    thickness_increment = ((TARGET_THICKNESS - INIT_THICKNESS) / const_maxAmountOfTicks)
    field_color = INIT_COLOR
    field_color_increment = [0, 0, 0]
    field_color_increment[0] = int((TARGET_COLOR.r - INIT_COLOR.r) / const_maxAmountOfTicks)
    field_color_increment[1] = int((TARGET_COLOR.g - INIT_COLOR.g) / const_maxAmountOfTicks)
    field_color_increment[2] = int((TARGET_COLOR.b - INIT_COLOR.b) / const_maxAmountOfTicks)
    # line(surface, color, start_pos, end_pos) -> Rect
    # line(surfAce, color, start_pos, end_pos, width=1) -> Rect
    # draw a straight line
    # field lines
    while (
        # !(sample charge get close enough)
        # TODO
        (distToNearestParticle >= MIN_DISTANCE)
        and
        # !(maximum simulation time is reached)
        (totalTimePassed <= maxTime)
        and
        # !(speed is too high)
        (MAX_SPEED >= particle.v.length())
        ):
        temp_end_pos = particle.s
        temp_start_pos_screen = transform_plane_to_window(temp_start_pos)
        temp_end_pos_screen = transform_plane_to_window(temp_end_pos)
        wierd_value = (int(255 * min(1, (particle.get_updated_acceleration(all_objects, False).length() if particle.a.length() == 0.0 else particle.a.length())/0.000005)) + 125)
        wierd_value=int(wierd_value)
        wierd_value=wierd_value % 255
        pygame.draw.line(
            window,
            pygame.Color(wierd_value, field_color.g, field_color.b),
            temp_start_pos_screen,
            temp_end_pos_screen,
            int(thickness)
        )
        distToNearestParticle = shortestDistToObjects(temp_start_pos, all_objects)

        # take step forward in time
        particle.update_acceleration(all_objects, False)
        particle.update_velocity(const_timestep)
        particle.update_position(const_timestep)
        temp_start_pos = temp_end_pos
        field_color.r += field_color_increment[0]
        field_color.g += field_color_increment[1]
        field_color.b += field_color_increment[2]
        thickness += thickness_increment
        if thickness < 1: thickness = 1
        correctColorValueBoundaries( field_color )
        totalTimePassed+=const_timestep
        # ENDWHILE

def basicGridTrace(window, all_objects, timestep, gridPos, distBetween, gridWidth, gridHeight):
    DEPTH = 4
    temp_node = pygame.Vector2(0.0, 0.0)
    const_amountOfNodes = gridWidth * gridHeight
    position_grid = pygame.Vector2(0.0, 0.0)
    for a in range(const_amountOfNodes):
        position_grid.x = a % gridWidth
        position_grid.y = int(a / gridWidth)
        position_plane = (position_grid * distBetween) + gridPos
        traceSampleChargePath(window, position_plane, 0.0000000000001, all_objects,
                timestep, timestep*DEPTH)
        # draw_circle_in_plane(
        #         window, # pygame.screen ?
        #         pygame.Color(255,255,255), # pygame.Color
        #         position_plane, # pygame.Vector2
        #         10, # uint
        #         0 # uint
        #         )

#-#-update and draw
def update():
    """
    Kode for oppdatering av objekt osv.
    """
    global ALL_OBJECTS
    for _obj in ALL_OBJECTS:
        _obj.update_acceleration(ALL_OBJECTS, GRAVITY_ACTIVATED)
    # fart og posisjon må kalkuleres etter akselerasjoner,
    # siden akselerasjonene er relaterte til objektenes posisjon.
    for _obj in ALL_OBJECTS:
        _obj.update_velocity(dt)
        _obj.update_position(dt)

def drawTestGrid():
    global SCREEN_WIDTH, SCREEN_HEIGHT; DEFAULT_K_METERS_PER_PIXEL, ALL_OBJECTS
    gridPos = pygame.Vector2(0.0, 0.0)
    const_initPixelsBetween = PIXELS_BETWEEN_GRID_NODES
    distBetween = const_initPixelsBetween * DEFAULT_K_METERS_PER_PIXEL
    gridWidth = int(SCREEN_WIDTH / const_initPixelsBetween) + 1 # round up 
    gridHeight = int(SCREEN_HEIGHT / const_initPixelsBetween) + 1
    basicGridTrace(screen, ALL_OBJECTS, electrical_field_sim_timestep, gridPos, distBetween, gridWidth, gridHeight)


def draw():
    """
    Kode for tegning
    """
    global font, screen, ALL_OBJECTS, electrical_field_sim_timestep, DEFAULT_K_METER_PER_PIXEL, SCREEN_WIDTH, SCREEN_HEIGHT
    screen.fill(pygame.Color(0,0,0))
    drawTestGrid()

    for _obj in ALL_OBJECTS:
        # solid color
        draw_circle_in_plane(
            screen, 
            _obj.color,
            _obj.s,
            int(_obj.m*7E-22) if R_RELATIVE_TO_M else object_size_pixels*k_meters_per_pixel,
            0
        )
        # white outline
        draw_circle_in_plane(
            screen, 
            pygame.Color(255,255,255),
            _obj.s,
            int((_obj.m/1E6) / k_meters_per_pixel) if R_RELATIVE_TO_M else object_size_pixels * k_meters_per_pixel,
            max(1, k_meters_per_pixel)
        )

    text = font.render(str(k_meters_per_pixel)+"m/pixel", True, (200,200,20))
    screen.blit(text, transform_plane_to_window(pygame.Vector2(0, 50)))

    # update visible window surface
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

#-#- main loop running while loop
while RUNNING:

    handle_all_events()

    update()

    draw()

    clock.tick(FPS_TARGET)  # limits FPS to 60

pygame.quit()
