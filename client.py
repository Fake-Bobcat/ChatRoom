import socket
import json

from _thread import *

import pygame, pygame.freetype

pygame.init()

display = pygame.display.set_mode([500,500])

clock = pygame.time.Clock() # Get Pygame Clock
maxfps = 60

pygame.display.set_caption("Chat Game")

messagelog = []

#create function to manage text objects
def text_objects(text, myrect, font, colour=(0,0,0), wraptext=False):
    if wraptext: # If the text needs to be wrapped or not
        y = 0
        lineSpacing = -2

        text_surface = pygame.Surface(myrect.size,pygame.SRCALPHA,32).convert_alpha()

        towrite = text

        # get the height of the font
        fontHeight = font.size("Tg")[1]

        while towrite: # Repeat until there is no more text to write
            i = 1

            # determine if the row of text will be outside our area, if so then don't write any more
            if y + fontHeight > myrect.size[1]:
                break

            # determine maximum width of line
            slash = False
            while font.size(towrite[:i])[0] < myrect.size[0] and i < len(towrite):
                i += 1
                if i < len(towrite)-1 and towrite[i]+towrite[i+1] == "\n":
                    break

            # if we've wrapped the text, then adjust the wrap to the last word      
            if i < len(towrite):
                i = towrite.rfind(" ", 0, i) + 1

            # render the line and blit it to the surface
            image = font.render(towrite[:i], False, colour)

            textwidth = image.get_size()[0]

            text_surface.blit(image, (myrect.size[0]/2-textwidth/2, y)) # Render the line onto a separate surface which is the same size as the rect
            y += fontHeight + lineSpacing

            # remove the text we just blitted
            towrite = towrite[i:]
        
        return text_surface,text_surface.get_rect() # Return the already drawn text to the renderer
    text_surface = font.render(text, False, colour) # Draw the text and return the text surface to the renderer
    return text_surface,text_surface.get_rect()

def RunClient(s,username,server):
    while True:
        data, addr = s.recvfrom(1024)
        data = json.loads(data.decode("utf-8"))
        if data == "CheckOnline":
            tosend = {
                "user" : username,
                "command" : "OnlineCheck",
                "message" : None,
            }
            s.sendto(json.dumps(tosend).encode("utf-8"), server)
        elif data == "ServerClose":
            running = False
        else:
            messagelog.append(data)

def RunMessaging(s,username,server):
    while True:
        message = input("-> ")
        if message != "":
            if message == "q":
                running = False
            command = "message"
            if message == "/online": # If user inputs /online then ask the server for a list of online users
                command = "getonline"
            tosend = {
                "user" : username,
                "command" : command,
                "message" : message,
            }
            s.sendto(json.dumps(tosend).encode("utf-8"), server)
        
            message = None

def Main():

    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    host = ip_address #client ip
    port = 0 # Chooses any available port

    server_address = input("Paste Server Address/Port: ")
    server_address = str.split(str.lstrip(server_address),"%") # Strip whitespaces
    
    server = (server_address[0], int(server_address[1]))
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host,port))

    username = input("Input Username: ")

    tosend = { # Send Message to server to say that you joined
        "user" : username,
        "command" : "join",
        "message" : None,
    }
    s.sendto(json.dumps(tosend).encode("utf-8"), server)
    
    data, addr = s.recvfrom(1024) # Wait until the server allows the player to join, if username is taken then break
    data = json.loads(data)
    if data == "Taken":
        print("Username Is Already Taken.")
        return
    else:
        print("-- Connected --")

    start_new_thread(RunClient,(s,username,server))
    start_new_thread(RunMessaging,(s,username,server))

    myfont = pygame.font.SysFont("Arial", 16)

    running = True
    while running:
        for event in pygame.event.get(): # If the game is quitting close pygame
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                
        clock.tick(maxfps)

        display.fill((255,255,255))

        index, length = 0, len(messagelog)
        for loadmsg in messagelog:
            text_surf, text_rect = text_objects(loadmsg,pygame.Rect(0,0,400,400),myfont,(0,0,0),True)
            display.blit(text_surf,(50,500-(length-index)*30))
            index += 1

        pygame.display.update()

    tosend = {
        "user" : username,
        "command" : "disc",
        "message" : None,
    }
    s.sendto(json.dumps(tosend).encode("utf-8"), server)
    s.close()

if __name__=='__main__':
    Main()