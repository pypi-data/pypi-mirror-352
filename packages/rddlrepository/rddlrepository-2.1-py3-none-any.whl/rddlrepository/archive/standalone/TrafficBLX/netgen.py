"""A tool for generating instances of the Traffic domain"""

import numpy as np
from itertools import product

indent_str = ' ' * 8
newline_indent_str = '\n' + indent_str

def dist(p0, p1):
    return np.linalg.norm(p1-p0)


def generate_simple_4leg_intersection(i, Ein, Nout, Nin, Wout, Win, Sout, Sin, Eout,
                                      min_left, min_through, max, red, right_on_red=True):
    """Generates the non-fluents for a four-phase four-leg intersection,
    with left, through, and right movements"""

    nonfluents_str = newline_indent_str*2 + f'//intersection {i}'
    nonfluents_str += newline_indent_str + '//turns' + newline_indent_str
    nonfluents_str += newline_indent_str.join((
        f'TURN({Ein},{Nout});',
        f'TURN({Ein},{Wout});',
        f'TURN({Ein},{Sout});',
        f'TURN({Nin},{Wout});',
        f'TURN({Nin},{Sout});',
        f'TURN({Nin},{Eout});',
        f'TURN({Win},{Sout});',
        f'TURN({Win},{Eout});',
        f'TURN({Win},{Nout});',
        f'TURN({Sin},{Eout});',
        f'TURN({Sin},{Nout});',
        f'TURN({Sin},{Wout});',
         '',
         '//link-to',
        f'LINK-TO({Ein},{i});',
        f'LINK-TO({Nin},{i});',
        f'LINK-TO({Win},{i});',
        f'LINK-TO({Sin},{i});',
         '',
         '//link-from',
        f'LINK-FROM({i},{Eout});',
        f'LINK-FROM({i},{Nout});',
        f'LINK-FROM({i},{Wout});',
        f'LINK-FROM({i},{Sout});',
         '',
         '//timing constraints',
        f'PHASE-MIN({i},@WEST-EAST-LEFT) = {min_left};',
        f'PHASE-MIN({i},@WEST-EAST-THROUGH) = {min_through};',
        f'PHASE-MIN({i},@NORTH-SOUTH-LEFT) = {min_left};',
        f'PHASE-MIN({i},@NORTH-SOUTH-THROUGH) = {min_through};',
        f'PHASE-MAX({i},@WEST-EAST-LEFT) = {max};',
        f'PHASE-MAX({i},@WEST-EAST-THROUGH) = {max};',
        f'PHASE-MAX({i},@NORTH-SOUTH-LEFT) = {max};',
        f'PHASE-MAX({i},@NORTH-SOUTH-THROUGH) = {max};',
         '',
        f'PHASE-MIN({i},@ALL-RED) = {red};'
        f'PHASE-MIN({i},@ALL-RED2) = {red};'
        f'PHASE-MIN({i},@ALL-RED3) = {red};'
        f'PHASE-MIN({i},@ALL-RED4) = {red};'
        f'PHASE-MAX({i},@ALL-RED) = {red};'
        f'PHASE-MAX({i},@ALL-RED2) = {red};'
        f'PHASE-MAX({i},@ALL-RED3) = {red};'
        f'PHASE-MAX({i},@ALL-RED4) = {red};'
         '//green turns',
        f'GREEN({Ein},{Sout},@WEST-EAST-LEFT);',
        f'GREEN({Win},{Nout},@WEST-EAST-LEFT);',
        f'GREEN({Ein},{Wout},@WEST-EAST-THROUGH);',
        f'GREEN({Win},{Eout},@WEST-EAST-THROUGH);',
        f'GREEN({Nin},{Eout},@NORTH-SOUTH-LEFT);',
        f'GREEN({Sin},{Wout},@NORTH-SOUTH-LEFT);',
        f'GREEN({Nin},{Sout},@NORTH-SOUTH-THROUGH);',
        f'GREEN({Sin},{Nout},@NORTH-SOUTH-THROUGH);'
    ))

    # Add right turns on green
    right_turn_pairs = ((Ein,Nout),
                        (Nin,Wout),
                        (Win,Sout),
                        (Sin,Eout))
    phases = ('@WEST-EAST-LEFT',
              '@WEST-EAST-THROUGH',
              '@NORTH-SOUTH-LEFT',
              '@NORTH-SOUTH-THROUGH')

    nonfluents_str += newline_indent_str
    nonfluents_str += newline_indent_str.join( (f'GREEN({i},{j},{p});'
                                                for (i,j) in right_turn_pairs for p in phases) )

    # Optionally, add right turns on red
    if right_on_red:
        red_phases = ('@ALL-RED',
                      '@ALL-RED2',
                      '@ALL-RED3',
                      '@ALL-RED4')
        nonfluents_str += newline_indent_str
        nonfluents_str += newline_indent_str.join( (f'GREEN({i},{j},{p});'
                                                    for (i,j) in right_turn_pairs for p in red_phases) )
    return nonfluents_str


def generate_nema_4leg_intersection(i, Ein, Nout, Nin, Wout, Win, Sout, Sin, Eout,
                                    min_left, min_through, max, red):
    """Generates the non-fluents for a NEMA four-leg intersection,
    with left, through, and right movements"""

    nonfluents_str = newline_indent_str*2 + f'//intersection {i}'
    nonfluents_str += newline_indent_str + '//turns' + newline_indent_str
    nonfluents_str += newline_indent_str.join((
        f'TURN({Ein},{Nout});',
        f'TURN({Ein},{Wout});',
        f'TURN({Ein},{Sout});',
        f'TURN({Nin},{Wout});',
        f'TURN({Nin},{Sout});',
        f'TURN({Nin},{Eout});',
        f'TURN({Win},{Sout});',
        f'TURN({Win},{Eout});',
        f'TURN({Win},{Nout});',
        f'TURN({Sin},{Eout});',
        f'TURN({Sin},{Nout});',
        f'TURN({Sin},{Wout});',
         '',
         '//link-to',
        f'LINK-TO({Ein},{i});',
        f'LINK-TO({Nin},{i});',
        f'LINK-TO({Win},{i});',
        f'LINK-TO({Sin},{i});',
         '',
         '//link-from',
        f'LINK-FROM({i},{Eout});',
        f'LINK-FROM({i},{Nout});',
        f'LINK-FROM({i},{Wout});',
        f'LINK-FROM({i},{Sout});',
         '',
         '//timing constraints',
        f'PHASE-MIN({i},p0) = {min_left};',
        f'PHASE-MIN({i},p1) = {min_left};',
        f'PHASE-MIN({i},p2) = {min_left};',
        f'PHASE-MIN({i},p3) = {min_through};',
        f'PHASE-MIN({i},p4) = {min_left};',
        f'PHASE-MIN({i},p5) = {min_left};',
        f'PHASE-MIN({i},p6) = {min_left};',
        f'PHASE-MIN({i},p7) = {min_through};',
         '',
        f'PHASE-MAX({i},p0) = {max};',
        f'PHASE-MAX({i},p1) = {max};',
        f'PHASE-MAX({i},p2) = {max};',
        f'PHASE-MAX({i},p3) = {max};',
        f'PHASE-MAX({i},p4) = {max};',
        f'PHASE-MAX({i},p5) = {max};',
        f'PHASE-MAX({i},p6) = {max};',
        f'PHASE-MAX({i},p7) = {max};',
         '',
        f'PHASE-ALL-RED-DUR({i},p0) = {red};',
        f'PHASE-ALL-RED-DUR({i},p1) = {red};',
        f'PHASE-ALL-RED-DUR({i},p2) = {red};',
        f'PHASE-ALL-RED-DUR({i},p3) = {red};',
        f'PHASE-ALL-RED-DUR({i},p4) = {red};',
        f'PHASE-ALL-RED-DUR({i},p5) = {red};',
        f'PHASE-ALL-RED-DUR({i},p6) = {red};',
        f'PHASE-ALL-RED-DUR({i},p7) = {red};',
         '',
         '//green turns',
        f'GREEN({Ein},{Sout},p0); GREEN({Win},{Nout},p0);',
        f'GREEN({Ein},{Sout},p1); GREEN({Ein},{Wout},p1);',
        f'GREEN({Win},{Nout},p2); GREEN({Win},{Eout},p2);',
        f'GREEN({Ein},{Wout},p3); GREEN({Win},{Eout},p3);',
        f'GREEN({Nin},{Eout},p4); GREEN({Sin},{Wout},p4);',
        f'GREEN({Sin},{Wout},p5); GREEN({Sin},{Nout},p5);',
        f'GREEN({Nin},{Eout},p6); GREEN({Nin},{Sout},p6);',
        f'GREEN({Nin},{Sout},p7); GREEN({Sin},{Nout},p7);'
    ))

    # Add right turns on green
    right_turn_pairs = ((Ein,Nout),
                        (Nin,Wout),
                        (Win,Sout),
                        (Sin,Eout))
    phases = ('p0', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7')

    nonfluents_str += newline_indent_str
    nonfluents_str += newline_indent_str.join( (f'GREEN({i},{j},{p});'
                                                for (i,j) in right_turn_pairs for p in phases) )

    return nonfluents_str



def generate_grid(nrows,
                  ncols,
                  phasing_type,
                  ew_link_len=(200,50), #(a,b) parsed as Uniform(a-b,a+b)
                  ns_link_len=(200,50),
                  apply_off_grid_perturbation=False,
                  feeder_link_elongation_factor=1.5,
                  Vl=13.8,
                  inflow_rate_per_lane=(0.08,0.02), # parsed as Uniform(a-b,a+b)
                  satflow_per_lane=0.53,
                  num_lanes=4,
                  high_left_prob=0,
                  min_green_left=3,
                  min_green_through=7,
                  max_green=80,
                  all_red=4,
                  right_on_red=True,
                  instance_name=None,
                  horizon=200,
                  discount=1.0):
    """Generates a grid network.

    The inflow rates are sampled from a uniform random distribution,
    and so are the link lengths. The feeder links can be elongated
    to fit more vehicles and provide more information to the boundary
    lights.

    Typically, through movements are assumed to get (2/4) of the lanes,
    and left and right turns 1/4 each. The saturation flow rate for a
    movement is obtained by multiplying the sat. flow rate per lane by
    the assumed number of lanes.

    There is a fixed probability for a left-turn to have higher demand than the
    through movement (defaults to 0). In this case, the left turns are assumed
    to have (2/4) of the lanes and the through movements (1/4) of the lanes.
    """
    assert phasing_type in {'simple', 'nema'}, \
        '[netgen.generate_grid] Only "simple" and "nema" phasing types currently supported'

    # Sample link lengths uniformly
    # Optionally, make the feeder links longer to fit more vehicles
    feeder_elongation_ew, feeder_elongation_ns = np.ones(ncols+1), np.ones(nrows+1)
    feeder_elongation_ew[0] = feeder_elongation_ew[-1] = \
        feeder_elongation_ns[0] = feeder_elongation_ns[-1] = feeder_link_elongation_factor

    ew_lens = np.random.uniform(ew_link_len[0]-ew_link_len[1], ew_link_len[0]+ew_link_len[1], ncols+1)
    ns_lens = np.random.uniform(ns_link_len[0]-ns_link_len[1], ns_link_len[0]+ns_link_len[1], nrows+1)

    ew_lens *= feeder_elongation_ew
    ns_lens *= feeder_elongation_ns
    max_len = np.max(np.concatenate((ew_lens, ns_lens)))

    # Derive the X and Y coordinates of the intersections, sinks and sources
    Xs, Ys = np.zeros(ncols+2), np.zeros(nrows+2)
    Xs[1:] = np.cumsum(ew_lens)
    Ys[1:] = np.cumsum(ns_lens)
    Ys = np.flip(Ys) # Want Ys to decrease with increasing i to be consistent with
                     # cartesian coords
    Xs = np.tile(Xs, (nrows+2,1))
    Ys = np.tile(Ys[np.newaxis,:].transpose(), (1,ncols+2))
    coords = np.concatenate((Xs[:,:,np.newaxis],
                             Ys[:,:,np.newaxis]),
                             axis=2)
    if apply_off_grid_perturbation:
        coords = coords + np.sqrt(50) * np.random.normal(size=coords.shape)
    coords = np.round(coords)


    num_intersections = nrows*ncols
    num_bdry = 2*(nrows + ncols)
    N = num_intersections + num_bdry
    num_ts = int(np.ceil(max_len/Vl))+2


    intersection_names = tuple(f'i{i}' for i in range(num_intersections))
    t_names = tuple(f't{i}' for i in range(num_ts))


    inames = np.array(['EMPTY' for _ in range(N+4)]).reshape((nrows+2,ncols+2))

    for i in range(nrows+2):
        for j in range(ncols+2):

            if 0 < i < nrows+1 and 0 < j < ncols+1:
                # Traffic light
                inames[i,j] = f'i{(j-1) + (i-1)*ncols}'
            else:
                # Source/sink
                if 0 < j < ncols+1:
                    if i==0:
                        inames[i,j] = f's{j-1}'
                    elif i==(nrows+1):
                        inames[i,j] = f's{2*ncols + nrows - j}'
                if 0 < i < nrows+1:
                    if j==(ncols+1):
                        inames[i,j] = f's{ncols+(i-1)}'
                    elif j==0:
                        inames[i,j] = f's{num_bdry - i}'


    link_names = []
    link_lengths = []
    left_turns, through_turns, right_turns = [], [], []

    for i in range(1,nrows+1):
        for j in range(1,ncols+1):
            link_names.extend([
                f'l-{inames[i,j]}-{inames[i-1,j]}',
                f'l-{inames[i,j]}-{inames[i,j+1]}',
                f'l-{inames[i,j]}-{inames[i+1,j]}',
                f'l-{inames[i,j]}-{inames[i,j-1]}'])
            link_lengths.extend([
                dist(coords[i-1,j], coords[i,j]),
                dist(coords[i,j+1], coords[i,j]),
                dist(coords[i+1,j], coords[i,j]),
                dist(coords[i,j-1], coords[i,j])])

            left_turns.extend([
                f'l-{inames[i,j-1]}-{inames[i,j]},l-{inames[i,j]}-{inames[i-1,j]}',
                f'l-{inames[i-1,j]}-{inames[i,j]},l-{inames[i,j]}-{inames[i,j+1]}',
                f'l-{inames[i,j+1]}-{inames[i,j]},l-{inames[i,j]}-{inames[i+1,j]}',
                f'l-{inames[i+1,j]}-{inames[i,j]},l-{inames[i,j]}-{inames[i,j-1]}'])
            through_turns.extend([
                f'l-{inames[i,j-1]}-{inames[i,j]},l-{inames[i,j]}-{inames[i,j+1]}',
                f'l-{inames[i,j+1]}-{inames[i,j]},l-{inames[i,j]}-{inames[i,j-1]}',
                f'l-{inames[i-1,j]}-{inames[i,j]},l-{inames[i,j]}-{inames[i+1,j]}',
                f'l-{inames[i+1,j]}-{inames[i,j]},l-{inames[i,j]}-{inames[i-1,j]}'])
            right_turns.extend([
                f'l-{inames[i,j-1]}-{inames[i,j]},l-{inames[i,j]}-{inames[i+1,j]}',
                f'l-{inames[i+1,j]}-{inames[i,j]},l-{inames[i,j]}-{inames[i,j+1]}',
                f'l-{inames[i,j+1]}-{inames[i,j]},l-{inames[i,j]}-{inames[i-1,j]}',
                f'l-{inames[i-1,j]}-{inames[i,j]},l-{inames[i,j]}-{inames[i,j-1]}'])

    # Add missing source links
    source_link_names = []
    for j in range(1,ncols+1):
        new_links = [
            f'l-{inames[0,j]}-{inames[1,j]}',
            f'l-{inames[nrows+1,j]}-{inames[nrows,j]}']
        link_names.extend(new_links)
        source_link_names.extend(new_links)
        link_lengths.extend([
            dist(coords[1,j], coords[0,j]),
            dist(coords[nrows,j], coords[nrows+1,j]) ])

    for i in range(1,nrows+1):
        new_links = [
            f'l-{inames[i,0]}-{inames[i,1]}',
            f'l-{inames[i,ncols+1]}-{inames[i,ncols]}']
        link_names.extend(new_links)
        source_link_names.extend(new_links)
        link_lengths.extend([
            dist(coords[i,1], coords[i,0]),
            dist(coords[i,ncols], coords[i,ncols+1]) ])

    # Optionally, make some left turns have heavier demand than the
    # through movements
    high_left_turn = np.random.binomial(1, high_left_prob, size=len(left_turns))
    deltas = np.random.uniform(-0.1, 0.1, size=len(left_turns))

    satflow_rates, turn_probs = {}, {}
    for L, T, R, dp, high_left in zip(left_turns, through_turns, right_turns, deltas, high_left_turn):
        if high_left:
            high_turn, low_turn = L, T
        else:
            high_turn, low_turn = T, L

        turn_probs[high_turn] = 0.7 - dp
        turn_probs[low_turn] = 0.2 + dp
        turn_probs[R] = 1-turn_probs[high_turn]-turn_probs[low_turn]
        total_satflow = satflow_per_lane * num_lanes
        satflow_rates[high_turn] = 0.5 * total_satflow
        satflow_rates[low_turn] = 0.3 * total_satflow
        satflow_rates[R] = 0.2 * total_satflow

    inflow_lb = (inflow_rate_per_lane[0]-inflow_rate_per_lane[1]) * num_lanes
    inflow_ub = (inflow_rate_per_lane[0]+inflow_rate_per_lane[1]) * num_lanes
    arrival_rates = np.round( np.random.uniform(inflow_lb, inflow_ub, num_bdry),
                              2)

    if instance_name is None:
        instance_name = f'grid_{nrows}x{ncols}'


    instance_str = '\n'.join((
        f'non-fluents {instance_name} {{',
        f'    domain = BLX_model;',
        f'',
        f'    objects {{',
        f'        intersection : {{{", ".join(intersection_names)}}};',
        f'        link         : {{{", ".join(link_names)}}};'))

    if phasing_type == 'nema':
        instance_str += '\n'.join((
            '',
            f'        signal-phase : {{p0, p1, p2, p3, p4, p5, p6, p7}};',
            f'        action-token : {{a0, a1, a2, a3, a4}};'))

    instance_str += '\n'.join((
        '',
        f'        time         : {{{", ".join(t_names)}}};',
        f'    }};',
        f'',
        f'    non-fluents {{'))

    if phasing_type == 'nema':
        instance_str += newline_indent_str.join(('',) + tuple(
            f'INTERSECTION-INDEX({i}) = {ni};' for ni, i in enumerate(intersection_names)))
        instance_str += newline_indent_str.join((
            '',
            '',
            'ACTION-TOKEN-INDEX(a0) = 0;',
            'ACTION-TOKEN-INDEX(a1) = 1;',
            'ACTION-TOKEN-INDEX(a2) = 2;',
            'ACTION-TOKEN-INDEX(a3) = 3;',
            'ACTION-TOKEN-INDEX(a4) = 4;',
            ''
            'PHASE-INDEX(p0) = 0;',
            'PHASE-INDEX(p1) = 1;',
            'PHASE-INDEX(p2) = 2;',
            'PHASE-INDEX(p3) = 3;',
            'PHASE-INDEX(p4) = 4;',
            'PHASE-INDEX(p5) = 5;',
            'PHASE-INDEX(p6) = 6;',
            'PHASE-INDEX(p7) = 7;',
            ''))

    instance_str += newline_indent_str + '//sources'
    instance_str += newline_indent_str.join(('',)
        + tuple(f'SOURCE(l-{inames[i,0]}-{inames[i,1]});'
                + newline_indent_str
                + f'SOURCE(l-{inames[i,ncols+1]}-{inames[i,ncols]});'
                for i in range(1, nrows+1))
        + tuple(f'SOURCE(l-{inames[0,j]}-{inames[1,j]});'
                + newline_indent_str
                + f'SOURCE(l-{inames[nrows+1,j]}-{inames[nrows,j]});'
                for j in range(1, ncols+1)))

    instance_str += newline_indent_str + '//sinks'
    instance_str += newline_indent_str.join(('',)
        + tuple(f'SINK(l-{inames[i,1]}-{inames[i,0]});'
                + newline_indent_str
                + f'SINK(l-{inames[i,ncols]}-{inames[i,ncols+1]});'
                for i in range(1, nrows+1))
        + tuple(f'SINK(l-{inames[1,j]}-{inames[0,j]});'
                + newline_indent_str
                + f'SINK(l-{inames[nrows,j]}-{inames[nrows+1,j]});'
                for j in range(1, ncols+1)))


    if Vl != 13.8:
        instance_str += newline_indent_str + '//speeds'
        instance_str += newline_indent_str.join(('',) + tuple(f'SPEED({link}) = {Vl};' for link in link_names))

    if num_lanes != 4:
        instance_str += newline_indent_str + '//number of lanes'
        instance_str += newline_indent_str.join(('',) + tuple(f'Nl({link}) = {num_lanes};' for link in link_names))

    instance_str += newline_indent_str + '//satflow rates'
    instance_str += newline_indent_str.join(('',) + tuple(f'MU({k}) = {v};' for k,v in satflow_rates.items()))

    instance_str += newline_indent_str + '//turn probabilities'
    instance_str += newline_indent_str.join(('',) + tuple(f'BETA({k}) = {v};' for k,v in turn_probs.items()))

    instance_str += newline_indent_str + '//link lengths'
    instance_str += newline_indent_str.join(('',) + tuple(f'Dl({k}) = {v};' for k,v in zip(link_names, link_lengths)))

    instance_str += newline_indent_str + '//source arrival rates'
    instance_str += newline_indent_str.join(('',) + tuple(f'SOURCE-ARRIVAL-RATE({k}) = {v};' for k,v in zip(source_link_names, arrival_rates)))

    for i in range(1, nrows+1):
        for j in range(1, ncols+1):
            if phasing_type == 'simple':
                instance_str += generate_simple_4leg_intersection(
                                    inames[i,j],
                                    f'l-{inames[i,j+1]}-{inames[i,j]}', #Ein
                                    f'l-{inames[i,j]}-{inames[i-1,j]}', #Nout
                                    f'l-{inames[i-1,j]}-{inames[i,j]}', #Nin
                                    f'l-{inames[i,j]}-{inames[i,j-1]}', #Wout
                                    f'l-{inames[i,j-1]}-{inames[i,j]}', #Win
                                    f'l-{inames[i,j]}-{inames[i+1,j]}', #Sout
                                    f'l-{inames[i+1,j]}-{inames[i,j]}', #Sin
                                    f'l-{inames[i,j]}-{inames[i,j+1]}', #Eout
                                    min_left=min_green_left,
                                    min_through=min_green_through,
                                    max=max_green,
                                    red=all_red,
                                    right_on_red=right_on_red)
            elif phasing_type == 'nema':
                instance_str += generate_nema_4leg_intersection(
                                    inames[i,j],
                                    f'l-{inames[i,j+1]}-{inames[i,j]}', #Ein
                                    f'l-{inames[i,j]}-{inames[i-1,j]}', #Nout
                                    f'l-{inames[i-1,j]}-{inames[i,j]}', #Nin
                                    f'l-{inames[i,j]}-{inames[i,j-1]}', #Wout
                                    f'l-{inames[i,j-1]}-{inames[i,j]}', #Win
                                    f'l-{inames[i,j]}-{inames[i+1,j]}', #Sout
                                    f'l-{inames[i+1,j]}-{inames[i,j]}', #Sin
                                    f'l-{inames[i,j]}-{inames[i,j+1]}', #Eout
                                    min_left=min_green_left,
                                    min_through=min_green_through,
                                    max=max_green,
                                    red=all_red)

    if phasing_type == 'nema':
        instance_str += '\n        '.join(('', '//phase transitions',
            'TRANSITION(p0, a0) = 0;',
            'TRANSITION(p0, a1) = 1;',
            'TRANSITION(p0, a2) = 2;',
            'TRANSITION(p0, a3) = 3;',
            '',
            'TRANSITION(p1, a0) = 1;',
            'TRANSITION(p1, a1) = 3;',
            '',
            'TRANSITION(p2, a0) = 2;',
            'TRANSITION(p2, a1) = 3;',
            '',
            'TRANSITION(p3, a0) = 3;',
            'TRANSITION(p3, a1) = 4;',
            'TRANSITION(p3, a2) = 5;',
            'TRANSITION(p3, a3) = 6;',
            'TRANSITION(p3, a4) = 7;',
            '',
            'TRANSITION(p4, a0) = 4;',
            'TRANSITION(p4, a1) = 5;',
            'TRANSITION(p4, a2) = 6;',
            'TRANSITION(p4, a3) = 7;',
            '',
            'TRANSITION(p5, a0) = 5;',
            'TRANSITION(p5, a1) = 7;',
            '',
            'TRANSITION(p6, a0) = 6;',
            'TRANSITION(p6, a1) = 7;',
            '',
            'TRANSITION(p7, a0) = 7;',
            'TRANSITION(p7, a1) = 0;',
            'TRANSITION(p7, a2) = 1;',
            'TRANSITION(p7, a3) = 2;',
            'TRANSITION(p7, a4) = 3;'))

    instance_str += '\n        '.join(('', '// time-delay properties',
       f'TIME-HEAD(t0);',
       f'TIME-TAIL(t{num_ts-1});') +
        tuple(f'TIME-VAL(t{i}) = {i};' for i in range(num_ts)) +
        tuple(f'NEXT(t{i},t{i+1});' for i in range(num_ts-1)))


    instance_str += newline_indent_str + '//cartesian coordinates (for visualization)'
    instance_str += newline_indent_str.join(('',) + tuple(
        f'X({inames[i,j]}) = {coords[i,j,0]}; Y({inames[i,j]}) = {coords[i,j,1]};'
        for i in range(1,nrows+1) for j in range(1,ncols+1) ))

    instance_str += newline_indent_str + newline_indent_str.join((
        f'SOURCE-X(l-{inames[i,0]}-{inames[i,1]}) = {coords[i,0,0]}; SOURCE-Y(l-{inames[i,0]}-{inames[i,1]}) = {coords[i,0,1]};'
        + newline_indent_str
        + f'SOURCE-X(l-{inames[i,ncols+1]}-{inames[i,ncols]}) = {coords[i,ncols+1,0]}; SOURCE-Y(l-{inames[i,ncols+1]}-{inames[i,ncols]}) = {coords[i,ncols+1,1]};'
        + newline_indent_str
        + f'SINK-X(l-{inames[i,1]}-{inames[i,0]}) = {coords[i,0,0]}; SINK-Y(l-{inames[i,1]}-{inames[i,0]}) = {coords[i,0,1]};'
        + newline_indent_str
        + f'SINK-X(l-{inames[i,ncols]}-{inames[i,ncols+1]}) = {coords[i,ncols+1,0]}; SINK-Y(l-{inames[i,ncols]}-{inames[i,ncols+1]}) = {coords[i,ncols+1,1]};'
        for i in range(1,nrows+1) ))

    instance_str += newline_indent_str + newline_indent_str.join((
        f'SOURCE-X(l-{inames[0,j]}-{inames[1,j]}) = {coords[0,j,0]}; SOURCE-Y(l-{inames[0,j]}-{inames[1,j]}) = {coords[0,j,1]};'
        + newline_indent_str
        + f'SOURCE-X(l-{inames[nrows+1,j]}-{inames[nrows,j]}) = {coords[nrows+1,j,0]}; SOURCE-Y(l-{inames[nrows+1,j]}-{inames[nrows,j]}) = {coords[nrows+1,j,1]};'
        + newline_indent_str
        + f'SINK-X(l-{inames[1,j]}-{inames[0,j]}) = {coords[0,j,0]}; SINK-Y(l-{inames[1,j]}-{inames[0,j]}) = {coords[0,j,1]};'
        + newline_indent_str
        + f'SINK-X(l-{inames[nrows,j]}-{inames[nrows+1,j]}) = {coords[nrows+1,j,0]}; SINK-Y(l-{inames[nrows,j]}-{inames[nrows+1,j]}) = {coords[nrows+1,j,1]};'
        for j in range(1,ncols+1) ))


    instance_str += '\n'
    instance_str += '\n'.join((
        f'    }};',
        f'}}',
        f'',
        f'instance {instance_name} {{',
        f'    domain = BLX_model;',
        f'    non-fluents = {instance_name};',
        f'    max-nondef-actions = {num_intersections};',
        f'    horizon = {horizon};',
        f'    discount = {discount};',
        f'}}' ))

    instance_str += '\n'
    instance_str += '// Source link ids\n//'
    source_link_indices = [f'{id}={link_names.index(id)}' for id in source_link_names]
    instance_str += '\n//'.join(source_link_indices)

    return instance_str





if __name__ == '__main__':
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Tool for automatically generating grid instances for the RDDL traffic domain')
    parser.add_argument('target_path', type=str, help='Path the generated rddl code will be saved to')
    parser.add_argument('-r', '--rows', type=int, help='Number of rows in the network', required=True)
    parser.add_argument('-c', '--cols', type=int, help='Number of columns in the network', required=True)
    parser.add_argument('-p', '--phasing', type=str, help='The phasing type. Either "simple" or "nema"', required=True)
    parser.add_argument('-f', '--force-overwrite', action='store_true', help='By default the generator will not overwrite existing files. With this argument, it will')
    parser.add_argument('-L', '--high-left-prob', default=0, help='Probability of having heavier demand on through than left from an approach')
    parser.add_argument('-T', '--horizon', type=int, default=200)
    parser.add_argument('--off-grid', action='store_true', help='Apply small perturbations to move the intersections off a perfect grid, making the network less symmetric')
    parser.add_argument('-n', '--instance-name', help='Name of instance')
    args = parser.parse_args()


    args.high_left_prob = float(args.high_left_prob)
    assert(0 <= args.high_left_prob <= 1)

    if os.path.isfile(args.target_path) and not args.force_overwrite:
        raise RuntimeError('[netgen.py] File with the requested path already exists. Pass a diffent path or add the -f argument to force overwrite')

    with open(args.target_path, 'w') as file:
        network = generate_grid(
            args.rows, args.cols,
            phasing_type=args.phasing,
            apply_off_grid_perturbation=args.off_grid,
            high_left_prob=args.high_left_prob,
            horizon=args.horizon,
            instance_name=args.instance_name)

        file.write(network)
    print(f'[netgen.py] Successfully generated the network instance RDDL file to {args.target_path}')
