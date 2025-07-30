# TODO for project

1. make Vec * Mat and Mat * Vec work
2. Add Transform
3. Add Util functions 
4. Add Obj and Mesh


a=Vec3(1,2,3)
b=Mat3()
b.rotateX(45.0)
c=a*b
d=b*a
print(c)
print(d)
print(c)
[1.0,-0.707107,3.535534]
print(d)
[1.0,3.535534,0.707107]

Mat3 @ Mat3 (__matmul__)
Mat3 @ Vec3 (__matmul__)
Mat3 * scalar (__mult__)
scalar * Mat3 (__imult__ == __mult__)

Vec3 @ Mat3  (in Vec3)




