sleep 20
until python3 /usr/local/bin/remotePD; do
 echo "Server crashed with exit code $?.  Respawning.." >&2
 sleep 1
done
