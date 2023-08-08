# %%
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pytesseract
import math
from PIL import Image
from scipy.signal import argrelmin, argrelmax
import tensorflow.compat.v1 as tf

tf.disable_v2_behavior()
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\lyt4\Desktop\temp\WIT\Summer 2023\COMP 5500 - Senior Project\SeniorProject\work-in-progress\test_images\Tesseract-OCR\tesseract.exe'

# %%
# read image, prepare it by resizing it to fixed height and converting it to grayscale
img1 = cv2.imread("test_images/img2.png")
plt.imshow(img1, cmap='gray')

# %%
img2 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
plt.imshow(img2, cmap='gray')

# %%
img3 = np.transpose(img2)
plt.imshow(img3, cmap='gray')

# %%
img = np.arange(49).reshape((7,7))
img
plt.imshow(img, cmap='gray')

# %%
def createKernel(kernelSize, sigma, theta):
    "create anisotropic filter kernel according to given parameters"
    assert kernelSize % 2 # must be odd size
    halfSize = kernelSize // 2

    kernel = np.zeros([kernelSize, kernelSize])
    sigmaX = sigma
    sigmaY = sigma * theta

    for i in range(kernelSize):
        for j in range(kernelSize):
            x = i - halfSize
            y = j - halfSize

            expTerm = np.exp(-x**2 / (2 * sigmaX) - y**2 / (2 * sigmaY))
            xTerm = (x**2 - sigmaX**2) / (2 * math.pi * sigmaX**5 * sigmaY)
            yTerm = (y**2 - sigmaY**2) / (2 * math.pi * sigmaY**5 * sigmaX)

            kernel[i, j] = (xTerm + yTerm) * expTerm

    kernel = kernel / np.sum(kernel)
    return kernel

# %%
kernelSize=9
sigma=4
theta=3

imgFiltered1 = cv2.filter2D(img3, -1, createKernel(kernelSize, sigma, theta), borderType=cv2.BORDER_REPLICATE)
plt.imshow(imgFiltered1, cmap='gray')

# %%
def applySummFunctin(img):
    res = np.sum(img, axis = 0)    #  summ elements in columns
    return res

# %%
def normalize(img):
    (m, s) = cv2.meanStdDev(img)
    m = m[0][0]
    s = s[0][0]
    img = img - m
    img = img / s if s>0 else img
    return img
img4 = normalize(imgFiltered1)

# %%
summ = applySummFunctin(img4)
plt.plot(summ)
plt.show()

# %%
def smooth(x, window_len=11, window='hanning'):
#     if x.ndim != 1:
#         raise ValueError("smooth only accepts 1 dimension arrays.") 
    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.") 
    if window_len<3:
        return x
    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'") 
    s = np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w = np.ones(window_len,'d')
    else:
        w = eval('np.'+window+'(window_len)')

    y = np.convolve(w/w.sum(),s,mode='valid')
    return y

# %%
windows=['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
smoothed = smooth(summ, 35)
plt.plot(smoothed)
plt.show()

# %%
mins = argrelmax(smoothed, order=2)
arr_mins = np.array(mins)
plt.plot(smoothed)
plt.plot(arr_mins, smoothed[arr_mins], "x")
plt.show()

# %%
def crop_text_to_lines(text, blanks):
    x1 = 0
    y = 0
    lines = []
    for i, blank in enumerate(blanks):
        x2 = blank
        print("x1=", x1, ", x2=", x2, ", Diff= ", x2-x1)
        line = text[:, x1:x2]
        lines.append(line)
        x1 = blank
    return lines

# %%
def display_lines(lines_arr, orient='vertical'):
    plt.figure(figsize=(30, 30))
    if not orient in ['vertical', 'horizontal']:
        raise ValueError("Orientation is on of 'vertical', 'horizontal', defaul = 'vertical'") 
    if orient == 'vertical': 
        for i, l in enumerate(lines_arr):
            line = l
            plt.subplot(2, 10, i+1)  # A grid of 2 rows x 10 columns
            plt.axis('off')
            plt.title("Line #{0}".format(i))
            _ = plt.imshow(line, cmap='gray', interpolation = 'bicubic')
            plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    else:
            for i, l in enumerate(lines_arr):
                line = l
                plt.subplot(40, 1, i+1)  # A grid of 40 rows x 1 columns
                plt.axis('off')
                plt.title("Line #{0}".format(i))
                _ = plt.imshow(line, cmap='gray', interpolation = 'bicubic')
                plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()

# %%
found_lines = crop_text_to_lines(img3, arr_mins[0])

# %%
sess = tf.Session()
found_lines_arr = []
with sess.as_default():
    for i in range(len(found_lines)-1):
        found_lines_arr.append(tf.expand_dims(found_lines[i], -1).eval())

# %%
display_lines(found_lines)

# %%
def transpose_lines(lines):
    res = []
    for l in lines:
        line = np.transpose(l)
        res.append(line)
    return res

# %%
res_lines = transpose_lines(found_lines)
display_lines(res_lines, 'horizontal')

# %%
seg_images = []
for line in res_lines:
    seg_images.append(Image.fromarray(line))
    
# %%
for image in seg_images:
    print(pytesseract.image_to_string(image))

# %%
