def create_bs(beamstop_width=4, image_width=512):
    """
    Create a beam stop for an image with a cross of cross_width width,
    assuming the detector is made of four rectangular detectors with
    a cross shaped gap between them
    """
    assert (image_width % 2 == 0) == (
        beamstop_width % 2 == 0
    ), "Image width and gap width must be either both even or both odd"
    # 0 - a - b - img_width
    # Adding 1 helps properly center the gap for odd-sized
    a = (image_width - beamstop_width + 1) // 2
    b = (image_width + beamstop_width + 1) // 2
    c = image_width
    beamstop = f"""
    0 {a}
    0 {b}
    {a} {b}
    {a} {c}
    {b} {c}
    {b} {b}
    {c} {b}
    {c} {a}
    {b} {a}
    {b} 0
    {a} 0
    {a} {a}
    """
    return beamstop


def create_center_bs(beamstop_width=4, image_width=512):
    """
    Create a beam stop for an image with a cross of cross_width width,
    assuming the detector is made of four rectangular detectors with
    a cross shaped gap between them, and everything but the center
    has been properly corrected for intensity increase
    """
    assert (image_width % 2 == 0) == (
        beamstop_width % 2 == 0
    ), "Image width and gap width must be either both even or both odd"
    # 0 - a - b - img_width
    # Adding 1 helps properly center the gap for odd-sized
    a = (image_width - beamstop_width + 1) // 2
    b = (image_width + beamstop_width + 1) // 2
    c = image_width
    beamstop = f"""
    0 {a}
    0 {b}
    {a} {b}
    {a} {c}
    {b} {c}
    {b} {b}
    {c} {b}
    {c} {a}
    {b} {a}
    {b} 0
    {a} 0
    {a} {a}
    """
    return beamstop
