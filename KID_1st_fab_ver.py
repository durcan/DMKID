#<development log>
#   16.10.23
#       First version's completed.
#       The only input needed is the "height (L)" of the KID.
#       Geometry is set to which presented in 160715 160805 and 160812's DMKID meeting slides.
#       According to SONNET simulation, this design behaves nicely as the resonant frequency f \prop \frac{1}{\sqrt{L}}, where L being the LENGTH, not inductance.



from gdsCAD import *



class KID:
    def __init__(self, L, W=80., w=20., G=20., g=10., g_LC=80., w_Cs=20., g_Cs=20., N_Cs=9., g_s=30., w_s=80.):
        #L:     side length of meander
        #W:     width of meander
        #w:     width of capacitor
        #G:     wide (innder) gap of meander
        #g:     narrow (outer) gap of meander
        #g_LC:  LC gap
        #w_Cs:  width of capacitor interdigitate strips
        #g_Cs:  gap between capacitor interdigitate strips
        #N_Cs:  number of capacitor interdigitate strips
        #g_s:   gap between feedline or ground shield and KID
        #w_s:   width of ground shield


        cell_KID_shielded = core.Cell('KID_SHIELDED')

        cell_KID = core.Cell('KID')

        cell_meander = core.Cell('MEANDER')
        cell_meander_left = core.Cell('MEANDER_LEFT')
        cell_meander_right = core.Cell('MEANDER_RIGHT')

        cell_capacitor = core.Cell('CAPACITOR')
        cell_neck_border = core.Cell('NECK_BORDER')
        cell_fingers = core.Cell('FINGERS')

        cell_gShield = core.Cell('GROUND_SHIELD')


    #meander:
        KID_full_w = G*6+g*5+W*12

        meander_points_right = [\
                (g/2,0.),\
                (g/2+g+2*G+4*W,0.),\
                (g/2+g+2*G+4*W,L-W*2-G),\
                (g/2+g*2+2*G+4*W,L-W*2-G),\
                (g/2+g*2+2*G+4*W,0.),\
                (g/2+g*2+3*G+6*W,0.),\
                (g/2+g*2+3*G+6*W,L),\
                (g/2+g+G+2*W,L),\
                (g/2+g+G+2*W,W*2+G),\
                (g/2+G+2*W,W*2+G),\
                (g/2+G+2*W,L),\
                (g/2,L),\
                (g/2,L-W),\
                (g/2+W+G,L-W),\
                (g/2+W+G,W+G),\
                (g/2+W*3+G+g,W+G),\
                (g/2+W*3+G+g,L-W),\
                (g/2+W*5+G*3+g*2,L-W),\
                (g/2+W*5+G*3+g*2,W),\
                (g/2+W*5+G*2+g*2,W),\
                (g/2+W*5+G*2+g*2,L-W-G),\
                (g/2+W*3+G*2+g,L-W-G),\
                (g/2+W*3+G*2+g,W),\
                (g/2+W,W),\
                (g/2+W,L-W-G),\
                (0.,L-W-G),\
                (0.,L-W*2-G),\
                (g/2,L-W*2-G)]

        meander_polygon_right = core.Boundary(meander_points_right,layer=2)
        cell_meander_right.add(meander_polygon_right)

        meander_points_left = []
        for (a,b) in meander_points_right:
            meander_points_left.append((-a,b))

        meander_polygon_left = core.Boundary(meander_points_left,layer=2)
        cell_meander_left.add(meander_polygon_left)

        cell_meander.add(cell_meander_right)
        cell_meander.add(cell_meander_left)




    #neck + capacitor border strip
        C_border_points_right = [\
                (g/2,L),\
                (g/2+W,L),\
                (g/2+W,L+g_LC),\
                (g/2+g*2+3*G+6*W,L+g_LC),\
                (g/2+g*2+3*G+6*W,L+g_LC+W+N_Cs*w+N_Cs*g_Cs),\
                (g/2+g*2+3*G+5*W,L+g_LC+W+N_Cs*w+N_Cs*g_Cs),\
                (g/2+g*2+3*G+5*W,L+g_LC+W),\
                (g/2,L+g_LC+W)]
        C_border_right = core.Boundary(C_border_points_right,layer=2)


        C_border_points_left = []
        for (a,b) in C_border_points_right:
            C_border_points_left.append((-a,b))
        C_border_left = core.Boundary(C_border_points_left,layer=2)

        cell_neck_border.add(C_border_right)
        cell_neck_border.add(C_border_left)

        cell_capacitor.add(cell_neck_border)




    #capacitor
        l_Cs = KID_full_w-2*W-g_Cs
        strip_box = [\
                (0.,0.),\
                (l_Cs,0.),\
                (l_Cs,w_Cs),\
                (0.,w_Cs)]

        capacitor_strips = []
        for i in range(int(N_Cs)):
            if i%2 == 1:
                capacitor_strips.append(core.Boundary(strip_box,layer=2))
                capacitor_strips[i].translate((KID_full_w/2.-W-l_Cs,L+g_LC+W+g_Cs*(i*2+1)))
                cell_fingers.add(capacitor_strips[i])
            elif i%2 == 0:
                capacitor_strips.append(core.Boundary(strip_box,layer=2))
                capacitor_strips[i].translate((KID_full_w/2.-W-l_Cs-g_Cs,L+g_LC+W+g_Cs*(i*2+1)))
                cell_fingers.add(capacitor_strips[i])

        cell_capacitor.add(cell_fingers)




    #ground shield
        w_gs = KID_full_w+2*g_s+2*w_s
        l_gs = L+g_LC+W+N_Cs*w+N_Cs*g_Cs+2*g_s+w_s
        gShield = [\
                (0,0),\
                (0,l_gs),\
                (w_gs,l_gs),\
                (w_gs,0),\
                (w_gs-w_s,0),\
                (w_gs-w_s,l_gs-w_s),\
                (w_s,l_gs-w_s),\
                (w_s,0)]
        gShield_polygon = core.Boundary(gShield,layer=1)




        cell_KID.add(cell_meander)
        cell_KID.add(cell_capacitor)

        cell_KID_shielded.add(cell_KID,(0,g_s))
        cell_KID_shielded.add(gShield_polygon.translate((-w_gs/2,0)))
##########
########## class members
##########
        self.w = w_gs
        self.l = l_gs
        self.meander = cell_meander
        self.capacitor = cell_capacitor
        self.KID = cell_KID
        self.KID_shielded = cell_KID_shielded



#full_layout = core.Layout('FULL_LAYOUT')
#full_layout.add(KID(5000.).KID_shielded)
#full_layout.add(KID(1000.).KID)
#full_layout.show()
