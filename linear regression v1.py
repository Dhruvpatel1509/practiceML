import numpy as np
import matplotlib.pyplot as plt

x_train = np.array([1.0,2.0])
y_train = np.array([300.0,500.0])

m=len(x_train)
print(m)

m=x_train.shape[0]
print(m)

i=0

x_i=x_train[i]
y_i=y_train[i]  
print(x_i)
print(y_i)


# plt.scatter(x_train,y_train,color='blue',marker='x',label='Training data')
# plt.title('Housing Prices')
# plt.xlabel('Size in 1000 sqft')
# plt.ylabel('Price in 1000 $')
# plt.show()


w=200
b=100


def compute(x_train, w, b, m):

    f_wb=np.zeros(m)
    for i in range(m):
        f_wb[i]=w*x_train[i]+b
        

    return f_wb

tmp_f_wb=compute(x_train,w,b,m,)
print(tmp_f_wb)
x_i=1.2
y_cap=w*x_i+b
print(y_cap)

plt.plot(x_train,tmp_f_wb,color='red',label='Prediction')
plt.scatter(x_train,y_train,color='blue',marker='x',label='Training data')
plt.scatter(x_i,y_cap,color='green',marker='*',label='New data point')
plt.text(x_i, y_cap + 20, f'({x_i}, {y_cap})', fontsize=10, ha='center')
plt.title('Housing Prices')
plt.xlabel('Size in 1000 sqft')
plt.ylabel('Price in 1000 $')
plt.show()




