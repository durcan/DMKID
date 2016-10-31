#!/usr/bin/env python

import numpy as np
from gdsCAD import * #this may require my patched version of gdsCAD
from KID_1st_fab_ver import KID
import matplotlib.pyplot as plt


# const globals
GW = 100 # ground width
GAP = 11 # gap width
SW = 20 # signal width
FW = 2*GW + 2*GAP + SW # total feedline width
KKS = 5000. # KID KID seperation
KW = 775 # Kid width
FKG = 0 # Feedline to KID gap
BOND_X = 9000 # bonding pad x location
PAD_H = 800 # bonding pad hight
R = 76200/2. # nominal radius
TOP_CUT = 72212.2/2.
SIDE_CUT = 75514.2/2.


# globals (mut)
NUM_KID = 0 # EVIL MUTABLE GLOBAL. tracks the number of kids. I am lazy


def main(n=2, flip=False, KKS=KKS, geom=None):
    global NUM_KID
    n += 1
    #plt.ion()
    # get main verticies

    if geom=="simple":
        x_pts, y_pts_up, y_pts_dn = points_of_interest(3)
        x_pts = [-BOND_X,BOND_X]
    elif geom=="shunt":
        x_pts, y_pts_up, y_pts_dn = points_of_interest(3)
        x_pts = [-BOND_X,BOND_X]
        y_pts_up[0] = y_pts_dn[0] + 800
        y_pts_up[-1] = y_pts_dn[-1] + 800
    else:
        x_pts, y_pts_up, y_pts_dn = points_of_interest(n)

    full_cell = core.Cell('FULL_MASK')
    full_cell.add(outlines())                                           # add waifer outline (for alignment)
    full_cell.add(vertical_feeds(x_pts, y_pts_up, y_pts_dn))            # vert feedlines
    full_cell.add(horizontal_feeds(x_pts, y_pts_up, y_pts_dn))          # horizontal feedlines
    full_cell.add(corners(x_pts, y_pts_up, y_pts_dn))                   # corners
    full_cell.add(kids_and_grounds(x_pts, y_pts_up, y_pts_dn, KKS=KKS)) # kids and grounds
    full_cell.add(allign(x_pts))                                       # add alignment marks
    full_cell.add(lower_feedline(x_pts, y_pts_up, y_pts_dn, geom=geom))            # add lower feedlines and bonding pads)
    full_cell.flatten()

    full_layout = core.Layout('FULL_LAYOUT')
    full_layout.add(full_cell)

    if flip:                                                   # optionally also add flipped kids
        full_layout.add(kids_and_grounds_r(x_pts, y_pts_up, y_pts_dn, KKS=KKS))

    nums = NUM_KID
    print nums," KIDs"
    #return full_cell
    plt.ion()
    full_layout.show()
    plt.savefig("fig.png", dpi=1200)
    full_layout.save("mask_{}.gds".format(n-1))
    NUM_KID = 0
    return nums

def points_of_interest(n):
    x_pts = np.linspace(-R, R, n, False)[1:]
    y_pts_up = np.array(map(subx2y, x_pts))
    y_pts_dn = -0.9*y_pts_up

    # deal with staggered lengths
    for i in range(len(x_pts)-1):
        if i%2 == 0: # evens
            v = min(y_pts_up[i], y_pts_up[i+1])
            y_pts_up[i], y_pts_up[i+1] = v, v
        else: # odds
            v = max(y_pts_dn[i], y_pts_dn[i+1])
            y_pts_dn[i], y_pts_dn[i+1] = v, v

    y_pts_dn[0], y_pts_dn[-1] = -y_pts_up[0], -y_pts_up[-1]

    return x_pts, y_pts_up, y_pts_dn

# vertical feedlines
def vertical_feeds(x_pts, y_pts, y_pts_dn):
    lengths = y_pts - y_pts_dn
    vf = core.Cell("VERT_FEED")
    for x,y,l in zip(x_pts, y_pts, lengths):
        vf.add(feedline(l, (x,y), 270))
    return vf

# horizontal feedlines
def horizontal_feeds(x_pts, y_pts_up, y_pts_dn):
    hf = core.Cell("HORIZ_FEED")
    lengths = np.diff(x_pts) - FW
    for i, v in enumerate(lengths):
        if i%2==0:
            y = y_pts_up[i] + FW/2
        else:
            y = y_pts_dn[i] - FW/2
        hf.add(feedline(v, (x_pts[i] + FW/2, y), 0))
    return hf

# corners (for main meander)
def corners(x_pts, y_pts_up, y_pts_dn):
    cor = core.Cell("CORNERS")
    for i, v in enumerate(x_pts):
        if i%2:
            reflect = True
        else:
            reflect = False
        if v not in [x_pts[0], x_pts[-1]]:
            cor.add((corner((v,y_pts_up[i]), 270, reflect),
                     corner((v,y_pts_dn[i]), 90, reflect)))
        else:
            cor.add(corner((v,y_pts_up[i]), 270, reflect))
    return cor

# kids and grounds
def kids_and_grounds(x_pts, y_pts_up, y_pts_dn,KKS):
    kag = core.Cell("KIDS_AND_GROUNDS")
    lengths = y_pts_up - y_pts_dn
    for i,x in enumerate(x_pts):
        l, yup, ydn = lengths[i], y_pts_up[i], y_pts_dn[i]
        nkids = int(round(l/KKS)) # number of kids for this vertical section
        ys = np.linspace(ydn, yup, nkids, endpoint=False)[1:]
        for y in ys:
            global NUM_KID
            NUM_KID = NUM_KID + 1

    L_list = map(f2l, np.linspace(3.0, 3.5, NUM_KID)) # list of inductor lengths
    print "L list: {}".format(L_list)
    Li = 0

    for i,x in enumerate(x_pts):
        l, yup, ydn = lengths[i], y_pts_up[i], y_pts_dn[i]
        nkids = int(round(l/KKS)) # number of kids for this vertical section
        ys = np.linspace(ydn, yup, nkids, endpoint=False)[1:]
        for y in ys:
            MIL  = L_list[Li]
            kid = KID(MIL)
            delta_y =  kid.w/2.0
            kag.add(kid.KID_shielded, rotation=90, origin=(x-FW/2 - FKG, y + delta_y))
            Li += 1


    return kag

# kids and grounds reflected
def kids_and_grounds_r(x_pts, y_pts_up, y_pts_dn,KKS):
    kag = core.Cell("KIDS_AND_GROUNDS_R")
    lengths = y_pts_up - y_pts_dn
    for i,x in enumerate(x_pts):
        l, yup, ydn = lengths[i], y_pts_up[i], y_pts_dn[i]
        nkids = int(round(l/KKS)) # number of kids for this vertical section
        ys = np.linspace(ydn, yup, nkids, endpoint=False)[1:]
        yf = ys[:-1] + np.diff(ys)/2
        yf = np.concatenate(([yf[0] - np.diff(ys)[0]], yf, [yf[-1] + np.diff(ys)[-1]]))
        for y in yf:
            kid = KID(ICL)
            delta_y =  (kid.KID_length - MIL) - kid.KID_length/2.0
            kag.add(core.CellReference(
                ground_shield((0,0), kid.KID_length), rotation=180, origin=(x+FW/2, y)))
            kag.add(utils.relayer(
                core.CellReference(
                    kid.KID,
                    rotation=90,
                    origin=(x+FW/2 + FKG + KW, y + delta_y)),
                [1],
                2))
            global NUM_KID
            NUM_KID = NUM_KID + 1

    return kag

# lower feedline (the part that goes from the last vertical to the edge) and bonding pad
def lower_feedline(x_pts, y_pts_up, y_pts_dn, geom=None):
    lf = core.Cell("LOWER_FEED")

    if (geom == "simple") or (geom=="shunt"):
        center_x, bond_y = subfun(3*np.pi/2, R)
        # bonding pads
        lf.add(pad((-BOND_X, bond_y)))
        lf.add(pad((BOND_X, bond_y)))

        # vert
        lf.add(feedline((y_pts_dn[0] - bond_y - PAD_H) , (-BOND_X,y_pts_dn[0] ), 270.0))
        lf.add(feedline((y_pts_dn[-1] - bond_y - PAD_H) , (BOND_X,y_pts_dn[-1]), 270.0))
        return lf


    t1 = np.arccos(2.842/3.)
    t_lr, t_ll = 3*np.pi/2. + t1, 3*np.pi/2. - t1 # theta lower left and lower right
    rho_r, t_ur = cart2pol(x_pts[-1]- FW/2, y_pts_dn[-1]- FW/2)
    rho_l, t_ul = cart2pol(x_pts[0]+ FW/2, y_pts_dn[0]- FW/2)

    # large curves
    lf.add(cpw_arc((0,0), t_ul, t_ll, rho_l))
    lf.add(cpw_arc((0,0), t_lr, t_ur, rho_r))

    # corners
    x_ul, y_ul = pol2cart(rho_l, t_ul)
    lf.add(cpw_arc((x_ul, y_ul), np.pi, t_ul, 0.0))

    x_ll, y_ll = pol2cart(rho_l, t_ll)
    lf.add(cpw_arc((x_ll, y_ll), t_ll, np.deg2rad(270),  0.0))

    x_lr, y_lr = pol2cart(rho_r, t_lr)
    lf.add(cpw_arc((x_lr, y_lr), np.deg2rad(270), t_lr,  0.0))

    x_ur, y_ur = pol2cart(rho_r, t_ur)
    lf.add(cpw_arc((x_ur, y_ur), t_ur, 2*np.pi,  0.0))

    # horizontal
    bond_l, bond_r = -BOND_X-x_ll, x_lr-BOND_X
    lf.add(feedline(bond_l - FW/2, (x_ll,y_ll), 0.0))
    lf.add(feedline(bond_r - FW/2, (x_lr,y_lr), 180.0))

    # vertical
    center_x, bond_y = subfun(3*np.pi/2, R)
    lf.add(feedline(y_ll-bond_y - PAD_H -FW/2, (-BOND_X,y_ll-FW/2), 270.0))
    lf.add(feedline(y_lr-bond_y - PAD_H -FW/2, (BOND_X,y_lr-FW/2), 270.0))

    # final corners
    lf.add(corner((-BOND_X,y_ll-FW/2), 270, True))
    lf.add(corner((BOND_X,y_lr-FW/2), 270, False))

    # bonding pads
    lf.add(pad((-BOND_X, bond_y)))
    lf.add(pad((BOND_X, bond_y)))

    return lf

# allignment marks
def allign(x_pts):
    al = core.Cell("ALLIGNMENT")
    x_pts = x_pts[:-1] + np.diff(x_pts)/2
    xs = np.concatenate(([x_pts[0] - np.diff(x_pts)[0]], x_pts, [x_pts[-1] + np.diff(x_pts)[-1]]))
    m = templates.AlignmentMarks(('A', 'C'), (1,2))
    for x in xs:
        al.add(m, origin=(x, 0.0))

    return al


# substrate outline.
def subfun(theta, rad = R+90):
    t1 = np.arccos(2.842/3.)
    t2 = np.arccos(2.972/3.)
    if theta < np.pi/2. + t1 and theta > np.pi/2. - t1:
        return ((TOP_CUT*rad/R)/np.tan(theta),TOP_CUT*rad/R)
    elif theta < 3*np.pi/2. + t1 and theta > 3*np.pi/2. - t1:
        return (-(TOP_CUT*rad/R)/np.tan(theta),-(TOP_CUT*rad/R))
    elif theta < t2 or theta > 2*np.pi-t2:
        return ((SIDE_CUT*rad/R), np.tan(theta)*(SIDE_CUT*rad/R))
    elif theta < np.pi + t2 and theta > np.pi - t2:
        return (-(SIDE_CUT*rad/R), np.tan(theta)*(-(SIDE_CUT*rad/R)))
    else:
        return (rad*np.cos(theta),rad*(np.sin(theta)))

# give edge y (positive), for input x
def subx2y(x, rad = R-3000):
    for theta in np.arange(0,np.pi,0.0001):
        ex, ey = subfun(theta, rad)
        if ex < x:
            return ey


# feedline
def feedline(l, orig, rot):

    w_sig = SW
    w_gnd = GW
    gap = GAP

    feedline = core.Cell('FEEDLINE')

    ground = shapes.Rectangle((0,0),(l,w_gnd))
    ground2 = ground.copy()
    signal = shapes.Rectangle((0,0),(l,w_sig))

    ground2.translate((0,w_gnd+w_sig+2*gap))
    signal.translate((0,w_gnd+gap))

    ground.layer=1
    ground2.layer=1
    signal.layer=1

    for i in [ground, ground2, signal]:
        feedline.add(i
            .translate((0.,-w_gnd-w_sig/2.-gap))
            .rotate(rot)
            .translate(orig))


    return feedline

# corner
def corner(orig, rotation=0, reflection=False):
    return cpw_arc(orig, np.pi, 3*np.pi/2, 0.0, rotation=rotation, reflection=reflection)

# general cpw arc (angles in radians)
def cpw_arc(orig, theta1, theta2, radius, rotation=0, reflection=False):
    theta1, theta2 = np.rad2deg(theta1), np.rad2deg(theta2)
    cor = core.Cell("CPW_ARC")
    pr = lambda x: x + radius
    for outer,inner in zip(map(pr, [GW, GW+GAP+SW, 2*GW+2*GAP+SW]), map(pr, [0.0001, GW+GAP, GW+2*GAP+SW])):
        c = (shapes
            .Disk((0,0),
                outer,
                inner_radius=inner,
                initial_angle=theta1,
                final_angle=theta2)
            .translate((0, FW/2))
            .rotate(rotation)
            .translate(orig))
        if reflection:
            c.reflect('y', orig)
        cor.add(c)

    return cor


def ground_shield(orig, KID_length, rot=90):
    shield_width = 100
    KID_width = KW
    gap = FKG
    cell = core.Cell('SHIELD')
    shield = core.Boundary( [(-KID_length/2.-gap-shield_width,0),\
            (-KID_length/2.-gap-shield_width,KID_width+2.*gap+shield_width),\
            (KID_length/2.+gap+shield_width,KID_width+2.*gap+shield_width),\
            (KID_length/2.+gap+shield_width,0),\
            (KID_length/2.+gap,0),\
            (KID_length/2.+gap,KID_width+2.*gap),\
            (-KID_length/2.-gap,KID_width+2.*gap),\
            (-KID_length/2.-gap,0)], layer=1).rotate(rot).translate(orig)
    cell.add(shield)

    return cell

# bonding pads
def pad(orig = (0,0)):
    pd = core.Cell("PAD")
    gw = GW #Ground width
    sw = SW #signal width
    gap = GAP #GAP
    l = PAD_H
    x, y = orig
    sx = sw/2.0
    gix = sx + gap
    gox = gix + gw

    s = 15 # scaling factor

    pd.add(core.Boundary(
        [(s*gox, 0),
        (s*gix, 0),
        (gix,  l),
        (gox,  l)]).translate(orig))

    pd.add(core.Boundary(
        [(-s*gox, 0),
        (-s*gix, 0),
        (-gix,  l),
        (-gox, l)]).translate(orig))

    pd.add(core.Boundary(
        [(-s*sx, 0),
        (s*sx, 0),
        (sx,  l),
        (-sx, l)]).translate(orig))


    return pd

def outlines():
    outline = core.Cell("OUTLINE")
    for i in [1]:#, 2]:
        outline.add(core.Path(
            map(subfun, np.linspace(0.,2*np.pi,num=180,endpoint=False)),
            width=20,
            layer=i))

    return outline

# utility functions

def f2l(f):
    return ((2.507**2) * 1043.0)/(f**2)

def pol2cart(rho, phi):
    x = rho * np.cos(phi)
    y = rho * np.sin(phi)
    return(x, y)

def cart2pol(x, y):
    rho = np.sqrt(x**2 + y**2)
    phi = np.arctan2(y, x) + np.pi*2
    return(rho, phi)

class chain:
    def __init__(self, obj):
        self.obj = obj
    def __repr__(self):
        return repr(self.obj)
    def __getattr__(self, name):
        attr = getattr(self.obj, name)
        if callable(attr):
            def selfie(*args, **kw):
                _ = attr(*args, **kw)
                return self
            return selfie
        else:
            return attr

if __name__ == "__main__":
    main(n = 4)
