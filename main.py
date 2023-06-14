import cv2
from xtherm_libs import InfiFrame

infiframe = InfiFrame(height=196, width=256)
infiframe.calibrate()

infiframe.set_correction(1)
infiframe.set_distance(2)
infiframe.set_humidity(0.5)

point = (192//2, 256//2)

while True:
    ret, frame_vis = infiframe.read_data()
    if not ret: break
    info, temp_lut = infiframe.update()
        
    print("cameraSoftVersion: ", info['cameraSoftVersion'])
    print("sn: ", info['sn'])
    print("correction: ", info['correction'])
    print("humidity: ", info["humidity"])
    
    outframe = infiframe.linear_algorithm()
    
    temp_str = "{:.1f} C".format(temp_lut[frame_vis[point]])
    
    outView = cv2.cvtColor(outframe, cv2.COLOR_GRAY2BGR)
    
    cv2.circle(outView, (point[1], point[0]), radius=2, color=(255, 120, 0), thickness=-1)
    cv2.putText(outView, temp_str, (point[0] - 4, point[1] - 4), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 120, 0), 1)
    
    cv2.imshow("Frame", outView)
    if cv2.waitKey(1) & 0xff == 27:
        break

infiframe.release()
cv2.destroyAllWindows
    