

def smooth_angle(old_angle, new_angle, alpha=0.75):
    if old_angle == None:
        return new_angle
    return old_angle + alpha * (new_angle - old_angle)
