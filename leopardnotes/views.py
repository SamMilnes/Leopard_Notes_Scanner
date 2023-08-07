from django.shortcuts import redirect, render
from django.core.files.base import ContentFile
from PIL import Image
import pytesseract
from profiles.models import OCRImage
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.contrib import messages
from io import BytesIO
import base64
from django.http import JsonResponse
import cv2
import numpy as np
from pix2tex.cli import LatexOCR
import json

pytesseract.pytesseract.tesseract_cmd = 'C://Program Files//Tesseract-OCR//tesseract.exe'
latex_model = LatexOCR()


def Crop(sorted_contours_lines, img):
    """
        Crop regions from an image based on sorted contours.

        This function takes a list of sorted contours (sorted_contours_lines) and an image (img),
        and crops the regions of the image that correspond to each contour's bounding rectangle.
        Each cropped region is highlighted with a blue rectangle drawn on the input image.

        Args:
            sorted_contours_lines (list): A list of contours (each represented as a list of points)
                                         sorted in a specific order.
            img (numpy.ndarray): The input image on which the cropped regions will be highlighted.

        Returns:
            None: The function modifies the input image in-place by drawing rectangles around
                  the bounding rectangles of each contour.
    """
    for ctr in sorted_contours_lines:
        rect = cv2.boundingRect(ctr)
        cv2.rectangle(img, (rect[0], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]), (40, 100, 250), 2)


def Kernel(img):
    """
        Apply a morphological kernel operation to an image and extract cropped regions.

        This function takes an image (img), applies a dilation operation using a custom kernel,
        finds contours in the resulting dilated image, and then sorts these contours based on their
        vertical positions. Finally, it calls the Crop function to extract and highlight the cropped
        regions corresponding to the sorted contours.

        Args:
            img (numpy.ndarray): The input image on which the kernel operation will be applied.

        Returns:
            None: The function modifies the input image in-place by extracting and highlighting
                  cropped regions based on sorted contours.
    """
    kernel = np.ones((1, 85), np.uint8)
    dilated = cv2.dilate(img, kernel, iterations=1)

    (contours, _) = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    sorted_contours_lines = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[1])

    Crop(sorted_contours_lines, img)


def Threshhold(img):
    """
        Apply various thresholding techniques to an image for noise removal and feature enhancement.

        This function takes an image (img), applies morphological operations and thresholding techniques
        to remove noise and enhance features. It utilizes adaptive thresholding methods and bitwise
        operations to obtain different thresholded versions of the image.

        Args:
            img (numpy.ndarray): The input grayscale image on which thresholding techniques will be applied.

        Returns:
            numpy.ndarray: A thresholded image obtained using the Gaussian-based adaptive thresholding.
    """
    se = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 8))
    bg = cv2.morphologyEx(img, cv2.MORPH_DILATE, se)
    out_gray = cv2.divide(img, bg, scale=255)
    out_binary = cv2.threshold(out_gray, 0, 255, cv2.THRESH_OTSU)[1]
    gaussian = cv2.adaptiveThreshold(out_binary, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    gaussian = cv2.bitwise_not(gaussian)

    return gaussian


def perform_segmentation(image):
    """
        Perform image segmentation on the provided image.

        Args:
            image (file-like object): A binary image file to be segmented.

        Returns:
            segmented_images_base64 (list): A list of base64-encoded strings representing individual segmented images.
            full_image_segmented_base64 (str): A base64-encoded string representing the full image with segmentation rectangles.
        """

    # Convert the image to numpy array
    nparr = np.frombuffer(image.read(), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Create a copy of the original image
    img_copy = img.copy()

    # Convert the image to grayscale and perform the segmentation
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_gray_img = cv2.medianBlur(gray_img, 5)
    invert_blur_gray_img = cv2.bitwise_not(blur_gray_img)
    new_img = Threshhold(invert_blur_gray_img)
    Kernel(new_img)

    # Draw the rectangle boxes on the original image copy
    (contours, _) = cv2.findContours(new_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours_lines = sorted(contours, key=lambda ctr: cv2.boundingRect(ctr)[1])
    Crop(sorted_contours_lines, img_copy)

    # Return a list of individual segmented images as base64 strings
    segmented_images_base64 = []
    for contour in sorted_contours_lines:
        rect = cv2.boundingRect(contour)
        x, y, w, h = rect
        cropped_img = img_copy[y:y+h, x:x+w]

        _, buffer = cv2.imencode('.png', cropped_img)
        segmented_image_base64 = base64.b64encode(buffer).decode('utf-8')
        segmented_images_base64.append(segmented_image_base64)

    # Encode the full segmented image
    _, buffer = cv2.imencode('.png', img_copy)
    full_image_segmented_base64 = base64.b64encode(buffer).decode('utf-8')

    return segmented_images_base64, full_image_segmented_base64


def performOCR(image_data, ocr_type):
    """
        Perform Optical Character Recognition (OCR) on an image.

        This function takes image data in base64 format and performs OCR based on the specified OCR type.

        Args:
            image_data (str): Base64-encoded image data.
            ocr_type (str): Type of OCR to perform. Can be 'text' for text OCR or 'math' for mathematical expressions
            OCR.

        Returns:
            str: OCR result as a string. If the OCR type is not recognized, an empty string is returned.
    """

    decoded_data = base64.b64decode(image_data)
    nparr = np.frombuffer(decoded_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    pil_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    if ocr_type == 'text':
        ocr_result = pytesseract.image_to_string(pil_image)
    elif ocr_type == 'math':
        ocr_result = latex_model(pil_image)
    else:
        ocr_result = ''

    return ocr_result


def processOCRResults(segmented_images, selected_options):
    """
        Process OCR results for a list of segmented images using selected OCR options.

        This function takes a list of segmented image data and a dictionary of selected OCR options for each segment.
        It performs OCR on each segmented image based on the selected option and returns a list of OCR results.

        Args:
            segmented_images (list): A list of segmented image data, where each element is a base64-encoded image.
            selected_options (dict): A dictionary containing selected OCR options for each segmented image.
                The keys are in the format 'segmented_dropdown_{index}', where index is the 1-based index of the
                segment.
                The values are the selected OCR option, which can be 'text' for text OCR or 'math' for mathematical
                expressions OCR.

        Returns:
            list: A list of OCR results as strings. The order of results corresponds to the order of segmented_images.
        """
    ocr_results = []

    for index, image_data in enumerate(segmented_images):
        selected_option = selected_options.get(f'segmented_dropdown_{index + 1}', 'text')
        ocr_result = performOCR(image_data, selected_option)
        ocr_results.append(ocr_result)

    return ocr_results


def segment_image(request):
    """
        Segment an uploaded image and return segmented results in a JSON response.

        This view function processes a POST request containing an uploaded image file. It performs image segmentation
        using the `perform_segmentation` function and returns the segmented images as well as the fully segmented image
        in a JSON response.

        Args:
            request (HttpRequest): The incoming HTTP request object.

        Returns:
            JsonResponse: A JSON response containing segmented images and the full segmented image, or an error message.
    """
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']

        segmented_images, full_image_segmented = perform_segmentation(image)

        if segmented_images is not None:
            response_data = {
                'segmented_images': segmented_images,
                'full_image_segmented': full_image_segmented,
            }
            return JsonResponse(response_data)
        else:
            return JsonResponse({'error': 'Error performing image segmentation.'})

    return JsonResponse({'error': 'Invalid request'})


def submit_marked_data(request):
    """
        Process marked image data, perform OCR, and save OCR results to the database.

        This view function processes a POST request containing marked image data in JSON format. It extracts segmented
        images and their corresponding OCR types from the data, performs OCR on the segmented images, and saves
        the combined OCR results along with other relevant information to the database.
        Args:
            request (HttpRequest): The incoming HTTP request object.

        Returns:
            HttpResponse: A rendered HTML response indicating the processing and saving status.

    """
    if request.method == 'POST':
        marked_data = json.loads(request.POST.get('image_data'))

        segmented_images = []
        selected_options = {}
        for item in marked_data:
            segmented_images.append(item['imageBase64'])
            selected_options[f'segmented_dropdown_{len(segmented_images)}'] = item['ocrType']

        print(segmented_images)

        # Perform OCR on the segmented images with their respective OCR types
        ocr_results = processOCRResults(segmented_images, selected_options)
        # Combine the OCR results into a single string
        combined_ocr_text = '\n'.join(ocr_results)
        print(combined_ocr_text)

        image = request.FILES.get('image')
        title = request.POST.get('title')

        full_image_segmented_base64 = request.POST.get('preview-image')
        full_image_segmented_binary = base64.b64decode(full_image_segmented_base64)

        filename = f"{title}.png"

        ocr_image = OCRImage.objects.create(
            profile=request.user.profile,
            title=title,
            ocr_text=combined_ocr_text,
            uploaded_image=image,
            fully_segmented_image=ContentFile(full_image_segmented_binary, name=filename),
            isSnipped=False,
        )
        context = {
            'ocr_text': ocr_image.ocr_text,
            'title': ocr_image.title,
            'image': ocr_image.uploaded_image,
            'fully_segmented_image': ocr_image.fully_segmented_image,
            'isSnipped': False,
        }

        messages.success(request, 'OCR image successfully processed and saved!')
        return render(request, 'main/ocr.html', context)

    return JsonResponse({'error': 'Invalid request'})


def home_view(request):
    """
    Display a welcoming page and redirect to the board if the user is authenticated.

    This view function renders a welcoming page. If the user is authenticated (logged in),
    it redirects them to the "posts/" page (board). If the user is not authenticated,
    it displays the welcoming page.

    Args:
        request (HttpRequest): The incoming HTTP request object.

    Returns:
        HttpResponse: A rendered HTML response indicating the welcoming page or redirection.
    """
    if request.user.is_authenticated:
        return redirect("posts/")
    return render(request, "main/home.html")


def ocr_view(request):
    """
        Display the OCR page or redirect to the home view based on user authentication.

        This view function renders the OCR page (main/ocr.html) if the user is authenticated (logged in).
        If the user is not authenticated, it redirects them to the home view.

        Args:
            request (HttpRequest): The incoming HTTP request object.

        Returns:
            HttpResponse: A rendered HTML response indicating the OCR page or redirection.
    """

    if request.user.is_authenticated:
        return render(request, 'main/ocr.html')
    else:
        return redirect('home-view')


def snip_view(request):
    """
        Process snipped image data, perform OCR, and save OCR results to the database.

        This view function processes a POST request containing snipped image data, performs OCR on the snipped image,
        and saves the OCR results, along with other relevant information, to the database. It also handles rendering
        the OCR snipping page and displaying error messages in case of issues.

        Args:
            request (HttpRequest): The incoming HTTP request object.

        Returns:
            HttpResponse: A rendered HTML response indicating the OCR snipping page or processing status.
    """
    if request.user.is_authenticated:
        if request.method == 'POST':
            print("Form submitted successfully!")

            snipped_image_data = request.POST.get('snipped_image_data')
            original_image_data = request.POST.get('original_image_data')
            ocr_type = request.POST.get('ocr_switch')

            title = request.POST.get('title')

            if not snipped_image_data:
                return render(request, 'main/ocr.html', {'error': 'Please snip the image first.'})

            try:
                # Save the original image to the file path
                filename = f"{title}.png"
                with open(filename, 'wb') as f:
                    f.write(base64.b64decode(original_image_data.split(',')[1]))

                # Perform OCR on the snipped image
                ocr_image = Image.open(BytesIO(base64.b64decode(snipped_image_data.split(',')[1])))
                if ocr_type == 'text':
                    ocr_text = pytesseract.image_to_string(ocr_image)
                elif ocr_type == 'math':
                    ocr_text = latex_model(ocr_image)
                else:
                    ocr_text = 'Did not work.... Try again'

                if ocr_text:
                    ocr_image = OCRImage.objects.create(
                        profile=request.user.profile,
                        title=title,
                        ocr_text=ocr_text,
                        uploaded_image=ContentFile(base64.b64decode(original_image_data.split(',')[1]), name=filename),
                        fully_segmented_image=ContentFile(base64.b64decode(snipped_image_data.split(',')[1]), name=filename),
                        isSnipped=True,
                    )
                    context = {
                        'ocr_text': ocr_image.ocr_text,
                        'title': ocr_image.title,
                        'image': ocr_image.uploaded_image,
                        'fully_segmented_image': ocr_image.fully_segmented_image,
                        'isSnipped': True,
                    }
                    messages.success(request, 'OCR image successfully processed and saved!')
                    return render(request, 'main/ocr_snipping.html', context)

            except Exception as e:
                print("Error processing snipped image:", e)
                return render(request, 'main/ocr_snipping.html', {'error': 'Error processing the snipped image.'})

        return render(request, 'main/ocr_snipping.html')
    else:
        return redirect('home-view')


def ocr_results_view(request):
    """
        Display OCR results associated with the authenticated user.

        This view function retrieves OCR images associated with the authenticated user's profile and renders them
        in the OCR results page (main/ocr_results.html).

        Args:
            request (HttpRequest): The incoming HTTP request object.

        Returns:
            HttpResponse: A rendered HTML response displaying the OCR results or redirecting to the home view.
    """
    if request.user.is_authenticated:
        ocr_images = OCRImage.objects.filter(profile=request.user.profile)
        context = {
            'ocr_images': ocr_images,
        }
        return render(request, 'main/ocr_results.html', context)
    else:
        return redirect('home-view')


class OCRImageDeleteView(DeleteView):
    """
        Delete view for deleting an OCRImage instance.

        This class-based view allows users to delete an OCRImage instance. It provides a confirmation template and
        redirects to the OCR results view after successful deletion.

        Attributes:
            model (class): The model associated with this view (OCRImage).
            template_name (str): The name of the template to be used for displaying the delete confirmation.
            success_url (str): The URL to redirect to after successful deletion.
    """
    model = OCRImage
    template_name = 'main/confirm_delete.html'  # Provide the confirmation template
    success_url = reverse_lazy('ocr-view-results')


