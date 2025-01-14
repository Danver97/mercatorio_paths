from typing import Sequence, Tuple

def circle_boundaries(radius) -> Sequence[Tuple[int, int, int]]:
    # Radius needs to be an integer for this grid-based approach
    radius = radius - 1 # excluding the center
    boundaries = []
    
    # Determine the size of the grid
    for x in range(-radius, radius + 1):
        line_boundaries = []
        for y in range(-radius, radius + 1):
            # Equation of a circle: x^2 + y^2 = r^2
            distance = (x**2 + y**2)**0.5
            # if radius - 0.5 <= distance <= radius:
            if radius - 0.5 <= distance <= radius + 0.5:
                line_boundaries.append(y)
                # print("#", end="")
            else:
                # print(" ", end="")
                pass
        boundaries.append((x, min(line_boundaries), max(line_boundaries)))
        # print()
    return boundaries

def compute_ranges(coords: Tuple[int, int], radius: int) -> Sequence[Tuple[Tuple[int, int], Tuple[int, int]]]:
    x, y = coords
    boundaries = circle_boundaries(radius)
    ranges = []
    for b in boundaries:
        (offset_x, offset_y_left, offset_y_right) = b
        ranges.append(((x + offset_x, y + offset_y_left), (x + offset_x, y + offset_y_right)))
    return ranges

circle_boundaries(8)
circle_boundaries(30)

# print()
      #####
    ##  |  ##
  ##    |    ##
  #     |     #
 #             #
 #      |      #
#       |       #
#       |       #
#--- ---x--- ---#
#               #
#               #
 #             #
 #             #
  #           #
  ##         ##
    ##     ##
      #####