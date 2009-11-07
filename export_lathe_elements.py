''' export_lathe_elements.py
takes lines and arcs in xz format- sorts them and converts them to something useble for 
lathe gcode output in xz format
input file should already have xy coords converted to zx (z=original x, x=original y)
python dictionary input format:
path.txt-
{'type':'ARC', 'startpt':( 0,0.25,0) ,'endpt':( -0.25,0.5,0) ,'radius':0.25 ,'ce
npt':( -0.25,0.25,0) ,'midpt':( -0.0732233,0.426777,0)}
{'type':'ARC', 'startpt':( -0.75,0.5,0) ,'endpt':( -1,0.75,0) ,'radius':0.25 ,'c
enpt':( -0.75,0.75,0) ,'midpt':( -0.926777,0.573223,0)}
{'type':'LINE', 'startpt':( 0,0,0) ,'endpt':( 0,0.25,0)}
{'type':'LINE', 'startpt':( -1,0.75,0) ,'endpt':( -1,1,0)}
{'type':'LINE', 'startpt':( -0.25,0.5,0) ,'endpt':( -0.75,0.5,0)}
{'type':'LINE', 'startpt':( -1,1,0) ,'endpt':( -2.28977,1,0)}

start_element.txt-
{'type':'LINE', 'startpt':( 0,0,0) ,'endpt':( 0,0.25,0)}

you can see that start_element.txt is part of the same geometry as path.txt
I needed to find some way of indicating to my sorting routine what the first element was and 
it needed to be going the correct direction to make the sorting work out
I made these two separate files because of the orignal scripting langauge that I have to use in
Ashlar Graphite. Things can be simplified for other open source cad programs
'''
# --------------------------------------------------------------------------------------
# export_lathe_elements.py Copywrite 2009/10/30 Dan Falck - ddfalck2002@yahoo.com
# --------------------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ***** END GPL LICENCE BLOCK *****
# --------------------------------------------------------------------------



import StringIO

dec_plcs=4 #rounding to 4 digits
#### sorting #####
def compare_unordered_points(beg_elem,profile):
    #returns elements in order and gets endpts connected to starpts 
    for item in profile:
        if item['startpt'] == beg_elem['endpt']:              
            return item
        elif (item['endpt'] == beg_elem['endpt'] and item['startpt'] ==beg_elem['startpt'])\
             or (item['endpt'] == beg_elem['startpt'] and item['startpt'] ==beg_elem['endpt']):
            pass
            #print 'same'
        elif item['endpt'] == beg_elem['endpt']:            
            tmp=item['endpt']
            item['endpt']=item['startpt']
            item['startpt']=tmp
            #print 'reversed item'
            #print item['type']
            #print item
            return item
        else:
            pass
def sort_unordered_profile(beg_elem,profile):
    #sort the order of the profile
    ordered_list=[beg_elem]
    for comp in range(0,len(profile)):
        connected=compare_unordered_points(beg_elem,profile)
        ordered_list.append(connected)         
        beg_elem=connected        
    return ordered_list

#### end of sorting ####

#### routine for finding arc direction ####
def DiamondAngle(x, y):
    if (x > 0 and y==0):
        return 0

    elif (x<0 and y==0):
        return 2

    elif (y > 0):
        if (x >= 0):
            return (y/(x+y)) 
        else:
            return  (1-x/(-x+y)) 
    else:
        if (x < 0):
            return  (2-y/(-x-y))
        else:
            return  (3+x/(x-y))


def find_dir(start_pt,mid_pt,end_pt):
    ''' refining it further -check to see what direction start to mid to end points are going '''
    xstart, ystart = start_pt
    xmid, ymid = mid_pt
    xend, yend = end_pt
    a=DiamondAngle(float(xstart),float(ystart));#print 'diamond_angle a ='+str(DiamondAngle(xstart,ystart))
    b=DiamondAngle(float(xmid), float(ymid));#print 'diamond_angle b ='+str(DiamondAngle(xmid, ymid))
    c=DiamondAngle(float(xend),float(yend));#print 'diamond_angle c ='+str(DiamondAngle(xend,yend))
    #print 'a='+str(a)+' b='+str(b)+' c='+str(c)+'\n'
    if (a > b) and (a < c): # c (end point)is in 4th quadrant
        return -1 # CCW
    elif(a>b>c):
        return -1
    elif (a==0):
        if(b>c):
            return -1
        else:
            return 1
    elif (a>c and c ==0):
        return 1
    else:
        return 1  # CW

def translate(start_pt, mid_pt, end_pt, cen_pt):
    ''' move arc so that cen_pt is at 0,0 for easy calculations'''
    xstart, ystart = start_pt
    xmid, ymid = mid_pt
    xend, yend = end_pt
    xcen, ycen = cen_pt

    new_xstart = xstart-xcen
    new_ystart = ystart-ycen
    new_xmid   = xmid - xcen
    new_ymid   = ymid - ycen
    new_xend   = xend - xcen
    new_yend   = yend - ycen
    new_xcen  = 0
    new_ycen  = 0
    pstart = new_xstart,new_ystart
    pmid   = new_xmid, new_ymid
    pend   = new_xend, new_yend
    pcen   = new_xcen, new_ycen
    return pstart,pmid,pend,pcen


def arc_dir(start_pt, mid_pt, end_pt, cen_pt):
    start,mid,end,cen=translate(start_pt, mid_pt, end_pt, cen_pt)
    dir=find_dir(start,mid,end)
    return dir     
#### end of routine for finding arc direction ####

#### Save_coords old coordinates to prevent redundant moves #####
class Save_coords:
  def __init__(self, str1,str2):    
    self.x = str1
    self.z = str2    
  # Two methods:
  def show(self):
    return self.x+' '+self.z
  def show_arc(self):
    return self.x+' '+self.z
  def x_old(self):
    return self.x
  def z_old(self):
    return self.z    

#### Save_coords old coord class ####


#### looping and parsing routines ####
def make_list(file):
    list1=[]
    for line in file:
        #line.rstrip('\"')
        list1.append(eval(line[:-2]))
    return list1

def strip_parens(st):
    st=str(st)
    st=str(st.replace('(',''))
    st=str(st.replace(')',''))
    return st


def output():
    file = StringIO.StringIO()
   # point_file=make_list(open('/tmp/start_point.txt','r').readlines())
    start_elem=make_list(open('/tmp/start_element.txt','r').readlines())
    post_file=(open('/tmp/lathe_post_it.txt','r').readline())

    #print start_elem[0]['startpt'][0:2]
    profile=make_list(open('/tmp/path.txt','r').readlines())    
    a=sort_unordered_profile(start_elem[0],profile)
    #startpoint=point_file[0]['point'][0:2]    
    startpoint=start_elem[0]['startpt'][0:2]
    x,y= ((startpoint))
    xsp=2*y;xsp=round(xsp,dec_plcs)
    zsp=x;zsp=round(zsp,dec_plcs)
    coords = Save_coords(xsp,zsp)
    rapids='G0'+'X'+str(xsp)+'Z'+ str(zsp)+'\n'
    file.write(rapids)
    
    for items in a[0:-1]:        
        if items['type']=='ARC':
            startpt=str(items['startpt'][0:2])            
            endpt=str(items['endpt'][0:2])
            endpt=strip_parens(endpt) 
            radius=(items['radius'])
            #print radius  
            cenpt=str(items['cenpt'][0:2])
            cenpt=strip_parens(cenpt)
            midpt=str(items['midpt'][0:2])
            midpt=strip_parens(midpt)            
            ep=eval(endpt)
            sp=eval(startpt)
            cp=eval(cenpt)
            mp=eval(midpt)
            jcp,icp=cp
            zsp,xsp=sp
            jcp=jcp-zsp;icp=icp-xsp                    
            zlast,xlast=eval(endpt)
            zlast=round(zlast,dec_plcs);xlast=round(xlast*2,dec_plcs);jcp=round(jcp,dec_plcs);icp=round(icp,dec_plcs)
            arc_direction = arc_dir(sp,mp,ep,cp)
            if arc_direction==1:
                arc='G3'
            else:
                arc='G2'

            if post_file=='RADIUS':
                    arcs=arc+'X'+str(xlast)+'Z'+str(zlast)+'R'+str(round(radius,dec_plcs))+'\n'
            else:
            
                


                el=arc+''+endpt+', '+cenpt
                if icp ==0:
                    arcs=arc+'X'+str(xlast)+'Z'+str(zlast)+'J'+str(jcp)+'\n'
                elif jcp == 0:
                    arcs=arc+'X'+str(xlast)+'Z'+str(zlast)+'I'+str(icp)+'\n'
                else:
                    arcs=arc+'X'+str(xlast)+'Z'+str(zlast)+'I'+str(icp)+'J'+str(jcp)+'\n'
            coords = Save_coords(xlast,zlast)
            file.write(arcs)

        elif items['type']=='LINE':
            endpt=str(items['endpt'][0:2])
            endpt=strip_parens(endpt)
            zlast,xlast=eval(endpt)            
            zlast=round(zlast,dec_plcs);xlast=round(xlast*2,dec_plcs)
            if xlast ==coords.x_old():
                feed_moves='G1'+'Z'+str(zlast)+'\n'
            elif zlast == coords.z_old():
                feed_moves='G1'+'X'+ str(xlast)+'\n'
            else:                
                feed_moves='G1'+'X'+ str(xlast)+'Z'+str(zlast)+'\n'
            coords = Save_coords(xlast,zlast)
            file.write(feed_moves)  
    print file.getvalue()


output()




