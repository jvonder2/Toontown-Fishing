This is a simple python program that I wrote that uses object detection from OpenCV in order to track a fish in the pond, then runs a calculation to cast your fishing rod at the fish. This program uses multicore libraries that allow for the image of the screen to be processed much faster than previously. Currently this program only works in The Brrrgh however I will hopefully get more screenshots of fish in the future to make for multi-playground functionality. The program also is not great at catching fish that are far left or right of the player just because of the calculations I am running, I am working on making it more accurate in the future.

DISCLAIMER: I DO NOT CONDONE PEOPLE USING THIS PROGRAM ON PUBLIC SERVERS, THIS IS JUST A FUN PROJECT I WROTE TO LEARN MORE ABOUT OPENCV AND PYAUTOGUI, I AM ALMOST CERTAIN THAT THIS IS AGAINST TOS IN BASICALLY EVERY PUBLIC SERVER

Potential add-ons:
1. A UI for the user is the first priority, this will come probably in for of Tkinter which I already somewhat know how to use with an on/off switch and a playground feature once I get that 
   working (again an easy add just need to not be lazy)
2. Fix the left/right calculation/power for less liklihood that the program misses the fish
3. Another major issue in this program that I don't really have a solution for right now is that if the program finds a fish while it is moving, it will cast at the spot the fish was and miss 
   completely, at the expense of speed might make an is_moving state where a second screenshot is taken and the position is compared and if its moving then wait
