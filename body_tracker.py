import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import time
import os
import pathlib
import textwrap
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown
from subtraction_manager import SubtractionManager
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

net = cv.dnn.readNetFromTensorflow("graph_opt.pb") ## weights

inWidth = 320
inHeight = 240
thr = 0.2
genai.configure(api_key=SECRET_KEY)
model = genai.GenerativeModel('gemini-pro')

BODY_PARTS = { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
                   "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
                   "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
                   "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }

POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
                   ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
                   ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"], ["Neck", "LHip"],
                   ["LHip", "LKnee"], ["LKnee", "LAnkle"], ["Neck", "Nose"], ["Nose", "REye"],
                   ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"] ]


def pose_estimation(frame):
    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    net.setInput(cv.dnn.blobFromImage(frame, 1.0, (inWidth, inHeight), (127.5, 127.5, 127.5), swapRB=True, crop=False))
    out = net.forward()
    out = out[:, :19, :, :]
    
    assert(len(BODY_PARTS) == out.shape[1])
    
    points = []
    
    for i in range(len(BODY_PARTS)):
        # Slice heatmap of corresponding body's part.
        heatMap = out[0, i, :, :]

        # Originally, we try to find all the local maximums. To simplify a sample
        # we just find a global one. However only a single pose at the same time
        # could be detected this way.
        _, conf, _, point = cv.minMaxLoc(heatMap)
        x = (frameWidth * point[0]) / out.shape[3]
        y = (frameHeight * point[1]) / out.shape[2]

        # Add a point if it's confidence is higher than threshold.
        points.append((int(x), int(y)) if conf > thr else None)

    for pair in POSE_PAIRS:
        partFrom = pair[0]
        partTo = pair[1]
        assert(partFrom in BODY_PARTS)
        assert(partTo in BODY_PARTS)

        idFrom = BODY_PARTS[partFrom]
        idTo = BODY_PARTS[partTo]

        if points[idFrom] and points[idTo]:
            cv.line(frame, points[idFrom], points[idTo], (0, 255, 0), 3)
            cv.ellipse(frame, points[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
            cv.ellipse(frame, points[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
        
    t, _ = net.getPerfProfile()
    freq = cv.getTickFrequency() / 1000
    cv.putText(frame, '%.2fms' % (t / freq), (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

    return frame

def resetCounters():
    answerCooldown = 50
    c1counter = 0
    c2counter = 0
    c3counter = 0
    c4counter = 0

# estimated_image = pose_estimation(img)
# plt.imshow(cv.cvtColor(estimated_image, cv.COLOR_BGR2RGB))

cap = cv.VideoCapture(1)
cap.set(cv.CAP_PROP_FPS, 30)
cap.set(3, 800)
cap.set(4, 800)
font = cv.FONT_HERSHEY_SIMPLEX

if not cap.isOpened():
    cap = cv.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")

c1counter = 0
c2counter = 0
c3counter = 0
c4counter = 0
cooldown_duration = 50
cooldown_counter = 0
score = 0
incorrectProblems = []
message_duration = 20  # Adjust this value as needed
message_counter = 0
message_text = ""
problem_counter = 0;
total_game_duration = 240  # Adjust as needed (in seconds)
game_start_time = cv.getTickCount()

    
while True:
    hasFrame, frame = cap.read()
    if not hasFrame:
        cv.waitKey()
        break

    frameWidth = frame.shape[1]
    frameHeight = frame.shape[0]
    net.setInput(cv.dnn.blobFromImage(frame, 1.0, (inWidth, inHeight), (127.5, 127.5, 127.5), swapRB=True, crop=False))
    out = net.forward()
    out = out[:, :19, :, :]

    assert(len(BODY_PARTS) == out.shape[1])

    points = []
    


    for i in range(len(BODY_PARTS)):
        # Slice heatmap of corresponding body's part.
        heatMap = out[0, i, :, :]

        # Originally, we try to find all the local maximums. To simplify a sample
        # we just find a global one. However only a single pose at the same time
        # could be detected this way.
        _, conf, _, point = cv.minMaxLoc(heatMap)
        x = (frameWidth * point[0]) / out.shape[3]
        y = (frameHeight * point[1]) / out.shape[2]

        # Add a point if it's confidence is higher than threshold.
        points.append((int(x), int(y)) if conf > thr else None)

    for pair in POSE_PAIRS:
        partFrom = pair[0]
        partTo = pair[1]
        assert(partFrom in BODY_PARTS)
        assert(partTo in BODY_PARTS)

        idFrom = BODY_PARTS[partFrom]
        idTo = BODY_PARTS[partTo]

        if points[idFrom] and points[idTo]:
            cv.line(frame, points[idFrom], points[idTo], (0, 255, 0), 3)
            cv.ellipse(frame, points[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
            cv.ellipse(frame, points[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)

            #Manages each hand individually
            if (pair[0] == 'LElbow' or pair[0] == 'RElbow'):
                print(pair)
                print(points[idFrom])
                print(str(points[idFrom][0]) + " " + str(points[idFrom][1]))


                # cv.rectangle(frame, (0, 0), (150, 150), (0, 255, 0), 3) #Option Box 1
                # cv.rectangle(frame, (0, frameHeight-150), (150, frameHeight), (0, 255, 0), 3) #Option Box 2
                # cv.rectangle(frame, (frameWidth - 150, 0), (frameWidth, 150), (0, 255, 0), 3) #Option Box 3
                # cv.rectangle(frame, (frameWidth - 150, frameHeight-150), (frameWidth, frameHeight), (0, 255, 0), 3) #Option Box 4

                
                #Top Left
                if (points[idFrom][0] <=180 and points[idFrom][1] <= 180):
                    c1counter = c1counter + 1
                    print(c1counter)


                #Top Right
                if (points[idFrom][0] >= (frameWidth - 180) and points[idFrom][1] <= 180): 
                    c2counter = c2counter + 1
                    print(c2counter)


                #Bottom Left
                if (points[idFrom][0] <= 180 and points[idFrom][1] >= (frameHeight - 180)):
                    c3counter = c3counter + 1
                    print(c3counter)

                #Bottom Right
                if (points[idFrom][0] >= (frameWidth - 180) and points[idFrom][1] >= (frameHeight - 180)):
                    c4counter = c4counter + 1
                    print(c4counter)


                # get first and second values of points[idFrom]


    #----------------------------------------------------------
    #Game Logic
    cv.rectangle(frame, (int(frameWidth/2) - 150, 20), (int(frameWidth/2) + 50, 80), (0, 0, 0), cv.FILLED)
    cv.rectangle(frame, (10, 20), (90, 80), (0, 0, 0), cv.FILLED)  # Answer choice 1
    cv.rectangle(frame, (frameWidth - 170, 20), (frameWidth - 70, 80), (0, 0, 0), cv.FILLED)  # Answer choice 2
    cv.rectangle(frame, (10, frameHeight - 80), (100, frameHeight - 20), (0, 0, 0), cv.FILLED)  # Answer choice 3
    cv.rectangle(frame, (frameWidth - 170, frameHeight - 80), (frameWidth - 70, frameHeight - 20), (0, 0, 0), cv.FILLED)  # Answer choice 4

    #drawing objects
    cv.rectangle(frame, (0, 0), (150, 150), (0, 255, 0), 3) #Option Box 1
    cv.rectangle(frame, (0, frameHeight-150), (150, frameHeight), (0, 255, 0), 3) #Option Box 2
    cv.rectangle(frame, (frameWidth - 150, 0), (frameWidth, 150), (0, 255, 0), 3) #Option Box 3
    cv.rectangle(frame, (frameWidth - 150, frameHeight-150), (frameWidth, frameHeight), (0, 255, 0), 3) #Option Box 4

    #drawing answer choices
    #call method from subtraction-manager.py
    problem = SubtractionManager.getProblem()
    cv.putText(frame, problem, (int(frameWidth/2) - 130, 60), font, 1, (255, 255, 255), 3) #problem
    cv.putText(frame, str(SubtractionManager.getAnswerChoices()[0]), (20, 60), font, 1, (255, 0, 0), 6) #ac1
    cv.putText(frame, str(SubtractionManager.getAnswerChoices()[1]), (int(frameWidth/2) + 200, 60), font, 1, (0, 255, 0), 6) #ac2
    cv.putText(frame, str(SubtractionManager.getAnswerChoices()[2]), (20, frameHeight - 70), font, 1, (0, 0, 255), 6) #ac3
    cv.putText(frame, str(SubtractionManager.getAnswerChoices()[3]), (int(frameWidth/2) + 200, frameHeight - 70), font, 1, (100, 100, 100), 6) #ac4

    cv.putText(frame, 'Score: ' + str(score), (int(frameWidth /2) - 50, frameHeight - 100), font, 1, (150, 150, 150), 3)

    correctAnswer = SubtractionManager.getCorrectIndex()

    # Game Logic
    if cooldown_counter > 0:
        cooldown_counter -= 1

    # Check if any option is selected and cooldown is over
    if cooldown_counter > 0:
        cooldown_counter -= 1

    # Check if any option is selected and cooldown is over
    if cooldown_counter == 0:
        for i in range(4):
            if (c1counter >= 25 and i == 0) or (c2counter >= 25 and i == 1) or \
               (c3counter >= 25 and i == 2) or (c4counter >= 25 and i == 3):

                # Reset counters
                c1counter = c2counter = c3counter = c4counter = 0

                # Check answer
                if i == correctAnswer:
                    message_text = f'Option {i+1} - Correct!'
                    score += 1
                    problem_counter += 1
                    SubtractionManager.makeNewProblem();
                else:
                    message_text = f'Option {i+1} - Incorrect!'
                    score -= 1
                    incorrectProblems.append(problem)

                # Set cooldown
                cooldown_counter = cooldown_duration
                message_counter = message_duration
                break

    # Display message
    if message_counter > 0:
        # Draw rectangle behind the text for visibility
        text_size = cv.getTextSize(message_text, font, 1.5, 6)[0]
        text_x = 10
        text_y = 250
        rect_top_left = (text_x - 5, text_y - text_size[1] - 5)
        rect_bottom_right = (text_x + text_size[0] + 5, text_y + 5)
        cv.rectangle(frame, rect_top_left, rect_bottom_right, (0, 0, 0), cv.FILLED)  # Draw filled rectangle
        cv.putText(frame, message_text, (text_x, text_y), font, 1.5, (255, 255, 255), 6)
        message_counter -= 1

    if problem_counter == 3:
        # Generate a text file with missed problems
        with open('missed_problems.txt', 'w') as f:
            f.write('Missed Problems:\n')
            response = "Pretend you are a tutor speaking directly to a child. The child got these following subtraction problems wrong:"
            for problem in incorrectProblems:
                f.write(problem + '\n')
                response = response + " " + problem
            response = response + ". Provide feedback on how they can improve and what types of problems they got wrong. Make sure your response sounds compassionate, empathetic, and is helpful."
            print(response)
            airesponse = model.generate_content(response).text
            f.write('Final Score: ' + str(score))
            f.write('\n Tutor Response: ')
            f.write('\n' + str(airesponse))

        # Display "Game Over!" message
        cv.putText(frame, 'You finished!', (int(frameWidth / 2) - 100, int(frameHeight / 2)), font, 2, (0, 0, 255), 6)
        time.sleep(5)

        # Break out of the loop to end the game
        break

    elapsed_time = (cv.getTickCount() - game_start_time) / cv.getTickFrequency()
    if elapsed_time >= total_game_duration:
        cv.putText(frame, 'Game', (int(frameWidth / 2) - 100, int(frameHeight / 2)), font, 2, (0, 0, 255), 6)

        # End the game
        with open('missed_problems.txt', 'w') as f:
            f.write('Missed Problems:\n')
            response = "Pretend you are a tutor speaking directly to a child. The child got these following subtraction problems wrong:"
            for problem in incorrectProblems:
                f.write(problem + '\n')
                response = response + " " + problem
            response = response + ". Provide feedback on how they can improve and what types of problems they got wrong. Make sure your response sounds compassionate, empathetic, and is helpful."
            print(response)
            airesponse = model.generate_content(response).text
            f.write('Final Score: ' + str(score))
            f.write('\n Tutor Response: ')
            f.write('\n' + str(airesponse))

        message_text = 'Game Over!'

        break;
    
    remaining_time = max(0, total_game_duration - elapsed_time)
    timer_text = f'Time Left: {int(remaining_time)}s'
    cv.putText(frame, timer_text, (int(frameWidth / 2) - 100, frameHeight - 50), font, 1, (255, 255, 255), 3)

    cv.imshow('Math Game!', frame)

    # Check for key press to exit
    key = cv.waitKey(1)
    if key == ord('q') or key == 27:  # 'q' key or ESC key
        break

# Release the video capture and close the OpenCV window
cap.release()
cv.destroyAllWindows()


