cwd=$(pwd)
echo "Current working directory $cwd"

echo "Stopping server just in case port 8000 is open"
PORT=8000
PID=$(lsof -ti tcp:$PORT)
if [ -n "$PID" ]; then
    kill $PID
fi

cd $1/code/ChemFH
echo "Starting server in the background..."
python manage.py runserver 8000 &
SERVER_PID=$!

echo "Waiting for server to start..."
sleep 5

echo "Performing query..."
cd $cwd
python $1/code/main.py $2 $3

echo "Stopping server..."
kill $SERVER_PID

cd $cwd
echo "Done!"
