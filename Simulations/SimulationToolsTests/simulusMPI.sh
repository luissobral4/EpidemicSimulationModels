#mpiexec -host "192.168.112.29":2 -np 2 python3 pTSimulus.py 90000 200 -c 4 --mpi > SimulusMPI/90000Nsimulus4p2.out &
#psrecord $! --interval 1 --duration 10000 --plot SimulusMPI/160000simulus4p2.png

#mpiexec -host "192.168.112.29" -np 8 --oversubscribe python3 pTSimulus.py 62500 200 -c 4 --mpi >  SimulusMPI/62500simulus4p8.out &
#psrecord $! --interval 1 --duration 10000 --plot SimulusMPI/62500simulus4p8.png

#mpiexec -host "192.168.112.29" -np 16 --oversubscribe python3 pTSimulus.py 62500 200 -c 4 --mpi >  SimulusMPI/62500simulus4p16.out &
#psrecord $! --interval 1 --duration 10000 --plot SimulusMPI/62500simulus4p16.png

dist="100"
lookahead="0.1"
seed="10"
duration="10000"
ip="192.168.112.29"

python3 pTSimian.py 250000 200 > Simian/simianS250000.out
mpiexec -host $ip:4 -np 4 python3 pTSimian.py 250000 200 --useMPI 1  > Simian/simianMPIS250000-P4.out
mpiexec -host $ip:4 -np 4 python3 pTSimulus.py 250000 200 -c 4 --mpi >  SimulusMPI/250000simulus4p4.out
python3 pTSimulus.py 250000 200 -c 2  > Simulus/simulus2S250000.out
python3 pTSimPy.py 250000 200 > Simpy/simpyS250000.out
python3 pTSimulus.py 250000 200 -c 1  > Simulus/simulusS250000.out


mpiexec -host $ip:2 -np 2 python3 pTSimian.py 10000 200 --useMPI 1  > Simian/simianMPIS10000-P2.out
mpiexec -host $ip:2 -np 2 python3 pTSimian.py 62500 200 --useMPI 1  > Simian/simianMPIS62500-P2.out
mpiexec -host $ip:2 -np 2 python3 pTSimian.py 90000 200 --useMPI 1  > Simian/simianMPIS90000-P2.out
mpiexec -host $ip:2 -np 2 python3 pTSimian.py 160000 200 --useMPI 1  > Simian/simianMPIS160000-P2.out

mpiexec -host $ip:4 -np 4 python3 pTSimian.py 10000 200 --useMPI 1  > Simian/simianMPIS10000-P4.out
mpiexec -host $ip:4 -np 4 python3 pTSimian.py 62500 200 --useMPI 1  > Simian/simianMPIS62500-P4.out
mpiexec -host $ip:4 -np 4 python3 pTSimian.py 90000 200 --useMPI 1  > Simian/simianMPIS90000-P4.out
mpiexec -host $ip:4 -np 4 python3 pTSimian.py 160000 200 --useMPI 1  > Simian/simianMPIS160000-P4.out

mpiexec -host $ip:8 -np 8 python3 pTSimian.py 10000 200 --useMPI 1  > Simian/simianMPIS10000-P8.out
mpiexec -host $ip:8 -np 8 python3 pTSimian.py 62500 200 --useMPI 1  > Simian/simianMPIS62500-P8.out
mpiexec -host $ip:8 -np 8 python3 pTSimian.py 90000 200 --useMPI 1  > Simian/simianMPIS90000-P8.out
mpiexec -host $ip:8 -np 8 python3 pTSimian.py 160000 200 --useMPI 1  > Simian/simianMPIS160000-P8.out

python3 pTSimulus.py 10000 200 -c 2 > SimulusMPI/10000Nsimulus2.out
python3 pTSimulus.py 62500 200 -c 2 > SimulusMPI/62500Nsimulus2.out
python3 pTSimulus.py 90000 200 -c 2 > SimulusMPI/90000Nsimulus2.out

mpiexec -host $ip:2 -np 2 python3 pTSimulus.py 10000 200 -c 4 --mpi >  SimulusMPI/10000simulus4p2.out
mpiexec -host $ip:2 -np 2 python3 pTSimulus.py 62500 200 -c 4 --mpi >  SimulusMPI/62500simulus4p2.out
mpiexec -host $ip:2 -np 2 python3 pTSimulus.py 90000 200 -c 4 --mpi >  SimulusMPI/90000simulus4p2.out

mpiexec -host $ip:4 -np 4 python3 pTSimulus.py 10000 200 -c 4 --mpi >  SimulusMPI/10000simulus4p4.out
mpiexec -host $ip:4 -np 4 python3 pTSimulus.py 62500 200 -c 4 --mpi >  SimulusMPI/62500simulus4p4.out
mpiexec -host $ip:4 -np 4 python3 pTSimulus.py 90000 200 -c 4 --mpi >  SimulusMPI/90000simulus4p4.out

mpiexec -host $ip:8 -np 8 python3 pTSimulus.py 10000 200 -c 4 --mpi >  SimulusMPI/10000simulus4p8.out
mpiexec -host $ip:8 -np 8 python3 pTSimulus.py 62500 200 -c 4 --mpi >  SimulusMPI/62500simulus4p8.out
mpiexec -host $ip:8 -np 8 python3 pTSimulus.py 90000 200 -c 4 --mpi >  SimulusMPI/90000simulus4p8.out

mpiexec -host $ip:16 -np 16 python3 pTSimulus.py 10000 200 -c 4 --mpi >  SimulusMPI/10000simulus4p16.out
mpiexec -host $ip:16 -np 16 python3 pTSimulus.py 62500 200 -c 4 --mpi >  SimulusMPI/62500simulus4p16.out
mpiexec -host $ip:16 -np 16 python3 pTSimulus.py 90000 200 -c 4 --mpi >  SimulusMPI/90000simulus4p16.out


python3 pTSimulus.py 160000 200 -c 2 > SimulusMPI/160000Nsimulus2.out
mpiexec -host $ip:2 -np 2 python3 pTSimulus.py 160000 200 -c 4 --mpi >  SimulusMPI/160000simulus4p2.out
mpiexec -host $ip:4 -np 4 python3 pTSimulus.py 160000 200 -c 4 --mpi >  SimulusMPI/160000simulus4p4.out
mpiexec -host $ip:8 -np 8 python3 pTSimulus.py 160000 200 -c 4 --mpi >  SimulusMPI/160000simulus4p8.out
mpiexec -host $ip:16 -np 16 python3 pTSimulus.py 160000 200 -c 4 --mpi >  SimulusMPI/160000simulus4p16.out




# mpiexec -host "192.168.112.29" -np 2 --oversubscribe python3 pTSimulus.py 62500 200 -c 3 --mpi > SimulusMPI/62500simulus3p2.out &
# psrecord $! --interval 1 --duration 10000 --plot SimulusMPI/62500simulus3p2.png

# mpiexec -host "192.168.112.29" -np 4 --oversubscribe python3 pTSimulus.py 62500 200 -c 3 --mpi >  SimulusMPI/62500simulus3p4.out &
# psrecord $! --interval 1 --duration 10000 --plot SimulusMPI/62500simulus3p4.png

# mpiexec -host "192.168.112.29" -np 8 --oversubscribe python3 pTSimulus.py 62500 200 -c 3 --mpi >  SimulusMPI/62500simulus3p8.out &
# psrecord $! --interval 1 --duration 10000 --plot SimulusMPI/62500simulus3p8.png

#mpiexec -host "192.168.112.29" -np 16 --oversubscribe python3 pTSimulus.py 62500 200 -c 3 --mpi >  SimulusMPI/62500simulus3p16.out &
#psrecord $! --interval 1 --duration 10000 --plot SimulusMPI/62500simulus3p16.png



mpiexec --hostfile myhosts1 -np 2 python3 pTSimulus.py 10000 200  -c 4 --mpi > Tests/simulus10000p2.out
mpiexec --hostfile myhosts2 -np 4 python3 pTSimulus.py 10000 200  -c 4 --mpi > Tests/simulus10000p4.out
mpiexec --hostfile myhosts3 -np 8 python3 pTSimulus.py 10000 200  -c 4 --mpi > Tests/simulus10000p8.out
mpiexec --hostfile myhosts4 -np 16 python3 pTSimulus.py 10000 200  -c 4 --mpi > Tests/simulus10000p16.out

mpiexec --hostfile myhosts1 -np 2 python3 pTSimulus.py 62500 200  -c 4 --mpi > Tests/simulus62500p2.out
mpiexec --hostfile myhosts2 -np 4 python3 pTSimulus.py 62500 200  -c 4 --mpi > Tests/simulus62500p4.out
mpiexec --hostfile myhosts3 -np 8 python3 pTSimulus.py 62500 200  -c 4 --mpi > Tests/simulus62500p8.out
mpiexec --hostfile myhosts4 -np 16 python3 pTSimulus.py 62500 200  -c 4 --mpi > Tests/simulus62500p16.out

mpiexec --hostfile myhosts1 -np 2 python3 pTSimulus.py 90000 200  -c 4 --mpi > Tests/simulus90000p2.out
mpiexec --hostfile myhosts2 -np 4 python3 pTSimulus.py 90000 200  -c 4 --mpi > Tests/simulus90000p4.out
mpiexec --hostfile myhosts3 -np 8 python3 pTSimulus.py 90000 200  -c 4 --mpi > Tests/simulus90000p8.out
mpiexec --hostfile myhosts4 -np 16 python3 pTSimulus.py 90000 200  -c 4 --mpi > Tests/simulus90000p16.out

mpiexec --hostfile myhosts1 -np 2 python3 pTSimulus.py 160000 200 -c 4 --mpi > Tests/simulus160000p2.out
mpiexec --hostfile myhosts2 -np 4 python3 pTSimulus.py 160000 200 -c 4 --mpi > Tests/simulus160000p4.out
mpiexec --hostfile myhosts3 -np 8 python3 pTSimulus.py 160000 200 -c 4 --mpi > Tests/simulus160000p8.out
mpiexec --hostfile myhosts4 -np 16 python3 pTSimulus.py 160000 200 -c 4 --mpi > Tests/simulus160000p16.out

mpiexec --hostfile myhosts1 -np 2 python3 pTSimulus.py 250000 200 -c 4 --mpi > Tests/simulus250000p2.out
mpiexec --hostfile myhosts2 -np 4 python3 pTSimulus.py 250000 200 -c 4 --mpi > Tests/simulus250000p4.out
mpiexec --hostfile myhosts3 -np 8 python3 pTSimulus.py 250000 200 -c 4 --mpi > Tests/simulus250000p8.out
mpiexec --hostfile myhosts4 -np 16 python3 pTSimulus.py 250000 200 -c 4 --mpi > Tests/simulus250000p16.out
