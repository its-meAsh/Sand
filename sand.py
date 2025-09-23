from PIL import Image
import copy
import random
import cv2
import os
import numpy

class Sand:
    def __init__(self,path:str,saveFrames:bool,time:int,fps:int) -> None:
        self.path:str = path
        image,self.size = self.readImage()
        self.currentImage:list[tuple[int,int,int]] = copy.deepcopy(list(image))
        frames:list[list[tuple[int,int,int]]] = self.getFrames(time)
        if saveFrames:
            try:
                os.mkdir(f'{self.path}/frames')
            except:
                None
            count:int = 1
            for frame in frames:
                self.saveImage(frame,f'frames/frame{count}')
                count+=1
        self.saveVideo(frames,fps,'sandVideo')

        print('Sand:')
        print(' Save frames:',saveFrames)
        if saveFrames:
            print(' Saved frames size:',os.path.getsize(f'{self.path}/frames'),'bytes')
        print(' Video size:',os.path.getsize(f'{self.path}/sandVideo.mp4'),'bytes')
        return
    
    def readImage(self) -> tuple[list[tuple[int,int,int]],tuple[int,int]]:
        file = Image.open(f'{self.path}/sand.png')
        return (file.getdata(),file.size)
    
    def indexToCoords(self,index:int) -> tuple[int,int]:
        return (index%self.size[0],index//self.size[1])
    
    def coordsToIndex(self,coords:tuple[int,int]) -> int:
        return coords[1]*self.size[0] + coords[0]

    def getBottomAdjacent(self,index:int) -> dict[int:int]:
        coordinates:tuple[int,int] = self.indexToCoords(index)
        adjacents:dict[int,int] = {}
        if coordinates[1] + 1 < self.size[1]:
            adjacents[1] = self.coordsToIndex((coordinates[0],coordinates[1]+1))
            if coordinates[0] - 1 >= 0:
                adjacents[0] = self.coordsToIndex((coordinates[0]-1,coordinates[1]+1))
            if coordinates[0] + 1 < self.size[0]:
                adjacents[2] = self.coordsToIndex((coordinates[0]+1,coordinates[1]+1))
        return adjacents
    
    def proceedFrame(self) -> bool:
        delta:bool = False
        for i in range(1,len(self.currentImage)+1):
            index:int = len(self.currentImage)-i
            item:tuple[int,int,int] = self.currentImage[index]
            if item == (239,228,176):
                adjacents:dict[int,int] = self.getBottomAdjacent(index)
                if len(adjacents) <= 0:
                    continue
                if not delta:
                    delta = True
                newIndex:int = None
                if 1 in adjacents and self.currentImage[adjacents[1]] not in [(0,0,0),(239,228,176)]:
                    newIndex = adjacents[1]
                else:
                    keys:list[int] = list(adjacents.keys())
                    for key in keys:
                        if self.currentImage[adjacents[key]] in [(0,0,0),(239,228,176)]:
                            keys.remove(key)
                    if len(keys) == 0:
                        continue
                    newIndex = adjacents[random.choice(keys)]
                self.currentImage[index] = (255,255,255)
                self.currentImage[newIndex] = (239,228,176)
        return delta
    
    def getFrames(self,till:int) -> list[list[tuple[int,int,int]]]:
        frames:list[list[tuple[int,int,int]]] = [copy.deepcopy(self.currentImage)]
        if till == 0:
            delta:bool = True
            while delta:
                delta = self.proceedFrame()
                frames.append(copy.deepcopy(self.currentImage))
        else:
            for _ in range(till):
                self.proceedFrame()
                frames.append(copy.deepcopy(self.currentImage))
        return frames
    
    def saveImage(self,image:list[tuple[int,int,int]],subpath:str) -> None:
        imageObj = Image.new("RGB",self.size)
        imageObj.putdata(image)
        imageObj.save(f'{self.path}/{subpath}.png')
        return

    def shrink2D(self,image:list[tuple[int,int,int]]) -> list[list[list[int]]]:
        count:int = 0
        imageShrinked:list[list[list[int]]] = []
        for j in range(self.size[1]):
            imageShrinked.append([])
            for i in range(self.size[0]):
                imageShrinked[-1].append(list(image[count]))
                count+=1
        return imageShrinked
    def saveVideo(self,frames:list[list[tuple[int,int,int]]],fps:int,filename:str) -> None:
        videoWriter = cv2.VideoWriter(f'{self.path}/{filename}.mp4',cv2.VideoWriter_fourcc(*f'MJPG'),fps,self.size)
        for image in frames:
            image = self.shrink2D(image)
            videoWriter.write(cv2.cvtColor(numpy.array(image,dtype=numpy.uint8),cv2.COLOR_RGB2BGR))
        videoWriter.release()

sand:Sand = Sand('sand1',True,50,2)
