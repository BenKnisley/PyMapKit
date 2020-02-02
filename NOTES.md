Notes
===

##### f




##### Independent point in polygon function
I found this function for independent point in polygon. I want to test it to see if: 1, it works. 2, how fast it is. Even if it is a bit slower than shapely or OGR, I would want to include it because I would not need another depend.

[Function Source](http://geospatialpython.com/2011/01/point-in-polygon.html)


```python
# Determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs. This function
# returns True or False.  The algorithm is called
# the "Ray Casting Method".

def point_in_poly(x,y,poly):

    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside

## Test

polygon = [(0,10),(10,10),(10,0),(0,0)]

point_x = 5
point_y = 5

## Call the function with the points and the polygon
print point_in_poly(point_x,point_y,polygon)
```
