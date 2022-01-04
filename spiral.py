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


def graphic_circle(center, radius, layer, width=0.05):
    ''' draws graphic circle as position with radius at layer with width
    '''
    text = f"(gr_circle (center {center[0]} {center[1]}) (end {center[0]} {center[1]+radius})"
    text += f"(layer {layer}) (width {width}))"
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

    def circle_formula(i):
        angle = segangle*i+np.radians(startangle)
        return np.array([np.sin(angle), np.cos(angle)])*radius

    for i in range(int(segs)):
        start = center + circle_formula(i)
        end = center + circle_formula(i+1)
        str_data += segment(start.tolist(), end.tolist(), **track_dct)
    return str_data


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
    # track distance should account for track width
    track_distance += track_dct['width']
    for j in range(turns):
        # each turn consists of more segments
        # and a smaller angle angle per segment
        segments += 4
        segangle = 360.0 / segments
        segradius = track_distance / segments

        if j == turns-1:
            segments = int(final_angle/360*segments)

        def spiral_formula(i):
            angle = np.radians(segangle*rotation*i + start_angle)
            return ((start_radius + segradius * i + track_distance*(j+1))
                    *np.array([np.sin(angle), np.cos(angle)]))

        for i in range(segments):
            # central rings for HV and SNS
            start = center + spiral_formula(i)
            end = center + spiral_formula(i+1)
            str_data += segment(start.tolist(), end.tolist(), **track_dct)

    return str_data

def drill_via(position, size=0.45, drill=0.3, net=0):
    '''drill via of size with dril in net
    '''
    text = f"(via (at {position[0]:6f} {position[1]:6f}) (size {size})"
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


def four_layer_coil(center, top_angle, connect_angle, bottom_angle, rotation,
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
                                             track_dct['width'],
                                             spiral_dct['track_distance'],
                                             spiral_dct['start_radius'])                                             
    # some additional offset to not touch tracks
    radius += 0.3
    
    angle = np.radians(90-connect_angle)
    pos_hole = center + radius * np.array([np.cos(angle), -np.sin(angle)])
    res += drill_via(pos_hole)
    spiral_dct['center'] = center
    # layer 0
    spiral_dct['start_angle'] = 180
    spiral_dct['rotation'] = 1*rotation
    spiral_dct['final_angle'] = top_angle
    track_dct['layer'] = layer_stack[0]
    res += archimidean_spiral(**spiral_dct, track_dct=track_dct)
    # layer 1
    spiral_dct['start_angle'] = 180
    spiral_dct['rotation'] = -1*rotation
    spiral_dct['final_angle'] = connect_angle
    track_dct['layer'] = layer_stack[1]
    res += archimidean_spiral(**spiral_dct, track_dct=track_dct)
    # layer 2
    spiral_dct['start_angle'] = 0
    spiral_dct['rotation'] = 1*rotation
    spiral_dct['final_angle'] = (180-connect_angle+360)%360
    track_dct['layer'] = layer_stack[2]
    res += archimidean_spiral(**spiral_dct, track_dct=track_dct)
    # layer 3
    spiral_dct['start_angle'] = 0
    spiral_dct['rotation'] = -1*rotation
    spiral_dct['final_angle'] = bottom_angle
    track_dct['layer'] = layer_stack[3]
    res += archimidean_spiral(**spiral_dct, track_dct=track_dct)
    return res


def pcb_motor(position, axis_radius, spiral_dct, track_dct, coil_dct):
    '''draws Carl Bugeja styled PCB motor at position

    pcbmotor has 6 coils and 4 layers
    connection between poles is done via the center and using 
    different layer stacks per coil
    user still has to draw the final connections
    
    position: position of PCB motor
    axis_radius: radius of central axis of PCB motor
    spiral_dct: settings for spiral in coils, dct
    coil_dct: settings for coil, dct
    track_dct: settings for tracks, dct
    '''
    
    poles = 6                        # poles of motor
    angle_included = 2*np.pi/poles   # included angle
    outer_radius = archimedian_spiral_outer_radius(spiral_dct['turns'],
                                                   track_dct['width'],
                                                   spiral_dct['track_distance'],
                                                   spiral_dct['start_radius'])   
    # safety margin
    outer_radius += spiral_dct['track_distance']/4
    # https://math.stackexchange.com/questions/134606/distance-between-any-two-points-on-a-unit-circle
    radius_motor = (2*outer_radius)/(2*np.sin(angle_included/2))


    # layer stack for each pole
    stacks = [['F.Cu', 'B.Cu', 'In1.Cu', 'In2.Cu']]
    stacks += [['F.Cu', 'In2.Cu', 'In1.Cu', 'B.Cu']]
    stacks += [['F.Cu', 'In2.Cu', 'B.Cu', 'In1.Cu']]
    stacks += [['F.Cu', 'In1.Cu', 'B.Cu', 'In2.Cu']]
    stacks += [['F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu']]
    stacks += [['F.Cu', 'B.Cu', 'In2.Cu', 'In1.Cu']]
    
    str_data = ""
    for pole in range(poles):
        angle = angle_included*pole +angle_included/2
        coil_center = position + np.array([np.cos(angle), np.sin(angle)])*radius_motor
        # top poles of motor should connect to phases
        if pole >= 3:
            coil_dct['top_angle'] = 0
            coil_dct['rotation'] = 1
            coil_dct['bottom_angle'] = (np.degrees(angle_included)*(2+pole)+360)%360
        else:
            coil_dct['top_angle'] = (np.degrees(-angle_included)*(1-pole)+360)%360
            coil_dct['bottom_angle'] = (np.degrees(-angle_included)*(2+pole)+360)%360
            coil_dct['rotation'] = -1
        coil_dct['center'] = coil_center
        coil_dct['layer_stack'] = stacks[pole]
        coil_dct['connect_angle'] = (45+np.degrees(angle_included)*pole + 360)%360
        str_data += four_layer_coil(**coil_dct, spiral_dct=spiral_dct, track_dct=track_dct)

    # center hole for slide bearing
    str_data += graphic_circle(position, axis_radius, 'Edge.Cuts')

    # connections between poles
    track_dct['width'] = 0.4
    track_dct['layer'] = 'In2.Cu'
    tracks_radius = radius_motor-outer_radius-0.4
    str_data += arc(position, tracks_radius, +np.degrees(angle_included), 
                    180+np.degrees(angle_included), track_dct)
    track_dct['layer'] = 'B.Cu'
    str_data += arc(position, tracks_radius, 0, 180, track_dct)
    track_dct['layer'] = 'In1.Cu'
    str_data += arc(position, tracks_radius, -np.degrees(angle_included), 
                    180-np.degrees(angle_included), track_dct)
    # triple revert connection
    track_dct['layer'] = 'F.Cu'
    str_data += arc(position, tracks_radius, -np.degrees(angle_included), 
                    np.degrees(angle_included), track_dct)

    return str_data


if __name__ == '__main__':

    track_dct = { "layer": "F.Cu",
                  "net": "0",
                  "width": 0.15}

    spiral_dct = {
        "center": np.array([115.0, 105.0]),
        "start_radius": 0.5,     # mm
        "track_distance": 0.15,  # mm
        "start_angle": 0,         # degrees
        "final_angle": 360,       # degrees
        "turns": 11,
        "rotation": -1}
    
    coil_dct = {
        "center": np.array([115.0, 105.0]),
        "top_angle": 0,       # degrees
        "connect_angle": 45,  # degrees
        "bottom_angle": 360,  # degrees
        "rotation": 1,
        "layer_stack": ['F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu']
    }
    position = np.array([152.0, 100.0])  # center of motor


    # open base file
    start = None
    end = None
    with open("base.kicad_pcb", "r") as f:
        lines = f.readlines()
        start = lines[:99]
        end = lines[99:]
   
    
    with open('spiral.kicad_pcb', 'w') as f:
        for line in start:
            f.write(line)
        
        str_data = pcb_motor(position, 1.05, spiral_dct, track_dct, coil_dct)
        f.write(str_data)

        for line in end:
            f.write(line)
