import os
from image_processor import imageProcessor
from controller import TrexGameController
import time
from mlp import *

class NewGame(object):
    def __init__(self, controller, img_processor, start_time, nn):
        self.controller = controller
        self.img_processor = img_processor
        self.start_time = start_time
        self.LastParams = [1 for i in range(8)]
        #self.LastRealParams = [1,1,1]
        self.nn = nn
        self.WaitonCrash = False
        self.NumJump = 0
    def StartGame(self):
        def Update():
            if self.controller.hasStart():
                time.sleep(0.1)
                obstacle_list = self.controller.getObstacles()
                if len(obstacle_list) == 0:
                    return
                if self.controller.getCrashed():
                    #print 'Num of Jump', self.NumJump
                    deltaFactor = (self.LastParams[0] * 0.1)
                    if (self.controller.isJumping and self.controller.getJumpVelocity() > 0):

                        self.LastParams[0] = self.LastParams[0] + deltaFactor;
                        self.nn.TrainModel(array([self.LastParams]), array([[1,0]]))
                        #print 'hit face ------------------jump'
                        self.LastParams[0] = self.LastParams[0] + deltaFactor;
                        self.nn.TrainModel(array([self.LastParams]), array([[0,1]]))
                        #print 'hit face ------------------stay'
                        #perceptron.propagate(learningRate, [1, 0])#you should have jumped

                    elif (self.controller.isJumping and self.controller.getJumpVelocity() < 0):

                        self.nn.TrainModel(array([self.LastParams]), array([[0,1]]))
                        #print 'hit feet ------------------ stay'
                        self.LastParams[0] = self.LastParams[0] - deltaFactor
                        self.nn.TrainModel(array([self.LastParams]), array([[1,0]]))
                        #print 'hit feet ------------------- jump'
                        #perceptron.propagate(learningRate, [1, 0])
                    else:
                        self.nn.TrainModel(array([self.LastParams]), array([[1,0]]))
                        #print 'hit when not jump'
                    self.controller.restart()
                    self.NumJump = 0

                else:
                    NearestObstacle = obstacle_list[0]
                    params = []
                    if NearestObstacle == None:
                        return
                    params.append(NearestObstacle[0])#position
                    params.append(NearestObstacle[1])#weight
                    params.append(NearestObstacle[2])#height
                    params.append(round(self.controller.getCurrentSpeed()))#speed with multiply bias

                    if len(obstacle_list) <= 1:
                        params += [1,1,1,1]
                    else:
                        params += [obstacle_list[1][i] for i in range(3)]
                        params += [round(self.controller.getCurrentSpeed())]
                    category, confidence = self.nn.TestModel(array([params]))
                    #confidence = output[0] - output[1] - 0.01 #weight bias
                    #category = [0]
                    if (category[0] == 0):#jump if network is really confident
                        #Jump jump jump :D !
                        print params[0]/params[3]
                        if params[0]/params[3] > 30:
                            return
                        if (self.controller.getJumpVelocity() == 0):
                            if self.LastParams != [1,1,1]:
                                self.nn.TrainModel(array([self.LastParams]), array([[1,0]]))
                                self.NumJump += 1
                                #print 'previous jump succeed'
                            self.controller.jump()
                            self.LastParams = params

                    else:
                        if (self.controller.isJumping()):
                            self.controller.duck()
                            self.LastParams = params#last move activation
            else:
                time.sleep(0.1)

        while True:
            if self.controller.hasStart():
                if start_time is not None:
                    delta_time = time.time() - self.start_time
                else:
                    delta_time = 0
                Update()
            time.sleep(0.01)



if __name__ == '__main__':
    game_path = 'file://' + os.path.abspath(os.path.join(os.getcwd(), '..')) + '/game/index.html'
    controller = TrexGameController(game_path)
    img_processor = imageProcessor()
    start_time = time.time()
    mlp = MLP()
    mlp.BuildModel()
    #mlp = None
    ng = NewGame(controller, img_processor, start_time, mlp)
    ng.StartGame()