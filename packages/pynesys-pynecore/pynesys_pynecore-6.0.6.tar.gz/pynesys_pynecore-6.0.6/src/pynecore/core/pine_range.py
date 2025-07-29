def pine_range(from_num, to_num, step_num=None):
    """
    Emulates Pine Script's for loop range behavior.

    :param from_num: Start value (inclusive)
    :param to_num: End value (inclusive)
    :param step_num: Step value (optional, defaults to +1/-1 based on direction)
    :return: A range-like object that includes both from_num and to_num
    :raises ValueError: If step_num is zero
    """
    # Determine direction based on from_num and to_num
    direction = 1 if from_num <= to_num else -1

    # Use default step if none provided
    if step_num is None:
        step_num = direction

    # Prevent infinite loops
    if step_num == 0:
        raise ValueError("Step cannot be zero in pine_range")

    # Ensure step direction matches the from->to direction
    if (direction > 0 > step_num) or (direction < 0 < step_num):
        step_num = -step_num

    # Adjust end value to include to_num
    end = to_num + direction

    # Create range with proper direction
    return range(from_num, end, step_num)
