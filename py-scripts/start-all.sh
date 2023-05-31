#auxiliar
echo "Starting auxiliar..."
python3 auxiliar.py > /dev/null 2>&1 &

#OBU 1
echo "Starting OBU1..."
python3 OBU1.py > /dev/null 2>&1 &

#OBU 2
echo "Starting OBU2..."
python3 OBU2.py > /dev/null 2>&1 &

#OBU 2R
# echo "Starting OBU2R..."
# python3 OBU2R.py > /dev/null 2>&1 &

#OBU 3
# echo "Starting OBU3..."
# python3 OBU3.py > /dev/null 2>&1 &

#RSU 1
echo "Starting RSU1..."
python3 RSU-all.py 1 40.636032 8.646632 2.8 '192.168.98.10' > /dev/null 2>&1 2>&1 &

#RSU 6
echo "Starting RSU6..."
python3 RSU-all.py 6 40.635727 8.647118 2.8 '192.168.98.60' > /dev/null 2>&1 &

#RSU 10
echo "Starting RSU10..."
python3 RSU-all.py 10 40.636584 8.648210 2.8 '192.168.98.100' > /dev/null 2>&1 &

#RSU 11
echo "Starting RSU11..."
python3 RSU-all.py 11 40.636991 8.647816 2.8 '192.168.98.110' > /dev/null &

#RSU 13
echo "Starting RSU13..."
python3 RSU-all.py 13 40.637100 8.649072 2.8 '192.168.98.130' > /dev/null 2>&1 &

#RSU 15
echo "Starting RSU15..."
python3 RSU-all.py 15 40.637318 8.649641 2.8 '192.168.98.150' > /dev/null 2>&1 &

#RSU 16
echo "Starting RSU16..."
python3 RSU-all.py 16 40.638006 8.649255 2.8 '192.168.98.160' > /dev/null 2>&1 &

#HIGHWAY

#RSU 19
echo "Starting RSU19..."
python3 RSU-all.py 19 40.640030 8.663484 1.25 '192.168.98.190' > /dev/null 2>&1 &

#RSU 22
echo "Starting RSU22..."
python3 RSU-all.py 22 40.641357 8.661778 1.25 '192.168.98.220' > /dev/null 2>&1 &

#RSU 25
echo "Starting RSU25..."
python3 RSU-all.py 25 40.642432 8.660319 1.25 '192.168.98.25' > /dev/null 2>&1 &

#RSU 28
echo "Starting RSU28..."
python3 RSU-all.py 28 40.643487 8.658731 1.25 '192.168.98.28' > /dev/null 2>&1 &

# #API
echo "Starting API..."
python3 ../api/app.py > /dev/null 2>&1 2>&1 &

echo "All machines started."