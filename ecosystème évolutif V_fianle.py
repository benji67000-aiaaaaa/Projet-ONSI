import pygame
import random

# 1. PARAMÈTRES 
LARGEUR =1350
HAUTEUR = 750
FPS = 60
M=0.005 #cout du maintien du metabolisme 

#2 CLASSE DES CRÉATURES:  LE PEUPLE GRUBZZ
class Creature:

    # nombreuxd arguments correspondent aux gènes, avec des valeurs par défaut aléatoires
    def __init__(self, x, y, generation=0, g_vitesse=None, g_fuite=None, g_social=None, g_appetit=None, g_attaque=None, clan=None):
        self.x = x
        self.y = y
        self.generation = generation
        self.energie = 100
        self.rayon = 5
        self.clan = clan
        
        
        self.gene_vitesse = g_vitesse if g_vitesse is not None else random.uniform(0.3, 1)
        self.gene_fuite = g_fuite if g_fuite is not None else random.uniform(10, 85)
        self.gene_social = g_social if g_social is not None else random.uniform(5, 50)
        self.gene_appetit = g_appetit if g_appetit is not None else random.uniform(5, 60)
        self.gene_attaque = g_attaque if g_attaque is not None else random.uniform(0.5, 2.0)

        # Initialisation du mouvement
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.appliquer_vitesse_gene() # On aligne la vitesse initiale avec le gène de vitesse

    def appliquer_vitesse_gene(self):
        actuelle = (self.vx**2 + self.vy**2)**0.5  # Calcul de la vitesse actuelle (Pythagore)
        if actuelle == 0: return # Éviter la division par zéro
        ratio = self.gene_vitesse / actuelle  # On redimensionne vx et vy pour que la longueur du vecteur soit égale au gène
        self.vx *= ratio
        self.vy *= ratio
    
    
    def manger(self, nourritures):
        for nourriture in nourritures:
            distance = ((self.x - nourriture['x'])**2 + (self.y - nourriture['y'])**2)**0.5
            if distance < 10:
                self.energie += 100
                nourritures.remove(nourriture)
                break
    
    def bouger(self, creatures, nourritures):
        cible, action = self.radar(creatures, nourritures)
        force = 0.1 # "prix" en énergie pour changer de direction 

        if cible:
            # Récupération des coordonnées x,y de la cible
            tx = cible.x if hasattr(cible, 'x') else cible['x']
            ty = cible.y if hasattr(cible, 'y') else cible['y']
            dx, dy = tx - self.x, ty - self.y
            dist = (dx**2 + dy**2)**0.5

            if action == "FUITE":
                self.vx -= dx * force
                self.vy -= dy * force
            elif action == "CHASSE":
                # On fonce vers l'ennemi
                self.vx += dx * force
                self.vy += dy * force
            elif action == "ATTRACTION":
                self.vx += dx * force
                self.vy += dy * force
            elif action == "SOCIAL":
                # "espace vital" pour eviter qu'ils restent collés
                if dist > 30: #  rejoint le groupe
                    self.vx += dx * (force * 0.5)
                    self.vy += dy * (force * 0.5)
                elif dist < 15: #  s'écarte
                    self.vx -= dx * force
                    self.vy -= dy * force

        # Appliquer le mouvement et limiter la vitesse
        self.appliquer_vitesse_gene()
        self.x += self.vx
        self.y += self.vy
        
        if self.x < 0 or self.x > LARGEUR: self.vx *= -1
        if self.y < 0 or self.y > HAUTEUR: self.vy *= -1

        # Perte d'énergie liée au mouvement et aux gènes
        self.energie -= M + 0.02*(self.gene_vitesse**2) + (self.gene_fuite * 0.0005) + (self.gene_social * 0.0003) + (self.gene_appetit * 0.0002) + (self.gene_attaque * 0.0004)



    def apte_a_reproduction(self):
     return self.energie > 150  # Seuil d'énergie

    def reproduire(self):
        self.energie -= 80
    
        # 1. On calcule les mutations 
        m_vitesse = self.gene_vitesse + random.uniform(-0.15, 0.15)
        m_fuite = self.gene_fuite + random.uniform(-10, 10)
        m_social = self.gene_social + random.uniform(-5, 5)
        m_appetit = self.gene_appetit + random.uniform(-5, 5)
        m_attaque = self.gene_attaque + random.uniform(-0.2, 0.2)

        # 2. On crée le bébé en lui "donnant" ces valeurs
        bebe = Creature(
            self.x + random.randint(-20, 20),
            self.y + random.randint(-20, 20),
            generation = self.generation + 1,
            g_vitesse = m_vitesse,  
            g_fuite = m_fuite,
            g_social = m_social,
            g_appetit = m_appetit,
            g_attaque = m_attaque,
            clan = self.clan
         )
    
        bebe.energie = 80  
        return bebe

    def radar(self, creatures, nourritures):
        cible = None
        action = None

        if not cible:
            plus_proche_dist = self.gene_appetit
            for n in nourritures:
                d = ((self.x - n['x'])**2 + (self.y - n['y'])**2)**0.5
                if d < plus_proche_dist:
                    plus_proche_dist = d
                    cible = n
                    action = "ATTRACTION"

        # Scan des ennemis (clan opposé), fuite ou chasse 
        if not cible:
            plus_proche_dist = self.gene_fuite  # portée de détection des ennemis = gene_fuite
            for c in creatures:
                if c == self or c.clan == self.clan: continue  # on ignore les alliés
                d = ((self.x - c.x)**2 + (self.y - c.y)**2)**0.5
                if d < plus_proche_dist:
                    plus_proche_dist = d
                    cible = c
                    # Comparaison des puissances d'attaque et de l'énergie
                    ma_puissance = self.energie * self.gene_attaque
                    puissance_ennemie = c.energie * c.gene_attaque
                    if ma_puissance >= puissance_ennemie:
                        action = "CHASSE"   
                    else:
                        action = "FUITE"    

        if not cible:
            plus_proche_dist = self.gene_social
            for c in creatures:
                if c == self or c.clan != self.clan: continue  # on ignore les ennemis 
                d = ((self.x - c.x)**2 + (self.y - c.y)**2)**0.5
                if d < plus_proche_dist:
                    plus_proche_dist = d
                    cible = c
                    action = "SOCIAL"

        return cible, action

    
    COEFF_ATTAQUE = 30

    def combattre(self, creatures):
        # On cherche un ennemi à portée de contact
        for ennemi in creatures[:]:
            if ennemi.clan == self.clan: continue
            distance = ((self.x - ennemi.x)**2 + (self.y - ennemi.y)**2)**0.5
            if distance < self.rayon + ennemi.rayon:
                ma_puissance     = self.energie  * self.gene_attaque
                puissance_ennemie = ennemi.energie * ennemi.gene_attaque
                if ma_puissance >= puissance_ennemie:
                    self.energie += ennemi.energie * 0.4  # récupère 40% de l'énergie de la victime
                    ennemi.energie = 0                    # la victime est éliminée
                break
         
    

    def dessiner(self, écran):
     intensite =max(0, min(1, self.energie / 150))  # Ratio de 0 à 1
     if self.clan ==0:
         couleur = (int(50 * intensite), int(150 * intensite), int(255 * intensite))
     else:
         couleur = (int(255 * intensite), int(50 * intensite), int(50 * intensite))
     pygame.draw.circle(écran, couleur, (int(self.x), int(self.y)), self.rayon)

# 3. INITIALISATION PYGAME
pygame.init()
écran = pygame.display.set_mode((LARGEUR, HAUTEUR))
horloge = pygame.time.Clock()

# 4. CRÉATION DE LA LISTE DE 
creatures = []
NB_PAR_CLAN = 15

for i in range(NB_PAR_CLAN):
    # Clan 0 : Apparaît à GAUCHE (Bleu)
    creatures.append(Creature(
        random.randint(50, 300), 
        random.randint(50, HAUTEUR-50), 
        clan=0
    ))
    
    # Clan 1 : Apparaît à DROITE (Rouge)
    creatures.append(Creature(
        random.randint(LARGEUR-300, LARGEUR-50), 
        random.randint(50, HAUTEUR-50), 
        clan=1
    ))

nourritures = []

# 5. STATS EN DIRECt
historique = {
    'pop_bleus': [],
    'pop_rouges': [],
    'vitesse_bleus': [],
    'vitesse_rouges': [],
    'fuite_bleus': [],
    'fuite_rouges': [],
    'social_bleus': [],
    'social_rouges': [],
    'appetit_bleus': [],
    'appetit_rouges': [],
    'attaque_bleus': [],
    'attaque_rouges': [],
    'gen_max': []
}
frame_count = 0
pause = False

#Fonction qui calcule moyennes génétiques des deux clans
def calculer_stats(creatures):
    if not creatures:
        return None
    bleus = [c for c in creatures if c.clan == 0]
    rouges = [c for c in creatures if c.clan == 1]
    def moy(liste, gene):
        return sum(getattr(c, gene) for c in liste) / len(liste) if liste else 0
    return {
        'total': len(creatures),
        'bleus': len(bleus),
        'rouges': len(rouges),
        'gen_max': max(c.generation for c in creatures) if creatures else 0,
        'vitesse_bleus':  moy(bleus,  'gene_vitesse'),
        'vitesse_rouges': moy(rouges, 'gene_vitesse'),
        'fuite_bleus':    moy(bleus,  'gene_fuite'),
        'fuite_rouges':   moy(rouges, 'gene_fuite'),
        'social_bleus':   moy(bleus,  'gene_social'),
        'social_rouges':  moy(rouges, 'gene_social'),
        'appetit_bleus':  moy(bleus,  'gene_appetit'),
        'appetit_rouges': moy(rouges, 'gene_appetit'),
        'attaque_bleus':  moy(bleus,  'gene_attaque'),
        'attaque_rouges': moy(rouges, 'gene_attaque'),
    }

# Fonction  dessin mini-graphique d'évolution 
def dessiner_graphique(écran, valeurs, couleur, x, y, w, h):
    if len(valeurs) < 2:
        return
    # On normalise entre min et max pour faire tenir dans la boîte
    vmin, vmax = min(valeurs), max(valeurs)
    if vmax == vmin:
        vmax = vmin + 1
    points = []
    for i, v in enumerate(valeurs):
        px = x + int(i / (len(valeurs) - 1) * w)
        py = y + h - int((v - vmin) / (vmax - vmin) * h)
        points.append((px, py))
    pygame.draw.lines(écran, couleur, False, points, 2)
    # Valeur actuelle à droite
    font_petit = pygame.font.Font(None, 22)
    label = font_petit.render(f"{valeurs[-1]:.2f}", True, couleur)
    écran.blit(label, (x + w + 5, y + h // 2 - 7))

# Affichage du panneau de stats
def afficher_panneau_stats(écran, creatures, historique):
    # Fond semi-transparent
    overlay = pygame.Surface((LARGEUR, HAUTEUR))
    overlay.set_alpha(215)
    overlay.fill((15, 15, 25))
    écran.blit(overlay, (0, 0))

    stats = calculer_stats(creatures)
    if not stats:
        return

    font_titre  = pygame.font.Font(None, 52)
    font_normal = pygame.font.Font(None, 34)
    font_petit  = pygame.font.Font(None, 26)

    # Titre
    titre = font_titre.render("STATISTIQUES DE L'ÉCOSYSTÈME", True, (255, 255, 255))
    écran.blit(titre, (LARGEUR // 2 - titre.get_width() // 2, 30))

    pygame.draw.line(écran, (80, 80, 80), (50, 90), (LARGEUR - 50, 90), 1)

    #Colonne gauche 
    y = 110
    écran.blit(font_normal.render(f"Population totale : {stats['total']}", True, (220, 220, 220)), (60, y)); y += 40
    écran.blit(font_normal.render(f"Grubz bleus  : {stats['bleus']}", True, (100, 180, 255)), (80, y)); y += 35
    écran.blit(font_normal.render(f"Grubz rouges : {stats['rouges']}", True, (255, 100, 100)), (80, y)); y += 45
    écran.blit(font_normal.render(f"Génération max : {stats['gen_max']}", True, (200, 255, 200)), (60, y)); y += 55

    # Tableau comparatif 
    écran.blit(font_normal.render("Trait moyen", True, (180, 180, 180)), (60, y))
    écran.blit(font_normal.render("Bleus", True, (100, 180, 255)), (340, y))
    écran.blit(font_normal.render("Rouges", True, (255, 100, 100)), (530, y))
    y += 38

    lignes = [
        ("Vitesse",   f"{stats['vitesse_bleus']:.3f}",  f"{stats['vitesse_rouges']:.3f}"),
        ("Fuite",     f"{stats['fuite_bleus']:.1f}",    f"{stats['fuite_rouges']:.1f}"),
        ("Social",    f"{stats['social_bleus']:.1f}",   f"{stats['social_rouges']:.1f}"),
        ("Appétit",   f"{stats['appetit_bleus']:.1f}",  f"{stats['appetit_rouges']:.1f}"),
        ("Attaque",   f"{stats['attaque_bleus']:.2f}",  f"{stats['attaque_rouges']:.2f}"),
    ]
    for nom, val_b, val_r in lignes:
        écran.blit(font_petit.render(nom, True, (200, 200, 200)), (80, y))
        écran.blit(font_petit.render(val_b, True, (100, 180, 255)), (340, y))
        écran.blit(font_petit.render(val_r, True, (255, 100, 100)), (530, y))
        y += 32

    #  Colonne droite 
    if len(historique['pop_bleus']) >= 2:
        gx, gy, gw, gh = 730, 110, 480, 70

        graphs = [
            ("Population bleus",    historique['pop_bleus'],      (100, 180, 255)),
            ("Population rouges",   historique['pop_rouges'],     (255, 100, 100)),
            ("Vitesse moy. bleus",  historique['vitesse_bleus'],  (100, 220, 255)),
            ("Vitesse moy. rouges", historique['vitesse_rouges'], (255, 160, 100)),
            ("Attaque moy. bleus",  historique['attaque_bleus'],  ( 80, 160, 255)),
            ("Attaque moy. rouges", historique['attaque_rouges'], (255,  80,  80)),
        ]
        for label, valeurs, couleur in graphs:
            écran.blit(font_petit.render(label, True, couleur), (gx, gy - 18))
            pygame.draw.rect(écran, (30, 30, 45), (gx, gy, gw, gh))
            pygame.draw.rect(écran, (60, 60, 80), (gx, gy, gw, gh), 1)
            dessiner_graphique(écran, valeurs, couleur, gx, gy, gw, gh)
            gy += gh + 35

    inst = font_petit.render("Appuyez sur ESPACE pour reprendre la simulation", True, (150, 255, 150))
    écran.blit(inst, (LARGEUR // 2 - inst.get_width() // 2, HAUTEUR - 45))

# 5. BOUCLE PRINCIPALE 
running = True
while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # ESPACE pour mettre en pause / reprendre
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pause = not pause

    # Si pause, afficher stats et att
    if pause:
        afficher_panneau_stats(écran, creatures, historique)
        pygame.display.flip()
        horloge.tick(FPS)
        continue

    écran.fill((0, 0, 0))
    
    if random.random() < 0.035:  
        nourritures.append({
            'x': random.randint(0, LARGEUR),
            'y': random.randint(0, HAUTEUR)
        })
    
    for nourriture in nourritures:
        pygame.draw.rect(écran, (255, 255, 0), (nourriture['x']-3, nourriture['y']-3, 6, 6))
    
    little_grubz = []
    for creature in creatures:
        creature.bouger(creatures, nourritures)
        creature.manger(nourritures)
        creature.combattre(creatures)  
        creature.dessiner(écran)
        if creature.apte_a_reproduction():
            bebe = creature.reproduire()
            little_grubz.append(bebe)
    
    creatures = [c for c in creatures if c.energie > 0]
    creatures.extend(little_grubz)

    # Enregistrement de l'historique toutes les 60 frames (~1 seconde) pour stats
    frame_count += 1
    if frame_count % 60 == 0:
        stats = calculer_stats(creatures)
        if stats:
            historique['pop_bleus'].append(stats['bleus'])
            historique['pop_rouges'].append(stats['rouges'])
            historique['vitesse_bleus'].append(stats['vitesse_bleus'])
            historique['vitesse_rouges'].append(stats['vitesse_rouges'])
            historique['fuite_bleus'].append(stats['fuite_bleus'])
            historique['fuite_rouges'].append(stats['fuite_rouges'])
            historique['social_bleus'].append(stats['social_bleus'])
            historique['social_rouges'].append(stats['social_rouges'])
            historique['appetit_bleus'].append(stats['appetit_bleus'])
            historique['appetit_rouges'].append(stats['appetit_rouges'])
            historique['attaque_bleus'].append(stats['attaque_bleus'])
            historique['attaque_rouges'].append(stats['attaque_rouges'])
            historique['gen_max'].append(stats['gen_max'])
            # On garde max 120 pts pour pas surcharger les graphiques
            for key in historique:
                if len(historique[key]) > 120:
                    historique[key] = historique[key][-120:]

    # Affichage
    font = pygame.font.Font(None, 36)
    grubz_bleus = len([c for c in creatures if c.clan == 0])
    grubz_rouges = len([c for c in creatures if c.clan == 1])
    texte_bleus = font.render(f"Grubz bleus: {grubz_bleus}", True, (50, 150, 255))
    écran.blit(texte_bleus, (10, 10))
    texte_rouges = font.render(f"Grubz rouges: {grubz_rouges}", True, (255, 50, 50))
    écran.blit(texte_rouges, (10, 50))
    font_hint = pygame.font.Font(None, 24)
    écran.blit(font_hint.render("ESPACE : pause / stats", True, (120, 120, 120)), (10, HAUTEUR - 30))
    pygame.display.flip()
    horloge.tick(FPS)
    

pygame.quit()