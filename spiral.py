import numpy as np

def segment(start, end, width, layer, net):
    '''draws segment from start to end

        start: start point of track, list
        end: end point of track, list
        width: width of line
        net: net used
        layer: layer line is drawn upon
    '''
    text = f"(segment (start {start[0]:6f} {start[1]:6f}) (end {end[0]:6f}  {end[1]:6f})"
    text += f" (width {width}) (layer {layer}) (net {net}))\n"
    return text


def arc(center, radius, startangle, finalangle, track_dct, segs=20):
    '''draws circular arc with center radius, start- and finalangle

        radius: radius of arc
        start angle: start angle of arc
        end angle: final angle of arc
        track_dct: width, net and layer of track, dct
        segs: number of straight semgents used to draw arc
    '''
    segangle = np.radians((finalangle-startangle) / segs)
    str_data = ""
    for i in range(int(segs)):
        start = center + [np.sin(segangle*i), np.cos(segangle*i)]*radius
        end = start + [np.sin(segangle), np.cos(segangle)]*radius
        str_data += segment(start.to_list(), end.to_list(), track_dct)


def archimidean_spiral(center, start_radius, track_distance,
                       start_angle, final_angle, turns, rotation,
                       track_dct, segments=20):
    '''draws spiral arc with center radius, start and finalangle

        radius: start radius of spiral
        track_distance: distance between tracks
        start angle: start angle of spiral
        final angle: final angle of spiral
        turns: number of turns in spiral
        rotation: rotation vector points toward screen, boolean
        track_distance: distance between tracks
        track_dct: settings for track
        segs: number of straight semgents used to draw arc
    '''
    str_data = ""
    for j in range(turns):
        # each turn consists of more segments
        # and a smaller angle angle per segment
        segments += 4
        segangle = 360.0 / segments
        segradius = track_distance / segments

        if j == turns-1:
            segments = int(final_angle/360*segments)

        def spiral_formula(i):
            angle = segangle*rotation*i + start_angle
            return ((start_radius + segradius * i + track_distance * (j+1))
                    *[np.sin(angle), np.cos(angle)])

        for i in range(segments):
            # central rings for HV and SNS
            start = center + spiral_formula(i)
            end = center + spiral_formula(i+1)
            str_data += segment(start.to_list(), end.to_list(), track_dct)

    return str_data

def drill_via(position, size=0.45, drill=0.3, net=0):
    '''drill via of size with dril in net
    '''
    posx, posy = position
    text = f"(via (at {posx:6f} {posy:6f}) (size {size})"
    text += f" (drill {drill}) (layers F.Cu B.Cu) (net {net}))\n" 
    return text

def archimedian_spiral_outer_radius(turns, track_width, track_distance, start_radius):
    ''' gives estimate of outer radius archimedian spiral 

        turns: number of turn in spiral
        track_width: width of track
        track_distance: distance between tracks
        start_radius: starting radius of archimedian spiral
    '''
    return (turns+1)*(track_width+track_distance) + start_radius


def four_layer_coil(center, top_angle, connect_angle, bottom_angle,
                    layer_stack, spiral_dct, track_dct):
    '''draws coil in electric pcb motor

       an electric motor consists of multiple coils in a circular pattern around
       a center. This coil consists out of four layers.
       Current can enter and exit the coil at the first and second layer.
       The entry angle of the first layer is known as the top angle
       The entry angle of the last layer is known as the bottom angle
       The via which connects layer 2 and 3 is placed at connect angle.

       center: center of coil, list
       top_angle: entry angle of first layer, float
       connect_angle: location of via between 2 and 3 layer, float
       bottom_angle: exit angle of final layer, float
       layer_stack: layers used to draw coils on, list
       spiral_dct: settings for spiral
       track_dct: settings for tracks

        returns String which can be read by KiCad PCB
    '''
    # vias to connect coils

    # vias of inner ring
    pos_hole = center + np.array([0, 0.35])
    res = drill_via(pos_hole)
    pos_hole -= np.array([0, 0.7])
    res += drill_via(pos_hole)
    # vias from outer ring
    radius = archimedian_spiral_outer_radius(spiral_dct['turns'],
                                             spiral_dct['start_radius'],
                                             track_dct['track_distance'],
                                             track_dct['track_width'])
    radius += 0.3
    
    angle = np.radians(90-connect_angle)
    pos_hole = center + radius * [np.cos(angle), np.sin(angle)]
    res += drill_via(pos_hole)

    # layer 0
    spiral_dct['start_angle'] = 180
    spiral_dct['rotation'] = 1
    spiral_dct['final_angle'] = top_angle
    track_dct['layer'] = layer_stack[0]
    res += archimidean_spiral(**spiral_dct, track_dct)
    # layer 1
    spiral_dct['start_angle'] = 180
    spiral_dct['rotation'] = -1
    spiral_dct['final_angle'] = connect_angle
    track_dct['layer'] = layer_stack[1]
    res += archimidean_spiral(**spiral_dct, track_dct)
    # layer 2
    spiral_dct['start_angle'] = 0
    spiral_dct['rotation'] = 1
    spiral_dct['final_angle'] = (180-connect_angle+360)%360
    track_dct['layer'] = layer_stack[2]
    res += archimidean_spiral(**spiral_dct, track_dct)
    # layer 3
    spiral_dct['start_angle'] = 0
    spiral_dct['rotation'] = -1
    spiral_dct['final_angle'] = bottom_angle
    track_dct['layer'] = layer_stack[3]
    res += archimidean_spiral(**spiral_dct, track_dct)
    return res


if __name__ == '__main__':

    track_dct = { "layer": "F.Cu",
                  "net": "0",
                  "width": 0.15}

    spiral_dct = {
        "center": np.array([115.0, 105.0]),
        "radius": 0.5,  # start radius in mm
        "track_distance": 0.15,  # distance between tracks
        "startangle": 0,
        "finalangle": 360, 
        "turns": 11,
        "rotation": -1}
    
    coil_dct = {
        "center": np.array([115.0, 105.0]),
        "top_angle": 0,       # degrees
        "connect_angle": 45,  # degrees
        "bottom_angle": 360,  # degrees
        "layer_stack": ['F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu']
    }
       
    # open base file
    start = None
    end = None
    with open("base.kicad_pcb", "r") as f:
        lines = f.readlines()
        start = lines[:99]
        end = lines[99:]
   
    
    # included angle
    poles = 6              # poles of motor
    cntr = np.array([115.0, 105.0])  # center of motor
    angle_included = 2*np.pi/poles
    outer_radius = archimedian_spiral_outer_radius(spiral_dct['turns'],
                                                   spiral_dct['start_radius'],
                                                   track_dct['track_distance'],
                                                   track_dct['track_width'])
    # safety margin
    outer_radius += coil_dct['track_distance']/2
    # https://math.stackexchange.com/questions/134606/distance-between-any-two-points-on-a-unit-circle
    radius_motor = (2*outer_radius)/(2*np.sin(angle_included/2))

    with open('spiral.kicad_pcb', 'w') as f:
        for line in start:
            f.write(line)

        top_angles = [60, 360, 300]
        for pole in range(poles):
            angle = angle_included*pole +angle_included/2
            coil_center = cntr + np.array([np.cos(angle), np.sin(angle)])*radius_motor
            # top poles of motor should connect to phases
            if pole >= 3:
                coil_dct['top_angle'] = 0
            else:
                coil_dct['top_angle'] = (np.degrees(angle_included)*(1-pole)+360)%360
            coil_dct['center'] = coil_center
            coil_dct['connect_angle'] = (45+np.degrees(angle_included)*pole + 360)%360
            coil_dct['bottom_angle'] = (np.degrees(angle_included)*(2+pole)+360)%360
            f.write(four_layer_coil(**coil_dct, spiral_dct, track_dct))

        for line in end:
            f.write(line)
