def resize_crop(orig_dims, dest_dims, crop):
    """
    return a new crop tuple
    """
    import math
    orig_width, orig_height = orig_dims
    dest_width, dest_height = dest_dims
    crop_l, crop_t, crop_r, crop_b = crop
    crop_width = crop_r - crop_l
    crop_height = crop_b - crop_t

    # Scale dest size to crop size (transmogrify will scale it back down)
    width_ratio = float(crop_width) / dest_width
    height_ratio = float(crop_height) / dest_height
    ratio = max(width_ratio, height_ratio)
    new_dest_width = int(dest_width * ratio)
    new_dest_height = int(dest_height * ratio)
    if new_dest_width > orig_width or new_dest_height > orig_height:
        ratio = min(width_ratio, height_ratio)
        new_dest_width = int(dest_width * ratio)
        new_dest_height = int(dest_height * ratio)

    # do we pad the width or the height?
    xdiff = abs(new_dest_width - crop_width)
    ydiff = abs(new_dest_height - crop_height)
    if xdiff:
        # "Must pad the width"
        padding1 = xdiff / 2
        padding2 = int(math.ceil(xdiff / 2.0))  # to account for odd numbers
        buffer1 = orig_width - crop_r  # Right side
        buffer2 = crop_l  # Left side
        if padding1 <= buffer1 and padding2 <= buffer2:
            # "pad equally"
            crop_r += padding1
            crop_l -= padding2
        elif padding1 > buffer1:
            # "pad left more than right"
            crop_r += buffer1
            crop_l -= padding2
            crop_l -= padding1 - buffer1
        else:
            # "pad right more than left"
            crop_l -= buffer2
            crop_r += padding1
            crop_r += padding2 - buffer2
    elif ydiff:
        # "Must pad the height"
        padding1 = ydiff / 2
        padding2 = int(math.ceil(ydiff / 2.0))  # to account for odd numbers
        buffer1 = orig_height - crop_b  # Bottom
        buffer2 = crop_t  # Top
        if padding1 <= buffer1 and padding2 <= buffer2:
            # "pad equally"
            crop_b += padding1
            crop_t -= padding2
        elif padding1 > buffer1:
            # "pad top more than bottom"
            crop_b += buffer1
            crop_t -= padding2
            crop_t -= padding1 - buffer1
        else:
            # "pad bottom more than top"
            crop_t -= buffer2
            crop_b += padding1
            crop_b += padding2 - buffer2

    return (crop_l, crop_t, crop_r, crop_b)

TOP = 'top'
LEFT = 'left'
CENTER = 'center'
RIGHT = 'right'
BOTTOM = 'bottom'


def fill_box(orig_dims, dest_dims, crop=None, origin=CENTER):
    """
    orig_dims = (w, h)
    dest_dims = (w, h)
    crop = optional (l, t, r, b) - Use this crop to determine scale, what to crop.
    origin  = optional ('tl', 't', 'tr', 'l', 'c', 'r', 'bl', 'b', 'br')

    Returns the (l, t, r, b) crop to fill the dest_dims
    """
    if crop and crop[2] != 0 and crop[3] != 0:
        return resize_crop(orig_dims, dest_dims, crop)
    else:
        if origin not in (TOP, LEFT, CENTER, RIGHT, BOTTOM):
            origin = CENTER
            # raise ValueError("'origin' parameter must be one of %s." % ", ".join((TOP, LEFT, CENTER, RIGHT, BOTTOM)))
        orig_width, orig_height = orig_dims
        dest_width, dest_height = dest_dims

        # Scale dest size to original size to find the crop (transmogrify will scale it back down)
        width_ratio = float(orig_width) / dest_width
        height_ratio = float(orig_height) / dest_height
        ratio = max(width_ratio, height_ratio)
        new_dest_width = int(dest_width * ratio)
        new_dest_height = int(dest_height * ratio)
        if new_dest_width > orig_width or new_dest_height > orig_height:
            ratio = min(width_ratio, height_ratio)
            new_dest_width = int(dest_width * ratio)
            new_dest_height = int(dest_height * ratio)

        xdiff = abs(orig_width - new_dest_width)
        ydiff = abs(orig_height - new_dest_height)
        if ydiff:
            # "Pad height"
            if origin == CENTER:
                padding1 = ydiff / 2
                return (0, padding1, new_dest_width, padding1 + new_dest_height)
            elif origin == TOP:
                return (0, 0, new_dest_width, new_dest_height)
            elif origin == BOTTOM:
                return (0, ydiff, new_dest_width, orig_height)
        else:
            # "Pad width"
            if origin == CENTER:
                padding1 = xdiff / 2
                return (padding1, 0, padding1 + new_dest_width, new_dest_height)
            elif origin == RIGHT:
                return (xdiff, 0, orig_width, new_dest_height)
            else:
                return (0, 0, new_dest_width, new_dest_height)


def fit_to_box(orig_dims, dest_width=20000, dest_height=20000):
    """
    Given a width, height or both, it will return the width and height to
    fit in the given area.
    """
    im_width, im_height = orig_dims

    if dest_width == 20000 and dest_height == 20000:
        return im_width, im_height
    elif dest_width is None:
        dest_width = 20000
    elif dest_height is None:
        dest_height = 20000

    if dest_width < dest_height:
        scale = float(dest_width) / float(im_width)
        dest_height = int(round(scale * im_height))
    else:
        scale = float(dest_height) / float(im_height)
        dest_width = int(round(scale * im_width))

    return dest_width, dest_height


def test():
    print "Fill all Top"
    c = fill_box((1000, 1000), (300, 250), (0, 334, 1000, 1000))
    assert (0, 167, 1000, 1000) == c

    print "Fill all on bottom"
    c = fill_box((1000, 1000), (300, 250), (0, 0, 1000, 666))
    assert (0, 0, 1000, 833) == c

    print "Fill top and bottom equally"
    c = fill_box((1000, 1000), (300, 250), (0, 167, 1000, 833))
    assert (0, 83, 1000, 916) == c

    print "Fill all Left"
    c = fill_box((1000, 1000), (250, 300), (334, 0, 1000, 1000))
    assert (167, 0, 1000, 1000) == c

    print "Fill all right"
    c = fill_box((1000, 1000), (250, 300), (0, 0, 666, 1000))
    assert (0, 0, 833, 1000) == c

    print "Fill left and right equally"
    c = fill_box((1000, 1000), (250, 300), (167, 0, 833, 1000))
    assert (83, 0, 916, 1000) == c

    print "No crop, fill height"
    c = fill_box((1000, 1000), (300, 250))
    assert (0, 83, 1000, 916) == c

    print "No crop, Fill width"
    c = fill_box((1000, 1000), (250, 300))
    assert (83, 0, 916, 1000) == c

if __name__ == "__main__":
    test()
