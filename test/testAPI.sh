curl -X GET localhost:5000/drone/api/v1.0/search
curl -X GET localhost:5000/drone/api/v1.0/assign
curl -X GET localhost:5000/drone/api/v1.0/battery/0
curl -X GET localhost:5000/drone/api/v1.0/getpicture/0
# curl -X POST -F 'destination=(5,4,3,2,1)' -F 'droneID=0' localhost:5000/drone/api/v1.0/navigate/0
curl -X POST -F 'x=5' -F 'y=4' -F 'z=3' -F 'o=2' -F 'h=1' -F 'droneID=0' localhost:5000/drone/api/v1.0/navigate/0
curl -X GET localhost:5000/drone/api/v1.0/regain/10
