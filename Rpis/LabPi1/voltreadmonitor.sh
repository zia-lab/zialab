sleep 20
until python3 /usr/local/bin/voltread; do
 echo "Server crashed with exit code $?.  Respawning.." >&2
 sleep 1
done
