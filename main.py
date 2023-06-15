import cv2
import numpy as np
from xtherm_libs import InfiFrame

def linear_algorithm(frame: np.float32, info: dict) -> None:
    ''' Processing 16 bit data frame and return processed frame

        Returns:
            outFrame : np.ndarray
                A processed bit frame 8
    '''
    outFrame = np.zeros_like(frame, dtype=np.uint8)

    ro = int(info["temp_max_raw"] - info["temp_min_raw"] if info["temp_max_raw"] - info["temp_min_raw"] > 0 else 1)
    avgSubMin = int(info["temp_average_raw"] - info["temp_min_raw"] if info["temp_average_raw"] - info["temp_min_raw"] > 0 else 1)
    maxSubAvg = int(info["temp_max_raw"] - info["temp_average_raw"] if info["temp_max_raw"] - info["temp_average_raw"] > 0 else 1)
    ro1 = int(97 if (info["temp_average_raw"] - info["temp_min_raw"]) > 97 else (info["temp_average_raw"] - info["temp_min_raw"]))
    ro2 = int(157 if (info["temp_max_raw"] - info["temp_average_raw"]) > 157 else (info["temp_max_raw"] - info["temp_average_raw"]))
    
    outFrame[frame > info["temp_average_raw"]] = ro2 * (frame[frame > info["temp_average_raw"]] - info["temp_average_raw"]) / maxSubAvg + 97
    outFrame[frame < info["temp_average_raw"]] = ro1 * (frame[frame < info["temp_average_raw"]] - info["temp_average_raw"]) / avgSubMin + 97
    
    return outFrame

infiframe = InfiFrame(height=196, width=256)
infiframe.calibrate()

# Config camera settings

## Default settings
infiframe.set_correction(1)
infiframe.set_distance(2)
infiframe.set_humidity(0.45)
infiframe.set_emissivity(0.98)
infiframe.set_reflection(25)
infiframe.set_amb(25)

# infiframe.save_parameters() # Save parameters in hardware

# mid point
point = (192//2, 256//2)

# Set user temperature ("temp_user_00", "temp_user_01", "temp_user_02" in info)
# Can only set 3 custom points
infiframe.set_point(x=point[1], y=point[0], index=0)

while True:
    ret, frame_vis = infiframe.read_data()
    if not ret: break
    info, temp_lut = infiframe.update()
        
    # print(info)
    
    temp_max_x = info["temp_max_x"]
    temp_max_y = info["temp_max_y"]
    
    temp_min_x = info["temp_min_x"]
    temp_min_y = info["temp_min_y"]
    
    # preprocessing frame
    frame_32 = frame_vis.copy().astype(np.float32)
    outframe = linear_algorithm(frame_32, info)
    
    # Convert pixel to temperature (pixel should be in frame 16-bit)
    temp_str = "{:.1f} C".format(temp_lut[frame_vis[point]])
    
    outView = cv2.cvtColor(outframe, cv2.COLOR_GRAY2BGR)
    
    # Custom position `point` and temperature
    cv2.circle(outView, (point[1], point[0]), radius=2, color=(0, 255, 0), thickness=-1)
    cv2.putText(outView, temp_str, (point[0] - 4, point[1] - 4), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 255, 0), 1)
    
    # Max temp position
    cv2.circle(outView, (temp_max_x, temp_max_y), radius=2, color=(0, 0, 255), thickness=-1)
    cv2.putText(outView, "{:.1f}".format(info["temp_max"]), (temp_max_x - 4, temp_max_y - 4), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0, 0, 255), 1)
    
    # Min temp position
    cv2.circle(outView, (temp_min_x, temp_min_y), radius=2, color=(255, 0, 0), thickness=-1)
    cv2.putText(outView, "{:.1f}".format(info["temp_min"]), (temp_min_x - 4, temp_min_y - 4), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 0, 0), 1)
    
    cv2.imshow("Frame", outView)
    if cv2.waitKey(1) & 0xff == 27:
        break

infiframe.release()
cv2.destroyAllWindows
    