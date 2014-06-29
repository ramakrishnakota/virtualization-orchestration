virtualization-orchestration
============================
echo installing software<br>
#apt-get install flask<br>
#apt-get install python-bottle<br>
echo Run cloud app<br>
python src/sample.py $1 $2 $3<br>
echo server running port 50000<br>
echo Opening browser to manage cloud service<br>
echo gnome-open http://localhost:50000<br>
