echo "--------RELEASE----------"
curl --user test:test -X GET  localhost:5000/drone/api/v1.0/release
sleep 3s

echo "--------SEARCH----------"
curl --user test:test -X GET  localhost:5000/drone/api/v1.0/search
sleep 3s

echo "--------ASSIGN----------"
curl --user test:test -X GET  localhost:5000/drone/api/v1.0/assign
sleep 3s
curl --user test:test -X GET  localhost:5000/drone/api/v1.0/assign
sleep 3s
curl --user test:test -X GET  localhost:5000/drone/api/v1.0/assign
sleep 3s

echo "--------NAVIGATE----------"
curl --user test:test -d "droneID=0&x=22.733227&y=120.280323&z=200&o=1&h=0" -X PATCH  localhost:5000/drone/api/v1.0/navigate
sleep 3s
curl --user test:test -d "droneID=1&x=22.733227&y=120.280323&z=200&o=1&h=0" -X PATCH  localhost:5000/drone/api/v1.0/navigate
sleep 3s


# otehr coordinate
# curl --user test:test -d "droneID=0&x=22.734453&y=120.283557&z=200&o=1&h=0" -X PATCH  localhost:5000/drone/api/v1.0/navigate
# sleep 3s
# curl --user test:test -d "droneID=1&x=22.734453&y=120.283557&z=200&o=1&h=0" -X PATCH  localhost:5000/drone/api/v1.0/navigate
# sleep 3s

# echo "--------RESULT----------"
# curl --user test:test -X GET  localhost:5000/drone/api/v1.0/drones
