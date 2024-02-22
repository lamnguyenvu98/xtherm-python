### Install dependencies
```
pip install opencv-python
```

### Requirements
Require Python version: >= 3.10

Supported different width of Infiray thermal monoculars: `640, 384, 256, 240`
    
### How to use

#### 1. Initialize camera
    ```
    from xtherm_libs import InfiFrame
    
    # width x height resolution of camera
    cam = InfiFrame(height=196, width=256)
    cam.calibrate()
    ```

#### 2. Config camera parameters (Optional)
Don't use this code if you want use default parameters

    # Default settings

    cam.set_correction(1)
    cam.set_distance(2)
    cam.set_humidity(0.45)
    cam.set_emissivity(0.98)
    cam.set_reflection(25)
    cam.set_amb(25)
    
    # save parameters in hardware (might lost default parameters)
    cam.save_parameters()

#### 3. Set custom points (Optional)

    # Set user temperature ("temp_user_00", "temp_user_01", "temp_user_02" in info)
    # Can only set 3 custom points (index from 0 to 2)
    
    cam.set_point(x=256//2, y=192//2, index=0) # set central point


#### 4. Read frame and data

    # frame processing function
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

    point = (192//2, 256//2)

    while True:
        ret, frame_vis = cam.read_data()
        if not ret: break
        info, temp_lut = cam.update()
        
        # Position of highest temperature
        temp_max_x = info["temp_max_x"]
        temp_max_y = info["temp_max_y"]
        
        # Position of lowest temperature
        temp_min_x = info["temp_min_x"]
        temp_min_y = info["temp_min_y"]
        
        # preprocessing frame
        frame_32 = frame_vis.copy().astype(np.float32)
        outframe = linear_algorithm(frame_32, info)

        # Convert pixel to temperature (pixel should be in frame 16-bit)
        temp_str = "{:.1f} C".format(temp_lut[frame_vis[point]])
        
        outView = cv2.cvtColor(outframe, cv2.COLOR_GRAY2BGR)

        cv2.imshow("Frame", outView)
        if cv2.waitKey(1) & 0xff == 27:
            break
    
    cam.release()
    cv2.destroyAllWindows


References:
1. https://github.com/stawel/ht301_hacklib

2. https://gitlab.com/netman69/inficam/-/blob/master/libinficam/src/main/jni/InfiCam/InfiFrame.cpp
