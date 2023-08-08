
import matplotlib.pyplot as plt
import pytesseract
import cv2
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Users\lyt4\Desktop\temp\WIT\Summer 2023\COMP 5500 - Senior Project\LeopardNotesScanner\segmentation\Tesseract-OCR\tesseract.exe'

def Crop(sorted_contours_lines, img):
    # crop image
    cpt = 0
    for ctr in sorted_contours_lines:
        rect=cv2.boundingRect(ctr)
        crop_img = img[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]]
        cv2.imshow(crop_img)
        cpt=cpt+1

def Kernel(img, org_img):
    # mask
    kernel = np.ones((1, 85), np.uint8)    # adjusting the params increases/decreases the kernel size (h, l)
    dilated = cv2.dilate(img, kernel, iterations = 1)  # can use invert_blur_gray_img, th1, th2, th3
    # cv2.imshow("mask", dilated)

    # draw contours on each line
    (contours, heirarchy) = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    sorted_contours_lines = sorted(contours, key=lambda ctr : cv2.boundingRect(ctr)[1]) # (x, y , w, h)
    
    for ctr in sorted_contours_lines:
        x,y,w,h = cv2.boundingRect(ctr)
        cv2.rectangle(org_img, (x,y), (x+w, y+h), (40, 100, 250), 2)

    # cv2.imshow("kernel", org_img)

    Crop(sorted_contours_lines, img)

    
def Threshhold(img):
    # removing noise
    se=cv2.getStructuringElement(cv2.MORPH_RECT , (8,8))
    bg=cv2.morphologyEx(img, cv2.MORPH_DILATE, se)
    out_gray=cv2.divide(img, bg, scale=255)
    out_binary=cv2.threshold(out_gray, 0, 255, cv2.THRESH_OTSU )[1]     
    
    # threshholds 
    ret, v127 = cv2.threshold(out_binary, 127, 255, cv2.THRESH_BINARY)
    mean = cv2.adaptiveThreshold(out_binary, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
    gaussian = cv2.adaptiveThreshold(out_binary, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    v127 = cv2.bitwise_not(v127)
    mean = cv2.bitwise_not(mean)
    gaussian = cv2.bitwise_not(gaussian)

    titles = ['binary', 'global v = 127', 'mean', 'gaussian']
    images = [img, v127, mean, gaussian]

    # for i in range(4):
    #     cv2.imshow(titles[i], images[i])

    return gaussian


def main():
    # read in img and convert it to 
    img = cv2.imread("test_images\img2.png")
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_gray_img = cv2.medianBlur(gray_img, 5)
    invert_blur_gray_img = cv2.bitwise_not(blur_gray_img)


    titles = ['original', 'gray', 'blur', 'invert']
    images = [img, gray_img, blur_gray_img, invert_blur_gray_img]

    # for i in range(4):
    #     cv2.imshow(titles[i], images[i])
    
    new_img = Threshhold(invert_blur_gray_img)
    Kernel(new_img, img)
    # cv2.imshow("gaussian", new_img)
    cv2.waitKey(0)

    # Crop(sorted_contours_lines, img)

if __name__ == '__main__':
    main()
