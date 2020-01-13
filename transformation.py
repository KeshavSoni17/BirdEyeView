def transformation(cap, imgHeight,imgWidth, theta):
    _, frame = cap.read()
    north = frame
    south = frame
    east = frame
    west = frame

    #cv2.imshow("Image",frame)
    
    #North - check if right
    north = cv2.resize(north, (640,360), interpolation = cv2.INTER_AREA)
    pts1 = np.float32([(0,imgHeight), (imgWidth,imgHeight), (imgWidth,0), (0,0)])
    pts2 = np.float32([(320-320*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (320+320*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (imgWidth,0), (0,0)])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    north = cv2.warpPerspective(north, matrix, (640, 360))
    
    #South
    south = cv2.resize(south, (640,360), interpolation = cv2.INTER_AREA)
    pts1 = np.float32([(0,imgHeight), (imgWidth,imgHeight), (imgWidth,0), (0,0)])
    pts2 = np.float32([(320-320*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (320+320*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (imgWidth,0), (0,0)])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    south = cv2.warpPerspective(south, matrix, (640, 360))
    #cv2.imshow("North",south)
    
    #East
    east = cv2.resize(east, (640,360), interpolation = cv2.INTER_AREA)
    pts1 = np.float32([(0,imgHeight), (imgWidth,imgHeight), (imgWidth,0), (0,0)])
    pts2 = np.float32([(320-320*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (320+320*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (imgWidth,0), (0,0)])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    east = cv2.warpPerspective(east, matrix, (640, 360))

    
    #West
    west = cv2.resize(west, (640,360), interpolation = cv2.INTER_AREA)
    pts1 = np.float32([(0,imgHeight), (imgWidth,imgHeight), (imgWidth,0), (0,0)])
    pts2 = np.float32([(320-320*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (320+320*math.cos(theta+math.pi/6)/math.cos(theta-math.pi/6),imgHeight), (imgWidth,0), (0,0)])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    west = cv2.warpPerspective(west, matrix, (640, 360))
    
    north = cv2.resize(north, (int(screenw/3), int(screenh/3)))
    x_offset=int(screenw/3)
    y_offset=0
    result[y_offset:y_offset+len(north), x_offset:x_offset+len(north[1])] = north

    south = cv2.resize(south, (int(screenw/3), int(screenh/3)))
    south = cv2.rotate(south, cv2.ROTATE_180)
    x_offset = int(screenw/3)
    y_offset = int(screenh/3)*2
    result[y_offset:y_offset+len(south), x_offset:x_offset+len(south[1])] = south
    
    west = cv2.resize(west, (int(screenw/3), int(screenh/3)))
    west = cv2.rotate(west, cv2.ROTATE_90_CLOCKWISE)
    x_offset = int(screenw/3)*2-int(len(west[1])/4)
    y_offset = int(screenh/3)-int(len(west)/4)
    result[y_offset:y_offset+len(west), x_offset:x_offset+len(west[1])] = west

    
    east = cv2.resize(east, (int(screenw/3), int(screenh/3)))
    east = cv2.rotate(east, cv2.ROTATE_90_COUNTERCLOCKWISE)
    x_offset = 0 + int(len(east[1]))
    y_offset = int(screenh/3)-int(len(east)*1/4)
    result[y_offset:y_offset+len(east), x_offset:x_offset+len(east[1])] = east

    #frame = cv2.resize(frame, (640,360), interpolation = cv2.INTER_AREA)
    
    return result
