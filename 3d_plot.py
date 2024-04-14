df = pd.DataFrame(data)

# Create a 3D scatter plot
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot
ax.scatter(df['broadband'], df['Gini-2019'], df['GDP-2019'], c='b', marker='o')

# Set labels and title
ax.set_xlabel('Broadband')
ax.set_ylabel('Gini-2019')
ax.set_zlabel('GDP-2019')
ax.set_title('3D Scatter plot of Broadband, Gini-2019, and GDP-2019')

# Show the plot
plt.show()