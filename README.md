# Learn-math-with-Vector v0.1
Learning math interactively with the robot Vector from Anki
-

![Learn-Math-With-Vector](static/img/math-vector-screenshot-v0.1.jpg)

What does it do exactly?
-
After you pick a type of math to learn and a range, Vector offers a series of math questions that need to be answered on screen. This can be either the computer from which the program was started or a (mobile) device inside the local network.

This program offers a choice of match training sets (pic 1). Once a choice is made, Vector asks a number of questions (pic 2). The answer can be entered on screen (pic 3). Vector tells you it’s ok or not (pic 4). This repeats ten times with questions within the chosen range and math type, then ends with a discreet celebration.

What do you need to use it?
-
1. Vector himself (http://anki.com/vector)
2. A computer
3. A little knowledge about Python
4. Knowledge of the Vector SDK (https://developer.anki.com/vector/docs)
5. The files in this repository
6. The python module Pillow. (pip3 install --user Pillow, usually already installed when working with the Vector SDK)
7. The python module Flask. (pip3 install --user flask)

If you know how to run an example file from the Vector SDK, you should be able to run this script. 

System requirements
-
- Computer with Windows OS, mac OSX or Linux
- Python 3.6.1 or later
- WiFi connection
- (optional) Mobile device

Compatibility
-
- Vector SDK 0.5.1 (alpha)
 
Known issues
-
- Local network availability is dependent on a lot of factors not covered by this program or its explanation. It should work if you know the computer's local ip-address and enter that in the address bar of another device's browser at port 5000 (i.e. 192.168.x.x:5000).
