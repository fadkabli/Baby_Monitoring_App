import requests as req

# Make a GET request to the API endpoint
response = req.get('http://localhost:5000/detect')

# Retrieve the JSON object from the response
results = response.json()

# Print the number of faces detected
print('Number of faces detected:', results['num_faces'])

# Print the coordinates of each face detected
for face in results['faces']:
    print('Face coordinates: x={}, y={}, width={}, height={}'.format(face['x'], face['y'], face['width'], face['height']))

curl -X POST -F 'image=@/Users/Kabli/Desktop/flask_app/image1.jpg' http://localhost:5000/detect_faces