from sklearn.preprocessing import MinMaxScaler
data = [[0, 630], [63, 64], [65,66], [69, 68]]
scaler = MinMaxScaler()
print(scaler.fit(data))
# print(scaler.data_max_)
print((scaler.transform(data)[2])[1])
#print(scaler.transform([[2, 2]]))