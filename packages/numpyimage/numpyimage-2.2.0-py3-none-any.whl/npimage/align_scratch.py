


def align(im1, im2, num_divisions=4):
    """
    Return a translated version of im1 that is aligned with im2.

    To align the images, this function divides im1 into a grid of
    num_divisions x num_divisions regions. For each region, we find the
    region in im2 that is most similar to it. After removing outliers
    for which the similarity score is too low, we calculate the average
    translation between the two images. We then shift im1 by this
    average translation.
    """
    # The code below is entirely GitHub copilot generated and needs to
    # be looked at, finished, tested, etc

    # Divide the image into a grid of num_divisions x num_divisions regions
    height, width = im1.shape
    region_height = height // num_divisions
    region_width = width // num_divisions

    # Initialize lists to store the translations for each region
    translations = []

    # For each region in im1, find the most similar region in im2
    for i in range(num_divisions):
        for j in range(num_divisions):
            # Define the region in im1
            top_left = (i * region_height, j * region_width)
            bottom_right = ((i + 1) * region_height, (j + 1) * region_width)
            region1 = im1[top_left[0]:bottom_right[0], top_left[1]:bottom_right[1]]

            # Define the search region in im2
            search_bbox = (slice(max(0, top_left[0] - region_height),
                                 min(height, bottom_right[0] + region_height)),
                           slice(max(0, top_left[1] - region_width),
                                 min(width, bottom_right[1] + region_width)))

            # Find the most similar region in im2
            top_left2, score = find_landmark(im2, region1, search_bbox=search_bbox)

            # Add the translation to the list of translations
            translations.append((top_left[0] - top_left2[0], top_left[1] - top_left2[1]))

    # Remove outliers from the list of translations
    translations = np.array(translations)
    mean_translations = np.mean(translations)
    # Shift im1 by the average translation
    aligned_im1 = np.roll(im1, mean_translations, axis=(0, 1))
