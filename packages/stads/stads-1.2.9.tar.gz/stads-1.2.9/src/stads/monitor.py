import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D

from stads.image_processing import extract_patch  # Make sure this function is correct

def configure_axis(ax, imageData):
    ax.set_xlim(0, imageData.shape[1])
    ax.set_ylim(0, imageData.shape[0])
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])

def draw_detail_rectangle(ax, detail_size, origin=(0, 0)):
    rectangle = patches.Rectangle(origin, detail_size[1], detail_size[0], linewidth=1.0, edgecolor='blue',
                                  facecolor='none')
    ax.add_patch(rectangle)

def draw_region_of_interest(ax, detailSize, regionOfInterest):
    ((x0, y0), (w, h)) = regionOfInterest

    # Fix width and height ordering
    rectangle = patches.Rectangle((x0, y0), w, h, linewidth=1.0, edgecolor='blue', facecolor='none')
    ax.add_patch(rectangle)

    # Replace polygons with proper lines
    line1 = Line2D([detailSize[1], y0 + w], [0, x0], color='blue', linestyle='dashed')
    line2 = Line2D([0, y0], [detailSize[0], x0 + h], color='blue', linestyle='dashed')
    ax.add_line(line1)
    ax.add_line(line2)

def draw_roi_highlight(ax, detailSize, regionOfInterest):
    draw_detail_rectangle(ax, detailSize)
    draw_region_of_interest(ax, detailSize, regionOfInterest)

def generate_mask_from_coordinates(yCoordinates, xCoordinates, imageShape):
    yCoordinates = np.asarray(yCoordinates, dtype=int)
    xCoordinates = np.asarray(xCoordinates, dtype=int)

    mask = np.zeros(imageShape, dtype=np.float32)
    valid = (
        (yCoordinates >= 0) & (yCoordinates < imageShape[0]) &
        (xCoordinates >= 0) & (xCoordinates < imageShape[1])
    )
    mask[yCoordinates[valid], xCoordinates[valid]] = 1.0
    return mask

def display_masked_image(mask, originalImage):
    plt.imshow(originalImage, cmap='gray')
    plt.title("Original Image")
    plt.show()

    plt.imshow(mask, cmap='binary')
    plt.title("Mask")
    plt.show()

    masked = np.multiply(originalImage, mask).astype(originalImage.dtype)
    plt.imshow(masked, cmap='gray')
    plt.title("Masked Image")
    plt.show()

def visualize_microscope_image(imageData, ax=None, regionOfInterest=None, imageTitle="", savePlot=False, savePath='output.png'):
    if ax is None:
        fig, ax = plt.subplots()

    imageCenter = (int(imageData.shape[0] / 2), int(imageData.shape[1] / 2))

    image = ax.imshow(imageData, cmap='gray')
    plt.colorbar(image, ax=ax, fraction=0.046, pad=0.04)

    configure_axis(ax, imageData)

    if regionOfInterest is not None:
        regionOfInterestPatch = extract_patch(imageData, regionOfInterest)
        ax.imshow(regionOfInterestPatch, extent=(0, imageCenter[1], imageCenter[0], 0),
                  interpolation='none', cmap='gray')
        draw_roi_highlight(ax, imageCenter, regionOfInterest)

    ax.set_title(imageTitle)

    if savePlot:
        extent = ax.get_window_extent().transformed(ax.figure.dpi_scale_trans.inverted())
        fig = ax.get_figure()
        fig.savefig(savePath, bbox_inches=extent, pad_inches=0.0, dpi=300)
        plt.close(fig)
    else:
        plt.show()

def overlay_images(firstImage, secondImage):
    if firstImage.shape != secondImage.shape:
        raise ValueError("Input images must have the same dimensions")

    firstImage = firstImage.astype(np.uint8)
    secondImage = secondImage.astype(np.uint8)
    greenChannel = np.zeros_like(firstImage)

    firstRGBImage = cv2.merge([greenChannel, greenChannel, firstImage])
    secondRGBImage = cv2.merge([secondImage, greenChannel, greenChannel])

    combinedImage = cv2.addWeighted(firstRGBImage, 1, secondRGBImage, 1, 0)
    combinedImage = np.clip(combinedImage, 0, 255).astype(np.uint8)

    return combinedImage

