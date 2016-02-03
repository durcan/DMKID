from gdsCAD import *



class KID:
    def __init__(self,capacitor_length):
        cell_meander = core.Cell('MEANDER')
        cell_meander_left = core.Cell('MEANDER_LEFT')
        cell_meander_right = core.Cell('MEANDER_RIGHT')
        #layout = core.Layout('LAYOUT')



    #meander:
        meander = core.Cell('MEANDER')
        meander_length = 3000.
        meander_inner_gap = 30.
        meander_outer_gap = 10.
        meander_rear_width = [80., 60., 80., 90.]
        meander_front_width = [80., 40., 80., 90.]
        meander_wide_bridge = 80.
        meander_narrow_bridge = 30.
        meander_neck_width = 30.
        meander_neck_length = 100.


        KID_full_w = 2*(meander_front_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap+meander_rear_width[1]+meander_inner_gap+meander_front_width[0])+meander_outer_gap

        meander_points = [(0,0), (meander_length,0),\
                (meander_length,meander_rear_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap+meander_rear_width[1]+meander_inner_gap+meander_rear_width[0]),\
                (meander_narrow_bridge+meander_inner_gap,meander_rear_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap+meander_rear_width[1]+meander_inner_gap+meander_rear_width[0]),\
                (meander_narrow_bridge+meander_inner_gap,meander_rear_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap+meander_rear_width[1]+meander_inner_gap+meander_rear_width[0]-meander_front_width[0]),\
                (meander_length-meander_wide_bridge,meander_rear_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap+meander_rear_width[1]+meander_inner_gap+meander_rear_width[0]-meander_front_width[0]),\
                (meander_length-meander_wide_bridge,meander_rear_width[3]),\
                (meander_wide_bridge,meander_front_width[3]),\
                (meander_wide_bridge,meander_front_width[3]+meander_inner_gap),\
                (meander_length-meander_wide_bridge-meander_inner_gap,meander_front_width[3]+meander_inner_gap),\
                (meander_length-meander_wide_bridge-meander_inner_gap,meander_front_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap+meander_rear_width[1]),\
                (meander_narrow_bridge,meander_front_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap+meander_rear_width[1]),\
                (meander_narrow_bridge,meander_front_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap+meander_rear_width[1]+meander_inner_gap+meander_front_width[0]-meander_neck_width),\
                (0,meander_front_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap+meander_rear_width[1]+meander_inner_gap+meander_front_width[0]-meander_neck_width),\
                (0,meander_front_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap+meander_rear_width[1]-meander_front_width[1]),\
                (meander_length-meander_wide_bridge-meander_inner_gap-meander_wide_bridge,meander_front_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap),\
                (meander_length-meander_wide_bridge-meander_inner_gap-meander_wide_bridge,meander_front_width[3]+meander_inner_gap+meander_rear_width[2]),\
                (0,meander_front_width[3]+meander_inner_gap+meander_front_width[2])]


        meander_polygon = core.Boundary(meander_points)
        cell_meander_left.add(meander_polygon)

        dummy = []
        for (a,b) in meander_points:
            dummy.append((a,-b))

        meander_polygon = core.Boundary(dummy)
        meander_polygon.translate((0,(meander_rear_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap+meander_rear_width[1]+meander_inner_gap+meander_rear_width[0])*2+meander_outer_gap))
        cell_meander_right.add(meander_polygon)

        cell_meander.add(cell_meander_right)
        cell_meander.add(cell_meander_left)



    #central bridge
        central_bridge_points = [(meander_narrow_bridge+meander_inner_gap,meander_rear_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap+meander_rear_width[1]+meander_inner_gap+meander_rear_width[0]),\
                (meander_narrow_bridge+meander_inner_gap+meander_wide_bridge,meander_rear_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap+meander_rear_width[1]+meander_inner_gap+meander_rear_width[0]),\
                (meander_narrow_bridge+meander_inner_gap+meander_wide_bridge,meander_rear_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap+meander_rear_width[1]+meander_inner_gap+meander_rear_width[0]+meander_outer_gap),\
                (meander_narrow_bridge+meander_inner_gap,meander_rear_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap+meander_rear_width[1]+meander_inner_gap+meander_rear_width[0]+meander_outer_gap)]

        central_bridge = core.Boundary(central_bridge_points)
        cell_meander.add(central_bridge)



    #neck
        neck = core.Boundary(((0,0), (0,meander_neck_width), (meander_neck_length,meander_neck_width), (meander_neck_length,0)), layer=1)

        neck.translate((meander_narrow_bridge-meander_neck_length,meander_front_width[3]+meander_inner_gap+meander_rear_width[2]+meander_outer_gap+meander_rear_width[1]+meander_inner_gap+meander_front_width[0]-meander_neck_width))
        cell_meander.add(neck)

        neck2 = neck.copy()
        neck2.translate((0,meander_outer_gap+meander_neck_width))
        cell_meander.add(neck2)




    #capacitor
        capacitor_strip_w = 50.
        cpacitor_end_gap = 20.
        capacitor_full_w = (int(capacitor_length/(KID_full_w-2*capacitor_strip_w-cpacitor_end_gap))+1.5)*capacitor_strip_w*2

        capacitor_points = [(0,0) , (capacitor_strip_w,0) , (capacitor_strip_w,(KID_full_w-meander_outer_gap)/2.-meander_neck_width) , (capacitor_strip_w-capacitor_full_w,(KID_full_w-meander_outer_gap)/2.-meander_neck_width) , (capacitor_strip_w-capacitor_full_w,(KID_full_w-meander_outer_gap)/2.-meander_neck_width-capacitor_strip_w) , (0,(KID_full_w-meander_outer_gap)/2.-meander_neck_width-capacitor_strip_w)]

        Poly_capacitor_outer_right = core.Boundary(capacitor_points, layer=1)
        Poly_capacitor_outer_right.translate((-meander_neck_length+meander_narrow_bridge,(KID_full_w+meander_outer_gap)/2.+meander_neck_width))

        cell_meander.add(Poly_capacitor_outer_right)

        dummy = []
        for (a,b) in capacitor_points:
            dummy.append((a,-b))
        Poly_capacitor_outer_left = core.Boundary(dummy, layer=1)
        Poly_capacitor_outer_left.translate((-meander_neck_length+meander_narrow_bridge,(KID_full_w-meander_outer_gap)/2.-meander_neck_width))

        cell_meander.add(Poly_capacitor_outer_left)

        capacitor_inner_strip = core.Boundary(( (0,0), (0,KID_full_w-2*capacitor_strip_w-cpacitor_end_gap), (capacitor_strip_w,KID_full_w-2*capacitor_strip_w-cpacitor_end_gap), (capacitor_strip_w,0) ), layer=1)
        capacitor_inner_strip.translate((meander_narrow_bridge-meander_neck_length-2*capacitor_strip_w,capacitor_strip_w))

        inner_strip_copy = []
        for i in range(int(capacitor_length/(KID_full_w-2*capacitor_strip_w-cpacitor_end_gap))):
                if i%2 == 0:
                    inner_strip_copy.append(capacitor_inner_strip.copy().translate((-2*capacitor_strip_w*i,0)))
                else:
                    inner_strip_copy.append(capacitor_inner_strip.copy().translate((-2*capacitor_strip_w*i,cpacitor_end_gap)))

        cell_meander.add(inner_strip_copy)


        capacitor_final_strip = core.Boundary(((0,0), (0,capacitor_length%(KID_full_w-2*capacitor_strip_w-cpacitor_end_gap)), (capacitor_strip_w,capacitor_length%(KID_full_w-2*capacitor_strip_w-cpacitor_end_gap)), (capacitor_strip_w,0)), layer=1)
        capacitor_final_strip.translate((meander_narrow_bridge-meander_neck_length-2*capacitor_strip_w,capacitor_strip_w))


        if int(capacitor_length/(KID_full_w-2*capacitor_strip_w-cpacitor_end_gap))%2 == 0:
            capacitor_final_strip.translate((-2*capacitor_strip_w*int(capacitor_length/(KID_full_w-2*capacitor_strip_w-cpacitor_end_gap+1)),0))
        else:
            capacitor_final_strip.translate((-2*capacitor_strip_w*int(capacitor_length/(KID_full_w-2*capacitor_strip_w-cpacitor_end_gap+1)),KID_full_w-2*capacitor_strip_w-capacitor_length%(KID_full_w-2*capacitor_strip_w-cpacitor_end_gap)))

        cell_meander.add(capacitor_final_strip)


        #Ref_cell_meander = core.CellReference(cell_meander, origin = ((0.5*-meander_length,0.)))



    #capacitor length lebel
        #capacitor_length_label = shapes.LineLabel("%i"%(capacitor_length), size=600, position = (500,900))
        #cell_meander.add(capacitor_length_label)





##########
########## class members
##########
        self.meander_length = meander_length
        self.KID = cell_meander
        self.KID_length = meander_length+meander_neck_length-meander_narrow_bridge-capacitor_strip_w+float(capacitor_full_w)
