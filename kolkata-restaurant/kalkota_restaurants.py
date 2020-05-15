# -*- coding: utf-8 -*-

# Nicolas, 2020-03-20

from __future__ import absolute_import, print_function, unicode_literals
from gameclass import Game,check_init_game_done
from spritebuilder import SpriteBuilder
from players import Player
from sprite import MovingSprite
from ontology import Ontology
from itertools import chain
import pygame
import glo

import random 
import numpy as np
import sys

import heapq 
taille= 20
from collections import deque

class Case():
    def __init__(self,g,pere,cor):
        self.cor=cor
        self.g=g
        self.pere = pere
       
    def estBut(self,buts):
        return self.cor == buts 
    def __lt__(self,other):
        return self.g > other.g
        

def h(case, but):
    return abs(case[0]-but[0]) + abs(case[1]-but[1])
    
def A_star(initStates ,goalStates , wallStates, dim  ):
    frontiere =[]
    reserve = np.zeros(dim)

    caseInit = Case(0,None ,initStates) #case initiale 
    frontiere = [ (caseInit.g+h(initStates,goalStates), caseInit) ] 
    #frontiere qui est la case init , je calcuyle son heuristique 

    bCase = caseInit 

    while  frontiere !=[] and not bCase.estBut(goalStates):
        f,bCase = heapq.heappop(frontiere)
        

        """ 
        étendre les cases 
        """
        i,j = bCase.cor 
        reserve[i,j] =1 
        #etendre les cases 
        if j+1<taille and not (i,j+1) in wallStates and reserve[i,j+1]==0 :
            case = Case(bCase.g+1, bCase, (i,j+1))
            heapq.heappush(frontiere,(h(case.cor,goalStates)+case.g, case))
            
        if j-1>0 and not (i,j-1) in wallStates and reserve[i,j-1]==0 :
            case = Case(bCase.g+1, bCase, (i,j-1))
            heapq.heappush(frontiere,(h(case.cor,goalStates)+case.g, case))
             
        if i+1 <taille and not (i+1,j) in wallStates and reserve[i+1,j]==0 :
            case = Case(bCase.g+1, bCase, (i+1,j))
            heapq.heappush(frontiere,(h(case.cor,goalStates)+case.g, case))
           
        if i-1>0 and not (i-1,j) in wallStates and reserve[i-1,j]==0 :
            case = Case(bCase.g+1, bCase, (i-1,j))
            heapq.heappush(frontiere,(h(case.cor,goalStates)+case.g, case))
            


    currcase = bCase  
    chemin = deque()
    while currcase.cor !=caseInit.cor:
        chemin.appendleft(currcase.cor)
        currcase= currcase.pere


    return chemin

    
# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()

def init(_boardname=None):
    global player,game
    # pathfindingWorld_MultiPlayer4
    name = _boardname if _boardname is not None else 'kolkata_6_10'
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5  # frames per second
    game.mainiteration()
    game.mask.allow_overlaping_players = True
    #player = game.player
    
def main():

    #for arg in sys.argv:
    iterations = 20 # default
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print ("Iterations: ")
    print (iterations)

    init()
    
    
    

    
    #-------------------------------
    # Initialisation
    #-------------------------------
    nbLignes = game.spriteBuilder.rowsize
    nbColonnes = game.spriteBuilder.colsize
    print("lignes", nbLignes)
    print("colonnes", nbColonnes)
    
    
    players = [o for o in game.layers['joueur']]
    nbPlayers = len(players)
    
    
    # on localise tous les états initiaux (loc du joueur)
    initStates = [o.get_rowcol() for o in game.layers['joueur']]
    print ("Init states:", initStates)
    
    
    # on localise tous les objets  ramassables (les restaurants)
    goalStates = [o.get_rowcol() for o in game.layers['ramassable']]
    print ("Goal states:", goalStates)
    global nbRestaus 
    nbRestaus = len(goalStates)
        
    # on localise tous les murs
    wallStates = [w.get_rowcol() for w in game.layers['obstacle']]
    #print ("Wall states:", wallStates)
    
    # on liste toutes les positions permises
    allowedStates = [(x,y) for x in range(nbLignes) for y in range(nbColonnes)\
                     if (x,y) not in wallStates or  goalStates] 
    
    #-------------------------------
    # Placement aleatoire des joueurs, en évitant les obstacles
    #-------------------------------
        
    posPlayers = initStates

    
    for j in range(nbPlayers):
        x,y = random.choice(allowedStates)
        players[j].set_rowcol(x,y)
        game.mainiteration()
        posPlayers[j]=(x,y)


        
        
    
    #-------------------------------
    # chaque joueur choisit un restaurant
    #-------------------------------
    # STRATEGIE DU CHOIX DU RESTAURANT 

    restau=[0]*nbPlayers

    #-------------------------------
    # Boucle principale de déplacements 
    #-------------------------------
    
        
    # bon ici on fait juste plusieurs random walker pour exemple...
    #MOI JE LE REMPLACE PAR A*
    
    
    #historique = {0:[0],1:[0],2:[0],3:[0],4:[0],5:[0]}
    historique = [[0] for i in range(nbRestaus)]
    
    gain = [0]* nbPlayers 
    
    
    global it
    """
    La stratégie du choix du restau 
    """
    global strategies
    strategies = { 0 :alea , 1 : tetu , 2 : most , 3 : less ,4 : derMax , 5 : derMin, 6 : iteration }
    global nbStrategie 
    nbStrategie = len(strategies)
    
    description = {0 :"Choix aléatoire" , 1 : "Stratégie Tetu " , 2 : "Le restau le plus fréquenté" , 3 : "Le restau le moins fréquenté " ,4 : "Le restau le plus fréquenté à la dernière itération ", 5 : "Le restau le moins fréquenté à la dernière itération" , 6 : "Choix séquentiel des restaurants"  }
    
    
    #"""
    for i in range(iterations):
        it = i 
        
        #Permet de savoir pour chaque itération quelle sont les jouerus qui ont choisi un restau donnée 
        
        choix = [[] for i in range(nbRestaus)]
        
        
        #élargir l'historique pour chaqie itération 
        
        if i !=0 :
            for h in historique:
                h.append(0)
            
        
        for j in range(nbPlayers):
            x,y = random.choice(allowedStates)
            players[j].set_rowcol(x,y)
            game.mainiteration()
            posPlayers[j]=(x,y)
        
      
        for j in range(nbPlayers):
            restau[j] = strategies[j%nbStrategie](historique ,nbPlayers)
                    
        
        for j in range(nbPlayers):
            rest = restau[j]
            row,col = posPlayers[j]
            restaurantP_pos = goalStates[rest]
            
            
            #Obtenir le chemin avec A*
            
            chemin = A_star((row,col) ,restaurantP_pos, wallStates, (taille, taille) )
            
            for ch in chemin :
                col=ch[1]
                row=ch[0]
                players[j].set_rowcol(row , col)
                print ("pos :", j,row,col)
                game.mainiteration()
                posPlayers[j]=(row,col)
                
            choix[rest].append(j) #on ajoute le joueur 
            
            historique[rest][i]+=1 
            
            
        
        #Le choix aléatoire d'un joueur qui s'est présenté a un restaurant 
        
        for r in choix :
            if len(r)>0 :
                g = random.randint(0,len(r)-1)
                joueur = r[g]
                gain[joueur]+=1 
        print(historique)
        print(gain)
        index =[idx for idx,e in enumerate(gain) if e == max(gain)]
    
    print("les tratégies qui ont donneles meilleurs gains sont :")    
    for s in index :
        print(description[s%nbStrategie])
    
    
    pygame.quit()
    
    
    
    
    
    
    """
    #VEUILLEZ DECOMMENTER CETTE PARTIE ET COMMENTER LA PARTIE EN DESSUS POUR FAIRE UNE SIMULATION DE DEUX STRATEGIES DIFFERENTES 
    #VEILLEZ FAIRE LE CHOIX DE DEUX STRATEGIES .. 
    #ICI PAR DEFAUT C'EST : RESTAU MOINS FREQUENTE ET RESTAU PLUS FREQUENTE 
    
    for i in range(iterations):
        it = i 
        
        #Permet de savoir pour chaque itération quelle sont les jouerus qui ont choisi un restau donnée 
        
        choix = [[] for i in range(nbRestaus)]
        
        
        #élargir l'historique pour chaqie itération 
        
        if i !=0 :
            for h in historique:
                h.append(0)
            
        
        for j in range(nbPlayers):
            x,y = random.choice(allowedStates)
            players[j].set_rowcol(x,y)
            game.mainiteration()
            posPlayers[j]=(x,y)
        
      
        for j in range(nbPlayers):
            if j %2 == 0 :
                restau[j] =less (historique ,nbPlayers)
            else :
            
                restau[j] = most(historique ,nbPlayers)
                    
        
        for j in range(nbPlayers):
            rest = restau[j]
            row,col = posPlayers[j]
            restaurantP_pos = goalStates[rest]
            
            #Obtenir le chemin avec A*
            
            chemin = A_star((row,col) ,restaurantP_pos, wallStates, (taille, taille) )
            
            for ch in chemin :
                col=ch[1]
                row=ch[0]
                players[j].set_rowcol(row , col)
                print ("pos :", j,row,col)
                game.mainiteration()
                posPlayers[j]=(row,col)
                
            choix[rest].append(j) #on ajoute le joueur 
            
            historique[rest][i]+=1 
            
            
        
        #Le choix aléatoire d'un joueur qui s'est présenté a un restaurant 
    
        for r in choix :
            if len(r)>0 :
                g = random.randint(0,len(r)-1)
                joueur = r[g]
                gain[joueur]+=1 
        print(historique)
        print(gain)
        index =[idx for idx,e in enumerate(gain) if e == max(gain)]
        
    
    print("la stratégie qui ont donne le meilleur gain est :")    
    s1 =0 
    s2=0
    
    for j in range(int(nbPlayers/2)):
        s1 += gain[j] 
        s2 +=gain[j+1]
    
    if (s1==s2) :
        print("les deux stratégies ont donnée les mêmes gains")
    if ( s1> s2):
        print("Le restau le moins fréquenté ")
    else :
        print("Le restau le plus fréquenté")
    
    
    
    pygame.quit()
    
    """
    
    
    
"""
Choix aléatoire 
"""
def alea(historique ,nbJoueur ):
    return random.randint(0,nbRestaus-1)
  
"""
Le jouerur choisit toujours le meme restaurant 
"""
def tetu(historique , nbJoueur ):
    return nbJoueur % nbRestaus 

"""
Le joueur choisit le restaurant le plus fréquenté pour toute les itérations
"""
def most(historique , nbJoueur ):
    l = [sum(h) for h in historique]
    r =[idx for idx,e in enumerate(l) if e == max(l)]
    return r[random.randint(0,len(r)-1)]
    
"""
Le joueur choisit le restaurant le moins fréquenté pour toute les itérations
"""    
def less(historique , nbJoueur ):
    l = [sum(h) for h in historique]
    r =[idx for idx,e in enumerate(l) if e == min(l)]
    return r[random.randint(0,len(r)-1)]

"""
Le joueur choisit le restaurant le moins fréquenté à la dernière itération  
""" 
def derMin(historique , nbJoueur):
    l= [h[-1] for h in historique] 
    r =[idx for idx,e in enumerate(l) if e == min(l)]
    return r[random.randint(0,len(r)-1)]
    
"""
Le joueur choisit le restaurant le plus  fréquenté à la dernière itération  
""" 
def derMax(historique , nbJoueur ):
    l= [h[-1] for h in historique] 
    r =[idx for idx,e in enumerate(l) if e == max(l)]
    return r[random.randint(0,len(r)-1)]

"""
Le joueur choisit les restaurants séquentiellement  
""" 
def iteration(historique , nbJoueur ):
    return it % nbRestaus 





if __name__ == '__main__':
    main()
    


