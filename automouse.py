#-*- coding: utf-8 -*-　
import pyautogui
import cv2
import numpy as np
from matplotlib import pyplot as plt
from BasicDefinition import CardIndex,WindIndex
from SimpleAgent import *
pyautogui.PAUSE = 1
pyautogui.FAILSAFE = True
width , height = pyautogui.size()
#waste time
for i in range(1):
      pyautogui.moveTo(300, 300, duration=0.25)
      pyautogui.moveTo(400, 300, duration=0.25)
      pyautogui.moveTo(400, 400, duration=0.25)
      pyautogui.moveTo(300, 400, duration=0.25)
#get position and handcard      
try:
	#get screenshot
	Random = RandomAgent()
	im = pyautogui.screenshot()
	x, y = pyautogui.position()
	print ('now at',(x , y))
	pyautogui.screenshot('screenshot.png')
	#use opencv to read
	img = cv2.imread('screenshot.png',0)
	img2 = img.copy()
	handcard = []
	handcard_posList = []
	#check through all cards , initial handcard
	for i in range(len(CardIndex)):
		filename = str(i) + '.png' # 0.png / 1.png
		target = cv2.imread(filename,10)
		w, h = target.shape[::-1]

		methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
	                'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

		for meth in methods:
			img = img2.copy()
			method = eval(meth)
			# Apply template Matching
			res = cv2.matchTemplate(img,target,method)
			min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
			print (min_val, max_val, min_loc, max_loc)
			# If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
			if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
			    top_left = min_loc
			else:
			    top_left = max_loc
			bottom_right = (top_left[0] + w, top_left[1] + h)
			cv2.rectangle(img,top_left, bottom_right, 255, 2)

			plt.subplot(121),plt.imshow(res,cmap = 'gray')
			plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
			plt.subplot(122),plt.imshow(img,cmap = 'gray')
			plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
			plt.suptitle(meth)
			plt.show()
		#append into handcard and positionlist
		if FIND:
			handcard.append(i)
			handcard_posList.append(location)
	
	Random.initialHandCard(handcard)


	# if our turns 

	#check which card is added
	theRightestPos = Random.handcard_posList[len(handcard_posList)]
	Random.takeaction()

	if not location : 
		print ('error!')
	else:	
		x, y = pyautogui.center(location)
		pyautogui.click(x , y, button='left')
		pyautogui.moveTo(300,300)
except KeyboardInterrupt:
	print ('\nExit.')	
