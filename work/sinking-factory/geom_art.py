def triangle(a,b,c,color,z,order=0,gg=(),ldm=False):
 pts=[a,b,c];i=max(range(3),key=lambda i:math.dist(pts[i],pts[(i+1)%3]))
 a,b,c=pts[i],pts[(i+1)%3],pts[(i+2)%3]
 ux,uy=b[0]-a[0],b[1]-a[1];length=math.hypot(ux,uy)
 if length<.001:return
 q=((c[0]-a[0])*ux+(c[1]-a[1])*uy)/(length*length)
 r=(a[0]+q*ux,a[1]+q*uy)
 for end in [a,b]:
  u=(end[0]-r[0],end[1]-r[1]);v=(c[0]-r[0],c[1]-r[1]);w=math.hypot(*u);h=math.hypot(*v)
  if min(w,h)<.01:continue
  theta=math.atan2(-u[1],-u[0]);dy=(-math.sin(theta),math.cos(theta))
  o=add(693,r[0]+(u[0]+v[0])/2,r[1]+(u[1]+v[1])/2,color,z,order,w/30,h/30,-math.degrees(theta),gg,ldm=ldm)
  if v[0]*dy[0]+v[1]*dy[1]<0:o['5']='1'

def poly(points,c,z,order=0,gg=(),ldm=False):
 for i in range(1,len(points)-1):triangle(points[0],points[i],points[i+1],c,z,order,gg,ldm)

def glow(x,y,w,h,c=616,z=-5,gg=()):
 # Native round glow, safely stretched and kept behind the scenery.
 add(1887,x,y,c,z,-2,w/10,h/10,gg=gg,ldm=True)
