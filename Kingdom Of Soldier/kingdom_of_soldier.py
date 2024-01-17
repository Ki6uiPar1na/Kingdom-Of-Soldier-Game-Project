#import all the module below
import os
import sys
import math
import random
import pygame
import json

#load all the file path below
img_path = 'data/images/'

#bird class
class Bird:
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth
    
    def update(self):
        self.pos[0] += self.speed
        
    def render(self, surf, offset=(0, 0)):
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        surf.blit(self.img, (render_pos[0] % (surf.get_width() + self.img.get_width()) - self.img.get_width(), render_pos[1] % (surf.get_height() + self.img.get_height()) - self.img.get_height()))
        
class Birds:
    def __init__(self, bird_images, count=16):
        self.birds = []
        
        for i in range(count):
            self.birds.append(Bird((random.random() * 9, random.random() * 99), random.choice(bird_images), random.random() * 0.4 + 0.4, random.random() * 0.6 + 0.2))
        
        self.birds.sort(key=lambda x: x.depth)
    
    def update(self):
        for bird in self.birds:
            bird.update()
    
    def render(self, surf, offset=(0, 0)):
        for bird in self.birds:
            bird.render(surf, offset=offset)
#This is code for clouds
class Cloud: 
    def __init__(self, pos, img, speed, depth):
        self.pos = list(pos)
        self.img = img
        self.speed = speed
        self.depth = depth
    
    def update(self):
        self.pos[0] += self.speed
        
    def render(self, surf, offset=(0, 0)):
        render_pos = (self.pos[0] - offset[0] * self.depth, self.pos[1] - offset[1] * self.depth)
        surf.blit(self.img, (render_pos[0] % (surf.get_width() + self.img.get_width()) - self.img.get_width(), render_pos[1] % (surf.get_height() + self.img.get_height()) - self.img.get_height()))
        
class Clouds:
    def __init__(self, clouds, count=16):
        self.clouds = []
        
        for i in range(count):
            self.clouds.append(Cloud((random.random() * 1000000, random.random() * 1000000), random.choice(clouds), random.random() * 0.05 + 0.05, random.random() * 0.6 + 0.2))


    
    def render(self, surf, offset=(0, 0)):
        for cloud in self.clouds:
            cloud.render(surf, offset=offset)
# Ending of cloud code

def load_image(path):
    img = pygame.image.load(img_path + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_images(path):

    images = []
    for img_name in sorted(os.listdir(img_path + path)):
        images.append(load_image(path + '/' + img_name))
    return images

class Animation:
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0
    
    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images))
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1)
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.img_duration)]

#This is the code for entities
class game_entity:
    def __init__(self, game, e_type, pos, size):
        self.game = game
        self.type = e_type
        self.pos = list(pos)
        self.size = size
        self.velocity = [0, 0]
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        self.action = ''
        self.anim_offset = (-3, -3)
        self.flip = False
        self.set_action('idle')
        
        self.last_movement = [0, 0]
    
    def rect(self):
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def set_action(self, action):
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
        
    def update(self, tilemap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        for rect in tilemap.physics_reacts(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True
                self.pos[0] = entity_rect.x
        
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tilemap.physics_reacts(self.pos):
            if entity_rect.colliderect(rect):
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
                
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
            
        self.last_movement = movement
        
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
            
        self.animation.update()
        
    def render(self, surf, offset=(0, 0)):
        surf.blit(pygame.transform.flip(self.animation.img(), self.flip, False), (self.pos[0] - offset[0] + self.anim_offset[0], self.pos[1] - offset[1] + self.anim_offset[1]))
        
class Enemy(game_entity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'enemy', pos, size)
        
        self.walking = 1
        
    def update(self, tilemap, movement=(0, 0)):
        if self.walking:
            if tilemap.solid_check((self.rect().centerx + (-7 if self.flip else 7), self.pos[1] + 23)):
                if (self.collisions['right'] or self.collisions['left']):
                    self.flip = not self.flip
                else:
                    movement = (movement[0] - 0.5 if self.flip else 0.5, movement[1])
            else:
                self.flip = not self.flip
            self.walking = max(0, self.walking - 1)
            if not self.walking:
                dis = (self.game.player.pos[0] - self.pos[0], self.game.player.pos[1] - self.pos[1])
                if (abs(dis[1]) < 16):
                    if (self.flip and dis[0] < 0):
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx - 7, self.rect().centery], -1.5, 0])
                    if (not self.flip and dis[0] > 0):
                        self.game.sfx['shoot'].play()
                        self.game.projectiles.append([[self.rect().centerx + 7, self.rect().centery], 1.5, 0])
                        
        elif random.random() < 0.01:
            self.walking = random.randint(30, 120)
        
        super().update(tilemap, movement=movement)
        
        if movement[0] != 0:
            self.set_action('run')
        else:
            self.set_action('idle')
            
        if abs(self.game.player.dashing) >= 50:
            if self.rect().colliderect(self.game.player.rect()):
                self.game.screenshake = max(16, self.game.screenshake)
                self.game.sfx['hit'].play()
                for i in range(30):
                    angle = random.random() * math.pi * 2
                    speed = random.random() * 5
                    self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
                return True
            
    def render(self, surf, offset=(0, 0)):
        super().render(surf, offset=offset)
        
        if self.flip:
            surf.blit(pygame.transform.flip(self.game.assets['gun'], True, False), (self.rect().centerx - 4 - self.game.assets['gun'].get_width() - offset[0], self.rect().centery - offset[1]))
        else:
            surf.blit(self.game.assets['gun'], (self.rect().centerx + 4 - offset[0], self.rect().centery - offset[1]))

class Player(game_entity):
    def __init__(self, game, pos, size):
        super().__init__(game, 'player', pos, size)
        self.air_time = 0
        self.jumps = 1
        self.wall_slide = False
        self.dashing = 0
    
    def update(self, tilemap, movement=(0, 0)):
        super().update(tilemap, movement=movement)
        
        self.air_time += 1
        
        if self.air_time > 120:
            if not self.game.dead:
                self.game.screenshake = max(16, self.game.screenshake)
            self.game.dead += 1
        
        if self.collisions['down']:
            self.air_time = 0
            self.jumps = 1
            
        self.wall_slide = False
        if (self.collisions['right'] or self.collisions['left']) and self.air_time > 4:
            self.wall_slide = True
            self.velocity[1] = min(self.velocity[1], 0.5)
            if self.collisions['right']:
                self.flip = False
            else:
                self.flip = True
            self.set_action('wall_slide')
        
        if not self.wall_slide:
            if self.air_time > 4:
                self.set_action('jump')
            elif movement[0] != 0:
                self.set_action('run')
            else:
                self.set_action('idle')
        
        if abs(self.dashing) in {60, 50}:
            for i in range(20):
                angle = random.random() * math.pi * 2
                speed = random.random() * 0.5 + 0.5
                pvelocity = [math.cos(angle) * speed, math.sin(angle) * speed]
                self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
        if self.dashing > 0:
            self.dashing = max(0, self.dashing - 1)
        if self.dashing < 0:
            self.dashing = min(0, self.dashing + 1)
        if abs(self.dashing) > 50:
            self.velocity[0] = abs(self.dashing) / self.dashing * 8
            if abs(self.dashing) == 51:
                self.velocity[0] *= 0.1
            pvelocity = [abs(self.dashing) / self.dashing * random.random() * 3, 0]
            self.game.particles.append(Particle(self.game, 'particle', self.rect().center, velocity=pvelocity, frame=random.randint(0, 7)))
                
        if self.velocity[0] > 0:
            self.velocity[0] = max(self.velocity[0] - 0.1, 0)
        else:
            self.velocity[0] = min(self.velocity[0] + 0.1, 0)
    
    def render(self, surf, offset=(0, 0)):
        if abs(self.dashing) <= 50:
            super().render(surf, offset=offset)
            
    def jump(self):
        if self.wall_slide:
            if self.flip and self.last_movement[0] < 0:
                self.velocity[0] = 3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
            elif not self.flip and self.last_movement[0] > 0:
                self.velocity[0] = -3.5
                self.velocity[1] = -2.5
                self.air_time = 5
                self.jumps = max(0, self.jumps - 1)
                return True
        #it can controle jump and one jump height
        elif self.jumps:
            self.velocity[1] = -5
            self.jumps -= 1
            self.air_time = 8
            return True
    
    def dash(self):
        if not self.dashing:
            self.game.sfx['dash'].play()
            if self.flip:
                self.dashing = -60
            else:
                self.dashing = 60
#end of entities part

#this is for particle
class Particle:
    def __init__(self, game, p_type, pos, velocity=[0, 0], frame=0):
        self.game = game
        self.type = p_type
        self.pos = list(pos)
        self.velocity = list(velocity)
        self.animation = self.game.assets['particle/' + p_type].copy()
        self.animation.frame = frame
    
    def update(self):
        kill = False
        if self.animation.done:
            kill = True
        
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        
        self.animation.update()
        
        return kill
    
    def render(self, surf, offset=(0, 0)):
        img = self.animation.img()
        surf.blit(img, (self.pos[0] - offset[0] - img.get_width() // 2, self.pos[1] - offset[1] - img.get_height() // 2))

#this is end of particle code

#This is the code for tile-map
AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0, 1)])): 0,
    tuple(sorted([(1, 0), (0, 1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0, 1)])): 2, 
    tuple(sorted([(-1, 0), (0, -1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0, -1)])): 4,
    tuple(sorted([(-1, 0), (0, -1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0, -1)])): 6,
    tuple(sorted([(1, 0), (0, -1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1, 0), (0, 1), (0, -1)])): 8,
}
NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0, 0), (-1, 1), (0, 1), (1, 1)]
PHYSICS_TILES = {'grass', 'stone'}
AUTOTILE_TYPES = {'grass', 'stone'}

class Tilemap:
    def __init__(self, game, tile_size=16):
        self.game = game
        self.tile_size = tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
        
    def extract(self, id_pairs, keep=False):
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)
                    
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            if (tile['type'], tile['variant']) in id_pairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]
        
        return matches
    
    def new_tiles(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size))
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
    
    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, f)
        f.close()
        
    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()
        
        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']
        
    def solid_check(self, pos):
        tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return self.tilemap[tile_loc]
    
    def physics_reacts(self, pos):
        rects = []
        for tile in self.new_tiles(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
        return rects
    
    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]

    def render(self, surf, offset=(0, 0)):
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
            
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width()) // self.tile_size + 1):
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tilemap:
                    tile = self.tilemap[loc]
                    surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
#end of tilemap code 

#This is the beggining of main game class
class Game:
    def __init__(self):
        pygame.init()

        #create the game screen
        pygame.display.set_caption('Kingdom Of Soldier')
        self.screen = pygame.display.set_mode((1000, 600))

        #create surface and clock
        self.display = pygame.Surface((320, 240), pygame.SRCALPHA)
        self.display_2 = pygame.Surface((320, 240))
        self.clock = pygame.time.Clock()
        
        #initialize game elements
        self.movement = [False, False]
        self.show_opening_interface()
        
        #load all the assets here
        self.assets = {
            
            #load image

            'decor': load_images('tiles/decor'),
            'grass': load_images('tiles/grass'),
            'large_decor': load_images('tiles/large_decor'),
            'stone': load_images('tiles/stone'),
            'player': load_image('entities/player.png'),
            'background': load_image('background.jpg'),
            'clouds': load_images('clouds'),
            'birds': load_images('birds'),
            'gun': load_image('gun.png'),
            'projectile': load_image('projectile.png'),

            #give image animation

            'enemy/idle': Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run': Animation(load_images('entities/enemy/run'), img_dur=4),
            'player/idle': Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run': Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump': Animation(load_images('entities/player/jump')),
            'player/slide': Animation(load_images('entities/player/slide')),
            'player/wall_slide': Animation(load_images('entities/player/wall_slide')),
            'particle/leaf': Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle': Animation(load_images('particles/particle'), img_dur=6, loop=False),

        }
        #controle the sound of the all entity
        self.sfx = {

            #load sound
            'jump': pygame.mixer.Sound('data/sfx/jump.wav'),
            'dash': pygame.mixer.Sound('data/sfx/dash.wav'),
            'hit': pygame.mixer.Sound('data/sfx/hit.wav'),
            'shoot': pygame.mixer.Sound('data/sfx/shoot.wav'),
            'ambience': pygame.mixer.Sound('data/sfx/ambience.wav'),
        }
        
        #controle the sound volume
        self.sfx['ambience'].set_volume(0.7)
        self.sfx['shoot'].set_volume(0.7)
        self.sfx['hit'].set_volume(0.8)
        self.sfx['dash'].set_volume(0.3)
        self.sfx['jump'].set_volume(0.7)
    
        #number of clouds image and birds image in the sky
        self.clouds = Clouds(self.assets['clouds'], count=16)
        self.birds = Birds(self.assets['birds'], count=16)
        
        self.player = Player(self, (50, 50), (8, 15))
        
        self.tilemap = Tilemap(self, tile_size=16)
        
        #intitalize the level of the game
        self.level = 0
        self.level_up(self.level)
        
        self.screenshake = 0

        #set the health initially 3
        self.health = 3

        #score and hitcount  is here
        self.score = 0
        self.player_hit_count = 0
    
    #create opening inteface function 
    def show_opening_interface(self):

        developer_font = pygame.font.Font(None, 25)
        # Developer names at bottom right corner
        developer_font = pygame.font.Font(None, 18)
        developer_text1 = developer_font.render("Developed by:", True, (255, 255, 0))
        developer_text2 = developer_font.render("Md. Khairul Islam", True, (255, 255, 255))
        developer_text3 = developer_font.render("Mst. Rokeya Akther", True, (255, 255, 255))
        self.screen.blit(developer_text1, (self.screen.get_width() - developer_text1.get_width() - 10, self.screen.get_height() - 45))
        self.screen.blit(developer_text2, (self.screen.get_width() - developer_text2.get_width() - 10, self.screen.get_height() - 30))
        self.screen.blit(developer_text3, (self.screen.get_width() - developer_text3.get_width() - 10, self.screen.get_height() - 15))

        # Supervisor name at bottom left corner
        supervisor_font = pygame.font.Font(None, 18)
        supervisor_text = supervisor_font.render("Supervised by:", True, (255, 255, 0))
        supervisor_text2 = supervisor_font.render("Dr. A. H. M. Kamal", True, (255, 255, 255))
        supervisor_text3 = supervisor_font.render("Professor, Department of Computer Science and Engineering, JKKNIU", True, (255, 255, 255))

        # supervisor_text4 = supervisor_font.render("Department of Computer Science and Engineering, JKKNIU", True, (255, 255, 255))
        self.screen.blit(supervisor_text, (10, self.screen.get_height() - 45))
        self.screen.blit(supervisor_text2, (10, self.screen.get_height() - 30))
        self.screen.blit(supervisor_text3, (10, self.screen.get_height() - 15))

        font = pygame.font.Font(None,36)
        button_width, button_height = 200, 50
        
        #create button
        start_button_rect = pygame.Rect((self.screen.get_width() - button_width) // 2, 300, button_width, button_height)
        close_button_rect = pygame.Rect((self.screen.get_width() - button_width) // 2, 400, button_width, button_height)

        #load interface background image
        background_image = pygame.image.load('data/bg.jpg')
        
        #caption font size
        caption_font = pygame.font.Font(None, 80)
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Check if the mouse click is within the button boundaries
                    if start_button_rect.collidepoint(event.pos):
                        return  # Exit the opening interface and start the game
                    elif close_button_rect.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()


            self.screen.blit(background_image, (0, 0))

            pygame.draw.rect(self.screen, (51, 153, 102), start_button_rect)
            pygame.draw.rect(self.screen, (128, 0, 0), close_button_rect)

            #rendering button
            start_text = font.render("PLAY", True, (255, 255, 255))
            close_text = font.render("EXIT", True, (255, 255, 255))


            self.screen.blit(start_text, ((self.screen.get_width() - start_text.get_width()) // 2, 315))
            self.screen.blit(close_text, ((self.screen.get_width() - close_text.get_width()) // 2, 415))

            game_caption = caption_font.render("Kingdom Of Soldier", True, (255, 255, 255))
            self.screen.blit(game_caption, ((self.screen.get_width() - game_caption.get_width()) // 2, 80))

            pygame.display.flip() #make all the things visible
            self.clock.tick(60) #frame rate

    def level_up(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')
        
        self.leaf_spawners = []
        for tree in self.tilemap.extract([('large_decor', 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
            
        self.enemies = []
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos']
                self.player.air_time = 0
            else:
                self.enemies.append(Enemy(self, spawner['pos'], (8, 15)))
        
        #initialization
        self.projectiles = []
        self.particles = []
        
        self.scroll = [0, 0]
        self.dead = 0
        self.transition = -30
        
    def run(self):
        pygame.mixer.music.load('data/music.mp3')
        pygame.mixer.music.set_volume(0.2)
        pygame.mixer.music.play(-1)
        
        self.sfx['ambience'].play(-1)

        while True:
            self.display.fill((0, 0, 0, 0))
            self.display_2.blit(self.assets['background'], (0, 0))
            
            self.screenshake = max(0, self.screenshake - 1)
            
            if not len(self.enemies):
                self.transition += 1
                if self.transition > 30:
                    self.level = min(self.level + 1, len(os.listdir('data/maps')) - 1)
                    self.level_up(self.level)
                    #score update
                    self.score += 1000

            if self.transition < 0:
                self.transition += 1
            
            if self.dead:
                self.dead += 1
                if self.dead >= 10:
                    self.transition = min(30, self.transition + 1)
                if self.dead > 40:
                    self.level_up(self.level)
            
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            #clouds rendering
            self.clouds.render(self.display_2, offset = render_scroll)
            self.clouds.render(self.display_2, offset=render_scroll)

            #birds rendering
            self.birds.update()
            self.birds.render(self.display_2, offset=render_scroll)
            
            self.tilemap.render(self.display, offset=render_scroll)
            
            #enemy kill points
            for enemy in self.enemies.copy():
                kill = enemy.update(self.tilemap, (0, 0))
                enemy.render(self.display, offset=render_scroll)
                if kill:
                    self.enemies.remove(enemy)
                    self.score += 100
            
            if not self.dead:
                self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                self.player.render(self.display, offset=render_scroll)

            #calculate the score for each level
            if self.dead:
                if self.score < 1300:
                    self.score = 0
                elif self.score >= 1300 and self.score < 3500:
                    self.score = 1300
                elif self.score >= 3500:
                    self.score = 3500

            for projectile in self.projectiles.copy():
                projectile[0][0] += projectile[1]
                projectile[2] += 1
                img = self.assets['projectile']
                self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                if self.tilemap.solid_check(projectile[0]):
                    self.projectiles.remove(projectile)

                elif projectile[2] > 180:
                    self.projectiles.remove(projectile)

                elif abs(self.player.dashing) < 50:
                    if self.player.rect().collidepoint(projectile[0]):
                        self.projectiles.remove(projectile)

                        self.player_hit_count += 1
                        self.health -= 1
                        self.sfx['hit'].play()
                        
                        if self.player_hit_count >= 3:
                            self.dead += 1
                            self.player_hit_count = 0
                        if self.health <= 0:
                            self.dead += 1
                            self.health = 3
                    
            display_mask = pygame.mask.from_surface(self.display)
            display_sillhouette = display_mask.to_surface(setcolor=(0, 0, 0, 180), unsetcolor=(0, 0, 0, 0))
            for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                self.display_2.blit(display_sillhouette, offset)
            
            for particle in self.particles.copy():
                kill = particle.update()
                particle.render(self.display, offset=render_scroll)
                if particle.type == 'leaf':
                    particle.pos[0] += math.sin(particle.animation.frame * 0.035) * 0.3
                if kill:
                    self.particles.remove(particle)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        if self.player.jump():
                            self.sfx['jump'].play()
                    if event.key == pygame.K_SPACE:
                        self.player.dash()
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT: 
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT:
                        self.movement[1] = False
            
            #controle the opening transition that is circle
            #we can controle it to square
            if self.transition:
                transition_surf = pygame.Surface(self.display.get_size())
                #sqaure
                square_size = (30 - abs(self.transition)) * 16  # Adjust the multiplier to control the size of the square
                square_rect = pygame.Rect((self.display.get_width() - square_size) // 2, (self.display.get_height() - square_size) // 2, square_size, square_size)
                # pygame.draw.circle(transition_surf, (255, 255, 255), (self.display.get_width() // 2, self.display.get_height() // 2), (30 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.display.blit(transition_surf, (0, 0))
    
            self.display_2.blit(self.display, (0, 0))
            self.render_score() #rendereing
            # Render the lives on the screen
            self.render_health()

            screenshake_offset = (random.random() * self.screenshake - self.screenshake / 2, random.random() * self.screenshake - self.screenshake / 2)
            self.screen.blit(pygame.transform.scale(self.display_2, self.screen.get_size()), screenshake_offset)
            pygame.display.update()
            self.clock.tick(60)
    def render_score(self):
        font = pygame.font.Font(None, 18)  # Adjust the font size here

        # Render the score
        score_text = font.render(f"Score: {self.score}", True, (255, 0, 0))  # Set the color to red
        score_rect = score_text.get_rect()
        score_rect.topleft = (10, 10)

        # Create a surface for the score box
        score_box_width = score_rect.width + 20  # Adjust the width of the box
        score_box_height = score_rect.height + 20  # Adjust the height of the box
        score_box_surface = pygame.Surface((score_box_width, score_box_height), pygame.SRCALPHA)
        # pygame.draw.rect(score_box_surface, (0, 0, 0, 0), score_box_surface.get_rect())  # Set the color of the box (black with alpha)

        # Blit the score box surface and then the score text on top of it
        self.display_2.blit(score_box_surface, score_rect.topleft)
        self.display_2.blit(score_text, (score_rect.left + 10, score_rect.top + 5))

        # Render the level on the right side
        level_text = font.render(f"Level: {self.level + 1}", True, (255, 0, 0))  # Set the color to red
        level_rect = level_text.get_rect()
        level_rect.right = self.display_2.get_width() - 10  # Adjust the position to the right side
        level_rect.top = 10  # Adjust the vertical position as needed

        # Create a surface for the level box
        level_box_width = level_rect.width + 20  # Adjust the width of the box
        level_box_height = level_rect.height + 10  # Adjust the height of the box
        level_box_surface = pygame.Surface((level_box_width, level_box_height), pygame.SRCALPHA)
        # pygame.draw.rect(level_box_surface, (0, 0, 0, 0), level_box_surface.get_rect())  # Set the color of the box (black with alpha)

        # Blit the level box surface and then the level text on top of it
        self.display_2.blit(level_box_surface, level_rect.topleft)
        self.display_2.blit(level_text, (level_rect.left + 10, level_rect.top + 5))

    def render_health(self):
        font = pygame.font.Font(None, 18)  # Adjust the font size here

        # Render the lives
        health_text = font.render(f"Health: {self.health}", True, (255, 0, 0))  # Set the color to red
        self.display_2.blit(health_text, (20, 30))  # Adjust the position as needed
    
Game().run()